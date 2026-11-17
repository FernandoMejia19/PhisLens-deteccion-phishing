# Evaluación del OCR

## Implementación inicial

El notebook original usa EasyOCR con los idiomas `es` y `en`, CPU, OpenCV para cargar la imagen y Matplotlib para visualizar regiones. Procesaba únicamente `data/ejcorreo.png`, concatenaba las regiones y no comparaba contra una transcripción de referencia.

La ejecución almacenada del notebook original detectó 18 regiones y preservó `contact@growthdot.com`. Separó incorrectamente “1 minute ago” en números aislados y omitió el 7 de “Email was read 7 seconds…”.

## Imágenes

- `ejcorreo.png`: captura nítida de 893×574 píxeles, fondo claro, texto en inglés. Contiene empresa/nombre “Email Tracking”, ruta “Europe/Kyiv” y el correo `contact@growthdot.com`.
- `ejwpp.jpg`: captura de WhatsApp de 1200×478 píxeles con el chat centrado, fondo ilustrado y texto en español. No contiene URL, correo ni teléfono; “facebook” es una palabra, no un enlace.
- Ambas están correctamente orientadas. No se aplicó rotación porque no había evidencia de inclinación.

## Método

Se creó una transcripción manual legible para cada imagen y se calcularon CER (tasa de error de caracteres) y WER (tasa de error de palabras) después de normalización. Se probaron original, escala de grises, ampliación 2×, CLAHE, Otsu y reducción de ruido seguida de Otsu. No se ejecutó ningún enlace.

| Imagen | Variante | CER | WER | Confianza media | Regiones | Tiempo (s) |
|---|---|---:|---:|---:|---:|---:|
| `ejcorreo` | `original` | 3.10% | 10.26% | 0.8768 | 18 | 4.267 |
| `ejcorreo` | `grayscale` | 3.32% | 11.54% | 0.8408 | 18 | 3.996 |
| `ejcorreo` | `upscale_2x` | 1.11% | 3.85% | 0.8903 | 17 | 9.834 |
| `ejcorreo` | `upscale_clahe` | 3.10% | 7.69% | 0.8825 | 17 | 9.587 |
| `ejcorreo` | `upscale_otsu` | 1.99% | 8.97% | 0.8264 | 17 | 9.436 |
| `ejcorreo` | `upscale_denoise_otsu` | 1.77% | 6.41% | 0.8346 | 17 | 9.422 |
| `ejwpp` | `original` | 0.81% | 4.35% | 0.7591 | 7 | 2.673 |
| `ejwpp` | `grayscale` | 0.81% | 4.35% | 0.7889 | 7 | 2.708 |
| `ejwpp` | `upscale_2x` | 4.07% | 17.39% | 0.7733 | 9 | 8.770 |
| `ejwpp` | `upscale_clahe` | 3.25% | 13.04% | 0.8434 | 10 | 10.791 |
| `ejwpp` | `upscale_otsu` | 16.26% | 17.39% | 0.8351 | 8 | 11.792 |
| `ejwpp` | `upscale_denoise_otsu` | 16.26% | 17.39% | 0.8123 | 8 | 10.796 |

## Resultados

### Correo

- La ampliación 2× fue la mejor: **CER 1.11% y WER 3.85%**, preservando correo, nombre y `Europe/Kyiv`.
- Denoise + Otsu quedó segundo (CER 1.77%, WER 6.41%).
- CLAHE mejoró WER frente al original, pero no CER.
- Escala de grises sola empeoró ligeramente y dividió el correo en `contact@` / `growthdot.com`; una extracción de entidades por línea podría perderlo.
- Otsu conservó el correo, pero introdujo un espacio en `Europe /Kyiv`.

### WhatsApp

- Original y escala de grises empataron como mejores: **CER 0.81% y WER 4.35%**.
- La ampliación y CLAHE añadieron un “0” espurio cerca del avatar y separaron líneas.
- Otsu, con o sin denoise, eliminó las marcas horarias y elevó CER a 16.26%.
- Las variantes conservaron “contraseña”, “facebook” y “Abuela”, pero la consola de Windows puede representar acentos de forma defectuosa; el JSON está guardado en UTF-8.

## Entidades críticas

- Dirección de correo: preservada por original, ampliación, CLAHE, Otsu y denoise+Otsu; escala de grises la partió en dos regiones.
- Números telefónicos: no hay ninguno en estas imágenes, por lo que no puede evaluarse esta capacidad.
- Enlaces: no hay URLs visibles; `Europe/Kyiv` no debe tratarse como URL.
- Empresas/nombres: “Email Tracking”, “Abuela” y “facebook” fueron reconocidos.
- Texto del mensaje: alto nivel de recuperación, con errores concentrados en orden/segmentación y marcas horarias.

## Limitaciones

- Sólo hay dos imágenes y ambas son legibles; no permiten estimar desempeño general.
- CER/WER dependen de la transcripción manual y del orden de regiones devuelto por EasyOCR.
- La confianza de EasyOCR no reemplaza CER/WER y no está calibrada como probabilidad de exactitud.
- EasyOCR emitió avisos de CPU/quantización. Procesar muchas variantes en un mismo proceso acumuló recursos; la ejecución completa finalmente produjo el JSON, pero para repetir de forma estable conviene procesar imagen por imagen.
- No se probaron desenfoque, rotación, compresión severa, modo oscuro, múltiples burbujas ni capturas móviles pequeñas.

## Recomendación

Usar la imagen original como primera opción. Si el texto es pequeño, probar ampliación 2× y seleccionar el resultado mediante una regla de calidad que considere cobertura de texto y preservación de correos/URLs. No aplicar umbralización global a capturas con fondos complejos sin comparar, porque en WhatsApp eliminó información. Añadir un posprocesado que una regiones contiguas para correos y URLs partidos por saltos de línea.

## Próxima validación

Construir un conjunto de al menos 30–50 capturas estratificadas por tipo (correo/WhatsApp), resolución, modo claro/oscuro, rotación, compresión y presencia de URL/correo/teléfono. Anotar ground truth y reportar CER, WER y recall exacto de entidades por categoría antes de integrar OCR con el clasificador.
