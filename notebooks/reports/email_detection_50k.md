# Análisis: email_detection_50k

## Descripción y procedencia

Correos en inglés con 44 campos de contenido, remitente, autenticación, reputación y una etiqueta binaria.

**Ubicación:** `notebooks/data/email-detection-dataset/dataset_v2.csv`  
**Procedencia verificable:** El repositorio no contiene README, URL, licencia ni referencia bibliográfica para verificar la procedencia. El nombre de carpeta no es evidencia suficiente de origen.

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

- Volumen alto y clases utilizables para comparación experimental.
- Incluye texto, asunto y variables técnicas que permiten estudiar varios grupos de características.
- No presenta filas ni textos duplicados dentro del archivo.

## Problemas, limitaciones y sesgos

- Los mensajes repiten plantillas y las variables son muy regulares; esto constituye evidencia de datos sintéticos o generados, aunque la procedencia no permite confirmarlo.
- `phishing_probability` separa las clases por construcción: 0–49 para legítimos y 50–100 para phishing. Usarla sería fuga directa de la etiqueta.
- `spoofed_domain`, reputación de URL y estados SPF/DKIM/DMARC están fuertemente asociados a la etiqueta y pueden producir una evaluación artificial si fueron usados para generarla.
- Sólo contiene inglés declarado; no valida desempeño en español.

**Sesgo probable:** Favorece correos con patrones explícitos de urgencia, fallos de autenticación y dominios marcados. Puede subrepresentar phishing bien redactado o con infraestructura comprometida legítima.

## Utilidad para el proyecto y Random Forest

**Utilidad estimada:** Media como benchmark en inglés y para prototipos; baja como única evidencia de generalización real.

**Random Forest:** Utilizable con TF-IDF reducido o variables léxicas/técnicas, excluyendo campos posteriores a la etiqueta y validando por plantillas o grupos. Random Forest sobre TF-IDF completo puede ser costoso y debe compararse con un baseline lineal.

**Combinación:** Mantener como corpus inglés separado. No concatenar con su copia. Combinar sólo después de armonizar etiquetas y conservar una columna `source_dataset` para dividir y auditar por origen.

## Recomendaciones

- Excluir `phishing_probability` y evaluar en ablación todas las variables de reputación/autenticación.
- Separar plantillas o remitentes entre entrenamiento y prueba para reducir fuga por patrón.
- Buscar y documentar fuente, licencia y método de generación antes de usarlo en la tesis.

## Reproducibilidad

Métricas generadas por `notebooks/exploracion-datasets/dataset_audit.py`. No se modificó el CSV original. La procedencia y licencia siguen pendientes cuando no aparecen en el repositorio.
