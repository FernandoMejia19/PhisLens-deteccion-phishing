#!/usr/bin/env python3
"""
SpearPhishMX - reproducibility and quality-control script (public release)

This script:
  1) Loads SpearPhishMX_dataset_publico.csv (UTF-8, ';' separator)
  2) Validates basic constraints (unique IDs, label domain, placeholder fields)
  3) Produces descriptive summaries used in the Data in Brief data article.

Usage:
  python3 spearphishmx_qc_summary.py --csv SpearPhishMX_dataset_publico.csv --outdir out

Outputs (outdir):
  - summary_overview.json
  - missingness.csv
  - url_stats.csv
  - directedness.csv
"""
import argparse, json, os, re
import pandas as pd

DEFANGED_URL_RE = re.compile(r'hxxps?://[^\s,\]]+', re.IGNORECASE)

def count_defanged_urls(s: str) -> int:
    if not isinstance(s, str):
        return 0
    return len(DEFANGED_URL_RE.findall(s))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True, help="Path to SpearPhishMX_dataset_publico.csv")
    ap.add_argument("--outdir", default="out", help="Output directory")
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    df = pd.read_csv(args.csv, sep=";", encoding="utf-8")
    assert df.shape[1] == 17, f"Expected 17 columns, got {df.shape[1]}"
    assert df["id_original"].is_unique, "id_original must be unique in the public release"
    assert set(df["etiqueta"].unique()) <= {0, 1}, "etiqueta must be binary {0,1}"

    overview = {
        "n_rows": int(df.shape[0]),
        "n_cols": int(df.shape[1]),
        "label_counts": df["etiqueta"].value_counts().to_dict(),
        "unique_hash": int(df["hash"].nunique()),
        "hash_duplicates": int(df.shape[0] - df["hash"].nunique()),
        "missing_asunto": int(df["asunto"].isna().sum()),
        "missing_fecha": int(df["fecha"].isna().sum()),
        "missing_destinatario_detectado_v2": int(df["destinatario_detectado_v2"].isna().sum()),
        "dirigido_a_persona_v2_true": int(df["dirigido_a_persona_v2"].sum()),
        "dirigido_a_persona_v2_false": int((~df["dirigido_a_persona_v2"]).sum()),
        "conteo_urls_min": int(df["conteo_urls"].min()),
        "conteo_urls_median": float(df["conteo_urls"].median()),
        "conteo_urls_max": int(df["conteo_urls"].max()),
        "conteo_urls_mean": float(df["conteo_urls"].mean()),
    }

    with open(os.path.join(args.outdir, "summary_overview.json"), "w", encoding="utf-8") as f:
        json.dump(overview, f, ensure_ascii=False, indent=2)

    # Missingness table
    miss = (df.isna().mean() * 100).round(2).rename("missing_%").to_frame()
    miss["missing_n"] = df.isna().sum()
    miss.to_csv(os.path.join(args.outdir, "missingness.csv"), encoding="utf-8")

    # URL stats (conteo_urls) + defanged count heuristic
    df["_defanged_url_count"] = df["urls_desactivadas"].apply(count_defanged_urls)
    url_stats = df["conteo_urls"].describe().to_frame().T
    url_stats["defanged_url_count_mean"] = df["_defanged_url_count"].mean()
    url_stats.to_csv(os.path.join(args.outdir, "url_stats.csv"), index=False, encoding="utf-8")

    # Directedness summary
    directed = df["dirigido_a_persona_v2"].value_counts().rename_axis("dirigido_a_persona_v2").reset_index(name="n")
    directed["pct"] = (directed["n"] / df.shape[0] * 100).round(2)
    directed.to_csv(os.path.join(args.outdir, "directedness.csv"), index=False, encoding="utf-8")

    print("OK - outputs written to:", args.outdir)

if __name__ == "__main__":
    main()
