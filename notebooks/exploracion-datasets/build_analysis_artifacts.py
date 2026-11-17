"""Genera informes Markdown y notebooks a partir de la auditoría ejecutada."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import nbformat as nbf

from dataset_audit import DATASETS, RESULTS_DIR, ROOT


REPORTS_DIR = ROOT / "notebooks" / "reports"
NOTEBOOKS_DIR = ROOT / "notebooks" / "exploracion-datasets"
AUDIT_PATH = RESULTS_DIR / "dataset_audit.json"

REPORT_NAMES = {
    "email_detection_50k": "email_detection_50k.md",
    "phishing_email_detection_50k_copy": "phishing_email_detection_50k_copy.md",
    "spam_multilingual_augmented": "spam_multilingual_augmented.md",
    "spam_spanish": "spam_spanish.md",
    "sms_spam_5971": "sms_spam_5971.md",
    "spanish_phishing": "spanish_phishing.md",
    "spear_phish_mx": "spear_phish_mx.md",
}

NOTEBOOK_NAMES = {
    "email_detection_50k": "email-detection.ipynb",
    "phishing_email_detection_50k_copy": "phishing-email-detection-50k-copy.ipynb",
    "spam_multilingual_augmented": "spam-multilingual-augmented.ipynb",
    "spam_spanish": "spam-spanish.ipynb",
    "sms_spam_5971": "sms-spam-5971.ipynb",
    "spanish_phishing": "spanish-dataset.ipynb",
    "spear_phish_mx": "spear-phish-mx.ipynb",
}

ASSESSMENTS = {
    "email_detection_50k": {
        "description": "Correos en inglés con 44 campos de contenido, remitente, autenticación, reputación y una etiqueta binaria.",
        "origin": "El repositorio no contiene README, URL, licencia ni referencia bibliográfica para verificar la procedencia. El nombre de carpeta no es evidencia suficiente de origen.",
        "strengths": [
            "Volumen alto y clases utilizables para comparación experimental.",
            "Incluye texto, asunto y variables técnicas que permiten estudiar varios grupos de características.",
            "No presenta filas ni textos duplicados dentro del archivo.",
        ],
        "limits": [
            "Los mensajes repiten plantillas y las variables son muy regulares; esto constituye evidencia de datos sintéticos o generados, aunque la procedencia no permite confirmarlo.",
            "`phishing_probability` separa las clases por construcción: 0–49 para legítimos y 50–100 para phishing. Usarla sería fuga directa de la etiqueta.",
            "`spoofed_domain`, reputación de URL y estados SPF/DKIM/DMARC están fuertemente asociados a la etiqueta y pueden producir una evaluación artificial si fueron usados para generarla.",
            "Sólo contiene inglés declarado; no valida desempeño en español.",
        ],
        "bias": "Favorece correos con patrones explícitos de urgencia, fallos de autenticación y dominios marcados. Puede subrepresentar phishing bien redactado o con infraestructura comprometida legítima.",
        "utility": "Media como benchmark en inglés y para prototipos; baja como única evidencia de generalización real.",
        "rf": "Utilizable con TF-IDF reducido o variables léxicas/técnicas, excluyendo campos posteriores a la etiqueta y validando por plantillas o grupos. Random Forest sobre TF-IDF completo puede ser costoso y debe compararse con un baseline lineal.",
        "combine": "Mantener como corpus inglés separado. No concatenar con su copia. Combinar sólo después de armonizar etiquetas y conservar una columna `source_dataset` para dividir y auditar por origen.",
        "recommendations": [
            "Excluir `phishing_probability` y evaluar en ablación todas las variables de reputación/autenticación.",
            "Separar plantillas o remitentes entre entrenamiento y prueba para reducir fuga por patrón.",
            "Buscar y documentar fuente, licencia y método de generación antes de usarlo en la tesis.",
        ],
    },
    "phishing_email_detection_50k_copy": {
        "description": "Copia exacta del archivo `email-detection-dataset/dataset_v2.csv`.",
        "origin": "No hay procedencia documentada. El SHA-256 coincide exactamente con el otro CSV de 50 000 correos.",
        "strengths": ["Mismas propiedades que `email_detection_50k`."],
        "limits": ["No aporta registros nuevos; contar ambos duplicaría por completo el corpus y contaminaría cualquier partición."],
        "bias": "Idéntico al archivo original; todos sus sesgos se repetirían dos veces.",
        "utility": "Nula como dataset adicional; conservar sólo como archivo inventariado hasta decidir cuál ruta será la canónica.",
        "rf": "No debe entrar dos veces al entrenamiento ni a la evaluación.",
        "combine": "No combinar. Seleccionar una sola copia mediante hash antes de construir datasets derivados.",
        "recommendations": ["No eliminarla en esta fase; documentar la duplicación y excluirla de futuros ensamblajes."],
    },
    "spam_multilingual_augmented": {
        "description": "Colección SMS en inglés con etiqueta ham/spam y 21 columnas de traducción automática.",
        "origin": "El repositorio no documenta fuente, licencia, traductor ni procedimiento de aumento.",
        "strengths": [
            "Incluye versiones por idioma y permite estudiar robustez multilingüe.",
            "La etiqueta ham/spam está presente para todos los registros.",
        ],
        "limits": [
            "Spam no equivale a phishing; muchos mensajes son publicidad o concursos sin suplantación.",
            "Hay 706 filas involucradas en textos duplicados en la columna original.",
            "Las traducciones no son observaciones independientes; dividirlas entre train/test produciría fuga semántica.",
            "Hay nulos en traducciones china, coreana y árabe, y no se documenta la calidad de traducción.",
        ],
        "bias": "Predomina ham y el estilo SMS británico/abreviado del texto original; las traducciones heredan ese contexto cultural.",
        "utility": "Baja para phishing directo; media como corpus auxiliar de spam y experimentos de idioma.",
        "rf": "Puede aportar características de SMS, pero debe agruparse por mensaje original antes de dividir. No usar cada traducción como muestra independiente.",
        "combine": "No combinar con `Dataset_5971` sin deduplicar: comparten 4 933 textos únicos. Las columnas traducidas deben conservar un identificador de familia.",
        "recommendations": [
            "Evaluar manualmente una muestra estratificada de `text_es` antes de usarla.",
            "Usar GroupKFold o partición por índice original si se comparan traducciones.",
            "Mantener la tarea spam separada de la tarea phishing o usarla sólo como preentrenamiento/auxiliar documentado.",
        ],
    },
    "spam_spanish": {
        "description": "Mensajes cortos en español con etiquetas numéricas 0/1; los ejemplos inspeccionados indican 0 legítimo y 1 spam.",
        "origin": "No hay fuente, licencia ni diccionario de etiquetas en el repositorio; la semántica 0/1 se infiere de ejemplos y debe confirmarse.",
        "strengths": [
            "15 016 registros y distribución cercana al equilibrio.",
            "Contenido mayoritariamente español según heurística reproducible.",
        ],
        "limits": [
            "Contiene 266 filas duplicadas y 416 filas involucradas en textos duplicados.",
            "Spam abarca promociones, fraudes y mensajes no solicitados; no es una etiqueta específica de phishing.",
            "No contiene asunto, remitente ni metadatos de correo.",
        ],
        "bias": "Mensajes breves y formulaciones de spam evidentes; representa peor correos largos o spear phishing.",
        "utility": "Media como señal auxiliar en español; baja-media para entrenar por sí solo un detector de phishing.",
        "rf": "Adecuado para probar TF-IDF + reducción/selección y variables de longitud/URLs, después de deduplicar y confirmar etiquetas.",
        "combine": "Puede añadirse como clase maliciosa auxiliar sólo si se conserva su etiqueta original `spam` y se evalúa por separado de phishing.",
        "recommendations": [
            "Confirmar la definición de 0/1 con la fuente original.",
            "Deduplicar antes de dividir y conservar un conjunto específico de phishing real.",
        ],
    },
    "sms_spam_5971": {
        "description": "Mensajes SMS con indicadores URL/EMAIL/PHONE y etiquetas ham, spam y smishing.",
        "origin": "No hay fuente, licencia ni definición de las columnas auxiliares en el repositorio.",
        "strengths": [
            "Distingue smishing de spam en parte de los registros.",
            "Incluye indicadores explícitos de URL, correo y teléfono.",
        ],
        "limits": [
            "Las etiquetas `Spam`/`spam` y `Smishing`/`smishing` difieren sólo por mayúsculas y requieren normalización.",
            "Existen 49 textos normalizados con etiquetas conflictivas.",
            "Comparte 4 933 textos únicos con el dataset aumentado; existe alto riesgo de fuga entre fuentes.",
            "El contenido es principalmente inglés y 145 filas muestran caracteres problemáticos en la lectura de texto.",
        ],
        "bias": "SMS cortos, promociones y vocabulario móvil; no representa correo electrónico corporativo.",
        "utility": "Media para un submodelo o reglas de smishing; baja-media para el clasificador general de correo phishing.",
        "rf": "Útil tras normalizar etiquetas, resolver conflictos y agrupar duplicados. Los indicadores auxiliares deben recalcularse para verificar que no son etiquetas derivadas.",
        "combine": "No combinar directamente con el aumentado. Deduplicar por texto normalizado y mantener una sola asignación de etiqueta tras revisión de conflictos.",
        "recommendations": [
            "Unificar mayúsculas de etiquetas en una copia procesada, nunca en el CSV original.",
            "Revisar manualmente los 49 conflictos y verificar cómo se generaron URL/EMAIL/PHONE.",
        ],
    },
    "spanish_phishing": {
        "description": "Correos en español con asunto, cuerpo, URLs, adjuntos, etiqueta binaria y anotaciones de principios de persuasión por tres evaluadores.",
        "origin": "No hay URL, licencia ni publicación citada dentro del repositorio.",
        "strengths": [
            "Clases relativamente equilibradas (731/664).",
            "Mensajes largos y metadatos de URL/adjuntos, más anotaciones útiles para explicaciones.",
            "No presenta textos duplicados normalizados ni conflictos de etiqueta.",
        ],
        "limits": [
            "Algunos campos de adjuntos son nulos en 1 124 registros y `urls` es nulo en 195.",
            "Hay pequeños problemas de codificación y asuntos nulos.",
            "Las variables agregadas de persuasión pueden depender de anotación posterior y deben separarse del detector principal para evitar confundir explicación con predicción.",
        ],
        "bias": "Corpus mexicano/español con mensajes de longitud muy variable y señales de persuasión explícitas; puede no cubrir variedades regionales o ataques muy breves.",
        "utility": "Alta para la tesis en español, sujeta a verificar procedencia/licencia y protocolo de anotación.",
        "rf": "Prometedor con texto TF-IDF reducido, conteos y metadatos. Las anotaciones A/B/C y agregadas deben evaluarse como módulo explicativo o experimento separado.",
        "combine": "Candidato principal para combinar con SpearPhishMX tras armonizar etiquetas, esquema y deduplicación cruzada. Conservar origen para evaluación por dominio.",
        "recommendations": [
            "Documentar significado exacto de Label y acuerdo entre anotadores.",
            "Tratar cuerpo y asunto por separado y añadir pruebas con/sin variables de persuasión.",
            "Imputar nulos sólo en un pipeline reproducible y con indicadores de ausencia.",
        ],
    },
    "spear_phish_mx": {
        "description": "Correos en español orientados a spear phishing, con cuerpo sanitizado, destinatario, URLs desactivadas y etiqueta binaria.",
        "origin": "El nombre sugiere un dataset mexicano, pero el repositorio no aporta fuente, licencia ni metodología verificable.",
        "strengths": [
            "3 006 registros con clases 1/0 y abundante contenido textual.",
            "URLs están desactivadas y no se ejecutaron durante el análisis.",
            "Incluye señales de personalización útiles para estudiar spear phishing.",
        ],
        "limits": [
            "`fecha`, tipos/tamaños de adjuntos y saltos son totalmente nulos.",
            "Hay 283 destinatarios detectados nulos y dos asuntos nulos.",
            "Se observaron pocos textos duplicados y problemas puntuales de caracteres.",
        ],
        "bias": "Favorece mensajes dirigidos y contexto corporativo mexicano; puede sobreestimar señales de nombres propios y urgencia formal.",
        "utility": "Alta para ampliar el corpus español y estudiar spear phishing, con cautela por procedencia no documentada.",
        "rf": "Adecuado para características textuales y de personalización. Eliminar columnas 100 % nulas y separar por destinatario/plantilla cuando sea posible.",
        "combine": "Combinar de forma controlada con `spanish_phishing`, preservando `source_dataset` y evaluando un holdout por fuente.",
        "recommendations": [
            "Verificar etiqueta y método de sanitización con la fuente original.",
            "No usar columnas completamente nulas y evaluar posible fuga mediante `id_original` o destinatario.",
        ],
    },
}


def fmt_number(value: float | int | None, decimals: int = 2) -> str:
    if value is None:
        return "n.d."
    if isinstance(value, int) or float(value).is_integer():
        return f"{int(value):,}".replace(",", " ")
    return f"{float(value):.{decimals}f}"


def bullet_list(values: list[str]) -> str:
    return "\n".join(f"- {value}" for value in values)


def schema_table(result: dict[str, Any]) -> str:
    lines = ["| Columna | Tipo inferido | Nulos | Nulos % |", "|---|---:|---:|---:|"]
    for column in result["column_names"]:
        lines.append(
            f"| `{column}` | `{result['dtypes'][column]}` | {result['nulls'][column]} | "
            f"{result['null_percent'][column]:.2f}% |"
        )
    return "\n".join(lines)


def target_table(result: dict[str, Any]) -> str:
    total = result["rows"]
    lines = ["| Clase | Registros | Porcentaje |", "|---|---:|---:|"]
    for label, count in result["target_distribution"].items():
        lines.append(f"| `{label}` | {count} | {count / total * 100:.2f}% |")
    return "\n".join(lines)


def examples_section(result: dict[str, Any]) -> str:
    lines = []
    for label, examples in result["examples"].items():
        lines.append(f"**Clase `{label}`**")
        lines.extend(f"- {example}" for example in examples)
        lines.append("")
    return "\n".join(lines).strip()


def dataset_report(result: dict[str, Any]) -> str:
    slug = result["spec"]["slug"]
    assessment = ASSESSMENTS[slug]
    chars = result["length_characters"]
    words = result["length_words"]
    languages = result["declared_languages"] or result["language_heuristic"]
    language_text = ", ".join(f"{key}: {value}" for key, value in languages.items())
    exact_duplicate = ""
    if slug in {"email_detection_50k", "phishing_email_detection_50k_copy"}:
        exact_duplicate = (
            "\nLos dos archivos de 50 000 correos tienen el mismo SHA-256 "
            f"`{result['sha256']}` y son copias exactas.\n"
        )
    translation_note = ""
    if result["translation_quality"]:
        missing = {key: value["nulls"] for key, value in result["translation_quality"].items() if value["nulls"]}
        translation_note = f"\nColumnas de traducción con nulos: {missing or 'ninguna'}. La calidad semántica no puede inferirse sólo de estos conteos.\n"

    return f"""# Análisis: {slug}

