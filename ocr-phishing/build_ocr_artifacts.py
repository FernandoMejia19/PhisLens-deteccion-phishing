"""Construye el informe y notebook de evaluación a partir de métricas OCR."""

from __future__ import annotations

import json
from pathlib import Path

import nbformat as nbf


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results" / "ocr_evaluation.json"
REPORT = ROOT / "OCR_EVALUATION.md"
NOTEBOOK = ROOT / "analisis-ocr-preprocesamiento.ipynb"


def metric_rows(payload: dict) -> str:
    rows = [
        "| Imagen | Variante | CER | WER | Confianza media | Regiones | Tiempo (s) |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for image_name, image in payload["images"].items():
        for variant_name, result in image["variants"].items():
            rows.append(
                f"| `{image_name}` | `{variant_name}` | {result['cer'] * 100:.2f}% | "
                f"{result['wer'] * 100:.2f}% | {result['mean_confidence']:.4f} | "
                f"{result['regions']} | {result['elapsed_seconds']:.3f} |"
            )
    return "\n".join(rows)


def report_text(payload: dict) -> str:
    return f"""# Evaluación del OCR

## Implementación inicial

El notebook original usa EasyOCR con los idiomas `es` y `en`, CPU, OpenCV para cargar la imagen y Matplotlib para visualizar regiones. Procesaba únicamente `data/ejcorreo.png`, concatenaba las regiones y no comparaba contra una transcripción de referencia.

La ejecución almacenada del notebook original detectó 18 regiones y preservó `contact@growthdot.com`. Separó incorrectamente “1 minute ago” en números aislados y omitió el 7 de “Email was read 7 seconds…”.

## Imágenes

- `ejcorreo.png`: captura nítida de 893×574 píxeles, fondo claro, texto en inglés. Contiene empresa/nombre “Email Tracking”, ruta “Europe/Kyiv” y el correo `contact@growthdot.com`.
- `ejwpp.jpg`: captura de WhatsApp de 1200×478 píxeles con el chat centrado, fondo ilustrado y texto en español. No contiene URL, correo ni teléfono; “facebook” es una palabra, no un enlace.
- Ambas están correctamente orientadas. No se aplicó rotación porque no había evidencia de inclinación.

## Método

Se creó una transcripción manual legible para cada imagen y se calcularon CER (tasa de error de caracteres) y WER (tasa de error de palabras) después de normalización. Se probaron original, escala de grises, ampliación 2×, CLAHE, Otsu y reducción de ruido seguida de Otsu. No se ejecutó ningún enlace.

{metric_rows(payload)}

## Resultados

### Correo

- La ampliación 2× fue la mejor: **CER 1.11% y WER 3.85%**, preservando correo, nombre y `Europe/Kyiv`.
- Denoise + Otsu quedó segundo (CER 1.77%, WER 6.41%).
- CLAHE mejoró WER frente al original, pero no CER.
- Escala de grises sola empeoró ligeramente y dividió el correo en `contact@` / `growthdot.com`; una extracción de entidades por línea podría perderlo.
- Otsu conservó el correo, pero introdujo un espacio en `Europe /Kyiv`.

### WhatsApp

- Original y escala de grises empataron como mejores: **CER 0.81% y WER 4.35%**.
- La ampliación y CLAHE añadieron un “0” espurio cerca del avatar y separaron líneas.
- Otsu, con o sin denoise, eliminó las marcas horarias y elevó CER a 16.26%.
- Las variantes conservaron “contraseña”, “facebook” y “Abuela”, pero la consola de Windows puede representar acentos de forma defectuosa; el JSON está guardado en UTF-8.

## Entidades críticas

- Dirección de correo: preservada por original, ampliación, CLAHE, Otsu y denoise+Otsu; escala de grises la partió en dos regiones.
- Números telefónicos: no hay ninguno en estas imágenes, por lo que no puede evaluarse esta capacidad.
- Enlaces: no hay URLs visibles; `Europe/Kyiv` no debe tratarse como URL.
- Empresas/nombres: “Email Tracking”, “Abuela” y “facebook” fueron reconocidos.
- Texto del mensaje: alto nivel de recuperación, con errores concentrados en orden/segmentación y marcas horarias.

## Limitaciones

- Sólo hay dos imágenes y ambas son legibles; no permiten estimar desempeño general.
- CER/WER dependen de la transcripción manual y del orden de regiones devuelto por EasyOCR.
- La confianza de EasyOCR no reemplaza CER/WER y no está calibrada como probabilidad de exactitud.
- EasyOCR emitió avisos de CPU/quantización. Procesar muchas variantes en un mismo proceso acumuló recursos; la ejecución completa finalmente produjo el JSON, pero para repetir de forma estable conviene procesar imagen por imagen.
- No se probaron desenfoque, rotación, compresión severa, modo oscuro, múltiples burbujas ni capturas móviles pequeñas.

## Recomendación

Usar la imagen original como primera opción. Si el texto es pequeño, probar ampliación 2× y seleccionar el resultado mediante una regla de calidad que considere cobertura de texto y preservación de correos/URLs. No aplicar umbralización global a capturas con fondos complejos sin comparar, porque en WhatsApp eliminó información. Añadir un posprocesado que una regiones contiguas para correos y URLs partidos por saltos de línea.

## Próxima validación

Construir un conjunto de al menos 30–50 capturas estratificadas por tipo (correo/WhatsApp), resolución, modo claro/oscuro, rotación, compresión y presencia de URL/correo/teléfono. Anotar ground truth y reportar CER, WER y recall exacto de entidades por categoría antes de integrar OCR con el clasificador.
"""


def build_notebook(payload: dict) -> nbf.NotebookNode:
    metrics = []
    for image_name, image in payload["images"].items():
        for variant_name, result in image["variants"].items():
            metrics.append(
                {
                    "imagen": image_name,
                    "variante": variant_name,
                    "CER": result["cer"],
                    "WER": result["wer"],
                    "confianza_media": result["mean_confidence"],
                    "regiones": result["regions"],
                    "segundos": result["elapsed_seconds"],
                }
            )
    notebook = nbf.v4.new_notebook()
    notebook.metadata["kernelspec"] = {"display_name": ".venv (Python 3)", "language": "python", "name": "python3"}
    notebook.cells = [
        nbf.v4.new_markdown_cell(
            "# Evaluación de preprocesamiento OCR\n\n"
            "Copia experimental del flujo original. Las imágenes fuente no se modifican. El informe completo está en "
            "[`OCR_EVALUATION.md`](OCR_EVALUATION.md)."
        ),
        nbf.v4.new_code_cell(
            "from pathlib import Path\nimport json\nimport pandas as pd\nimport matplotlib.pyplot as plt\n\n"
            "ROOT = Path.cwd()\n"
            "if not (ROOT / 'results' / 'ocr_evaluation.json').exists():\n"
            "    ROOT = ROOT / 'ocr-phishing'\n"
            "payload = json.loads((ROOT / 'results' / 'ocr_evaluation.json').read_text(encoding='utf-8'))"
        ),
        nbf.v4.new_markdown_cell("## Métricas ejecutadas"),
        nbf.v4.new_code_cell(
            f"metrics = {metrics!r}\n"
            "metrics_df = pd.DataFrame(metrics)\n"
            "display(metrics_df.sort_values(['imagen', 'WER']))"
        ),
        nbf.v4.new_code_cell(
            "for image, group in metrics_df.groupby('imagen'):\n"
            "    group.set_index('variante')[['CER', 'WER']].plot(kind='bar', title=f'Errores OCR: {image}')\n"
            "    plt.ylabel('Tasa de error'); plt.tight_layout(); plt.show()"
        ),
        nbf.v4.new_markdown_cell("## Textos y conservación de entidades"),
        nbf.v4.new_code_cell(
            "for image_name, image in payload['images'].items():\n"
            "    print(f'\\n### {image_name}')\n"
            "    for variant, result in image['variants'].items():\n"
            "        print(f'\\n[{variant}] entidades={result[\"important_terms\"]}')\n"
            "        print(result['text'])"
        ),
        nbf.v4.new_markdown_cell(
            "## Repetición del experimento\n\n"
            "Ejecutar `evaluate_ocr.py` desde `ocr-phishing/`. Para equipos con memoria limitada, usar `--images` y `--variants` para "
            "procesar una variante por ejecución. No enviar imágenes ni texto a servicios externos."
        ),
    ]
    return notebook


def main() -> None:
    payload = json.loads(RESULTS.read_text(encoding="utf-8"))
    REPORT.write_text(report_text(payload), encoding="utf-8")
    nbf.write(build_notebook(payload), NOTEBOOK)
    print(f"Generados: {REPORT.name}, {NOTEBOOK.name}")


if __name__ == "__main__":
    main()
