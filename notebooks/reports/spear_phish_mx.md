# Análisis: spear_phish_mx

## Descripción y procedencia

Correos en español orientados a spear phishing, con cuerpo sanitizado, destinatario, URLs desactivadas y etiqueta binaria.

**Ubicación:** `notebooks/data/spear-pish/SpearPhishMX_dataset_publico.csv`  
**Procedencia verificable:** El nombre sugiere un dataset mexicano, pero el repositorio no aporta fuente, licencia ni metodología verificable.

## Estructura

- Formato: CSV, UTF-8, separador `;`.
- Registros: **3,006**.
- Columnas: **17**.
- Variable objetivo: **`etiqueta`**.
- Columnas de texto evaluadas: `asunto`, `cuerpo_sanitizado`.
- Tamaño: 5,118,920 bytes.
- SHA-256: `12c4f5fbd6458fe0a73f44db4abd634f04055e64e40d8d104f7cece5ce53ae32`.

| Columna | Tipo inferido | Nulos | Nulos % |
|---|---:|---:|---:|
| `hash` | `str` | 0 | 0.00% |
| `id_original` | `int64` | 0 | 0.00% |
| `etiqueta` | `int64` | 0 | 0.00% |
| `asunto` | `str` | 2 | 0.07% |
| `cuerpo_sanitizado` | `str` | 0 | 0.00% |
| `fecha` | `float64` | 3006 | 100.00% |
| `conteo_urls` | `int64` | 0 | 0.00% |
| `urls_desactivadas` | `str` | 0 | 0.00% |
| `dirigido_a_persona_v2` | `bool` | 0 | 0.00% |
| `destinatario_detectado_v2` | `str` | 283 | 9.41% |
| `destinatario_tiene_apellido_v2` | `bool` | 0 | 0.00% |
| `destinatario_normalizado` | `str` | 0 | 0.00% |
| `conteo_adjuntos` | `int64` | 0 | 0.00% |
| `tipos_adjuntos` | `float64` | 3006 | 100.00% |
| `tamano_total_adjuntos` | `int64` | 0 | 0.00% |
| `tamanos_adjuntos` | `float64` | 3006 | 100.00% |
| `conteo_saltos` | `float64` | 3006 | 100.00% |

## Distribución de clases

| Clase | Registros | Porcentaje |
|---|---:|---:|
| `1` | 1891 | 62.91% |
| `0` | 1115 | 37.09% |

## Calidad y duplicados

- Filas completamente duplicadas: **0**.
- Filas involucradas en textos normalizados repetidos: **4**.
- Textos normalizados con etiquetas conflictivas: **0**.
- Filas sin texto: **0**.
- Filas con caracteres de reemplazo: **16**.
- Filas con marcadores de posible mojibake: **28**.
- Patrones encontrados sin abrir enlaces: URL **1928**, correo **4**, teléfono **304**.

## Longitud del texto

| Métrica | Caracteres | Palabras |
|---|---:|---:|
| Mínimo | 50 | 6 |
| Q1 | 254 | 34 |
| Mediana | 433 | 60 |
| Media | 1011.36 | 151.01 |
| Q3 | 896.75 | 135.75 |
| P95 | 3652.50 | 550 |
| Máximo | 28 478 | 4 178 |

## Idiomas

Resultado observado: es: 2916, indeterminado: 54, en: 36. La heurística sólo distingue señales claras de español e inglés; `indeterminado` no representa un tercer idioma. Cuando existe una columna declarada se reporta esa columna, no una detección independiente.

## Ejemplos representativos

Los ejemplos se seleccionaron cerca de la longitud mediana de cada clase. Se desactivaron esquemas URL y se ocultaron correos/teléfonos en el informe.

**Clase `0`**
- Maestria Hola Emanuel Ortega Carbajal, Nesti mira... donde trabajaba mike.... ¿Sabías que en la Unidad del CICESE en Tepic tenemos una maestría que pertenece al Sistema Nacional de Posgrado? ¿Que sus objetivos son "Formar recursos humanos altamente especializados con conocimiento…
- Missxtranger, Advertencia final: ¡tu cuenta de Netflix será eliminada! Hola Juan Galván Torres, ¡Continúa disfrutando de películas, programas de TV y más ilimitados! ¿Listo para mirar? N E T F L I X ¡Tu membresía ha caducado! Querido cliente, Su membresía ha caducado. Pero, como …

**Clase `1`**
- Problema con Configuración de Load Balancer Hola Bernal Ramos García, Su configuración de load balancer presenta errores. Revisar settings en: hxxp://www[.]xmadwater[.]com[.]cn/js/?app=com-d3&us[.]battle[.]net/login/en/?ref=us[.]battle[.]net/d3/en/index Urgente - plazo 10 días. L…
- Oferta de Capacitación en Containers Estimado Herlindo De La Cruz Gómez, Programa especial de capacitación en tecnologías de contenedores. Registro en: hxxp://paypal[.]com[.]myaccount[.]validation[.]jossy[.]psess<TELEFONO>[.]blesuites[.]com Cupos limitados - válido hasta 19/12/20…

## Características útiles

- Texto del asunto y cuerpo o mensaje.
- Longitud, conteos de palabras y caracteres especiales.
- Presencia y cantidad de URLs, correos, teléfonos y términos de urgencia.
- Metadatos propios del dataset, únicamente tras comprobar que no derivan de la etiqueta.
- TF-IDF de palabras y caracteres, con selección o reducción de dimensionalidad para Random Forest.

## Ventajas

- 3 006 registros con clases 1/0 y abundante contenido textual.
- URLs están desactivadas y no se ejecutaron durante el análisis.
- Incluye señales de personalización útiles para estudiar spear phishing.

## Problemas, limitaciones y sesgos

- `fecha`, tipos/tamaños de adjuntos y saltos son totalmente nulos.
- Hay 283 destinatarios detectados nulos y dos asuntos nulos.
- Se observaron pocos textos duplicados y problemas puntuales de caracteres.

**Sesgo probable:** Favorece mensajes dirigidos y contexto corporativo mexicano; puede sobreestimar señales de nombres propios y urgencia formal.

## Utilidad para el proyecto y Random Forest

**Utilidad estimada:** Alta para ampliar el corpus español y estudiar spear phishing, con cautela por procedencia no documentada.

**Random Forest:** Adecuado para características textuales y de personalización. Eliminar columnas 100 % nulas y separar por destinatario/plantilla cuando sea posible.

**Combinación:** Combinar de forma controlada con `spanish_phishing`, preservando `source_dataset` y evaluando un holdout por fuente.

## Recomendaciones

- Verificar etiqueta y método de sanitización con la fuente original.
- No usar columnas completamente nulas y evaluar posible fuga mediante `id_original` o destinatario.

## Reproducibilidad

Métricas generadas por `notebooks/exploracion-datasets/dataset_audit.py`. No se modificó el CSV original. La procedencia y licencia siguen pendientes cuando no aparecen en el repositorio.
