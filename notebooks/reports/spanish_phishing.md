# Análisis: spanish_phishing

## Descripción y procedencia

Correos en español con asunto, cuerpo, URLs, adjuntos, etiqueta binaria y anotaciones de principios de persuasión por tres evaluadores.

**Ubicación:** `notebooks/data/spanish-dataset/SpanishDataset.csv`  
**Procedencia verificable:** No hay URL, licencia ni publicación citada dentro del repositorio.

## Estructura

- Formato: CSV, UTF-8, separador `,`.
- Registros: **1,395**.
- Columnas: **47**.
- Variable objetivo: **`Label`**.
- Columnas de texto evaluadas: `subject`, `body`.
- Tamaño: 5,098,917 bytes.
- SHA-256: `656b2245d58da72d640680e5c2a168673a130b38607f2a427c773bbb167e995e`.

| Columna | Tipo inferido | Nulos | Nulos % |
|---|---:|---:|---:|
| `hash` | `str` | 0 | 0.00% |
| `subject` | `str` | 3 | 0.22% |
| `body` | `str` | 0 | 0.00% |
| `date` | `str` | 24 | 1.72% |
| `url_count` | `int64` | 0 | 0.00% |
| `urls` | `str` | 195 | 13.98% |
| `attachments_count` | `int64` | 0 | 0.00% |
| `attachments_types` | `str` | 1124 | 80.57% |
| `attachments_total_size` | `int64` | 0 | 0.00% |
| `attachments_sizes` | `str` | 1124 | 80.57% |
| `hops_count` | `int64` | 0 | 0.00% |
| `Label` | `int64` | 0 | 0.00% |
| `authority_A` | `int64` | 0 | 0.00% |
| `justif_authority_A` | `str` | 0 | 0.00% |
| `social_proof_A` | `int64` | 0 | 0.00% |
| `justif_social_proof_A` | `str` | 0 | 0.00% |
| `liking_similarity_deception_A` | `int64` | 0 | 0.00% |
| `justif_liking_similarity_deception_A` | `str` | 0 | 0.00% |
| `commitment_integrity_reciprocation_A` | `int64` | 0 | 0.00% |
| `justif_commitment_integrity_reciprocation_A` | `str` | 0 | 0.00% |
| `distraction_A` | `int64` | 0 | 0.00% |
| `justif_distraction_A` | `str` | 5 | 0.36% |
| `authority_B` | `int64` | 0 | 0.00% |
| `justif_authority_B` | `str` | 0 | 0.00% |
| `social_proof_B` | `int64` | 0 | 0.00% |
| `justif_social_proof_B` | `str` | 0 | 0.00% |
| `liking_similarity_deception_B` | `int64` | 0 | 0.00% |
| `justif_liking_similarity_deception_B` | `str` | 0 | 0.00% |
| `commitment_integrity_reciprocation_B` | `int64` | 0 | 0.00% |
| `justif_commitment_integrity_reciprocation_B` | `str` | 0 | 0.00% |
| `distraction_B` | `int64` | 0 | 0.00% |
| `justif_distraction_B` | `str` | 3 | 0.22% |
| `authority_C` | `int64` | 0 | 0.00% |
| `justif_authority_C` | `str` | 0 | 0.00% |
| `social_proof_C` | `int64` | 0 | 0.00% |
| `justif_social_proof_C` | `str` | 0 | 0.00% |
| `liking_similarity_deception_C` | `int64` | 0 | 0.00% |
| `justif_liking_similarity_deception_C` | `str` | 0 | 0.00% |
| `commitment_integrity_reciprocation_C` | `int64` | 0 | 0.00% |
| `justif_commitment_integrity_reciprocation_C` | `str` | 0 | 0.00% |
| `distraction_C` | `int64` | 0 | 0.00% |
| `justif_distraction_C` | `str` | 0 | 0.00% |
| `authority` | `int64` | 0 | 0.00% |
| `social_proof` | `int64` | 0 | 0.00% |
| `liking_similarity_deception` | `int64` | 0 | 0.00% |
| `commitment_integrity_reciprocation` | `int64` | 0 | 0.00% |
| `distraction` | `int64` | 0 | 0.00% |

## Distribución de clases

| Clase | Registros | Porcentaje |
|---|---:|---:|
| `1` | 731 | 52.40% |
| `0` | 664 | 47.60% |

## Calidad y duplicados

- Filas completamente duplicadas: **0**.
- Filas involucradas en textos normalizados repetidos: **0**.
- Textos normalizados con etiquetas conflictivas: **0**.
- Filas sin texto: **0**.
- Filas con caracteres de reemplazo: **6**.
- Filas con marcadores de posible mojibake: **16**.
- Patrones encontrados sin abrir enlaces: URL **411**, correo **334**, teléfono **601**.

