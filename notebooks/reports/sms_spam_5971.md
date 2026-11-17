# Análisis: sms_spam_5971

## Descripción y procedencia

Mensajes SMS con indicadores URL/EMAIL/PHONE y etiquetas ham, spam y smishing.

**Ubicación:** `notebooks/data/spam/Dataset_5971.csv`  
**Procedencia verificable:** No hay fuente, licencia ni definición de las columnas auxiliares en el repositorio.

## Estructura

- Formato: CSV, UTF-8, separador `,`.
- Registros: **5,971**.
- Columnas: **5**.
- Variable objetivo: **`LABEL`**.
- Columnas de texto evaluadas: `TEXT`.
- Tamaño: 595,987 bytes.
- SHA-256: `649844f1c62a6b27e145eaf17a65f7010c56c390e11a794ea8329993a05ba71e`.

| Columna | Tipo inferido | Nulos | Nulos % |
|---|---:|---:|---:|
| `LABEL` | `str` | 0 | 0.00% |
| `TEXT` | `str` | 0 | 0.00% |
| `URL` | `str` | 0 | 0.00% |
| `EMAIL` | `str` | 0 | 0.00% |
| `PHONE` | `str` | 0 | 0.00% |

## Distribución de clases

| Clase | Registros | Porcentaje |
|---|---:|---:|
| `ham` | 4844 | 81.13% |
| `Smishing` | 616 | 10.32% |
| `spam` | 466 | 7.80% |
| `Spam` | 23 | 0.39% |
| `smishing` | 22 | 0.37% |

## Calidad y duplicados

- Filas completamente duplicadas: **17**.
- Filas involucradas en textos normalizados repetidos: **273**.
- Textos normalizados con etiquetas conflictivas: **49**.
- Filas sin texto: **0**.
- Filas con caracteres de reemplazo: **145**.
- Filas con marcadores de posible mojibake: **145**.
- Patrones encontrados sin abrir enlaces: URL **183**, correo **22**, teléfono **709**.

## Longitud del texto

| Métrica | Caracteres | Palabras |
|---|---:|---:|
| Mínimo | 2 | 0 |
| Q1 | 38 | 8 |
| Mediana | 66 | 13 |
| Media | 83.20 | 15.95 |
| Q3 | 127 | 23 |
| P95 | 161 | 32 |
| Máximo | 910 | 190 |

## Idiomas

Resultado observado: en: 3253, indeterminado: 2716, es: 2. La heurística sólo distingue señales claras de español e inglés; `indeterminado` no representa un tercer idioma. Cuando existe una columna declarada se reporta esa columna, no una detección independiente.

## Ejemplos representativos

Los ejemplos se seleccionaron cerca de la longitud mediana de cada clase. Se desactivaron esquemas URL y se ocultaron correos/teléfonos en el informe.

**Clase `Smishing`**
- FreeMsg Why haven't you replied to my text? I'm female and live local. Luv to hear from u. Netcollex Ltd 08700621170150p per msg reply Stop to end
- SMS. ac Blind Date 4U!: Rodds1 is 21/m from Aberdeen, United Kingdom. Check Him out hxxp://img. sms. ac/W/icmb3cktz8r7!-4 no Blind Dates send HIDE

**Clase `Spam`**
- -PLS STOP bootydelious (32/F) is inviting you to be her friend. Reply YES-434 or NO-434 See her: www.SMS.ac/u/bootydelious STOP? Send STOP FRND to 62468
- Property Bhi Aapki Rent Bhi Aapka, Invest Rs 17k Lacs in Fully Furnished Office Spaces & Earn Rs 17k per Month Wid Bank Guarantee, Noida Cont.[telefono-oculto]

**Clase `ham`**
- Gud ni8 dear..slp well..take care..swt dreams..Muah..
- Yupz... I've oredi booked slots 4 my weekends liao...

**Clase `smishing`**
- WIN: We have a winner! Mr. T. Tilo won an iPod! More exciting prizes soon, so keep an eye on ur mobile or visit www.win-82050.co.uk
- Loan INR5,00,000 - 7,50,000. Homeowners + Tenants welcome. Have you been previously refused? We can still help. Call Free [telefono-oculto]

**Clase `spam`**
- Had your mobile 11mths+? You are entitled to update to the latest colour camera mobile for Free! Call The Mobile Update Co FREE on [telefono-oculto]
- Wan2 win a Meet+Greet with Westlife 4 U or a m8? They are currently on what tour? 1)Unbreakable, 2)Untamed, 3)Unkempt. Text 1,2 or 3 to 83049.

## Características útiles

- Texto del asunto y cuerpo o mensaje.
- Longitud, conteos de palabras y caracteres especiales.
- Presencia y cantidad de URLs, correos, teléfonos y términos de urgencia.
- Metadatos propios del dataset, únicamente tras comprobar que no derivan de la etiqueta.
- TF-IDF de palabras y caracteres, con selección o reducción de dimensionalidad para Random Forest.

## Ventajas

- Distingue smishing de spam en parte de los registros.
- Incluye indicadores explícitos de URL, correo y teléfono.

## Problemas, limitaciones y sesgos

- Las etiquetas `Spam`/`spam` y `Smishing`/`smishing` difieren sólo por mayúsculas y requieren normalización.
- Existen 49 textos normalizados con etiquetas conflictivas.
- Comparte 4 933 textos únicos con el dataset aumentado; existe alto riesgo de fuga entre fuentes.
- El contenido es principalmente inglés y 145 filas muestran caracteres problemáticos en la lectura de texto.

**Sesgo probable:** SMS cortos, promociones y vocabulario móvil; no representa correo electrónico corporativo.

## Utilidad para el proyecto y Random Forest

**Utilidad estimada:** Media para un submodelo o reglas de smishing; baja-media para el clasificador general de correo phishing.

**Random Forest:** Útil tras normalizar etiquetas, resolver conflictos y agrupar duplicados. Los indicadores auxiliares deben recalcularse para verificar que no son etiquetas derivadas.

**Combinación:** No combinar directamente con el aumentado. Deduplicar por texto normalizado y mantener una sola asignación de etiqueta tras revisión de conflictos.

## Recomendaciones

- Unificar mayúsculas de etiquetas en una copia procesada, nunca en el CSV original.
- Revisar manualmente los 49 conflictos y verificar cómo se generaron URL/EMAIL/PHONE.

## Reproducibilidad

Métricas generadas por `notebooks/exploracion-datasets/dataset_audit.py`. No se modificó el CSV original. La procedencia y licencia siguen pendientes cuando no aparecen en el repositorio.