## Descripción y procedencia

{assessment['description']}

**Ubicación:** `{result['path']}`  
**Procedencia verificable:** {assessment['origin']}
{exact_duplicate}
## Estructura

- Formato: CSV, UTF-8, separador `{result['spec']['sep']}`.
- Registros: **{result['rows']:,}**.
- Columnas: **{result['columns']}**.
- Variable objetivo: **`{result['spec']['target']}`**.
- Columnas de texto evaluadas: {', '.join(f'`{value}`' for value in result['spec']['text_columns'])}.
- Tamaño: {result['bytes']:,} bytes.
- SHA-256: `{result['sha256']}`.

{schema_table(result)}

## Distribución de clases

{target_table(result)}

## Calidad y duplicados

- Filas completamente duplicadas: **{result['full_row_duplicates']}**.
- Filas involucradas en textos normalizados repetidos: **{result['text_duplicates']}**.
- Textos normalizados con etiquetas conflictivas: **{result['conflicting_normalized_texts']}**.
- Filas sin texto: **{result['empty_text_rows']}**.
- Filas con caracteres de reemplazo: **{result['rows_with_replacement_character']}**.
- Filas con marcadores de posible mojibake: **{result['rows_with_mojibake_marker']}**.
- Patrones encontrados sin abrir enlaces: URL **{result['rows_with_url_pattern']}**, correo **{result['rows_with_email_pattern']}**, teléfono **{result['rows_with_phone_pattern']}**.
{translation_note}
## Longitud del texto

