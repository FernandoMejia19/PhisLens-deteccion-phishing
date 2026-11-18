# Preparación del corpus principal SpaPhish V5

**Fecha de ejecución:** 17 de noviembre de 2026

**Rama:** `preparacion-datos`

**Fuente exclusiva:** SpaPhish V5
**Estado:** corpus procesado y partición reproducible preparados; candidatos de similitud pendientes de decisión antes de entrenar.

## 1. Alcance y trazabilidad

Se utilizó únicamente `notebooks/data/spanish-dataset/SpanishDataset.csv`. El archivo original no se modificó. Su SHA-256 verificado es `656b2245d58da72d640680e5c2a168673a130b38607f2a427c773bbb167e995e`, correspondiente a la versión 5 documentada con DOI `10.17632/hz2d6gz7pc.5` y licencia CC BY 4.0.

SpearPhishMX no es leído por el script, no aparece en `source_dataset` y no se incorpora a `target`. No se entrenó ningún modelo.

## 2. Metodología reproducible

La preparación se implementó en `notebooks/preparacion-datos/prepare_spaphish_v5.py` y se documentó en `notebooks/preparacion-datos/spaphish-v5-preparation.ipynb`.

El proceso:

1. verifica el hash, la forma esperada de 1.395 filas por 47 columnas, los hashes únicos y el dominio binario de `Label`;
2. combina `subject` y `body` con dos saltos de línea;
3. conserva `text_original` y crea `text` con normalización mínima de finales de línea y espacios exteriores;
4. copia `Label` sin cambios a `target`;
5. identifica duplicados y candidatos de similitud antes de particionar;
6. forma grupos conservadores y asigna un `group_id` estable;
7. crea train/validation/test con `StratifiedGroupKFold`, 20 folds, semilla 42 y mapeo 14/3/3;
8. verifica que ningún grupo ni conflicto de etiqueta atraviese particiones;
9. genera el corpus, el manifiesto y los archivos de revisión.

## 3. Auditoría de columnas y contrato de características

Las columnas fuente para el modelo base son `subject` y `body`; la etiqueta original es `Label` y el identificador es `hash`.

El contrato del primer experimento usa exclusivamente `text` como predictor. Las decisiones completas para las 47 columnas están en `manifest.json`.

| Tipo de columna | Decisión | Justificación |
|---|---|---|
| `subject`, `body` | combinar en `text` | Contienen el mensaje observable por el usuario. |
| `Label` | copiar a `target`, nunca predictor | Es la variable objetivo; se preservan sus valores. |
| `hash` | usar solo para `record_id` | Un identificador/hash no representa contenido generalizable y podría inducir memorización. |
| `date` | reservar | Tiene 24 nulos y puede introducir señales temporales o de procedencia; requiere una ablación separada. |
| URL, adjuntos y saltos (`url_count`, `urls`, `attachments_*`, `hops_count`) | reservar para una ablación posterior | El baseline debe aislar la contribución del texto. Las URLs visibles dentro del mensaje sí se conservan en `text`. |
| 35 columnas psicológicas y justificaciones | excluir | Son anotaciones posteriores a la lectura y pueden filtrar conocimiento del objetivo. |

No se eliminan URL, dominios, números, signos, mayúsculas, acentos ni Unicode. Esta decisión conserva señales potencialmente útiles de phishing.

## 4. Calidad y transformaciones del texto

| Control | Resultado |
|---|---:|
| Registros originales | 1.395 |
| Registros conservados | 1.395 |
| Registros excluidos | 0 |
| `subject` nulo | 3, conservados con cuerpo |
| `body` nulo | 0 |
| Texto final vacío | 0 |
| Hash/`record_id` duplicado | 0 |
| Avisos conservadores de posible codificación u ofuscación | 16, conservados |

`text_original` conserva la combinación de los valores leídos del CSV antes de la normalización mínima. La inmutabilidad byte a byte del origen se garantiza mediante el CSV original y su hash. Los 16 avisos de caracteres potencialmente mal codificados no se corrigen automáticamente porque algunos pueden ser ofuscación real; necesitan revisión humana antes de definir una reparación.

## 5. Duplicados, plantillas y similitud

Para comparaciones se aplica NFKC, minúsculas y colapso de espacios. La versión de plantilla sustituye correos, URLs, teléfonos y secuencias numéricas solo para detectar variantes; esta transformación no modifica `text`.

La similitud aproximada usa TF-IDF de caracteres `char_wb` de 3 a 5, hasta 60.000 características, y coseno. Se registran pares con coseno >= 0,90.

La revisión inicial mostró que coseno >= 0,95 por sí solo puede unir correos legítimos no relacionados que comparten pies institucionales. Por ello, la regla automática quedó deliberadamente conservadora:

- plantilla normalizada exactamente igual; o
- coseno >= 0,95 **y** asunto normalizado exactamente igual.

