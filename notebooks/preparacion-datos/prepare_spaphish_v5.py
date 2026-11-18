"""Prepara el corpus binario inicial a partir de SpaPhish V5.

El CSV original se trata como inmutable. El script no lee SpearPhishMX, no
modifica etiquetas y no entrena modelos.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.neighbors import NearestNeighbors


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "notebooks/data/spanish-dataset/SpanishDataset.csv"
OUTPUT_DIR = ROOT / "notebooks/data/processed/spaphish_v5"
CORPUS_PATH = OUTPUT_DIR / "spaphish_v5_corpus.csv"
MANIFEST_PATH = OUTPUT_DIR / "manifest.json"
GROUP_REVIEW_PATH = OUTPUT_DIR / "group_review.csv"
NEAR_CANDIDATES_PATH = OUTPUT_DIR / "near_duplicate_candidates.csv"
EXCLUSIONS_PATH = OUTPUT_DIR / "exclusions.csv"

SOURCE_SHA256 = "656b2245d58da72d640680e5c2a168673a130b38607f2a427c773bbb167e995e"
VERSION = 5
DOI = "10.17632/hz2d6gz7pc.5"
LICENSE = "CC BY 4.0"
SEED = 42
APPROX_GROUP_THRESHOLD = 0.95
CANDIDATE_THRESHOLD = 0.90

EMAIL_RE = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")
URL_RE = re.compile(r"(?i)\b(?:https?://|www\.)\S+")
PHONE_RE = re.compile(r"(?<!\d)(?:\+?\d[\d\s().-]{7,}\d)(?!\d)")
ENCODING_WARNING_RE = re.compile(r"(?:Ã.|Â.|â€|ðŸ|\ufffd)")

PERSUASION_BASE = {
    "authority",
    "social_proof",
    "liking_similarity_deception",
    "commitment_integrity_reciprocation",
    "distraction",
}


class UnionFind:
    def __init__(self, size: int) -> None:
        self.parent = list(range(size))

    def find(self, item: int) -> int:
        while self.parent[item] != item:
            self.parent[item] = self.parent[self.parent[item]]
            item = self.parent[item]
        return item

    def union(self, left: int, right: int) -> None:
        left_root = self.find(left)
        right_root = self.find(right)
        if left_root != right_root:
            self.parent[right_root] = left_root


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize_comparison(value: object) -> str:
    text = "" if pd.isna(value) else str(value)
    text = unicodedata.normalize("NFKC", text).lower()
    return re.sub(r"\s+", " ", text).strip()


def template_comparison(text: str) -> str:
    text = EMAIL_RE.sub(" <email> ", text)
    text = URL_RE.sub(" <url> ", text)
    text = PHONE_RE.sub(" <phone> ", text)
    text = re.sub(r"\b\d+(?:[.,:/#-]\d+)*\b", " <number> ", text)
    return re.sub(r"\s+", " ", text).strip()


def normalize_model_text(value: str) -> str:
    """Transformación mínima; preserva URL, números, dominios y Unicode."""
    return value.replace("\r\n", "\n").replace("\r", "\n").strip()


def combine_text(subject: object, body: object) -> tuple[str, str]:
    raw_subject = "" if pd.isna(subject) else str(subject)
    raw_body = "" if pd.isna(body) else str(body)
    original = raw_body if not raw_subject else f"{raw_subject}\n\n{raw_body}"
    processed_subject = normalize_model_text(raw_subject)
    processed_body = normalize_model_text(raw_body)
    processed = processed_body if not processed_subject else f"{processed_subject}\n\n{processed_body}"
    return original, processed


def stable_group_id(record_ids: list[str]) -> str:
    payload = "\n".join(sorted(record_ids)).encode("utf-8")
    return "spaphish-group-" + hashlib.sha256(payload).hexdigest()[:16]


def build_similarity(texts: pd.Series) -> list[tuple[int, int, float]]:
    vectorizer = TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(3, 5),
        min_df=2,
        max_features=60_000,
        sublinear_tf=True,
        dtype=np.float32,
    )
    matrix = vectorizer.fit_transform(texts)
    neighbors = NearestNeighbors(metric="cosine", algorithm="brute")
    neighbors.fit(matrix)
    distances, indices = neighbors.radius_neighbors(
        matrix, radius=1.0 - CANDIDATE_THRESHOLD, sort_results=True
    )
    pairs: dict[tuple[int, int], float] = {}
    for left, (row_distances, row_indices) in enumerate(zip(distances, indices)):
        for distance, right in zip(row_distances, row_indices):
            right = int(right)
            if left == right:
                continue
            key = (min(left, right), max(left, right))
            similarity = float(1.0 - distance)
            pairs[key] = max(pairs.get(key, 0.0), similarity)
    ordered = [(left, right, score) for (left, right), score in pairs.items()]
    ordered.sort(key=lambda item: (-item[2], item[0], item[1]))
    return ordered


def column_audit(columns: list[str]) -> list[dict]:
    audit = []
    for column in columns:
        if column == "Label":
            role = "target"
            use = "Mapear sin cambios a target; nunca usar como predictor."
        elif column == "hash":
            role = "identifier"
            use = "Usar solo en record_id y trazabilidad; excluir como predictor."
        elif column in {"subject", "body"}:
            role = "base_predictor_source"
            use = "Combinar en text preservando URL, números, dominios y Unicode."
        elif column.startswith("justif_") or column in PERSUASION_BASE or any(
            column == f"{name}_{suffix}" for name in PERSUASION_BASE for suffix in "ABC"
        ):
            role = "psychological_annotation"
            use = "Excluir: anotación posterior a la lectura del mensaje y fuga del objetivo."
        elif column == "date":
            role = "metadata_reserved"
            use = "Excluir del modelo base: posible señal temporal/fuente y 24 valores nulos."
        else:
            role = "technical_metadata_reserved"
            use = "Excluir del modelo textual base; evaluar después en una ablación controlada."
        audit.append({"column": column, "role": role, "decision": use})
    return audit


def assign_splits(corpus: pd.DataFrame) -> tuple[pd.Series, dict]:
    splitter = StratifiedGroupKFold(n_splits=20, shuffle=True, random_state=SEED)
    fold_for_row = np.full(len(corpus), -1, dtype=int)
    dummy = np.zeros((len(corpus), 1), dtype=np.int8)
    for fold, (_, test_indices) in enumerate(
        splitter.split(dummy, corpus["target"], groups=corpus["group_id"])
    ):
        fold_for_row[test_indices] = fold
    if (fold_for_row < 0).any():
        raise RuntimeError("No se asignaron todas las filas a un fold.")
    split = pd.Series(
        np.where(fold_for_row < 14, "train", np.where(fold_for_row < 17, "validation", "test")),
        index=corpus.index,
        dtype="string",
    )
    return split, {
        "method": "StratifiedGroupKFold de 20 folds; 14 train, 3 validation, 3 test",
        "seed": SEED,
        "target_proportions": {"train": 0.70, "validation": 0.15, "test": 0.15},
        "fold_mapping": {"train": list(range(0, 14)), "validation": [14, 15, 16], "test": [17, 18, 19]},
    }


def prepare() -> dict:
    if file_sha256(SOURCE) != SOURCE_SHA256:
        raise ValueError("El SHA-256 de SpaPhish no coincide con la versión 5 esperada.")

    raw = pd.read_csv(SOURCE)
    if raw.shape != (1395, 47):
        raise ValueError(f"Estructura inesperada: {raw.shape}")
    if raw["hash"].isna().any() or not raw["hash"].is_unique:
        raise ValueError("Los hashes deben existir y ser únicos.")
    if not raw["Label"].isin([0, 1]).all():
        raise ValueError("Label debe contener únicamente 0 y 1.")

    combined = [combine_text(subject, body) for subject, body in zip(raw["subject"], raw["body"])]
    original_text = pd.Series([item[0] for item in combined], dtype="string")
    model_text = pd.Series([item[1] for item in combined], dtype="string")
    if model_text.str.strip().eq("").any():
        raise ValueError("No se permiten textos procesados vacíos.")

    record_ids = "spaphish:" + raw["hash"].astype("string")
    comparison_text = model_text.map(normalize_comparison)
    comparison_subject = raw["subject"].fillna("").map(normalize_comparison)
    template_text = comparison_text.map(template_comparison)

    approximate_pairs = build_similarity(comparison_text)
    union = UnionFind(len(raw))
    group_rules: dict[tuple[int, int], set[str]] = defaultdict(set)

    exact_groups = 0
    for _, members in pd.Series(range(len(raw))).groupby(comparison_text):
        members = list(map(int, members))
        if len(members) > 1:
            exact_groups += 1
            for member in members[1:]:
                union.union(members[0], member)
                group_rules[(min(members[0], member), max(members[0], member))].add("exact_normalized")

    template_groups = 0
    for _, members in pd.Series(range(len(raw))).groupby(template_text):
        members = list(map(int, members))
        if len(members) > 1:
            template_groups += 1
            for member in members[1:]:
                union.union(members[0], member)
                group_rules[(min(members[0], member), max(members[0], member))].add("exact_template")

    for left, right, similarity in approximate_pairs:
        # La similitud alta por sí sola puede provenir de pies institucionales
        # extensos. Solo se autoagrupa cuando también coincide el asunto; las
        # plantillas exactas ya fueron agrupadas en el bloque anterior.
        same_subject = comparison_subject.iloc[left] == comparison_subject.iloc[right]
        if similarity >= APPROX_GROUP_THRESHOLD and same_subject:
            union.union(left, right)
            group_rules[(left, right)].add("cosine_ge_0.95_same_subject")

    components: dict[int, list[int]] = defaultdict(list)
    for row in range(len(raw)):
        components[union.find(row)].append(row)

    group_id_by_row: dict[int, str] = {}
    for members in components.values():
        group_id = stable_group_id(record_ids.iloc[members].tolist())
        for member in members:
            group_id_by_row[member] = group_id

    corpus = pd.DataFrame(
        {
            "text_original": original_text,
            "text": model_text,
            "target": raw["Label"].astype("int8"),
            "language": "es",
            "source_dataset": "spaphish_v5",
            "record_id": record_ids,
            "group_id": pd.Series(group_id_by_row).sort_index().astype("string"),
        }
    )

    group_label_counts = corpus.groupby("group_id")["target"].nunique()
    if group_label_counts.gt(1).any():
        raise ValueError("Hay grupos con conflictos de etiqueta; se requiere adjudicación.")

    corpus["split"], split_protocol = assign_splits(corpus)
    overlap = corpus.groupby("group_id")["split"].nunique()
    if overlap.gt(1).any():
        raise RuntimeError("Un group_id aparece en más de una partición.")

    edge_scores: dict[tuple[int, int], float] = {
        (left, right): similarity for left, right, similarity in approximate_pairs
    }
    group_rows = []
    for members in sorted(components.values(), key=lambda values: min(values)):
        if len(members) == 1:
            continue
        group_id = group_id_by_row[members[0]]
        member_set = set(members)
        applicable_rules = set()
        scores = []
        for edge, rules in group_rules.items():
            if edge[0] in member_set and edge[1] in member_set:
                applicable_rules.update(rules)
                if edge in edge_scores:
                    scores.append(edge_scores[edge])
        group_rows.append(
            {
                "group_id": group_id,
                "group_size": len(members),
                "target": int(corpus.loc[members[0], "target"]),
                "member_record_ids": "|".join(sorted(corpus.loc[members, "record_id"].tolist())),
                "rules": "|".join(sorted(applicable_rules)),
                "subject_variants": int(comparison_subject.iloc[members].nunique()),
                "max_cosine": round(max(scores), 6) if scores else "",
                "min_grouping_cosine": round(min(scores), 6) if scores else "",
                "label_conflict": False,
                "review_status": "accepted_conservative_group",
            }
        )
    group_review = pd.DataFrame(group_rows)

    candidate_rows = []
    for left, right, similarity in approximate_pairs:
        same_group = corpus.loc[left, "group_id"] == corpus.loc[right, "group_id"]
        same_subject = comparison_subject.iloc[left] == comparison_subject.iloc[right]
        cross_split = corpus.loc[left, "split"] != corpus.loc[right, "split"]
        if same_group:
            decision = "grouped"
            reason = "same_component_after_conservative_grouping"
        elif similarity >= APPROX_GROUP_THRESHOLD and not same_subject:
            decision = "pending_semantic_review"
            reason = "cosine>=0.95_but_subject_differs"
        else:
            decision = "pending_threshold_review"
            reason = "0.90<=cosine<0.95_not_auto_grouped"
        candidate_rows.append(
            {
                "left_record_id": corpus.loc[left, "record_id"],
                "right_record_id": corpus.loc[right, "record_id"],
                "cosine_similarity": round(similarity, 6),
                "same_normalized_subject": bool(same_subject),
                "same_target": bool(corpus.loc[left, "target"] == corpus.loc[right, "target"]),
                "same_group": bool(same_group),
                "cross_split": bool(cross_split),
                "decision": decision,
                "reason": reason,
            }
        )
    candidates = pd.DataFrame(candidate_rows)

    exclusions = pd.DataFrame(columns=["record_id", "reason", "detail"])
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    corpus.to_csv(CORPUS_PATH, index=False, encoding="utf-8", lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
    group_review.to_csv(GROUP_REVIEW_PATH, index=False, encoding="utf-8", lineterminator="\n")
    candidates.to_csv(NEAR_CANDIDATES_PATH, index=False, encoding="utf-8", lineterminator="\n")
    exclusions.to_csv(EXCLUSIONS_PATH, index=False, encoding="utf-8", lineterminator="\n")

    split_counts = corpus.groupby(["split", "target"]).size().unstack(fill_value=0)
    split_summary = {}
    for split_name in ("train", "validation", "test"):
        subset = corpus[corpus["split"] == split_name]
        split_summary[split_name] = {
            "records": int(len(subset)),
            "proportion": round(len(subset) / len(corpus), 6),
            "target_0": int(split_counts.loc[split_name, 0]),
            "target_1": int(split_counts.loc[split_name, 1]),
            "groups": int(subset["group_id"].nunique()),
        }

    multi_groups = group_review
    manifest = {
        "dataset": {
            "name": "SpaPhish",
            "version": VERSION,
            "doi": DOI,
            "license": LICENSE,
            "source_path": str(SOURCE.relative_to(ROOT)).replace("\\", "/"),
            "source_sha256": SOURCE_SHA256,
            "source_records": int(len(raw)),
            "source_columns": int(raw.shape[1]),
        },
        "records": {
            "original": int(len(raw)),
            "conserved": int(len(corpus)),
            "excluded": int(len(exclusions)),
            "exclusion_reasons": {},
            "missing_subject_conserved": int(raw["subject"].isna().sum()),
            "missing_body": int(raw["body"].isna().sum()),
            "encoding_warning_records_conserved": int(model_text.str.contains(ENCODING_WARNING_RE, regex=True).sum()),
        },
        "schema": list(corpus.columns),
        "feature_contract": {
            "base_predictors": ["text"],
            "target": "target",
            "non_predictive_tracking": ["text_original", "language", "source_dataset", "record_id", "group_id", "split"],
            "column_audit": column_audit(raw.columns.tolist()),
        },
        "transformations": [
            "Verificar SHA-256 y estructura SpaPhish V5.",
            "Conservar text_original antes de la normalización mínima.",
            "Sustituir asunto nulo por cadena vacía; conservar el cuerpo completo.",
            "Normalizar solo finales de línea y espacios exteriores en text.",
            "Combinar asunto y cuerpo con dos saltos de línea.",
            "Preservar URL, dominios, números, signos, mayúsculas, acentos y caracteres Unicode.",
            "Mapear Label sin cambios a target.",
            "Asignar record_id desde el hash de origen y group_id antes de particionar.",
        ],
        "duplicates_and_groups": {
            "exact_normalized_groups": exact_groups,
            "exact_template_groups": template_groups,
            "near_candidate_pairs_cosine_ge_0.90": int(len(approximate_pairs)),
            "near_pairs_cosine_ge_0.95": int(sum(score >= APPROX_GROUP_THRESHOLD for _, _, score in approximate_pairs)),
            "near_grouping_pairs_cosine_ge_0.95_same_subject": int(
                sum(
                    score >= APPROX_GROUP_THRESHOLD
                    and comparison_subject.iloc[left] == comparison_subject.iloc[right]
                    for left, right, score in approximate_pairs
                )
            ),
            "multi_record_groups": int(len(multi_groups)),
            "records_in_multi_record_groups": int(multi_groups["group_size"].sum()) if len(multi_groups) else 0,
            "max_group_size": int(multi_groups["group_size"].max()) if len(multi_groups) else 1,
            "total_groups": int(corpus["group_id"].nunique()),
            "label_conflict_groups": 0,
            "pending_candidate_pairs": int((~candidates["same_group"]).sum()),
            "pending_candidate_pairs_cross_split": int(
                ((~candidates["same_group"]) & candidates["cross_split"]).sum()
            ),
        },
        "labels": {
            "overall": {str(key): int(value) for key, value in corpus["target"].value_counts().sort_index().items()},
            "by_split": split_summary,
        },
        "partition": {
            **split_protocol,
            "actual": split_summary,
            "group_overlap_count": int(overlap.gt(1).sum()),
        },
        "outputs": {
            "corpus": str(CORPUS_PATH.relative_to(ROOT)).replace("\\", "/"),
            "corpus_sha256": file_sha256(CORPUS_PATH),
            "group_review": str(GROUP_REVIEW_PATH.relative_to(ROOT)).replace("\\", "/"),
            "group_review_sha256": file_sha256(GROUP_REVIEW_PATH),
            "near_candidates": str(NEAR_CANDIDATES_PATH.relative_to(ROOT)).replace("\\", "/"),
            "near_candidates_sha256": file_sha256(NEAR_CANDIDATES_PATH),
            "exclusions": str(EXCLUSIONS_PATH.relative_to(ROOT)).replace("\\", "/"),
            "exclusions_sha256": file_sha256(EXCLUSIONS_PATH),
        },
        "reproducibility": {
            "script": str(Path(__file__).resolve().relative_to(ROOT)).replace("\\", "/"),
            "script_sha256": file_sha256(Path(__file__).resolve()),
            "preparation_date": "2026-11-17",
        },
        "limitations": [
            "Los pares con coseno >= 0.90 que no cumplen la regla conservadora permanecen pendientes de revisión antes de ML.",
            "La detección de plantillas es heurística; group_id evita fuga conocida, no prueba independencia semántica total.",
            f"Los {int(model_text.str.contains(ENCODING_WARNING_RE, regex=True).sum())} avisos conservadores de codificación se mantienen para no borrar posibles señales de ofuscación.",
        ],
    }
    MANIFEST_PATH.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return manifest


def main() -> None:
    manifest = prepare()
    print(json.dumps({"records": manifest["records"], "partition": manifest["partition"]["actual"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