| Métrica | Caracteres | Palabras |
|---|---:|---:|
| Mínimo | {fmt_number(chars['min'])} | {fmt_number(words['min'])} |
| Q1 | {fmt_number(chars['q25'])} | {fmt_number(words['q25'])} |
| Mediana | {fmt_number(chars['median'])} | {fmt_number(words['median'])} |
| Media | {fmt_number(chars['mean'])} | {fmt_number(words['mean'])} |
| Q3 | {fmt_number(chars['q75'])} | {fmt_number(words['q75'])} |
| P95 | {fmt_number(chars['p95'])} | {fmt_number(words['p95'])} |
| Máximo | {fmt_number(chars['max'])} | {fmt_number(words['max'])} |

## Idiomas

Resultado observado: {language_text}. La heurística sólo distingue señales claras de español e inglés; `indeterminado` no representa un tercer idioma. Cuando existe una columna declarada se reporta esa columna, no una detección independiente.

## Ejemplos representativos

Los ejemplos se seleccionaron cerca de la longitud mediana de cada clase. Se desactivaron esquemas URL y se ocultaron correos/teléfonos en el informe.

{examples_section(result)}

## Características útiles

- Texto del asunto y cuerpo o mensaje.
- Longitud, conteos de palabras y caracteres especiales.
- Presencia y cantidad de URLs, correos, teléfonos y términos de urgencia.
- Metadatos propios del dataset, únicamente tras comprobar que no derivan de la etiqueta.
- TF-IDF de palabras y caracteres, con selección o reducción de dimensionalidad para Random Forest.