| Resultado de agrupación | Cantidad |
|---|---:|
| Grupos de texto normalizado exacto | 0 |
| Grupos de plantilla exacta | 26 |
| Pares candidatos con coseno >= 0,90 | 486 |
| Pares con coseno >= 0,95 | 154 |
| Pares >= 0,95 y mismo asunto usados por la regla | 121 |
| Grupos con más de un registro | 47 |
| Registros dentro de esos grupos | 141 |
| Tamaño máximo de grupo | 10 |
| Grupos totales | 1.301 |
| Grupos con conflicto de etiqueta | 0 |

La similitud no demuestra un origen común. `group_review.csv` permite revisar los 47 grupos sin imprimir cuerpos completos. `near_duplicate_candidates.csv` conserva todos los candidatos: 161 pares pertenecen a componentes agrupados y 325 quedan pendientes. De estos últimos, 142 caen actualmente en particiones diferentes y deben ser aprobados o reagrupados antes de usar la partición para ML.

## 6. Esquema procesado

El corpus contiene:

- `text_original`: copia de trabajo previa a la normalización mínima;
- `text`: único predictor autorizado para el baseline;
- `target`: copia entera sin cambios de `Label`;
- `language`: `es`;
- `source_dataset`: `spaphish_v5`;
- `record_id`: `spaphish:<hash-origen>`;
- `group_id`: identificador estable del componente de duplicados/plantillas;
- `split`: partición reproducible.

Los seis campos solicitados (`text`, `target`, `language`, `source_dataset`, `record_id`, `group_id`) están presentes. `text_original` y `split` son campos adicionales de trazabilidad y no son predictores.

## 7. Distribución y particiones

La distribución global preservada es 664 registros con etiqueta 0 y 731 con etiqueta 1.

| Partición | Registros | Proporción | Target 0 | Target 1 | Grupos |
|---|---:|---:|---:|---:|---:|
| Train | 977 | 70,036 % | 466 | 511 | 905 |
| Validación | 208 | 14,910 % | 99 | 109 | 197 |
| Prueba | 210 | 15,054 % | 99 | 111 | 199 |

Las desviaciones respecto a 70/15/15 son +0,036, -0,090 y +0,054 puntos porcentuales. El solapamiento de `group_id` entre conjuntos es cero y cada grupo contiene una única etiqueta.

## 8. Registros conservados, descartados y pendientes

| Estado | Registros/pares | Tratamiento |
|---|---:|---|
| Registros conservados | 1.395 | Incluidos sin cambiar etiqueta. |
| Registros descartados | 0 | No se encontró motivo verificable para excluirlos. |
| Registros con asunto nulo | 3 | Conservados; se usa el cuerpo. |
| Registros con aviso conservador de codificación | 16 | Conservados; revisión humana pendiente. |
| Pares candidatos pendientes | 325 | No eliminados ni reetiquetados; documentados para decisión. |
| Pares pendientes que cruzan particiones | 142 | Riesgo residual de fuga que debe resolverse antes de ML. |

`exclusions.csv` queda vacío, con encabezados, para mantener trazabilidad explícita.

## 9. Limitaciones

- Las reglas de plantilla y coseno son heurísticas: reducen fugas conocidas, pero no prueban independencia semántica.
- Los 325 pares pendientes requieren adjudicación o una política aprobada; 142 cruzan particiones.
- La detección de caracteres problemáticos es conservadora y puede mezclar errores de codificación con ofuscación intencional.
- La partición estratificada por grupos aproxima, pero no puede garantizar exactamente, 70/15/15.
- El baseline propuesto mide texto solamente; las variables técnicas aún no se han evaluado mediante ablaciones.

## 10. Decisiones recomendadas antes de ML

1. **Aprobar la política de grupos:** mantener la regla conservadora actual o ampliar la agrupación después de revisar los 325 pares pendientes. No debe iniciarse el experimento definitivo mientras los 142 pares pendientes entre particiones no tengan una decisión documentada.
2. **Aprobar el contrato del baseline:** `text` como único predictor, con metadatos técnicos reservados para experimentos posteriores.
3. **Aprobar la conservación de los 16 avisos de codificación:** mantenerlos sin cambio en el baseline o adjudicar correcciones registro por registro.
4. **Congelar la semilla y los identificadores de partición:** semilla 42 y división actual, una vez cerrada la revisión de similitud.
5. **Mantener SpearPhishMX fuera del objetivo binario:** cualquier uso futuro debe ser un experimento separado y documentado.

## 11. Archivos generados

- `notebooks/preparacion-datos/prepare_spaphish_v5.py`
- `notebooks/preparacion-datos/spaphish-v5-preparation.ipynb`
- `notebooks/data/processed/spaphish_v5/spaphish_v5_corpus.csv`
- `notebooks/data/processed/spaphish_v5/manifest.json`
- `notebooks/data/processed/spaphish_v5/group_review.csv`
- `notebooks/data/processed/spaphish_v5/near_duplicate_candidates.csv`
- `notebooks/data/processed/spaphish_v5/exclusions.csv`

Los hashes de los archivos derivados están registrados en el manifiesto.
