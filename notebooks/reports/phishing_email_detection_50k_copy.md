# Análisis: phishing_email_detection_50k_copy

## Descripción y procedencia

Copia exacta del archivo `email-detection-dataset/dataset_v2.csv`.

**Ubicación:** `notebooks/data/PhishingEmailDetection50KEmails/phishing_email_detection_dataset_v2.csv`  
**Procedencia verificable:** No hay procedencia documentada. El SHA-256 coincide exactamente con el otro CSV de 50 000 correos.

Los dos archivos de 50 000 correos tienen el mismo SHA-256 `c090464babc627f396e3211113c48b94a533ac27a16be691d29e45c1c70110e9` y son copias exactas.

## Estructura

- Formato: CSV, UTF-8, separador `,`.
- Registros: **50,000**.
- Columnas: **44**.
- Variable objetivo: **`label`**.
- Columnas de texto evaluadas: `subject`, `email_body`.
- Tamaño: 34,795,895 bytes.
- SHA-256: `c090464babc627f396e3211113c48b94a533ac27a16be691d29e45c1c70110e9`.

| Columna | Tipo inferido | Nulos | Nulos % |
|---|---:|---:|---:|
| `email_id` | `str` | 0 | 0.00% |
| `sender_name` | `str` | 0 | 0.00% |
| `sender_email` | `str` | 0 | 0.00% |
| `sender_ip` | `str` | 0 | 0.00% |
| `sender_country` | `str` | 0 | 0.00% |
| `sender_domain` | `str` | 0 | 0.00% |
| `domain_age_days` | `int64` | 0 | 0.00% |
| `recipient_email` | `str` | 0 | 0.00% |
| `subject` | `str` | 0 | 0.00% |
| `email_body` | `str` | 0 | 0.00% |
| `contains_link` | `str` | 0 | 0.00% |
| `url_domain` | `str` | 21128 | 42.26% |
| `url_reputation` | `str` | 0 | 0.00% |
| `contains_attachment` | `str` | 0 | 0.00% |
| `attachment_type` | `str` | 22695 | 45.39% |
| `brand_impersonated` | `str` | 24036 | 48.07% |
| `spf_status` | `str` | 0 | 0.00% |
| `dkim_status` | `str` | 0 | 0.00% |
| `dmarc_status` | `str` | 0 | 0.00% |
| `is_html_email` | `str` | 0 | 0.00% |
| `email_length` | `int64` | 0 | 0.00% |
| `word_count` | `int64` | 0 | 0.00% |
| `reading_time_minutes` | `float64` | 0 | 0.00% |
| `character_entropy` | `float64` | 0 | 0.00% |
| `readability_score` | `int64` | 0 | 0.00% |
| `num_links` | `int64` | 0 | 0.00% |
| `num_special_characters` | `int64` | 0 | 0.00% |
| `num_uppercase_words` | `int64` | 0 | 0.00% |
| `suspicious_keyword_count` | `int64` | 0 | 0.00% |
| `urgency_score` | `int64` | 0 | 0.00% |
| `grammar_score` | `int64` | 0 | 0.00% |
| `sender_reputation` | `str` | 0 | 0.00% |
| `spoofed_domain` | `str` | 0 | 0.00% |
| `sent_date` | `str` | 0 | 0.00% |
| `sent_time` | `str` | 0 | 0.00% |
| `day_of_week` | `str` | 0 | 0.00% |
| `month` | `str` | 0 | 0.00% |
| `hour` | `int64` | 0 | 0.00% |
| `language` | `str` | 0 | 0.00% |
| `email_category` | `str` | 0 | 0.00% |
| `device_type` | `str` | 0 | 0.00% |
| `email_client` | `str` | 0 | 0.00% |
| `phishing_probability` | `int64` | 0 | 0.00% |
| `label` | `str` | 0 | 0.00% |

## Distribución de clases

| Clase | Registros | Porcentaje |
|---|---:|---:|
| `Legitimate` | 29629 | 59.26% |
| `Phishing` | 20371 | 40.74% |

## Calidad y duplicados

- Filas completamente duplicadas: **0**.
- Filas involucradas en textos normalizados repetidos: **0**.
- Textos normalizados con etiquetas conflictivas: **0**.
- Filas sin texto: **0**.
- Filas con caracteres de reemplazo: **0**.
- Filas con marcadores de posible mojibake: **0**.
- Patrones encontrados sin abrir enlaces: URL **0**, correo **0**, teléfono **0**.

## Longitud del texto

| Métrica | Caracteres | Palabras |
|---|---:|---:|
| Mínimo | 234 | 32 |
| Q1 | 318 | 44 |
| Mediana | 362 | 51 |
| Media | 362.21 | 50.69 |
| Q3 | 406 | 57 |
| P95 | 448 | 63 |
| Máximo | 516 | 75 |

## Idiomas

Resultado observado: English: 50000. La heurística sólo distingue señales claras de español e inglés; `indeterminado` no representa un tercer idioma. Cuando existe una columna declarada se reporta esa columna, no una detección independiente.

## Ejemplos representativos

Los ejemplos se seleccionaron cerca de la longitud mediana de cada clase. Se desactivaron esquemas URL y se ocultaron correos/teléfonos en el informe.

**Clase `Legitimate`**
- Payment Schedule Received Dear User, We're reaching out regarding your recent activity. The requested report has been generated. No additional action is required. Your transaction was completed successfully. Your payment has been received. Your transaction was completed successfu…
- Monthly Report Processed Good Afternoon, Please review the following information. Your transaction was completed successfully. Your transaction was completed successfully. Your meeting invitation has been created. No additional action is required. Your transaction was completed s…

**Clase `Phishing`**
- Action Required: Recover Your Security Hi, Your banking information requires verification. Click the secure link below. Claim your reward before it expires. Login now to prevent interruption. Your payment method has expired. Failure to respond may suspend your account. Click the …
- Attention: Confirm Your Identity Dear User, Your mailbox storage is almost full. Your payment method has expired. Your password expires today. Restore account access now. Verify your account immediately. Update your billing information. Failure to respond may suspend your account…

## Características útiles

- Texto del asunto y cuerpo o mensaje.
- Longitud, conteos de palabras y caracteres especiales.
- Presencia y cantidad de URLs, correos, teléfonos y términos de urgencia.
- Metadatos propios del dataset, únicamente tras comprobar que no derivan de la etiqueta.
- TF-IDF de palabras y caracteres, con selección o reducción de dimensionalidad para Random Forest.

## Ventajas

- Mismas propiedades que `email_detection_50k`.

## Problemas, limitaciones y sesgos

- No aporta registros nuevos; contar ambos duplicaría por completo el corpus y contaminaría cualquier partición.

**Sesgo probable:** Idéntico al archivo original; todos sus sesgos se repetirían dos veces.

## Utilidad para el proyecto y Random Forest

**Utilidad estimada:** Nula como dataset adicional; conservar sólo como archivo inventariado hasta decidir cuál ruta será la canónica.

**Random Forest:** No debe entrar dos veces al entrenamiento ni a la evaluación.

**Combinación:** No combinar. Seleccionar una sola copia mediante hash antes de construir datasets derivados.

## Recomendaciones

- No eliminarla en esta fase; documentar la duplicación y excluirla de futuros ensamblajes.

## Reproducibilidad

Métricas generadas por `notebooks/exploracion-datasets/dataset_audit.py`. No se modificó el CSV original. La procedencia y licencia siguen pendientes cuando no aparecen en el repositorio.