## Ventajas

{bullet_list(assessment['strengths'])}

## Problemas, limitaciones y sesgos

{bullet_list(assessment['limits'])}

**Sesgo probable:** {assessment['bias']}

## Utilidad para el proyecto y Random Forest

**Utilidad estimada:** {assessment['utility']}

**Random Forest:** {assessment['rf']}

**Combinación:** {assessment['combine']}

## Recomendaciones

{bullet_list(assessment['recommendations'])}

## Reproducibilidad

Métricas generadas por `notebooks/exploracion-datasets/dataset_audit.py`. No se modificó el CSV original. La procedencia y licencia siguen pendientes cuando no aparecen en el repositorio.
"""


def create_notebook(result: dict[str, Any], report_name: str) -> nbf.NotebookNode:
    slug = result["spec"]["slug"]
    notebook = nbf.v4.new_notebook()
    notebook.metadata["kernelspec"] = {"display_name": ".venv (Python 3)", "language": "python", "name": "python3"}
    notebook.cells = [
        nbf.v4.new_markdown_cell(
            f"# Exploración reproducible: `{slug}`\n\n"
            "Este notebook lee el CSV original sin modificarlo. El análisis completo se guarda en "
            f"[`../reports/{report_name}`](../reports/{report_name})."
        ),
        nbf.v4.new_code_cell(
            "from pathlib import Path\nimport sys\nimport pandas as pd\nimport matplotlib.pyplot as plt\n\n"
            "HERE = Path.cwd()\n"
            "while not (HERE / 'notebooks' / 'exploracion-datasets' / 'dataset_audit.py').exists():\n"
            "    if HERE.parent == HERE:\n        raise FileNotFoundError('No se encontró la raíz del repositorio')\n"
            "    HERE = HERE.parent\n"
            "sys.path.insert(0, str(HERE / 'notebooks' / 'exploracion-datasets'))\n"
            "from dataset_audit import DATASETS, analyze_dataset, load_dataset, combined_text\n"
            f"spec = next(item for item in DATASETS if item.slug == '{slug}')\n"
            "df = load_dataset(spec)\nresult = analyze_dataset(spec)\n"
            "print(f'Dimensiones: {df.shape[0]:,} filas × {df.shape[1]} columnas')\n"
            "print(f'Objetivo: {spec.target}')"
        ),
        nbf.v4.new_markdown_cell("## Esquema, tipos y nulos"),
        nbf.v4.new_code_cell(
            "schema = pd.DataFrame({\n"
            "    'tipo': df.dtypes.astype(str),\n"
            "    'nulos': df.isna().sum(),\n"
            "    'nulos_pct': (df.isna().mean() * 100).round(2),\n"
            "})\ndisplay(schema)"
        ),
        nbf.v4.new_markdown_cell("## Clases, duplicados y conflictos"),
        nbf.v4.new_code_cell(
            "display(df[spec.target].value_counts(dropna=False).rename('registros').to_frame())\n"
            "print('Filas duplicadas:', result['full_row_duplicates'])\n"
            "print('Filas con texto repetido:', result['text_duplicates'])\n"
            "print('Textos con etiquetas conflictivas:', result['conflicting_normalized_texts'])\n"
            "df[spec.target].astype(str).value_counts().plot(kind='bar', title='Distribución de clases')\n"
            "plt.xlabel('Clase'); plt.ylabel('Registros'); plt.tight_layout(); plt.show()"
        ),
        nbf.v4.new_markdown_cell("## Longitud, idioma y patrones"),
        nbf.v4.new_code_cell(
            "display(pd.DataFrame({\n"
            "    'caracteres': result['length_characters'],\n"
            "    'palabras': result['length_words'],\n"
            "}))\n"
            "print('Idiomas declarados o estimados:', result['declared_languages'] or result['language_heuristic'])\n"
            "print('Filas con URL/correo/teléfono:', result['rows_with_url_pattern'], result['rows_with_email_pattern'], result['rows_with_phone_pattern'])\n"
            "text = combined_text(df, spec.text_columns)\n"
            "text.str.len().clip(upper=text.str.len().quantile(.99)).hist(bins=30)\n"
            "plt.title('Longitud en caracteres (recorte visual P99)'); plt.xlabel('Caracteres'); plt.ylabel('Registros'); plt.show()"
        ),
        nbf.v4.new_markdown_cell("## Ejemplos sanitizados y conclusión"),
        nbf.v4.new_code_cell("for label, examples in result['examples'].items():\n    print(f'\\nClase {label}')\n    for example in examples:\n        print('-', example)"),
        nbf.v4.new_markdown_cell(
            f"La interpretación, riesgos de fuga, sesgos, utilidad para Random Forest y estrategia de combinación están documentados en "
            f"[`../reports/{report_name}`](../reports/{report_name})."
        ),
    ]
    return notebook


def comparative_report(payload: dict[str, Any]) -> str:
    by_slug = {item["spec"]["slug"]: item for item in payload["datasets"]}
    rows = [
        "| Dataset | Registros | Idioma | Clases | Calidad | Utilidad |",
        "|---|---:|---|---|---|---|",
    ]
    summaries = {
        "email_detection_50k": ("Inglés", "Regular: probable sintético y fuga", "Media"),
        "phishing_email_detection_50k_copy": ("Inglés", "Duplicado exacto", "Nula adicional"),
        "spam_multilingual_augmented": ("Inglés + traducciones", "Regular: aumento no documentado", "Baja directa"),
        "spam_spanish": ("Español", "Regular: duplicados y etiqueta sin diccionario", "Media auxiliar"),
        "sms_spam_5971": ("Inglés", "Baja-regular: conflictos y solapamiento", "Media smishing"),
        "spanish_phishing": ("Español", "Buena con nulos y procedencia pendiente", "Alta"),
        "spear_phish_mx": ("Español", "Buena en texto; columnas totalmente nulas", "Alta"),
    }
    for spec in DATASETS:
        item = by_slug[spec.slug]
        language, quality, utility = summaries[spec.slug]
        classes = ", ".join(f"{key}: {value}" for key, value in item["target_distribution"].items())
        rows.append(f"| `{spec.slug}` | {item['rows']:,} | {language} | {classes} | {quality} | {utility} |")
    overlap_lines = "\n".join(
        f"- `{key}`: {value['shared_unique_texts']:,} textos únicos compartidos."
        for key, value in payload["text_overlaps"].items()
    )
    return f"""# Análisis comparativo de datasets

