# Análisis comparativo de datasets

## Resumen

| Dataset | Registros | Idioma | Clases | Calidad | Utilidad |
|---|---:|---|---|---|---|
| `email_detection_50k` | 50,000 | Inglés | Legitimate: 29629, Phishing: 20371 | Regular: probable sintético y fuga | Media |
| `phishing_email_detection_50k_copy` | 50,000 | Inglés | Legitimate: 29629, Phishing: 20371 | Duplicado exacto | Nula adicional |
| `spam_multilingual_augmented` | 5,572 | Inglés + traducciones | ham: 4825, spam: 747 | Regular: aumento no documentado | Baja directa |
| `spam_spanish` | 15,016 | Español | 1: 7982, 0: 7034 | Regular: duplicados y etiqueta sin diccionario | Media auxiliar |
| `sms_spam_5971` | 5,971 | Inglés | ham: 4844, Smishing: 616, spam: 466, Spam: 23, smishing: 22 | Baja-regular: conflictos y solapamiento | Media smishing |
| `spanish_phishing` | 1,395 | Español | 1: 731, 0: 664 | Buena con nulos y procedencia pendiente | Alta |
| `spear_phish_mx` | 3,006 | Español | 1: 1891, 0: 1115 | Buena en texto; columnas totalmente nulas | Alta |

Los archivos más prometedores para el objetivo principal en español son `spanish_phishing` y `spear_phish_mx`. Ninguno debe usarse como fuente definitiva hasta documentar procedencia, licencia, definición de etiqueta y protocolo de recolección. El archivo inglés de 50 000 correos sirve como benchmark controlado, no como sustituto del corpus español.

## Duplicados y solapamientos entre fuentes

- `email_detection_50k__phishing_email_detection_50k_copy`: 50,000 textos únicos compartidos.
- `spam_multilingual_augmented__sms_spam_5971`: 4,933 textos únicos compartidos.

- Los dos archivos de 50 000 correos son idénticos byte a byte. Se debe seleccionar una sola copia.
- El alto solapamiento entre `spam_multilingual_augmented` y `sms_spam_5971` impide tratarlos como fuentes independientes.
- La deduplicación debe ocurrir antes de separar train/validación/test y debe conservar grupos de traducciones/plantillas.

## Estrategia recomendada de combinación

1. Construir una tabla procesada, sin alterar fuentes, con `text`, `subject`, `target_original`, `target_binary`, `language`, `source_dataset`, `record_id` y `group_id`.
2. Usar `spanish_phishing` y `spear_phish_mx` como núcleo español. Armonizar 0/1 sólo después de confirmar su semántica.
3. Deduplicar por hash de texto normalizado y agrupar variantes del mismo mensaje, destinatario o plantilla.
4. Reservar un holdout por fuente además de una partición estratificada. Así se mide generalización entre dominios.
5. Mantener `spam_spanish` y smishing como tareas auxiliares o clases de análisis, no convertir automáticamente todo spam en phishing.
6. Mantener el corpus de 50 000 correos como evaluación inglesa separada y excluir variables con fuga (`phishing_probability`, y posiblemente reputación/autenticación).

## Random Forest

Random Forest no recibe texto crudo. La opción defendible es comparar: (a) TF-IDF de palabras/caracteres con selección o reducción de dimensionalidad y (b) características interpretables como longitudes, URLs, dominios, urgencia, mayúsculas y entidades. Se debe usar un baseline lineal para comprobar que Random Forest aporta valor y calibrar probabilidades antes de mostrarlas al usuario.

## Riesgos principales

- Fuga por variables generadas a partir de la etiqueta o por traducciones/duplicados repartidos entre conjuntos.
- Confundir spam con phishing.
- Mezclar español e inglés sin evaluación separada.
- Sobreajuste a plantillas, marcas, destinatarios o dominios.
- Procedencia y licencia no documentadas en todos los datasets.

## Siguiente experimento

Antes del modelo definitivo: confirmar metadatos de origen, resolver etiquetas conflictivas, crear un manifiesto de datos procesados y diseñar particiones agrupadas. Después ejecutar un baseline reproducible con métricas por idioma, fuente y clase, con atención a falsos negativos.
