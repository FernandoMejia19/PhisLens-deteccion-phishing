"""Validacion reproducible de SpaPhish y SpearPhishMX.

El script es de solo lectura sobre los CSV originales y escribe un resumen JSON
sin cuerpos completos de mensajes. No entrena modelos ni genera el corpus final.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors


ROOT = Path(__file__).resolve().parents[2]
SPA_PATH = ROOT / "notebooks/data/spanish-dataset/SpanishDataset.csv"
SPEAR_PATH = ROOT / "notebooks/data/spear-pish/SpearPhishMX_dataset_publico.csv"
DEFAULT_OUTPUT = ROOT / "notebooks/reports/data/spanish_corpus_validation.json"

EMAIL_RE = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")
URL_RE = re.compile(r"(?i)\b(?:https?://|www\.)\S+")
DEFANGED_URL_RE = re.compile(r"(?i)\b(?:hxxps?://|\w+\[\.\]\w+)\S*")
PHONE_RE = re.compile(r"(?<!\d)(?:\+?\d[\d\s().-]{7,}\d)(?!\d)")
MOJIBAKE_RE = re.compile(r"(?:Ã.|Â.|â€|ðŸ|\ufffd)")


def normalize_text(value: object) -> str:
    text = "" if pd.isna(value) else str(value)
    text = unicodedata.normalize("NFKC", text).lower()
    return re.sub(r"\s+", " ", text).strip()


def template_text(text: str) -> str:
    text = EMAIL_RE.sub(" <email> ", text)
    text = URL_RE.sub(" <url> ", text)
    text = DEFANGED_URL_RE.sub(" <url> ", text)
    text = PHONE_RE.sub(" <phone> ", text)
    text = re.sub(r"\b\d+(?:[.,:/-]\d+)*\b", " <num> ", text)
    return re.sub(r"\s+", " ", text).strip()


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def redact_excerpt(text: str, limit: int = 180) -> str:
    text = EMAIL_RE.sub("<EMAIL>", text)
    text = URL_RE.sub("<URL>", text)
    text = DEFANGED_URL_RE.sub("<URL_DESACTIVADA>", text)
    text = PHONE_RE.sub("<TELEFONO>", text)
    text = re.sub(r"\b\d{5,}\b", "<NUMERO>", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit] + ("…" if len(text) > limit else "")


def prepare_frames() -> tuple[pd.DataFrame, pd.DataFrame]:
    spa_raw = pd.read_csv(SPA_PATH)
    spear_raw = pd.read_csv(SPEAR_PATH, sep=";")

    spa = pd.DataFrame(
        {
            "source_dataset": "spanish_phishing",
            "source_row": np.arange(len(spa_raw)),
            "source_hash": spa_raw["hash"].astype("string"),
            "subject": spa_raw["subject"].astype("string"),
            "body": spa_raw["body"].astype("string"),
            "target": spa_raw["Label"],
        }
    )
    spear = pd.DataFrame(
        {
            "source_dataset": "spear_phish_mx",
            "source_row": np.arange(len(spear_raw)),
            "source_hash": spear_raw["hash"].astype("string"),
            "subject": spear_raw["asunto"].astype("string"),
            "body": spear_raw["cuerpo_sanitizado"].astype("string"),
            "target": spear_raw["etiqueta"],
        }
    )
    for frame in (spa, spear):
        frame["subject_norm"] = frame["subject"].map(normalize_text)
        frame["body_norm"] = frame["body"].map(normalize_text)
        frame["text_norm"] = (
            frame["subject_norm"] + "\n" + frame["body_norm"]
        ).str.strip()
        frame["text_digest"] = frame["text_norm"].map(digest)
        frame["template_digest"] = frame["text_norm"].map(template_text).map(digest)
    return spa, spear


def duplicate_groups(frame: pd.DataFrame, column: str) -> dict:
    sizes = frame.groupby(column, dropna=False).size()
    dup = sizes[sizes > 1]
    return {
        "groups": int(len(dup)),
        "records_in_groups": int(dup.sum()),
        "surplus_records": int((dup - 1).sum()),
        "max_group_size": int(dup.max()) if len(dup) else 0,
    }


def cross_exact(spa: pd.DataFrame, spear: pd.DataFrame, column: str) -> dict:
    left = set(spa[column])
    right = set(spear[column])
    common = left & right
    return {
        "shared_groups": len(common),
        "spanish_phishing_records": int(spa[column].isin(common).sum()),
        "spear_phish_mx_records": int(spear[column].isin(common).sum()),
    }


def nearest_pairs(spa: pd.DataFrame, spear: pd.DataFrame) -> dict:
    all_text = pd.concat([spa["text_norm"], spear["text_norm"]], ignore_index=True)
    vectorizer = TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(3, 5),
        min_df=2,
        max_features=60_000,
        sublinear_tf=True,
        dtype=np.float32,
    )
    matrix = vectorizer.fit_transform(all_text)
    a = matrix[: len(spa)]
    b = matrix[len(spa) :]
    nn = NearestNeighbors(metric="cosine", algorithm="brute", n_neighbors=min(5, len(spear)))
    nn.fit(b)
    distances, indices = nn.kneighbors(a)

    pairs = []
    for i in range(len(spa)):
        for distance, j in zip(distances[i], indices[i]):
            similarity = float(1.0 - distance)
            if similarity >= 0.75:
                pairs.append(
                    {
                        "spanish_row": int(spa.iloc[i]["source_row"]),
                        "spanish_target": int(spa.iloc[i]["target"]),
                        "spear_row": int(spear.iloc[j]["source_row"]),
                        "spear_target": int(spear.iloc[j]["target"]),
                        "similarity": round(similarity, 6),
                    }
                )
    pairs.sort(key=lambda item: item["similarity"], reverse=True)
    best = 1.0 - distances[:, 0]
    best_pairs = []
    for i, (distance, j) in enumerate(zip(distances[:, 0], indices[:, 0])):
        best_pairs.append(
            {
                "spanish_row": int(spa.iloc[i]["source_row"]),
                "spanish_target": int(spa.iloc[i]["target"]),
                "spear_row": int(spear.iloc[j]["source_row"]),
                "spear_target": int(spear.iloc[j]["target"]),
                "similarity": float(1.0 - distance),
            }
        )

    threshold_summary = {}
    for threshold in (0.75, 0.80, 0.85, 0.90, 0.95):
        selected = [item for item in best_pairs if item["similarity"] >= threshold]
        label_pairs = Counter(
            f"{item['spanish_target']}->{item['spear_target']}" for item in selected
        )
        threshold_summary[f"{threshold:.2f}"] = {
            "spanish_records_with_best_match": len(selected),
            "same_label": sum(
                item["spanish_target"] == item["spear_target"] for item in selected
            ),
            "different_label": sum(
                item["spanish_target"] != item["spear_target"] for item in selected
            ),
            "label_pairs": dict(sorted(label_pairs.items())),
        }

    conflict_pairs = sorted(
        (item for item in best_pairs if item["spanish_target"] != item["spear_target"]),
        key=lambda item: item["similarity"],
        reverse=True,
    )
    return {
        "method": "TF-IDF de caracteres (3-5) y similitud coseno; máximo vecino cruzado",
        "vocabulary_size": int(matrix.shape[1]),
        "best_similarity_distribution": {
            "min": round(float(best.min()), 6),
            "median": round(float(np.median(best)), 6),
            "p90": round(float(np.quantile(best, 0.90)), 6),
            "p95": round(float(np.quantile(best, 0.95)), 6),
            "p99": round(float(np.quantile(best, 0.99)), 6),
            "max": round(float(best.max()), 6),
        },
        "candidate_pair_counts_all_five_neighbors": {
            threshold: int(sum(pair["similarity"] >= float(threshold) for pair in pairs))
            for threshold in ("0.75", "0.80", "0.85", "0.90", "0.95")
        },
        "best_match_threshold_summary": threshold_summary,
        "top_pairs": pairs[:20],
        "top_conflicting_best_pairs": [
            {**item, "similarity": round(item["similarity"], 6)}
            for item in conflict_pairs[:20]
        ],
    }


def privacy_counts(frame: pd.DataFrame) -> dict:
    texts = frame["text_norm"]
    return {
        "records_with_email_pattern": int(texts.str.contains(EMAIL_RE, regex=True).sum()),
        "records_with_phone_pattern": int(texts.str.contains(PHONE_RE, regex=True).sum()),
        "records_with_active_url_pattern": int(texts.str.contains(URL_RE, regex=True).sum()),
        "records_with_defanged_url_pattern": int(texts.str.contains(DEFANGED_URL_RE, regex=True).sum()),
        "note": "Los patrones son indicadores técnicos; no prueban que los datos sean reales ni identificables.",
    }


def frame_quality(frame: pd.DataFrame) -> dict:
    invalid_label = ~frame["target"].isin([0, 1])
    empty_text = frame["text_norm"].eq("")
    missing_subject = frame["subject_norm"].eq("")
    missing_body = frame["body_norm"].eq("")
    encoding = frame["text_norm"].str.contains(MOJIBAKE_RE, regex=True)
    dup_text = frame.duplicated("text_digest", keep=False)
    dup_hash = frame["source_hash"].duplicated(keep=False)
    pending = invalid_label | empty_text | encoding | dup_text | dup_hash
    return {
        "records": int(len(frame)),
        "invalid_labels": int(invalid_label.sum()),
        "empty_text": int(empty_text.sum()),
        "missing_subject": int(missing_subject.sum()),
        "missing_body": int(missing_body.sum()),
        "encoding_warning_records": int(encoding.sum()),
        "duplicate_text_records": int(dup_text.sum()),
        "duplicate_hash_records": int(dup_hash.sum()),
        "preliminarily_conservable": int((~pending).sum()),
        "pending_manual_review": int(pending.sum()),
        "automatically_discarded": 0,
    }


def samples(frame: pd.DataFrame) -> list[dict]:
    result = []
    for target in (0, 1):
        subset = frame[frame["target"] == target].copy()
        lengths = subset["text_norm"].str.len()
        for quantile in (0.10, 0.50, 0.90):
            wanted = lengths.quantile(quantile)
            idx = (lengths - wanted).abs().idxmin()
            row = frame.loc[idx]
            result.append(
                {
                    "source_row": int(row["source_row"]),
                    "target": int(target),
                    "length_quantile": quantile,
                    "subject_excerpt_redacted": redact_excerpt(str(row["subject"])),
                    "body_excerpt_redacted": redact_excerpt(str(row["body"])),
                }
            )
    return result


def spear_leakage_table() -> dict:
    raw = pd.read_csv(SPEAR_PATH, sep=";")
    table = pd.crosstab(raw["dirigido_a_persona_v2"], raw["etiqueta"], dropna=False)
    return {
        str(index): {str(column): int(value) for column, value in row.items()}
        for index, row in table.iterrows()
    }


def build_summary() -> dict:
    spa, spear = prepare_frames()
    combined = pd.concat([spa, spear], ignore_index=True)
    return {
        "inputs": {
            "spanish_phishing": str(SPA_PATH.relative_to(ROOT)).replace("\\", "/"),
            "spear_phish_mx": str(SPEAR_PATH.relative_to(ROOT)).replace("\\", "/"),
        },
        "sha256": {
            "spanish_phishing": hashlib.sha256(SPA_PATH.read_bytes()).hexdigest(),
            "spear_phish_mx": hashlib.sha256(SPEAR_PATH.read_bytes()).hexdigest(),
        },
        "label_distribution": {
            "spanish_phishing": {str(k): int(v) for k, v in spa["target"].value_counts().sort_index().items()},
            "spear_phish_mx": {str(k): int(v) for k, v in spear["target"].value_counts().sort_index().items()},
        },
        "quality": {
            "spanish_phishing": frame_quality(spa),
            "spear_phish_mx": frame_quality(spear),
        },
        "duplicates": {
            "spanish_phishing_exact_text": duplicate_groups(spa, "text_digest"),
            "spear_phish_mx_exact_text": duplicate_groups(spear, "text_digest"),
            "combined_exact_text": duplicate_groups(combined, "text_digest"),
            "combined_template": duplicate_groups(combined, "template_digest"),
            "cross_exact_text": cross_exact(spa, spear, "text_digest"),
            "cross_exact_template": cross_exact(spa, spear, "template_digest"),
            "near_cross_dataset": nearest_pairs(spa, spear),
        },
        "privacy_patterns": {
            "spanish_phishing": privacy_counts(spa),
            "spear_phish_mx": privacy_counts(spear),
        },
        "potential_leakage": {
            "spear_dirigido_a_persona_v2_by_target": spear_leakage_table(),
            "spanish_annotation_columns": 35,
            "warning": "Campos de anotación o derivados posteriores a la lectura del mensaje no deben ser predictores del modelo base.",
        },
        "representative_samples": {
            "spanish_phishing": samples(spa),
            "spear_phish_mx": samples(spear),
        },
        "unified_schema": {
            "text": "subject/asunto + salto de línea + body/cuerpo_sanitizado, con faltantes como cadena vacía",
            "target": "int8: 0=legítimo, 1=phishing (en SpearPhishMX, spear-phishing)",
            "language": "es",
            "source_dataset": "spanish_phishing | spear_phish_mx",
            "record_id": "prefijo de fuente + source_row + hash; no usar solo hash",
            "group_id": "componente de duplicados exactos/plantillas; recalcular antes de particionar",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    summary = build_summary()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Resumen escrito en {args.output}")


if __name__ == "__main__":
    main()
