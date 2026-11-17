# Análisis: spam_multilingual_augmented

## Descripción y procedencia

Colección SMS en inglés con etiqueta ham/spam y 21 columnas de traducción automática.

**Ubicación:** `notebooks/data/spam/data-augmented.csv`  
**Procedencia verificable:** El repositorio no documenta fuente, licencia, traductor ni procedimiento de aumento.

## Estructura

- Formato: CSV, UTF-8, separador `,`.
- Registros: **5,572**.
- Columnas: **23**.
- Variable objetivo: **`labels`**.
- Columnas de texto evaluadas: `text`.
- Tamaño: 14,234,243 bytes.
- SHA-256: `f90ca26ca52ca65acdb71c1d73bf1d1c3806bb12f9489ae3f0b6e4e64a76920f`.

| Columna | Tipo inferido | Nulos | Nulos % |
|---|---:|---:|---:|
| `Unnamed: 0` | `int64` | 0 | 0.00% |
| `labels` | `str` | 0 | 0.00% |
| `text` | `str` | 0 | 0.00% |
| `text_hi` | `str` | 0 | 0.00% |
| `text_de` | `str` | 0 | 0.00% |
| `text_fr` | `str` | 0 | 0.00% |
| `text_es` | `str` | 0 | 0.00% |
| `text_zh` | `str` | 26 | 0.47% |
| `text_ar` | `str` | 1 | 0.02% |
| `text_bn` | `str` | 0 | 0.00% |
| `text_ru` | `str` | 0 | 0.00% |
| `text_pt` | `str` | 0 | 0.00% |
| `text_ja` | `str` | 0 | 0.00% |
| `text_id` | `str` | 0 | 0.00% |
| `text_ur` | `str` | 0 | 0.00% |
| `text_pa` | `str` | 0 | 0.00% |
| `text_jv` | `str` | 0 | 0.00% |
| `text_tr` | `str` | 0 | 0.00% |
| `text_ko` | `str` | 56 | 1.00% |
| `text_mr` | `str` | 0 | 0.00% |
| `text_uk` | `str` | 0 | 0.00% |
| `text_sv` | `str` | 0 | 0.00% |
| `text_no` | `str` | 0 | 0.00% |

## Distribución de clases

| Clase | Registros | Porcentaje |
|---|---:|---:|
| `ham` | 4825 | 86.59% |
| `spam` | 747 | 13.41% |

## Calidad y duplicados

- Filas completamente duplicadas: **0**.
- Filas involucradas en textos normalizados repetidos: **706**.
- Textos normalizados con etiquetas conflictivas: **0**.
- Filas sin texto: **0**.
- Filas con caracteres de reemplazo: **0**.
- Filas con marcadores de posible mojibake: **0**.
- Patrones encontrados sin abrir enlaces: URL **108**, correo **7**, teléfono **417**.

Columnas de traducción con nulos: {'text_zh': 26, 'text_ar': 1, 'text_ko': 56}. La calidad semántica no puede inferirse sólo de estos conteos.

## Longitud del texto

| Métrica | Caracteres | Palabras |
|---|---:|---:|
| Mínimo | 2 | 0 |
| Q1 | 35.75 | 7 |
| Mediana | 61 | 12 |
| Media | 80.37 | 15.71 |
| Q3 | 122 | 23 |
| P95 | 160 | 33 |
| Máximo | 910 | 190 |

## Idiomas

Resultado observado: en: 2927, indeterminado: 2640, es: 5. La heurística sólo distingue señales claras de español e inglés; `indeterminado` no representa un tercer idioma. Cuando existe una columna declarada se reporta esa columna, no una detección independiente.

## Ejemplos representativos

Los ejemplos se seleccionaron cerca de la longitud mediana de cada clase. Se desactivaron esquemas URL y se ocultaron correos/teléfonos en el informe.

**Clase `ham`**
- I can't right this second, gotta hit people up first
- Can ü all decide faster cos my sis going home liao..

**Clase `spam`**
- Spook up your mob with a Halloween collection of a logo & pic message plus a free eerie tone, txt CARD SPOOK to 8007 zed 08701417012150p per logo/pic
- complimentary 4 STAR Ibiza Holiday or £10,000 cash needs your URGENT collection. [telefono-oculto] NOW from Landline not to lose out! Box434SK38WP150PPM18+

## Características útiles

- Texto del asunto y cuerpo o mensaje.
- Longitud, conteos de palabras y caracteres especiales.
- Presencia y cantidad de URLs, correos, teléfonos y términos de urgencia.
- Metadatos propios del dataset, únicamente tras comprobar que no derivan de la etiqueta.
- TF-IDF de palabras y caracteres, con selección o reducción de dimensionalidad para Random Forest.

## Ventajas

- Incluye versiones por idioma y permite estudiar robustez multilingüe.
- La etiqueta ham/spam está presente para todos los registros.

## Problemas, limitaciones y sesgos

- Spam no equivale a phishing; muchos mensajes son publicidad o concursos sin suplantación.
- Hay 706 filas involucradas en textos duplicados en la columna original.
- Las traducciones no son observaciones independientes; dividirlas entre train/test produciría fuga semántica.
- Hay nulos en traducciones china, coreana y árabe, y no se documenta la calidad de traducción.

**Sesgo probable:** Predomina ham y el estilo SMS británico/abreviado del texto original; las traducciones heredan ese contexto cultural.

## Utilidad para el proyecto y Random Forest

**Utilidad estimada:** Baja para phishing directo; media como corpus auxiliar de spam y experimentos de idioma.

**Random Forest:** Puede aportar características de SMS, pero debe agruparse por mensaje original antes de dividir. No usar cada traducción como muestra independiente.

**Combinación:** No combinar con `Dataset_5971` sin deduplicar: comparten 4 933 textos únicos. Las columnas traducidas deben conservar un identificador de familia.

## Recomendaciones

- Evaluar manualmente una muestra estratificada de `text_es` antes de usarla.
- Usar GroupKFold o partición por índice original si se comparan traducciones.
- Mantener la tarea spam separada de la tarea phishing o usarla sólo como preentrenamiento/auxiliar documentado.

## Reproducibilidad

Métricas generadas por `notebooks/exploracion-datasets/dataset_audit.py`. No se modificó el CSV original. La procedencia y licencia siguen pendientes cuando no aparecen en el repositorio.
