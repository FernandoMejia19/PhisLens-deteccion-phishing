# Validación de `spanish_phishing` y `spear_phish_mx`

**Fecha de ejecución:** 17 de noviembre de 2026  
**Rama:** `validacion-dataset`  
**Alcance:** decidir si ambos datasets pueden formar un corpus binario principal en español. No se entrenó ningún modelo ni se modificaron los CSV originales.

## Conclusión ejecutiva

Los datasets **no deben concatenarse directamente** para construir el corpus principal. Las etiquetas documentadas usan los valores compatibles `0 = legítimo` y `1 = phishing`, pero el objetivo positivo no es idéntico: SpaPhish clasifica phishing general y SpearPhishMX clasifica spear-phishing. Además, se encontró un solapamiento textual cruzado amplio y no declarado en los metadatos locales: 465 registros de SpaPhish tienen un mejor vecino en SpearPhishMX con similitud coseno igual o superior a 0,90. De esos 465 pares, 354 tienen etiquetas diferentes; 322 siguen el patrón `SpaPhish 1 -> SpearPhishMX 0`.

Los ejemplos de mayor similitud muestran el mismo asunto y cuerpo base, con cambios como una salutación personalizada, anonimización y desactivación de enlaces. Por tanto, los datasets no pueden considerarse independientes. Concatenarlos y hacer una división aleatoria provocaría fuga entre entrenamiento y prueba, sobreestimaría el rendimiento y mezclaría dos conceptos de etiqueta que necesitan una decisión explícita.

La combinación es **condicionalmente viable**, no viable en bruto. Requiere aclarar el significado operativo de la clase 0 de SpearPhishMX frente a mensajes que SpaPhish marca como phishing, construir grupos cruzados de mensajes base, adjudicar conflictos y dividir por `group_id`.

## Archivos y reproducibilidad

- SpaPhish local: `notebooks/data/spanish-dataset/SpanishDataset.csv`.
- SpearPhishMX local: `notebooks/data/spear-pish/SpearPhishMX_dataset_publico.csv`.
- Script reproducible: `notebooks/validacion-datasets/validate_spanish_corpus.py`.
- Resumen estructurado: `notebooks/reports/data/spanish_corpus_validation.json`.

El script es de solo lectura sobre los CSV. Produce métricas, hashes de integridad, muestras redactadas y pares identificados por número de fila; no guarda los cuerpos completos ni genera el corpus definitivo.

Hashes SHA-256 de los archivos analizados:

| Dataset | SHA-256 |
|---|---|
| `spanish_phishing` | `656b2245d58da72d640680e5c2a168673a130b38607f2a427c773bbb167e995e` |
| `spear_phish_mx` | `038fdfeac20c554a66b1ef42b2044627b3d2f5692135ac444b8a9e8486444a5b` |

Ejecución:

```powershell
.\.venv\Scripts\python.exe notebooks\validacion-datasets\validate_spanish_corpus.py
```

## Metodología

1. Se cargaron los CSV con Pandas, usando coma para SpaPhish y punto y coma para SpearPhishMX.
2. Se verificaron columnas, tipos, dominio de etiquetas, nulos, textos vacíos, hashes, duplicados y señales de codificación dañada.
3. Se formó el texto analítico como `asunto + salto de línea + cuerpo`, conservando el cuerpo cuando el asunto falta.
4. Para duplicados exactos se aplicó Unicode NFKC, minúsculas y compactación de espacios; luego se calculó SHA-256 del texto normalizado.
5. Para plantillas se sustituyeron correos, enlaces, teléfonos y números por marcadores antes del hash.
6. Para similitud cruzada se utilizó TF-IDF de caracteres de 3 a 5 gramos, hasta 60.000 características, y distancia coseno. Se buscó el mejor vecino de cada registro de SpaPhish en SpearPhishMX. Esta técnica detecta variaciones pequeñas, pero no demuestra por sí sola identidad de origen.
7. Se revisaron muestras deterministas cortas, medianas y largas de cada clase y los pares cruzados de mayor similitud. Los extractos se redactaron y no se ejecutó ningún enlace.
8. Se contrastó la estructura local con las publicaciones originales disponibles. La información no confirmada se mantiene como limitación.

## 1. Verificación de etiquetas

### `spanish_phishing` / SpaPhish

- Texto: `subject` y `body`.
- Etiqueta: `Label`.
- Evidencia: el esquema completo de 47 variables define `0 = legitimate` y `1 = phishing`; indica triple anotación, voto mayoritario y adjudicación por un cuarto experto cuando existía desacuerdo total. La publicación de SpaPhish confirma 664 registros de clase 0 y 731 de clase 1.
- Revisión de ejemplos: la clase 0 contiene comunicaciones institucionales, académicas y comerciales; la clase 1 contiene avisos falsos de bloqueo, suspensión de cuentas y solicitudes de verificación. Los ejemplos son coherentes en general con phishing binario.