## Resumen

{chr(10).join(rows)}

Los archivos más prometedores para el objetivo principal en español son `spanish_phishing` y `spear_phish_mx`. Ninguno debe usarse como fuente definitiva hasta documentar procedencia, licencia, definición de etiqueta y protocolo de recolección. El archivo inglés de 50 000 correos sirve como benchmark controlado, no como sustituto del corpus español.

## Duplicados y solapamientos entre fuentes

{overlap_lines}

- Los dos archivos de 50 000 correos son idénticos byte a byte. Se debe seleccionar una sola copia.
- El alto solapamiento entre `spam_multilingual_augmented` y `sms_spam_5971` impide tratarlos como fuentes independientes.
- La deduplicación debe ocurrir antes de separar train/validación/test y debe conservar grupos de traducciones/plantillas.

## Estrategia recomendada de combinación

1. Construir una tabla procesada, sin alterar fuentes, con `text`, `subject`, `target_original`, `target_binary`, `language`, `source_dataset`, `record_id` y `group_id`.
2. Usar `spanish_phishing` y `spear_phish_mx` como núcleo español. Armonizar 0/1 sólo después de confirmar su semántica.
3. Deduplicar por hash de texto normalizado y agrupar variantes del mismo mensaje, destinatario o plantilla.
4. Reservar un holdout por fuente además de una partición estratificada. Así se mide generalización entre dominios.
5. Mantener `spam_spanish` y smishing como tareas auxiliares o clases de análisis, no convertir automáticamente todo spam en phishing.
6. Mantener el corpus de 50 000 correos como evaluación inglesa separada y excluir variables con fuga (`phishing_probability`, y posiblemente reputación/autenticación).

