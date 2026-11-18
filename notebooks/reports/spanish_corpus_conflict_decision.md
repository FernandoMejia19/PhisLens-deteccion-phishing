# Investigación de conflictos y decisión del corpus español

**Fecha:** 17 de noviembre de 2026  
**Rama:** `analisis-conflictos-decision`  
**Alcance:** investigar si SpaPhish y SpearPhishMX pueden usarse bajo una misma definición de phishing. No se modificaron etiquetas ni CSV, no se entrenaron modelos y no se generó el corpus.

## Recomendación final

No existe evidencia suficiente para tratar hoy las etiquetas de ambos datasets como una única variable binaria equivalente. SpaPhish documenta una definición amplia de phishing basada en intención engañosa y beneficio para un atacante. SpearPhishMX documenta `1 = spear-phishing` y `0 = legítimo`, pero los archivos públicos recuperados no describen reglas operativas de anotación comparables a las de SpaPhish.

La evidencia empírica refuerza esa incompatibilidad. Entre los 175 mejores pares con similitud coseno ≥ 0,95, 120 tienen etiquetas diferentes. En 109 casos SpaPhish asigna phishing y SpearPhishMX asigna 0. De estos 109 casos, 108 conservan el mismo asunto, 105 están marcados en SpearPhishMX como dirigidos a una persona y 52 quedan casi idénticos después de normalizar personalización, PII, enlaces y caracteres invisibles.

La recomendación es:

1. Usar SpaPhish versión 5 como corpus principal inicial para phishing binario en español.
2. No incorporar todavía las etiquetas de SpearPhishMX al mismo `target`.
3. Conservar SpearPhishMX como fuente complementaria para una futura anotación jerárquica o adjudicada.
4. Solicitar a los autores o consultar el capítulo completo para aclarar la definición operativa de la clase 0 y la construcción de la versión pública.

## Entregables reproducibles

- Script: `notebooks/validacion-datasets/analyze_spanish_conflicts.py`.
- Registro derivado: `notebooks/reports/data/spanish_conflict_analysis.json`.
- Documentación original: `notebooks/reports/sources/spanish-corpus/`.
- Manifiesto de fuentes y hashes: `notebooks/reports/sources/spanish-corpus/SOURCES.md`.

El registro derivado contiene identificadores, etiquetas originales, similitudes y categorías de cambio. No contiene los cuerpos completos y no adjudica etiquetas.

## 1. Documentación recuperada

### SpaPhish

Se recuperaron desde Mendeley Data versión 5:

- `README.txt`.
- `dataset_schema.json`.
- `SpaPhish_Dataset_Schema.pdf`.
- `annotation_guidelines.pdf`.

El SHA-256 del CSV local coincide exactamente con `Spaphish dataset - DiB.csv` de la versión 5. Por tanto, la versión local queda identificada de forma verificable.

Información confirmada:

| Elemento | Evidencia |
|---|---|
| Versión | V5, publicada el 12 de mayo de 2026 |
| DOI | `10.17632/hz2d6gz7pc.5` |
| Licencia | CC BY 4.0 |
| Recopilación | 1.395 correos de buzones personales e institucionales de los contribuidores, junio de 2014 a octubre de 2025 |
| Privacidad | Anonimización manual y sustitución por entidades ficticias antes de la publicación |
| Etiqueta | `0 = legítimo`, `1 = phishing` |
| Anotadores | Tres expertos independientes y un cuarto adjudicador |
| Control | Voto mayoritario, adjudicación conceptual y auditoría posterior de una muestra aleatoria del 10 % |

La definición operativa de phishing es un correo engañoso diseñado para inducir una acción que beneficie a un atacante mediante suplantación, confianza, urgencia o manipulación. Incluye robo de credenciales, datos personales o dinero, instalación de malware y acceso a sitios fraudulentos. Un mensaje se marca como legítimo únicamente cuando no existe evidencia de intención maliciosa.

Las pautas también aclaran que urgencia, promociones o persuasión no bastan por sí solas para marcar phishing. Un aviso universitario urgente y un boletín promocional pueden ser legítimos. Esto separa la intención maliciosa de los principios de persuasión.

Fuentes primarias:

- [SpaPhish V5 en Mendeley Data](https://data.mendeley.com/datasets/hz2d6gz7pc/5).
- [Artículo de datos de SpaPhish](https://doi.org/10.1016/j.dib.2026.112890).

### SpearPhishMX

Se recuperaron desde Mendeley Data versión 2:

- `SpearPhishMX_README.txt`.
- `SpearPhishMX_schema_es.json`.
- `SpearPhishMX_supplementary_code.zip` y su contenido.

El CSV local usa CRLF mientras el oficial usa LF. Después de normalizar los finales de línea, ambos archivos son idénticos y producen el SHA-256 oficial. La versión local queda identificada como V2.

Información confirmada:

| Elemento | Evidencia |
|---|---|
| Versión | V2, publicada el 15 de febrero de 2026 |
| DOI | `10.17632/h4bxjk84jb.2` |
| Licencia | CC BY 4.0 |
| Etiqueta publicada | `1 = spear-phishing`, `0 = legítimo` |
| Texto público | Cuerpo sanitizado, PII sustituida y enlaces desactivados |
| Personalización | Heurísticas para saludos, nombres y destinatarios |
| Uso | Investigación defensiva; no reactivar enlaces |

El README y el esquema no explican:

- La definición operativa de spear-phishing usada por los anotadores.
- Los criterios necesarios y suficientes para asignar la clase 1.
- Cómo se distingue phishing genérico de un correo legítimo dentro de la clase 0.
- El origen de los mensajes relacionados con SpaPhish.
- El procedimiento de consenso o adjudicación.

El artículo asociado, accesible solo como vista previa pública, informa 3.005 correos únicos recopilados entre agosto de 2025 y enero de 2026, tres anotadores de ciberseguridad y un alfa de Krippendorff de 0,87 en una muestra de control de 150 correos. También menciona un subconjunto experimental sanitizado de 2.057 mensajes, con 1.108 legítimos y 949 spear-phishing.

Estas cifras no coinciden directamente con las 3.006 filas y distribución `0 = 1.115`, `1 = 1.891` del CSV público. La diferencia puede corresponder a subconjuntos experimentales, balanceo o selección posterior, pero la vista previa no permite confirmarlo.

Fuentes primarias:

- [SpearPhishMX V2 en Mendeley Data](https://data.mendeley.com/datasets/h4bxjk84jb/2).
- [Capítulo de SpearPhishMX en Springer](https://doi.org/10.1007/978-3-032-42770-0_12).

## 2. Metodología para investigar los pares

Se reprodujo la búsqueda anterior con:

1. Unión de asunto y cuerpo.
2. Normalización Unicode NFKC, minúsculas y espacios.
3. TF-IDF de caracteres de 3 a 5 gramos, máximo 60.000 características.
4. Mejor vecino de cada registro de SpaPhish dentro de SpearPhishMX.
5. Selección de similitud coseno ≥ 0,95.

Para caracterizar cambios se construyó una segunda vista solo para comparación. Esta vista:

- elimina marcas invisibles;
- normaliza `hxxp` y `[.]`;
- sustituye URL, correo, teléfono y números por marcadores;
- identifica la adición de un destinatario o saludo;
- compara el asunto y el cuerpo resultante mediante `SequenceMatcher`.

Estas transformaciones no se aplicaron a los CSV. Las categorías son diagnósticas y no demuestran que dos mensajes tengan el mismo origen.

Se aplicó la revisión estructurada a los 175 pares. Además, se inspeccionaron manualmente ejemplos de mayor similitud de las cuatro transiciones de etiqueta, con extractos redactados y sin abrir enlaces.

## 3. Resultados de los 175 pares

### Etiquetas

| SpaPhish → SpearPhishMX | Pares |
|---|---:|
| `0 → 0` | 52 |
| `0 → 1` | 11 |
| `1 → 0` | 109 |
| `1 → 1` | 3 |
| **Total** | **175** |

- Misma etiqueta: 55.
- Etiqueta diferente: 120.
- Asunto normalizado igual: 173.
- Personalización añadida o diferente: 159.
- Contenido canónico casi idéntico, similitud de secuencia ≥ 0,98: 96.
- Cambio de enlace activo a enlace desactivado: 34.
- Sustitución o reducción de PII detectada: 42.

### Clasificación de posibles causas

Las categorías principales son mutuamente excluyentes, pero se construyen a partir de señales que pueden coexistir.

| Causa principal | Pares | Interpretación |
|---|---:|---|
| Personalización | 105 | Se añade o cambia saludo/destinatario; el contenido restante es altamente similar |
| Personalización y sanitización | 54 | Además del destinatario cambian PII o enlaces |
| Sanitización | 10 | Predominan defang y sustitución de datos |
| Unicode, formato o espaciado | 4 | Las diferencias son principalmente caracteres invisibles o formato |
| Variación adicional no resuelta | 2 | La regla automática no explica suficientemente el cambio |

Desglose por transición:

| Transición | Formato | Personalización | Personalización + sanitización | Sanitización | No resuelto |
|---|---:|---:|---:|---:|---:|
| `0 → 0` | 2 | 26 | 24 | 0 | 0 |
| `0 → 1` | 0 | 0 | 2 | 9 | 0 |
| `1 → 0` | 2 | 79 | 26 | 0 | 2 |
| `1 → 1` | 0 | 0 | 2 | 1 | 0 |

### Ejemplos representativos redactados

- Un aviso comercial legítimo conserva asunto y contenido, mientras SpearPhishMX añade `Hola <DESTINATARIO>` y desactiva enlaces. Las etiquetas permanecen `0 → 0`.
- Un mensaje que anuncia bloqueo de cuenta conserva el asunto ofuscado y el cuerpo malicioso. SpearPhishMX añade un nombre y desactiva el enlace, pero la transición es `1 → 0`.
- Un aviso falso de suspensión de PayPal conserva el contenido y los caracteres de evasión. Se sustituye un correo y se añade destinatario, con transición `1 → 0`.
- Un correo comercial personalizado aparece como `0 → 1` con cambios limitados a defang o tratamiento del destinatario. Esto muestra que la personalización visible no explica por sí sola la clase 1.

## 4. Análisis de `SpaPhish 1 → SpearPhishMX 0`

Resultados sobre los 109 pares:

| Evidencia | Pares |
|---|---:|
| Mismo asunto normalizado | 108 |
| SpearPhishMX marca `dirigido_a_persona_v2 = True` | 105 |
| Similitud canónica ≥ 0,98 | 52 |
| Cambio principal: personalización | 79 |
| Cambio principal: personalización y sanitización | 26 |
| Cambio principal: formato | 2 |
| Cambio no resuelto | 2 |

### Hipótesis 1: diferencia de objetivo

Es posible que un phishing genérico sea negativo para una tarea estricta de spear-phishing. Esta interpretación es conceptualmente válida: spear-phishing es un subconjunto de phishing y requiere un carácter dirigido.

Evidencia a favor:

- Los nombres de los datasets y sus etiquetas describen objetivos distintos.
- El artículo de SpearPhishMX enfatiza señales de personalización.

Evidencia en contra o insuficiente:

- El README no define la clase 0 como “no spear-phishing”; la define como “legítimo”.
- 105 de los 109 pares están marcados como dirigidos a una persona.
- En numerosos ejemplos el cambio visible consiste precisamente en añadir un destinatario a contenido que SpaPhish considera malicioso.
- La documentación pública no explica qué condición adicional impide clasificar esos mensajes como spear-phishing.

Conclusión: la diferencia de objetivo es una explicación posible, pero no suficiente para armonizar las etiquetas automáticamente.

### Hipótesis 2: sanitización o pérdida de contexto

SpaPhish indica que sus anotadores revisaron remitente, dirección, enlaces, adjuntos y contexto. SpearPhishMX publica cuerpos sanitizados y enlaces desactivados. Una anotación realizada sobre representaciones diferentes podría cambiar la evidencia disponible.

La hipótesis es plausible para algunos casos, pero no explica los pares cuyo cuerpo sigue mostrando intención engañosa explícita, como bloqueos falsos, verificación de credenciales o suplantación. Tampoco se documenta si SpearPhishMX fue anotado antes o después de sanitizar.

### Hipótesis 3: construcción, subconjuntos o error de documentación

La diferencia entre el CSV público y el subconjunto descrito en el artículo, junto con la ausencia de reglas completas, permite considerar:

- clases construidas para un experimento específico;
- versiones o subconjuntos con distinto criterio;
- ruido o errores de etiqueta;
- uso de “legítimo” donde operativamente se quiso decir “no spear-phishing”.

No hay evidencia pública suficiente para elegir una de estas explicaciones. Debe solicitarse aclaración y no cambiar etiquetas.

## 5. Evaluación de alternativas

| Alternativa | Ventajas | Riesgos y requisitos | Decisión |
|---|---|---|---|
| SpaPhish como corpus principal | Definición completa, triple anotación, adjudicación, versión exacta, balance razonable | Solo 1.395 registros; posible sesgo de contribuidores y periodo | **Recomendada para la primera versión binaria** |
| Combinación adjudicada | Mayor diversidad y posibilidad de conservar variantes dirigidas | Requiere agrupar, doble revisión humana, aclarar clase 0 y resolver conflictos sin sobrescribir originales | Viable después de adjudicación, no ahora |
| Clasificación jerárquica | Representa correctamente que spear-phishing es un subtipo de phishing | Requiere dos etiquetas independientes y valores desconocidos; no pueden inferirse de los labels actuales | Mejor diseño conceptual a largo plazo |

### Esquema jerárquico sugerido

- `is_phishing`: `0`, `1` o `unknown`.
- `is_spear_phishing`: `0`, `1` o `unknown`.
- Restricción: `is_spear_phishing = 1` implica `is_phishing = 1`.

SpaPhish aporta `is_phishing`, pero no una etiqueta validada de spear-phishing. SpearPhishMX aporta una etiqueta publicada de spear-phishing, pero sus negativos no deben convertirse en `is_phishing = 0` sin aclaración o nueva anotación.

## 6. Protocolo reproducible propuesto

### 6.1. Congelar fuentes

1. Registrar DOI, versión, nombre, tamaño y SHA-256.
2. Conservar una copia inmutable del texto original y una vista derivada para comparación.
3. Registrar cada transformación con versión del script y parámetros.

### 6.2. Agrupar mensajes relacionados

Aplicar etapas en este orden:

1. Mismo hash de origen, cuando sea comparable.
2. Texto exacto después de NFKC y espacios.
3. Plantilla exacta después de sustituir PII, URL y números.
4. Candidatos de similitud con TF-IDF de caracteres.
5. Validación manual de aristas antes de formar componentes conectados.

Regla inicial propuesta para revisión, no para unión automática:

- Alta confianza: asunto igual, coseno ≥ 0,95 y similitud canónica ≥ 0,98.
- Revisión obligatoria: coseno ≥ 0,95 pero no cumple las otras dos condiciones.
- No agrupar automáticamente por similitud menor a 0,95.

Cada componente validado recibe un `group_id` estable. La pertenencia se registra sin alterar `record_id` ni etiqueta original.

### 6.3. Duplicados internos

1. Si texto y etiqueta son iguales, elegir un registro canónico y marcar los excedentes como `duplicate_excluded`.
2. Si las etiquetas difieren, crear un conflicto; no elegir por mayoría.
3. En SpearPhishMX existen dos grupos exactos, cuatro filas y dos excedentes, sin conflictos de etiqueta.
4. Conservar tabla de exclusiones con motivo, registro canónico y evidencia.

### 6.4. Registro de conflictos

Campos mínimos:

- `conflict_id`, `group_id`.
- Identificadores y versiones de ambos registros.
- Etiquetas originales inmutables.
- Similitudes y reglas activadas.
- Diferencias de asunto, personalización, PII, URL y contenido.
- Decisión de revisor 1 y revisor 2.
- Adjudicación, definición aplicada y justificación.
- Estado: `pending`, `agreed`, `adjudicated`, `excluded`.
- Fecha y versión del protocolo.

La etiqueta armonizada, si se autoriza, debe ser una columna nueva. Nunca debe sobrescribir `Label` o `etiqueta`.

### 6.5. Separación de datos

1. Construir grupos antes de dividir.
2. Asignar cada `group_id` completo a una única partición.
3. Objetivo inicial: 70 % entrenamiento, 15 % validación y 15 % prueba, estratificando por etiqueta y fuente en la medida permitida por los grupos.
4. Usar semilla fija y guardar un manifiesto de partición.
5. Congelar la prueba antes de cualquier selección de características o parámetros.
6. Verificar que no se compartan entre particiones hashes, texto exacto, plantilla, URL normalizada ni grupos aprobados.
7. Si el tamaño de grupos impide mantener proporciones, priorizar ausencia de fuga sobre balance exacto y documentar la desviación.

Una partición temporal combinada no es viable actualmente porque SpearPhishMX no aporta fechas observadas en el CSV público.

## 7. Limitaciones

- La similitud textual no demuestra origen común.
- Las categorías de cambio son heurísticas reproducibles, no decisiones semánticas.
- La inspección manual se concentró en ejemplos representativos de alta similitud; no constituye una nueva anotación experta de los 175 pares.
- El capítulo completo de SpearPhishMX no estuvo accesible públicamente; solo se usaron resumen, metadatos y archivos del dataset.
- No se dispone del paquete restringido ni de remitentes originales de SpearPhishMX.
- No se puede determinar si las etiquetas de SpearPhishMX se asignaron antes o después de la sanitización.
- El umbral 0,95 debe calibrarse antes de convertirse en una regla de agrupación productiva.

## 8. Decisiones que requieren aprobación

1. Aprobar SpaPhish V5 como corpus principal binario de la primera iteración.
2. Aprobar que SpearPhishMX permanezca fuera del `target` binario hasta recibir aclaración o completar una adjudicación independiente.
3. Elegir si el objetivo final seguirá siendo binario o evolucionará al esquema jerárquico `is_phishing` / `is_spear_phishing`.
4. Autorizar contacto con los autores o acceso institucional al capítulo completo para aclarar la clase 0, los subconjuntos y la etapa de anotación.
5. Aprobar el protocolo de agrupación y la revisión humana de los 175 pares ≥ 0,95.
6. Aprobar la exclusión trazable de los dos duplicados excedentes internos de SpearPhishMX.
7. Aprobar la política de partición 70/15/15 por `group_id`, con prioridad absoluta a evitar fuga.