La etiqueta principal no debe confundirse con las 35 columnas de principios de persuasión y justificaciones. Esas columnas fueron producidas por anotadores y constituyen fuga de información si se usan como predictores del modelo base.

### `spear_phish_mx` / SpearPhishMX

- Texto: `asunto` y `cuerpo_sanitizado`.
- Etiqueta: `etiqueta`.
- Evidencia: la página oficial y sus pasos de reproducción definen `1 = spear-phishing` y `0 = legítimo`.
- Revisión de ejemplos: la clase 1 contiene mensajes dirigidos con nombres o señales de personalización. La clase 0 contiene comunicaciones legítimas, pero también aparecen cuerpos casi idénticos a mensajes que SpaPhish clasifica como phishing.

La contradicción observada no autoriza a cambiar etiquetas automáticamente. Puede reflejar una diferencia entre “phishing” y “spear-phishing”, un procedimiento de construcción no explicado en los archivos locales o ruido de etiquetado. Debe resolverse con el README/esquema original y, si es posible, confirmación de los autores.

### Distribución

| Dataset | Clase 0 | Clase 1 | Total |
|---|---:|---:|---:|
| SpaPhish | 664 (47,60 %) | 731 (52,40 %) | 1.395 |
| SpearPhishMX | 1.115 (37,09 %) | 1.891 (62,91 %) | 3.006 |
| Suma sin depurar | 1.779 | 2.622 | 4.401 |

No hay etiquetas nulas ni valores fuera de `{0, 1}`.

## 2. Procedencia y licencia

### Información confirmada

**SpaPhish**