## Random Forest

Random Forest no recibe texto crudo. La opción defendible es comparar: (a) TF-IDF de palabras/caracteres con selección o reducción de dimensionalidad y (b) características interpretables como longitudes, URLs, dominios, urgencia, mayúsculas y entidades. Se debe usar un baseline lineal para comprobar que Random Forest aporta valor y calibrar probabilidades antes de mostrarlas al usuario.

## Riesgos principales

- Fuga por variables generadas a partir de la etiqueta o por traducciones/duplicados repartidos entre conjuntos.
- Confundir spam con phishing.
- Mezclar español e inglés sin evaluación separada.
- Sobreajuste a plantillas, marcas, destinatarios o dominios.
- Procedencia y licencia no documentadas en todos los datasets.

## Siguiente experimento

Antes del modelo definitivo: confirmar metadatos de origen, resolver etiquetas conflictivas, crear un manifiesto de datos procesados y diseñar particiones agrupadas. Después ejecutar un baseline reproducible con métricas por idioma, fuente y clase, con atención a falsos negativos.
"""


def repository_audit(payload: dict[str, Any]) -> str:
    return """# Auditoría inicial del repositorio

## Estructura observada

- `notebooks/data/`: siete CSV en cinco subcarpetas.
- `notebooks/exploracion-datasets/`: dos notebooks iniciales; fueron revisados y ampliados. La documentación usa también el nombre erróneo `noteboks/`.
- `ocr-phishing/`: notebook EasyOCR y dos imágenes de prueba.
- `frontend/` y `backend/`: directorios vacíos en esta revisión; no se modificaron.
- `instrucciones/`: documentación local. `PROJECT.md` está realmente nombrado `PROYECT.md`.
- `requirements.txt`: dependencias sin versiones fijadas.
- `.venv/`: entorno local no versionado. Python global no estaba disponible en el sandbox; la auditoría usó el entorno existente con autorización.