## Longitud del texto

| Métrica | Caracteres | Palabras |
|---|---:|---:|
| Mínimo | 17 | 2 |
| Q1 | 505 | 72.50 |
| Mediana | 759 | 111 |
| Media | 1255.00 | 190.22 |
| Q3 | 1317.50 | 198 |
| P95 | 3731.50 | 590.90 |
| Máximo | 28 673 | 3 384 |

## Idiomas

Resultado observado: es: 1350, indeterminado: 25, en: 20. La heurística sólo distingue señales claras de español e inglés; `indeterminado` no representa un tercer idioma. Cuando existe una columna declarada se reporta esa columna, no una detección independiente.

## Ejemplos representativos

Los ejemplos se seleccionaron cerca de la longitud mediana de cada clase. Se desactivaron esquemas URL y se ocultaron correos/teléfonos en el informe.

**Clase `0`**
- Registro_Beneficiarios_Plataforma_SNI REGISTRO DE BENEFICIARIOS EN CASO DE FALLECIMIENTO A los investigadores de nuevo ingreso y reingreso no-vigente cuya vigencia inició el 1º de enero del 2025, se hace de su conocimiento que pueden realizar el registro de sus beneficiarios en l…
- MyOwn Mario Castillo Buen día Dr. Lázaro, un gusto saludarle, no sé si me recuerde, soy Mario Castillo de MyOwn, tomé materia de la Maestría en Ciberseguridad con Usted, le comento que actualmente sigo en MyOwn, y estoy realizando trámites para el ingreso a Doctorado aquí en MyOw…

**Clase `1`**
- Ezequiela Miguelina - Tienes (1) paquete esperando ser entregado 📦. Usa tu código para rastrearlo y recibirlo ___🚚. ID#41868 ❒ ENTREGA DEL PAQUETE PENDIENTE ◉ Registro / Inicio de sesión ❒ Correos [telefono-oculto] SEGUIMIENTO ➢ pablito Tienes (1) paquete pendiente de entrega ---…
- >>Ezequiela Miguelina!! - Hai un (1) pacco in attesa di consegna 📦. Usa il tuo codice per tracciarlo e riceverlo ___🚚. ENTREGA DEL PAQUETE PENDIENTE ◉ Registro / Inicio de sesión ❒SEUR. [telefono-oculto] SEGUIMIENTO ➢ Claudia Ramírez Tienes (1) paquete pendiente de entrega ------…

## Características útiles

- Texto del asunto y cuerpo o mensaje.
- Longitud, conteos de palabras y caracteres especiales.
- Presencia y cantidad de URLs, correos, teléfonos y términos de urgencia.
- Metadatos propios del dataset, únicamente tras comprobar que no derivan de la etiqueta.
- TF-IDF de palabras y caracteres, con selección o reducción de dimensionalidad para Random Forest.

## Ventajas

- Clases relativamente equilibradas (731/664).
- Mensajes largos y metadatos de URL/adjuntos, más anotaciones útiles para explicaciones.
- No presenta textos duplicados normalizados ni conflictos de etiqueta.

## Problemas, limitaciones y sesgos

- Algunos campos de adjuntos son nulos en 1 124 registros y `urls` es nulo en 195.
- Hay pequeños problemas de codificación y asuntos nulos.
- Las variables agregadas de persuasión pueden depender de anotación posterior y deben separarse del detector principal para evitar confundir explicación con predicción.

**Sesgo probable:** Corpus mexicano/español con mensajes de longitud muy variable y señales de persuasión explícitas; puede no cubrir variedades regionales o ataques muy breves.

## Utilidad para el proyecto y Random Forest

**Utilidad estimada:** Alta para la tesis en español, sujeta a verificar procedencia/licencia y protocolo de anotación.

**Random Forest:** Prometedor con texto TF-IDF reducido, conteos y metadatos. Las anotaciones A/B/C y agregadas deben evaluarse como módulo explicativo o experimento separado.

**Combinación:** Candidato principal para combinar con SpearPhishMX tras armonizar etiquetas, esquema y deduplicación cruzada. Conservar origen para evaluación por dominio.

## Recomendaciones

- Documentar significado exacto de Label y acuerdo entre anotadores.
- Tratar cuerpo y asunto por separado y añadir pruebas con/sin variables de persuasión.
- Imputar nulos sólo en un pipeline reproducible y con indicadores de ausencia.

## Reproducibilidad

Métricas generadas por `notebooks/exploracion-datasets/dataset_audit.py`. No se modificó el CSV original. La procedencia y licencia siguen pendientes cuando no aparecen en el repositorio.