- Nombre original: *SpaPhish: A Spanish Dataset for Phishing and Psychological Pattern Detection*.
- Idioma: español nativo.
- Recopilación: correos reales de buzones personales e institucionales de los autores, entre 2014 y 2025.
- Privacidad: la publicación documenta anonimización manual mediante eliminación o sustitución ficticia de elementos identificables.
- Licencia del dataset: CC BY 4.0 en Mendeley Data.
- DOI de la versión 2, cuya estructura coincide con el archivo local: `10.17632/hz2d6gz7pc.2`. Existe una versión 5 posterior.
- Fuentes: [Mendeley Data, versión 2](https://data.mendeley.com/datasets/hz2d6gz7pc/2), [artículo Data in Brief](https://doi.org/10.1016/j.dib.2026.112890) y [esquema de variables publicado con el dataset](https://prod-dcd-datasets-public-files-eu-west-1.s3.eu-west-1.amazonaws.com/f4a964b2-eadd-4749-8423-15d1e8b669a3).

**SpearPhishMX**

- Nombre original: *Spear-Phishing en español: dataset de correos dirigidos con señales de personalización (SpearPhishMX)*.
- Idioma: español.
- Privacidad: `cuerpo_sanitizado` anonimiza correos, teléfonos y patrones fiscales/financieros; los enlaces se publican desactivados.
- Licencia del dataset: CC BY 4.0 en Mendeley Data.
- DOI de la versión 2: `10.17632/h4bxjk84jb.2`.
- Fuente: [Mendeley Data, versión 2](https://data.mendeley.com/datasets/h4bxjk84jb/2).

### Información no confirmada localmente

- El repositorio no conserva el README, esquema JSON ni archivo de licencia que acompañan a SpearPhishMX en Mendeley.
- Los CSV locales no contienen número de versión, DOI ni checksum publicado. Su estructura coincide con las versiones descritas, pero no se puede afirmar qué versión exacta fue descargada solo con los archivos del repositorio.
- La publicación accesible de SpearPhishMX describe 3.005 correos únicos, mientras el CSV local tiene 3.006 filas y 3.005 hashes únicos. Esto es compatible con un duplicado de hash, pero requiere contrastarlo con el paquete oficial.
- Ninguna fuente accesible consultada declara que SpearPhishMX derive de SpaPhish. El amplio solapamiento observado es evidencia local e inferencia técnica, no una atribución de procedencia confirmada.

## 3. Duplicados, plantillas y similitud

### Duplicados exactos

| Comprobación | Resultado |
|---|---:|
| Duplicados exactos internos en SpaPhish | 0 grupos / 0 filas |
| Duplicados exactos internos en SpearPhishMX | 2 grupos / 4 filas / 2 excedentes |
| Hash duplicado en SpaPhish | 0 filas |
| Hash duplicado en SpearPhishMX | 2 filas, mismo hash y etiqueta 1 |
| Textos exactos compartidos entre datasets | 0 |
| Plantillas exactas compartidas tras sustituir entidades | 7 grupos / 14 filas |

Los dos grupos exactos internos de SpearPhishMX no presentan conflicto de etiqueta. Uno comparte también el hash; el otro tiene el mismo texto con hashes diferentes. No se eliminó ninguna fila.

### Similitud cruzada

| Umbral del mejor vecino | Registros de SpaPhish | Misma etiqueta | Etiqueta diferente |
|---:|---:|---:|---:|
| ≥ 0,75 | 954 | 302 | 652 |
| ≥ 0,80 | 840 | 248 | 592 |
| ≥ 0,85 | 669 | 173 | 496 |
| ≥ 0,90 | 465 | 111 | 354 |
| ≥ 0,95 | 175 | 55 | 120 |

En el umbral 0,90, los 465 pares se distribuyen así:

| SpaPhish → SpearPhishMX | Pares |
|---|---:|
| `0 → 0` | 103 |
| `0 → 1` | 32 |
| `1 → 0` | 322 |
| `1 → 1` | 8 |

La mediana de la máxima similitud cruzada es 0,8424; el percentil 90 es 0,9552 y el máximo 0,9980. Las coincidencias más altas no son solo frases comunes: muestran asuntos y cuerpos prácticamente iguales, con salutaciones personalizadas, sustitución de datos y enlaces `http` transformados en `hxxp`. Esto evidencia familias de mensajes o plantillas compartidas.

El umbral 0,90 es diagnóstico, no una regla final de descarte. Debe calibrarse mediante revisión manual de una muestra mayor y reglas adicionales, como coincidencia de asunto, cobertura de tokens y normalización de caracteres invisibles.

## 4. Calidad y privacidad

| Métrica | SpaPhish | SpearPhishMX |
|---|---:|---:|
| Filas | 1.395 | 3.006 |
| Texto combinado vacío | 0 | 0 |
| Asunto vacío | 3 | 2 |
| Cuerpo vacío | 0 | 0 |
| Filas con alerta conservadora de codificación | 6 | 16 |
| Filas involucradas en texto exacto duplicado | 0 | 4 |
| Filas involucradas en hash duplicado | 0 | 2 |

Los asuntos vacíos no obligan a descartar: el cuerpo está presente y puede usarse con un asunto vacío. La alerta de codificación detecta `�` y patrones típicos de mojibake; no cubre todos los caracteres invisibles u ofuscaciones intencionales, que deben preservarse o transformarse de manera documentada.

### Posible fuga de datos

- SpaPhish: excluir del conjunto de características todas las columnas de anotadores, justificaciones y consensos psicológicos. También excluir `hash` como predictor.
- SpearPhishMX: `dirigido_a_persona_v2`, `destinatario_detectado_v2`, `destinatario_tiene_apellido_v2` y `destinatario_normalizado` son atributos derivados del fenómeno que define spear-phishing. No deben entrar automáticamente en un modelo textual base. `id_original` y `hash` son identificadores, no características.
- En SpearPhishMX, `dirigido_a_persona_v2` no es equivalente a la etiqueta: hay 266 positivos con valor falso y 20 negativos con valor falso; aun así puede introducir una señal excesivamente directa.
- Los grupos de plantillas deben permanecer íntegros en una sola partición. Una división aleatoria por fila no es válida.

### Información personal

La documentación de ambas fuentes afirma que el material fue anonimizado o sanitizado. La inspección por expresiones regulares encontró:

| Patrón técnico | SpaPhish | SpearPhishMX |
|---|---:|---:|
| Sintaxis de correo | 334 | 4 |
| Sintaxis de teléfono o secuencia similar | 532 | 296 |
| URL activa | 406 | 2 |
| URL desactivada | 0 | 1.955 |

Estas cifras no prueban presencia de PII: la expresión de teléfono también captura fechas, identificadores y secuencias largas, y SpaPhish documenta sustituciones ficticias. Sin embargo, los cuatro correos y dos enlaces activos detectados en SpearPhishMX deben revisarse manualmente antes de distribuir un corpus derivado. Los nombres añadidos en SpearPhishMX parecen formar parte de la personalización; no se verificó si todos son ficticios. La recomendación es conservar marcadores (`<EMAIL>`, `<TELEFONO>`) y no intentar reidentificar ni resolver enlaces.

## 5. Tabla de decisión por registros

La tabla es conservadora. “Pendiente” agrupa filas con alertas de codificación, texto/hash duplicado o ambas; los asuntos vacíos con cuerpo válido se conservan. Ningún registro fue eliminado.

| Dataset | Total | Conservables preliminarmente | Descartados | Pendientes de revisión | Motivo principal pendiente |
|---|---:|---:|---:|---:|---|
| SpaPhish | 1.395 | 1.389 | 0 | 6 | codificación |
| SpearPhishMX | 3.006 | 2.986 | 0 | 20 | codificación y/o duplicado |
| Total | 4.401 | 4.375 | 0 | 26 | revisión antes de depurar |

Las categorías no resuelven todavía el solapamiento cruzado. Las 465 coincidencias de similitud ≥ 0,90 requieren agrupación, y las 354 con etiquetas distintas requieren una política de adjudicación. No se cuentan como “descartadas” porque el umbral y el objetivo de etiqueta aún necesitan aprobación.

## 6. Esquema unificado propuesto

| Campo | Tipo recomendado | Regla |
|---|---|---|
| `text` | `string` | `subject/asunto + "\n" + body/cuerpo_sanitizado`; vacío solo para el asunto faltante |
| `target` | `int8` | `0 = legítimo`, `1 = phishing`; no aplicar a SpearPhishMX hasta resolver la diferencia conceptual |
| `language` | `category/string` | `es`; conservar `und` si una validación posterior no confirma español |
| `source_dataset` | `category/string` | `spanish_phishing` o `spear_phish_mx` |
| `record_id` | `string` | SpaPhish: `spaphish:<hash>`; SpearPhishMX: `spearphishmx:<id_original>`; no usar solo su hash duplicado |
| `group_id` | `string` | identificador de componente conectado para textos exactos, plantillas y vecinos aprobados |

Para trazabilidad interna conviene conservar, fuera del conjunto de características, `source_row`, `source_hash`, la versión/DOI de origen y el estado de revisión. `source_dataset`, `record_id` y `group_id` tampoco deben convertirse en predictores.

## 7. Transformaciones necesarias

1. Recuperar y versionar los README/esquemas originales sin modificar los CSV.
2. Normalizar solamente para comparación: Unicode NFKC, espacios y marcas invisibles; conservar una columna de texto de origen inmutable.
3. Mantener enlaces desactivados. Para coherencia, transformar `http(s)` a una representación segura sin resolver dominios.
4. Corregir mojibake solo con reglas verificables y guardar la transformación aplicada.
5. Resolver duplicados internos conservando un registro canónico y un registro de exclusiones justificadas.
6. Construir `group_id` en el conjunto combinado antes de dividir datos.
7. Revisar manualmente los conflictos de etiqueta de alta similitud, empezando por los 175 pares ≥ 0,95.
8. Dividir con estrategia de grupos y, si se usan fechas, considerar una evaluación temporal adicional.
9. Excluir campos de anotación, identificadores y derivados de personalización del modelo textual base.

## 8. Viabilidad y decisión recomendada

**Decisión recomendada:** usar SpaPhish como corpus principal inicial para phishing binario en español y mantener SpearPhishMX como conjunto complementario separado hasta resolver la semántica y el solapamiento. No se recomienda sumar las 3.006 filas como si fueran observaciones independientes.

Opciones posteriores:

- **Corpus binario general:** incorporar de SpearPhishMX solo registros adjudicados como phishing o legítimos bajo la misma definición que SpaPhish; agrupar variantes y excluir duplicados excedentes.
- **Problema jerárquico:** conservar dos objetivos, por ejemplo `is_phishing` e `is_spear_phishing`, permitiendo valores desconocidos. Esta opción exige cambiar el esquema solicitado y completar anotaciones faltantes.
- **Evaluación externa:** mantener SpearPhishMX separado para medir transferencia a mensajes personalizados, siempre que se retiren del conjunto de prueba todos los grupos que solapan con SpaPhish.

## Limitaciones

- La similitud de caracteres no es una prueba formal de que dos registros compartan el mismo correo original.
- No se accedió al paquete restringido de SpearPhishMX ni se intentó reidentificar información.
- El repositorio carece de los README y esquemas originales, por lo que la versión exacta de cada CSV sigue sin confirmar.
- Las expresiones regulares de privacidad generan falsos positivos y no sustituyen una auditoría de PII.
- La revisión manual fue dirigida a muestras representativas y a los pares de mayor similitud; no se adjudicaron 4.401 mensajes uno por uno.
- No se evaluó un modelo, porque está fuera del alcance de esta fase.

## Decisiones que requieren aprobación

1. Adoptar SpaPhish como corpus principal inicial y tratar SpearPhishMX como complemento, no como concatenación directa.
2. Elegir entre objetivo binario general y formulación jerárquica phishing/spear-phishing.
3. Autorizar el umbral y protocolo de revisión para crear `group_id`; se recomienda revisar primero ≥ 0,95 y calibrar antes de fijar 0,90.
4. Definir cómo adjudicar conflictos `SpaPhish 1 -> SpearPhishMX 0`; no deben resolverse por mayoría ni por nombre del dataset.
5. Aprobar la exclusión de los dos duplicados excedentes internos de SpearPhishMX después de conservar trazabilidad.
6. Aprobar una revisión manual de los patrones residuales de correo/URL en SpearPhishMX y la política de normalización segura.
7. Decidir si se solicitará a los autores la confirmación de procedencia, versión exacta y significado de la clase 0 en los casos solapados.