## Git inicial

- Rama: `exploracion-dataset-fernando`.
- Árbol inicial: limpio.
- HEAD inicial: `1a5c33f`, también apuntado por `origin/main`.
- `origin/exploracion-dataset-fernando` apuntaba a `0d9c818`.
- Remoto: `origin` en GitHub.
- La rama es apropiada porque contiene el trabajo inicial de exploración y OCR.

## Documentación y trazabilidad

`.gitignore` excluye `/instrucciones`, por lo que `TASKS.md` no estaba versionado. Se actualiza localmente y se debe añadir explícitamente si se requiere conservarlo en Git. No se corrigieron nombres ni se eliminaron archivos para evitar cambios estructurales fuera de alcance.

## Dependencias y ejecución

El entorno contiene pandas, NumPy, scikit-learn, OpenCV, EasyOCR y Jupyter. Las dependencias de `requirements.txt` no están fijadas, por lo que una instalación futura puede no reproducir exactamente las versiones usadas. No se instaló ningún paquete.

## Estado de los notebooks iniciales

Los dos notebooks de datasets sólo mostraban carga, nulos, duplicados y clases. El notebook OCR usaba EasyOCR (`es`, `en`, CPU) sobre una sola imagen y ya conservaba correctamente el correo `contact@growthdot.com`, pero no tenía ground truth, métricas ni comparación de preprocesamiento.

## Inventario

El inventario cuantitativo y los hashes se encuentran en `notebooks/reports/data/dataset_audit.json`; el análisis interpretado está en los informes individuales y comparativo.
"""


def technical_recommendations() -> str:
    return """# Recomendaciones técnicas para las siguientes fases

## Preparación de datos y Random Forest

- Crear datos derivados fuera de `notebooks/data/` y registrar hash, fuente, versión y transformación.
- Normalizar etiquetas sin perder `target_original`; deduplicar antes de dividir.
- Usar particiones agrupadas por plantilla, mensaje base, destinatario o fuente cuando exista relación.
- Comparar TF-IDF de palabras y caracteres con variables léxicas/estructurales. Para Random Forest, limitar dimensionalidad mediante selección (`chi2`, frecuencia mínima) o reducción; documentar la pérdida de interpretabilidad.
- Establecer baseline lineal (regresión logística o Linear SVM) y evaluar accuracy, precision, recall, F1, matriz de confusión, PR-AUC y métricas por fuente/idioma. Priorizar recall de phishing sin ignorar falsos positivos.
- Calibrar probabilidades antes de llamarlas “confianza”. La salida debe expresar incertidumbre y limitaciones.

## Español e inglés

- Entrenar/evaluar por idioma y reportar resultados separados antes de considerar un modelo conjunto.
- No traducir automáticamente todo el corpus como sustituto de datos naturales; las traducciones de una misma muestra deben quedar en el mismo split.
- Conservar URLs, correos, números, moneda, negaciones y marcas antes de aplicar stemming/stopwords.
- Probar n-gramas de caracteres para errores ortográficos, variantes regionales y texto de OCR.

## Dominios y correo

