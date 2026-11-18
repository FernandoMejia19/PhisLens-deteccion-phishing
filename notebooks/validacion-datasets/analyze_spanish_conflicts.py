"""Analiza conflictos de alta similitud entre SpaPhish y SpearPhishMX.

Lee los CSV originales sin modificarlos y genera un registro sin cuerpos completos.
No cambia etiquetas, no entrena modelos y no construye el corpus definitivo.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors


ROOT = Path(__file__).resolve().parents[2]
SPA_PATH = ROOT / "notebooks/data/spanish-dataset/SpanishDataset.csv"
SPEAR_PATH = ROOT / "notebooks/data/spear-pish/SpearPhishMX_dataset_publico.csv"
OUTPUT = ROOT / "notebooks/reports/data/spanish_conflict_analysis.json"

EMAIL_RE = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")
ACTIVE_URL_RE = re.compile(r"(?i)\bhttps?://\S+")
DEFANGED_URL_RE = re.compile(r"(?i)\b(?:hxxps?://|[\w-]+\[\.\][\w.-]+)\S*")
PHONE_RE = re.compile(r"(?<!\d)(?:\+?\d[\d\s().-]{7,}\d)(?!\d)")
PLACEHOLDER_RE = re.compile(r"(?i)<(?:EMAIL|TELEFONO|RFC|CLABE|CUENTA|TARJETA|PII)>")
GREETING_RE = re.compile(
    r"(?is)^\s*(?:hola|estimad[oa](?:/a)?|apreciable|buen(?:os días|as tardes|as noches))"
    r"[^\n\r]{0,100}[,:]?\s*[\r\n]+"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize(value: object, remove_marks: bool = False) -> str:
    text = "" if pd.isna(value) else str(value)
    text = unicodedata.normalize("NFKC", text).lower()
    if remove_marks:
        text = "".join(
            char
            for char in unicodedata.normalize("NFKD", text)
            if unicodedata.category(char) not in {"Mn", "Cf", "Cc"}
        )
    return re.sub(r"\s+", " ", text).strip()


def canonicalize(text: str, recipient: object = None) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = GREETING_RE.sub(" ", text, count=1)
    if recipient is not None and not pd.isna(recipient):
        value = str(recipient).strip()
        if value:
            text = re.sub(re.escape(value), " <destinatario> ", text, flags=re.IGNORECASE)
    text = re.sub(r"(?i)hxxps?://", "http://", text)
    text = text.replace("[.]", ".")
    text = EMAIL_RE.sub(" <email> ", text)
    text = ACTIVE_URL_RE.sub(" <url> ", text)
    text = DEFANGED_URL_RE.sub(" <url> ", text)
    text = PHONE_RE.sub(" <telefono> ", text)
    text = PLACEHOLDER_RE.sub(" <pii> ", text)
    text = re.sub(r"\b\d+(?:[.,:/-]\d+)*\b", " <numero> ", text)
    return normalize(text, remove_marks=True)


def redact(value: object, recipient: object = None, limit: int = 160) -> str:
    text = "" if pd.isna(value) else str(value)
    if recipient is not None and not pd.isna(recipient):
        text = re.sub(re.escape(str(recipient)), "<DESTINATARIO>", text, flags=re.IGNORECASE)
    text = EMAIL_RE.sub("<EMAIL>", text)
    text = ACTIVE_URL_RE.sub("<URL>", text)
    text = DEFANGED_URL_RE.sub("<URL_DESACTIVADA>", text)
    text = PHONE_RE.sub("<TELEFONO>", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit] + ("…" if len(text) > limit else "")


def primary_cause(flags: list[str], canonical_similarity: float) -> str:
    if "personalizacion" in flags and ("defang" in flags or "sanitizacion_pii" in flags):
        return "personalizacion_y_sanitizacion"
    if "personalizacion" in flags:
        return "personalizacion"
    if "defang" in flags or "sanitizacion_pii" in flags:
        return "sanitizacion"
    if canonical_similarity >= 0.98:
        return "formato_unicode_o_espaciado"
    return "variacion_adicional_no_resuelta"


def build_analysis(threshold: float = 0.95) -> dict:
    spa = pd.read_csv(SPA_PATH)
    spear = pd.read_csv(SPEAR_PATH, sep=";")

    spa_text = (spa["subject"].fillna("").astype(str) + "\n" + spa["body"].fillna("").astype(str)).map(normalize)
    spear_text = (
        spear["asunto"].fillna("").astype(str)
        + "\n"
        + spear["cuerpo_sanitizado"].fillna("").astype(str)
    ).map(normalize)
    all_text = pd.concat([spa_text, spear_text], ignore_index=True)

    vectorizer = TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(3, 5),
        min_df=2,
        max_features=60_000,
        sublinear_tf=True,
        dtype=np.float32,
    )
    matrix = vectorizer.fit_transform(all_text)
    nn = NearestNeighbors(metric="cosine", algorithm="brute", n_neighbors=1)
    nn.fit(matrix[len(spa) :])
    distances, indices = nn.kneighbors(matrix[: len(spa)])

    pairs: list[dict] = []
    for spa_row, (distance, spear_row) in enumerate(zip(distances[:, 0], indices[:, 0])):
        similarity = float(1.0 - distance)
        if similarity < threshold:
            continue
        a = spa.iloc[spa_row]
        b = spear.iloc[int(spear_row)]
        a_text = str(a.get("subject", "")) + "\n" + str(a.get("body", ""))
        b_text = str(b.get("asunto", "")) + "\n" + str(b.get("cuerpo_sanitizado", ""))
        a_canonical = canonicalize(a_text)
        b_canonical = canonicalize(b_text, b.get("destinatario_detectado_v2"))
        canonical_similarity = SequenceMatcher(None, a_canonical, b_canonical, autojunk=False).ratio()

        flags: list[str] = []
        recipient = b.get("destinatario_detectado_v2")
        if bool(b.get("dirigido_a_persona_v2")) and not pd.isna(recipient):
            if normalize(recipient) not in normalize(a_text):
                flags.append("personalizacion")
        if ACTIVE_URL_RE.search(a_text) and DEFANGED_URL_RE.search(b_text):
            flags.append("defang")
        if PLACEHOLDER_RE.search(b_text) or len(EMAIL_RE.findall(a_text)) > len(EMAIL_RE.findall(b_text)):
            flags.append("sanitizacion_pii")
        if normalize(a.get("subject")) == normalize(b.get("asunto")):
            flags.append("asunto_igual")
        if canonical_similarity >= 0.98:
            flags.append("contenido_canonico_casi_igual")

        pairs.append(
            {
                "pair_id": f"conflict-{len(pairs) + 1:04d}",
                "spa_row": int(spa_row),
                "spa_record_id": f"spaphish:{a['hash']}",
                "spa_target": int(a["Label"]),
                "spear_row": int(spear_row),
                "spear_record_id": f"spearphishmx:{int(b['id_original'])}",
                "spear_hash": str(b["hash"]),
                "spear_target": int(b["etiqueta"]),
                "cosine_similarity": round(similarity, 6),
                "canonical_sequence_similarity": round(canonical_similarity, 6),
                "subject_equal_normalized": "asunto_igual" in flags,
                "directed_to_person": bool(b["dirigido_a_persona_v2"]),
                "change_flags": flags,
                "primary_cause": primary_cause(flags, canonical_similarity),
            }
        )

    label_pairs = Counter(f"{p['spa_target']}->{p['spear_target']}" for p in pairs)
    causes = Counter(p["primary_cause"] for p in pairs)
    flags = Counter(flag for p in pairs for flag in p["change_flags"])
    causes_by_transition = {
        transition: dict(
            sorted(
                Counter(
                    p["primary_cause"]
                    for p in pairs
                    if f"{p['spa_target']}->{p['spear_target']}" == transition
                ).items()
            )
        )
        for transition in sorted(label_pairs)
    }
    conflicts = [p for p in pairs if p["spa_target"] != p["spear_target"]]
    focus = [p for p in pairs if p["spa_target"] == 1 and p["spear_target"] == 0]

    samples = []
    selected_keys: set[tuple[int, int]] = set()
    for transition in ("0->0", "0->1", "1->0", "1->1"):
        subset = [p for p in pairs if f"{p['spa_target']}->{p['spear_target']}" == transition]
        for p in sorted(subset, key=lambda item: item["cosine_similarity"], reverse=True)[:2]:
            key = (p["spa_row"], p["spear_row"])
            if key in selected_keys:
                continue
            selected_keys.add(key)
            a = spa.iloc[p["spa_row"]]
            b = spear.iloc[p["spear_row"]]
            samples.append(
                {
                    **p,
                    "spa_subject_redacted": redact(a["subject"]),
                    "spear_subject_redacted": redact(b["asunto"], b["destinatario_detectado_v2"]),
                    "spa_body_redacted": redact(a["body"]),
                    "spear_body_redacted": redact(b["cuerpo_sanitizado"], b["destinatario_detectado_v2"]),
                }
            )

    exact_text = (
        spear["asunto"].fillna("").astype(str).map(normalize)
        + "\n"
        + spear["cuerpo_sanitizado"].fillna("").astype(str).map(normalize)
    )
    duplicate_rows = spear[exact_text.duplicated(keep=False)].copy()

    return {
        "method": {
            "threshold": threshold,
            "similarity": "TF-IDF de caracteres 3-5 y coseno; mejor vecino de cada SpaPhish en SpearPhishMX",
            "canonical_review": "NFKC, eliminación de marcas invisibles, saludo/destinatario, defang, PII y números",
            "warning": "La similitud y las reglas de cambio no demuestran origen común ni adjudican etiquetas.",
        },
        "inputs": {
            "spaphish_sha256": sha256(SPA_PATH),
            "spearphishmx_sha256": sha256(SPEAR_PATH),
        },
        "summary": {
            "pairs": len(pairs),
            "label_pairs": dict(sorted(label_pairs.items())),
            "same_label": len(pairs) - len(conflicts),
            "different_label": len(conflicts),
            "primary_causes": dict(sorted(causes.items())),
            "primary_causes_by_label_pair": causes_by_transition,
            "change_flags": dict(sorted(flags.items())),
            "spa1_to_spear0": {
                "pairs": len(focus),
                "directed_to_person_true": sum(p["directed_to_person"] for p in focus),
                "subject_equal": sum(p["subject_equal_normalized"] for p in focus),
                "canonical_similarity_ge_0_98": sum(
                    p["canonical_sequence_similarity"] >= 0.98 for p in focus
                ),
                "cause_counts": dict(sorted(Counter(p["primary_cause"] for p in focus).items())),
            },
            "spear_internal_exact_duplicates": {
                "records": int(len(duplicate_rows)),
                "groups": int(exact_text[exact_text.duplicated(keep=False)].nunique()),
                "surplus_records": int(len(duplicate_rows) - exact_text[exact_text.duplicated(keep=False)].nunique()),
                "label_conflicts": int(duplicate_rows.groupby(exact_text[exact_text.duplicated(keep=False)]).etiqueta.nunique().gt(1).sum()),
            },
        },
        "representative_samples_redacted": samples,
        "pair_registry": pairs,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--threshold", type=float, default=0.95)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    result = build_analysis(args.threshold)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Escrito: {args.output}")


if __name__ == "__main__":
    main()
