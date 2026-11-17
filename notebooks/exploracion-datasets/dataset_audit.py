"""Auditoría reproducible de los datasets locales de PhisLens.

El módulo sólo lee los CSV originales. Los resultados derivados se guardan fuera
de ``notebooks/data`` para mantener intactas las fuentes.
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = ROOT / "notebooks" / "data"
RESULTS_DIR = ROOT / "notebooks" / "reports" / "data"


@dataclass(frozen=True)
class DatasetSpec:
    slug: str
    path: str
    target: str
    text_columns: tuple[str, ...]
    sep: str = ","
    declared_language_column: str | None = None
    notes: str = ""


DATASETS: tuple[DatasetSpec, ...] = (
    DatasetSpec(
        "email_detection_50k",
        "email-detection-dataset/dataset_v2.csv",
        "label",
        ("subject", "email_body"),
        declared_language_column="language",
        notes="Copia ubicada en email-detection-dataset.",
    ),
    DatasetSpec(
        "phishing_email_detection_50k_copy",
        "PhishingEmailDetection50KEmails/phishing_email_detection_dataset_v2.csv",
        "label",
        ("subject", "email_body"),
        declared_language_column="language",
        notes="Copia ubicada en PhishingEmailDetection50KEmails.",
    ),
    DatasetSpec(
        "spam_multilingual_augmented",
        "spam/data-augmented.csv",
        "labels",
        ("text",),
        notes="Incluye una columna original y 21 columnas de traducciones.",
    ),
    DatasetSpec(
        "spam_spanish",
        "spam/data.csv",
        "labels",
        ("text",),
    ),
    DatasetSpec(
        "sms_spam_5971",
        "spam/Dataset_5971.csv",
        "LABEL",
        ("TEXT",),
    ),
    DatasetSpec(
        "spanish_phishing",
        "spanish-dataset/SpanishDataset.csv",
        "Label",
        ("subject", "body"),
    ),
    DatasetSpec(
        "spear_phish_mx",
        "spear-pish/SpearPhishMX_dataset_publico.csv",
        "etiqueta",
        ("asunto", "cuerpo_sanitizado"),
        sep=";",
    ),
)


ES_WORDS = {
    "de", "la", "el", "que", "en", "y", "para", "por", "su", "sus",
    "una", "un", "con", "cuenta", "correo", "mensaje", "usted", "hola",
    "gracias", "seguridad", "verificar", "acceso", "datos", "cliente",
}
EN_WORDS = {
    "the", "and", "to", "of", "in", "for", "your", "you", "is", "are",
    "account", "email", "message", "please", "security", "verify", "access",
    "data", "customer", "hello", "thanks", "with", "this", "from",
}
WORD_RE = re.compile(r"[a-záéíóúñü]+", re.IGNORECASE)
URL_RE = re.compile(r"(?:https?://|hxxps?://|www\[?\.\]?|www\.)\S+", re.IGNORECASE)
EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
PHONE_RE = re.compile(r"(?<!\w)(?:\+?\d[\s().-]*){7,15}(?!\w)")
MOJIBAKE_RE = re.compile(r"(?:�|Ã.|Â.|â€|ðŸ)")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_dataset(spec: DatasetSpec) -> pd.DataFrame:
    return pd.read_csv(DATA_ROOT / spec.path, sep=spec.sep, encoding="utf-8")


def combined_text(df: pd.DataFrame, columns: tuple[str, ...]) -> pd.Series:
    available = [column for column in columns if column in df.columns]
    if not available:
        return pd.Series("", index=df.index, dtype="string")
    text = df[available[0]].fillna("").astype(str)
    for column in available[1:]:
        text = text.str.cat(df[column].fillna("").astype(str), sep="\n")
    return text.str.strip()


def normalized_text(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).lower()
    value = re.sub(r"https?://\S+", " url ", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def language_guess(value: str) -> str:
    tokens = [token.lower() for token in WORD_RE.findall(value)]
    if len(tokens) < 4:
        return "indeterminado"
    es = sum(token in ES_WORDS for token in tokens)
    en = sum(token in EN_WORDS for token in tokens)
    if es >= 2 and es >= en * 1.5:
        return "es"
    if en >= 2 and en >= es * 1.5:
        return "en"
    return "indeterminado"


def count_values(series: pd.Series) -> dict[str, int]:
    return {str(key): int(value) for key, value in series.value_counts(dropna=False).items()}


def describe_numeric(series: pd.Series) -> dict[str, float | int | None]:
    clean = pd.to_numeric(series, errors="coerce").dropna()
    if clean.empty:
        return {key: None for key in ("count", "min", "q25", "median", "mean", "q75", "p95", "max")}
    quantiles = clean.quantile([0.25, 0.5, 0.75, 0.95])
    return {
        "count": int(clean.size),
        "min": float(clean.min()),
        "q25": float(quantiles.loc[0.25]),
        "median": float(quantiles.loc[0.5]),
        "mean": float(clean.mean()),
        "q75": float(quantiles.loc[0.75]),
        "p95": float(quantiles.loc[0.95]),
        "max": float(clean.max()),
    }


def safe_example(value: str, limit: int = 280) -> str:
    value = re.sub(r"https?://", "hxxp://", value, flags=re.IGNORECASE)
    value = EMAIL_RE.sub("[correo-oculto]", value)
    value = PHONE_RE.sub("[telefono-oculto]", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value[:limit] + ("…" if len(value) > limit else "")


def analyze_dataset(spec: DatasetSpec) -> dict[str, Any]:
    path = DATA_ROOT / spec.path
    df = load_dataset(spec)
    text = combined_text(df, spec.text_columns)
    normalized = text.map(normalized_text)
    chars = text.str.len()
    words = text.str.findall(WORD_RE).str.len()
    target = df[spec.target]

    conflicting = (
        pd.DataFrame({"text": normalized, "target": target.astype(str)})
        .query("text != ''")
        .groupby("text")["target"]
        .nunique()
    )

    class_length: dict[str, Any] = {}
    for label, indexes in target.groupby(target, dropna=False).groups.items():
        class_length[str(label)] = {
            "records": int(len(indexes)),
            "characters": describe_numeric(chars.loc[indexes]),
            "words": describe_numeric(words.loc[indexes]),
        }

    examples: dict[str, list[str]] = {}
    for label, indexes in target.groupby(target, dropna=False).groups.items():
        candidates = text.loc[indexes]
        candidates = candidates[candidates.str.len() > 0]
        if candidates.empty:
            examples[str(label)] = []
            continue
        order = (candidates.str.len() - candidates.str.len().median()).abs().sort_values().index[:2]
        examples[str(label)] = [safe_example(candidates.loc[index]) for index in order]

    declared_languages = None
    if spec.declared_language_column and spec.declared_language_column in df:
        declared_languages = count_values(df[spec.declared_language_column])

    translation_quality = None
    translation_columns = [column for column in df if column.startswith("text_")]
    if translation_columns:
        translation_quality = {}
        for column in translation_columns:
            values = df[column].fillna("").astype(str)
            translation_quality[column] = {
                "nulls": int(df[column].isna().sum()),
                "rows_with_mojibake": int(values.str.contains(MOJIBAKE_RE, regex=True).sum()),
                "mean_characters": round(float(values.str.len().mean()), 2),
            }

    leakage_checks: dict[str, Any] = {}
    if "phishing_probability" in df:
        leakage_checks["phishing_probability_by_target"] = {
            str(label): describe_numeric(group["phishing_probability"])
            for label, group in df.groupby(spec.target, dropna=False)
        }
    for column in ("url_reputation", "spf_status", "dkim_status", "dmarc_status", "spoofed_domain"):
        if column in df:
            leakage_checks[f"{column}_by_target"] = {
                str(label): count_values(group[column])
                for label, group in df.groupby(spec.target, dropna=False)
            }

    result: dict[str, Any] = {
        "spec": asdict(spec),
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "column_names": list(df.columns),
        "dtypes": {column: str(dtype) for column, dtype in df.dtypes.items()},
        "nulls": {column: int(value) for column, value in df.isna().sum().items()},
        "null_percent": {column: round(float(value), 4) for column, value in (df.isna().mean() * 100).items()},
        "full_row_duplicates": int(df.duplicated().sum()),
        "text_duplicates": int(normalized.duplicated(keep=False).sum()),
        "unique_normalized_texts": int(normalized.nunique()),
        "conflicting_normalized_texts": int((conflicting > 1).sum()),
        "target_distribution": count_values(target),
        "length_characters": describe_numeric(chars),
        "length_words": describe_numeric(words),
        "length_by_target": class_length,
        "language_heuristic": count_values(text.map(language_guess)),
        "declared_languages": declared_languages,
        "rows_with_url_pattern": int(text.str.contains(URL_RE, regex=True).sum()),
        "rows_with_email_pattern": int(text.str.contains(EMAIL_RE, regex=True).sum()),
        "rows_with_phone_pattern": int(text.str.contains(PHONE_RE, regex=True).sum()),
        "rows_with_replacement_character": int(text.str.contains("�", regex=False).sum()),
        "rows_with_mojibake_marker": int(text.str.contains(MOJIBAKE_RE, regex=True).sum()),
        "empty_text_rows": int((text.str.len() == 0).sum()),
        "examples": examples,
        "translation_quality": translation_quality,
        "leakage_checks": leakage_checks,
    }
    return result


def normalized_text_sets(results: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    sets: dict[str, set[str]] = {}
    for spec in DATASETS:
        frame = load_dataset(spec)
        values = combined_text(frame, spec.text_columns).map(normalized_text)
        sets[spec.slug] = {value for value in values if value}
    overlap: dict[str, dict[str, int]] = {}
    for left_index, left in enumerate(DATASETS):
        for right in DATASETS[left_index + 1 :]:
            shared = len(sets[left.slug] & sets[right.slug])
            if shared:
                overlap[f"{left.slug}__{right.slug}"] = {
                    "shared_unique_texts": shared,
                    "left_unique_texts": len(sets[left.slug]),
                    "right_unique_texts": len(sets[right.slug]),
                }
    return overlap


def run_all() -> dict[str, Any]:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    analyses = [analyze_dataset(spec) for spec in DATASETS]
    payload = {
        "datasets": analyses,
        "text_overlaps": normalized_text_sets(analyses),
    }
    output = RESULTS_DIR / "dataset_audit.json"
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


if __name__ == "__main__":
    result = run_all()
    print(f"Analizados {len(result['datasets'])} archivos CSV.")
    print(f"Resultado: {RESULTS_DIR / 'dataset_audit.json'}")