- Extraer dominio con un parser de direcciones y normalizar IDN/Punycode. Comparar dominio visible, `Reply-To` y dominios de enlaces cuando existan cabeceras.
- Consultar DNS con `dnspython` para MX/SPF/DMARC; no interpretar la mera existencia de registros como legitimidad.
- Preferir RDAP para datos de registro. ICANN describe RDAP como reemplazo estandarizado de WHOIS y advierte que parte de los datos puede estar redactada: [ICANN RDAP](https://www.icann.org/en/contracted-parties/registry-operators/resources/registration-data-access-protocol).
- Google Safe Browsing puede comprobar URLs maliciosas en uso no comercial, requiere proyecto y clave, y exige advertir sobre falsos positivos/negativos. No tiene costo para ese uso: [límites y políticas](https://developers.google.com/safe-browsing/v4/usage-limits), [configuración](https://developers.google.com/safe-browsing/v4/get-started).
- VirusTotal Public API requiere cuenta/clave, limita 500 solicitudes diarias y 4 por minuto y no permite producto comercial; Premium es de pago por licencia: [Public vs Premium](https://docs.virustotal.com/reference/public-vs-premium-api).
- urlscan requiere clave para el flujo normal, aplica cuotas y puede hacer públicos los URLs enviados. Deben quitarse datos personales o usarse scans privados/no listados: [prácticas](https://docs.urlscan.io/pages/api-best-practices), [cuotas](https://docs.urlscan.io/pages/api-rate-limits), [precios](https://urlscan.io/pricing/). No enviar enlaces sospechosos automáticamente durante la tesis.

## Números telefónicos

- `phonenumbers` funciona sin API para parsear, normalizar E.164, comprobar longitud/patrón y asociar prefijo/región. No requiere credenciales ni pago. Su propia documentación aclara que la validación no demuestra que el número esté en uso ni quién es su propietario: [python-phonenumbers](https://github.com/daviddrysdale/python-phonenumbers).
- Mostrar “prefijo asociado a Ecuador” o “estructura posible”, nunca “número legítimo”, “usuario de WhatsApp” o ubicación actual.
- Servicios de lookup comerciales sólo deben evaluarse después por costo, privacidad, cobertura regional y credenciales; no son necesarios para la fase de modelado.

## Noticias y educación

- Priorizar fuentes institucionales con fecha, autor y enlace canónico. CERT-EU ofrece RSS por categoría para advisories, guidance y threat intelligence: [anuncio de feeds](https://cert.europa.eu/blog/read-feed-and-lead-fresh-features-for-our-cyber-fans).
- INCIBE-CERT es una fuente en español y su servicio de alerta temprana dispone de avisos/RSS; se debe filtrar por phishing porque muchos avisos son vulnerabilidades, no campañas de fraude.
- CISA publica advisories y recursos, pero tampoco todo su contenido es phishing. Implementar una lista blanca de fuentes, deduplicación, fecha de publicación y revisión de relevancia.
- RSS suele ser gratuito y sin credenciales; APIs y redistribución pueden tener condiciones propias. Guardar sólo metadatos y extractos permitidos, no copiar artículos completos.

## Orden recomendado

1. Confirmar procedencia/licencias y semántica de etiquetas.
2. Crear manifiesto y pipeline de limpieza/deduplicación.
3. Diseñar splits agrupados y baseline por idioma/fuente.
4. Entrenar Random Forest con conjuntos de características controlados.
5. Integrar OCR sólo después de medir cómo sus errores afectan la clasificación.
6. Evaluar servicios externos al diseñar el backend, con presupuesto, privacidad y términos de uso.
"""


def main() -> None:
    payload = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    NOTEBOOKS_DIR.mkdir(parents=True, exist_ok=True)
    for result in payload["datasets"]:
        slug = result["spec"]["slug"]
        report_name = REPORT_NAMES[slug]
        (REPORTS_DIR / report_name).write_text(dataset_report(result), encoding="utf-8")
        notebook = create_notebook(result, report_name)
        nbf.write(notebook, NOTEBOOKS_DIR / NOTEBOOK_NAMES[slug])
    (REPORTS_DIR / "comparative_analysis.md").write_text(comparative_report(payload), encoding="utf-8")
    (REPORTS_DIR / "repository_audit.md").write_text(repository_audit(payload), encoding="utf-8")
    (REPORTS_DIR / "technical_recommendations.md").write_text(technical_recommendations(), encoding="utf-8")
    print("Informes y notebooks generados.")


if __name__ == "__main__":
    main()
