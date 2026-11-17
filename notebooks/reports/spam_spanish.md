# Análisis: spam_spanish

## Descripción y procedencia

Mensajes cortos en español con etiquetas numéricas 0/1; los ejemplos inspeccionados indican 0 legítimo y 1 spam.

**Ubicación:** `notebooks/data/spam/data.csv`  
**Procedencia verificable:** No hay fuente, licencia ni diccionario de etiquetas en el repositorio; la semántica 0/1 se infiere de ejemplos y debe confirmarse.

## Estructura

- Formato: CSV, UTF-8, separador `,`.
- Registros: **15,016**.
- Columnas: **2**.
- Variable objetivo: **`labels`**.
- Columnas de texto evaluadas: `text`.
- Tamaño: 1,289,659 bytes.
- SHA-256: `1d455d3a28bbd58e310591be4bee236cf6d2244b5406af76ce1052f7301158ac`.

| Columna | Tipo inferido | Nulos | Nulos % |
|---|---:|---:|---:|
| `text` | `str` | 0 | 0.00% |
| `labels` | `int64` | 0 | 0.00% |

## Distribución de clases

| Clase | Registros | Porcentaje |
|---|---:|---:|
| `1` | 7982 | 53.16% |
| `0` | 7034 | 46.84% |

## Calidad y duplicados

- Filas completamente duplicadas: **266**.
- Filas involucradas en textos normalizados repetidos: **416**.
- Textos normalizados con etiquetas conflictivas: **0**.
- Filas sin texto: **0**.
- Filas con caracteres de reemplazo: **0**.
- Filas con marcadores de posible mojibake: **1**.
- Patrones encontrados sin abrir enlaces: URL **707**, correo **94**, teléfono **192**.

## Longitud del texto

| Métrica | Caracteres | Palabras |
|---|---:|---:|
| Mínimo | 14 | 0 |
| Q1 | 66 | 10 |
| Mediana | 78 | 12 |
| Media | 79.78 | 12.31 |
| Q3 | 91 | 14 |
| P95 | 114 | 18 |
| Máximo | 1 320 | 149 |

## Idiomas

Resultado observado: es: 12244, indeterminado: 2751, en: 21. La heurística sólo distingue señales claras de español e inglés; `indeterminado` no representa un tercer idioma. Cuando existe una columna declarada se reporta esa columna, no una detección independiente.

## Ejemplos representativos

Los ejemplos se seleccionaron cerca de la longitud mediana de cada clase. Se desactivaron esquemas URL y se ocultaron correos/teléfonos en el informe.

**Clase `0`**
- Hola, ¿cómo estás? Me gustaría concertar una cita para la próxima semana.
- El evento de today fue un éxito. Gracias por tu apoyo y par la próxima!,.

**Clase `1`**
- ¡Esquema piramidal! Invita a 3 personas y gane $5000. ¡Comparte este mensaje ahora!
- ¡Felicidades! Has ganado un viaje a Puerto Rico. Clic en este enlace para confirmar

## Características útiles

- Texto del asunto y cuerpo o mensaje.
- Longitud, conteos de palabras y caracteres especiales.
- Presencia y cantidad de URLs, correos, teléfonos y términos de urgencia.
- Metadatos propios del dataset, únicamente tras comprobar que no derivan de la etiqueta.
- TF-IDF de palabras y caracteres, con selección o reducción de dimensionalidad para Random Forest.

## Ventajas

- 15 016 registros y distribución cercana al equilibrio.
- Contenido mayoritariamente español según heurística reproducible.

## Problemas, limitaciones y sesgos

- Contiene 266 filas duplicadas y 416 filas involucradas en textos duplicados.
- Spam abarca promociones, fraudes y mensajes no solicitados; no es una etiqueta específica de phishing.
- No contiene asunto, remitente ni metadatos de correo.

**Sesgo probable:** Mensajes breves y formulaciones de spam evidentes; representa peor correos largos o spear phishing.

## Utilidad para el proyecto y Random Forest

**Utilidad estimada:** Media como señal auxiliar en español; baja-media para entrenar por sí solo un detector de phishing.

**Random Forest:** Adecuado para probar TF-IDF + reducción/selección y variables de longitud/URLs, después de deduplicar y confirmar etiquetas.

**Combinación:** Puede añadirse como clase maliciosa auxiliar sólo si se conserva su etiqueta original `spam` y se evalúa por separado de phishing.

## Recomendaciones

- Confirmar la definición de 0/1 con la fuente original.
- Deduplicar antes de dividir y conservar un conjunto específico de phishing real.

## Reproducibilidad

Métricas generadas por `notebooks/exploracion-datasets/dataset_audit.py`. No se modificó el CSV original. La procedencia y licencia siguen pendientes cuando no aparecen en el repositorio.
