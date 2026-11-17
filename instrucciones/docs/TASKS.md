# TASKS.md

# Plan de trabajo y seguimiento

## Estado general

**Proyecto:** Sistema inteligente de detección y prevención de phishing.

**Estado:** Investigación y experimentación inicial.

**Metodología:** Desarrollo progresivo por fases, con experimentos documentados, validaciones y commits incrementales.

---

# FASE 01 - Exploración de datasets

**Estado:** Completada el 16 de noviembre de 2026.

**Rama de trabajo:** `exploracion-dataset-fernando`

## Objetivo

Analizar individualmente todos los datasets disponibles para determinar su calidad, características, idiomas, distribución de clases y utilidad para desarrollar un modelo de detección de phishing basado en Random Forest.

## Actividades

### 1.1. Inventario de datasets

- [x] Identificar todos los datasets disponibles.
- [x] Identificar sus formatos.
- [x] Registrar sus ubicaciones.
- [x] Identificar su procedencia cuando esté documentada.
- [x] Revisar notebooks existentes.
- [x] Identificar datasets duplicados o versiones diferentes.

### 1.2. Análisis individual

Para cada dataset:

- [x] Identificar cantidad de registros.
- [x] Identificar columnas y tipos de datos.
- [x] Identificar variable objetivo.
- [x] Analizar distribución de clases.
- [x] Revisar valores nulos.
- [x] Revisar registros duplicados.
- [x] Analizar longitud de los mensajes.
- [x] Analizar idioma.
- [x] Revisar ejemplos de registros.
- [x] Identificar características útiles para ML.
- [x] Identificar limitaciones y posibles sesgos.

### 1.3. Evaluación de utilidad

Para cada dataset, determinar:

- [x] Si permite identificar phishing.
- [x] Si permite identificar mensajes legítimos.
- [x] Si contiene texto suficiente para entrenar.
- [x] Si es adecuado para español o inglés.
- [x] Si contiene información complementaria útil.
- [x] Si puede combinarse con otros datasets.
- [x] Si requiere transformaciones.
- [x] Si presenta riesgos de data leakage.

### 1.4. Informes

- [x] Generar un informe individual por dataset.
- [x] Crear un informe comparativo.
- [x] Identificar los datasets más prometedores.
- [x] Proponer una estrategia de combinación.
- [x] Recomendar próximos experimentos.

### 1.5. Entregables

- Inventario de datasets.
- Notebooks de análisis individual.
- Informes individuales.
- Informe comparativo.
- Recomendaciones técnicas.

### Criterio de finalización

La fase se considera completada cuando todos los datasets disponibles han sido identificados, analizados y documentados, y existe una recomendación fundamentada sobre su posible utilización.

No entrenar todavía el modelo definitivo.

### Resultados ejecutados

- Se inventariaron y analizaron siete archivos CSV.
- Los dos CSV de 50 000 correos son copias exactas según SHA-256.
- `spam/data-augmented.csv` y `spam/Dataset_5971.csv` comparten 4 933 textos únicos.
- Se generaron y ejecutaron notebooks individuales sin errores.
- Se generaron informes individuales, comparativo, auditoría y recomendaciones técnicas en `notebooks/reports/`.
- La procedencia y licencia no están documentadas en el repositorio para ninguno de los datasets; queda como dependencia previa al uso definitivo.

---

# FASE 02 - Exploración y mejora del OCR

**Estado:** Completada con conjunto de prueba limitado el 16 de noviembre de 2026.

**Rama de trabajo:** `fase/02-mejora-ocr`

## Objetivo

Evaluar la implementación actual de OCR y mejorar la extracción de texto de imágenes de correos electrónicos y conversaciones de WhatsApp.

## Actividades

- [x] Revisar el notebook existente.
- [x] Identificar la tecnología OCR utilizada.
- [x] Comprender el flujo actual.
- [x] Evaluar los resultados de extracción.
- [x] Analizar las imágenes disponibles.
- [x] Probar técnicas de preprocesamiento.
- [x] Evaluar diferentes configuraciones.
- [x] Identificar errores de reconocimiento.
- [x] Conservar correctamente enlaces y direcciones.
- [x] Evaluar el resultado con ejemplos de prueba.
- [x] Documentar mejoras y limitaciones.

## Entregables

- Notebook actualizado.
- Comparativa de resultados.
- Ejemplos de extracción.
- Informe de evaluación del OCR.
- Recomendaciones para su integración.

## Criterio de finalización

Contar con un procedimiento de extracción de texto evaluado y documentado, adecuado para continuar con el procesamiento de mensajes.

### Resultados ejecutados

- Se evaluaron las dos imágenes disponibles con EasyOCR en CPU y ground truth manual.
- Se compararon original, escala de grises, ampliación 2×, CLAHE, Otsu y denoise + Otsu mediante CER/WER.
- La ampliación 2× mejoró el correo; la imagen original fue mejor para WhatsApp.
- Se preservó el correo visible en las mejores variantes. No había teléfonos ni URLs en las imágenes, por lo que esa capacidad queda sin validar.
- El informe está en `ocr-phishing/OCR_EVALUATION.md` y el experimento en `ocr-phishing/analisis-ocr-preprocesamiento.ipynb`.

---

# FASE 03 - Preprocesamiento e ingeniería de características

**Estado:** Pendiente.

**Rama de trabajo:** `fase/03-preprocesamiento`

## Objetivo

Definir cómo transformar los mensajes en características utilizables por Random Forest.

## Actividades

- [ ] Evaluar estrategias de limpieza textual.
- [ ] Analizar tokenización.
- [ ] Evaluar normalización.
- [ ] Analizar características TF-IDF.
- [ ] Evaluar características adicionales.
- [ ] Considerar URLs y dominios.
- [ ] Analizar diferencias entre español e inglés.
- [ ] Evitar pérdida de información relevante.
- [ ] Diseñar pipeline de procesamiento.
- [ ] Definir separación de datos.

## Entregables

- Notebook de experimentación.
- Pipeline de procesamiento.
- Justificación de características.
- Documentación de decisiones.

## Criterio de finalización

Disponer de un pipeline reproducible para transformar los datos en características de entrenamiento.

---

# FASE 04 - Entrenamiento y evaluación del modelo

**Estado:** Pendiente.

**Rama de trabajo:** `fase/04-modelo-random-forest`

## Objetivo

Entrenar, ajustar y evaluar un modelo Random Forest para detectar phishing.

## Actividades

- [ ] Definir dataset de entrenamiento.
- [ ] Definir dataset de validación y prueba.
- [ ] Establecer baseline.
- [ ] Entrenar Random Forest.
- [ ] Evaluar hiperparámetros.
- [ ] Evaluar desbalance de clases.
- [ ] Analizar falsos positivos.
- [ ] Analizar falsos negativos.
- [ ] Evaluar métricas.
- [ ] Comparar experimentos.
- [ ] Seleccionar configuración.
- [ ] Guardar el modelo.
- [ ] Documentar resultados.

## Entregables

- Notebook de entrenamiento.
- Modelo entrenado.
- Resultados experimentales.
- Comparativas.
- Informe de evaluación.

## Criterio de finalización

Disponer de un modelo evaluado, reproducible y acompañado de resultados que justifiquen su selección.

---

# FASE 05 - Diseño de arquitectura y backend

**Estado:** Pendiente.

**Rama de trabajo:** `fase/05-backend`

## Objetivo

Diseñar e implementar el backend que conectará los módulos de análisis.

## Actividades

- [ ] Definir arquitectura.
- [ ] Diseñar estructura de FastAPI.
- [ ] Definir contratos de API.
- [ ] Implementar validación de entradas.
- [ ] Integrar el modelo.
- [ ] Integrar procesamiento de texto.
- [ ] Integrar OCR.
- [ ] Diseñar módulo de análisis de remitentes.
- [ ] Evaluar APIs externas.
- [ ] Implementar explicaciones.
- [ ] Implementar recomendaciones.
- [ ] Implementar consulta de noticias.
- [ ] Crear pruebas.

## Entregables

- Backend funcional.
- Documentación de endpoints.
- Pruebas.
- Documentación arquitectónica.

---

# FASE 06 - Desarrollo del frontend

**Estado:** Pendiente.

**Rama de trabajo:** `fase/06-frontend`

## Objetivo

Desarrollar una interfaz intuitiva para usuarios sin conocimientos técnicos.

## Actividades

- [ ] Seleccionar tecnología.
- [ ] Diseñar experiencia de usuario.
- [ ] Diseñar pantalla de análisis.
- [ ] Implementar entrada de texto.
- [ ] Implementar carga de imágenes.
- [ ] Mostrar resultados.
- [ ] Mostrar explicaciones.
- [ ] Mostrar recomendaciones.
- [ ] Crear sección educativa.
- [ ] Crear sección de noticias.
- [ ] Implementar comunicación con backend.
- [ ] Realizar pruebas de usabilidad.

## Entregables

- Interfaz funcional.
- Integración con backend.
- Pruebas de interfaz.
- Documentación.

---

# FASE 07 - Integración y evaluación general

**Estado:** Pendiente.

**Rama de trabajo:** `fase/07-integracion`

## Objetivo

Integrar todos los componentes y verificar el funcionamiento de la aplicación.

## Actividades

- [ ] Integrar frontend y backend.
- [ ] Verificar flujo de análisis textual.
- [ ] Verificar flujo de análisis mediante imágenes.
- [ ] Verificar OCR.
- [ ] Verificar clasificación.
- [ ] Verificar análisis de remitentes.
- [ ] Verificar explicaciones.
- [ ] Verificar recomendaciones.
- [ ] Verificar noticias.
- [ ] Evaluar seguridad.
- [ ] Evaluar rendimiento.
- [ ] Realizar pruebas funcionales.
- [ ] Documentar resultados.
- [ ] Preparar evidencias de sustentación.

## Entregables

- Aplicación integrada.
- Informe de pruebas.
- Documentación final.
- Evidencias.
- Resultados de evaluación.

---

# GESTIÓN DE TAREAS

## Reglas

1. Ejecutar las fases en el orden establecido, salvo dependencias justificadas.
2. No marcar tareas como completadas sin evidencia.
3. Registrar problemas y bloqueos.
4. Actualizar este documento al finalizar cada unidad de trabajo.
5. No iniciar una fase dependiente si faltan resultados esenciales de la anterior.
6. Cada fase debe contar con commits identificables.
7. Mantener la trazabilidad de los experimentos.

## Estado de las tareas

Utilizar los siguientes estados:

- Pendiente.
- En progreso.
- Bloqueada.
- Completada.

Cuando una tarea esté bloqueada, documentar la razón y qué información o decisión se necesita.

## Historial de fases

Registrar al finalizar cada fase:

| Fase | Estado | Rama | Commit principal |
|---|---|---|---|
| 01. Exploración de datasets | Completada | exploracion-dataset-fernando | `baee8d5`, `a46f240` |
| 02. OCR | Completada con muestra limitada | exploracion-dataset-fernando | `850710c` |
| 03. Preprocesamiento | Pendiente | fase/03-preprocesamiento | Pendiente |
| 04. Modelo ML | Pendiente | fase/04-modelo-random-forest | Pendiente |
| 05. Backend | Pendiente | fase/05-backend | Pendiente |
| 06. Frontend | Pendiente | fase/06-frontend | Pendiente |
| 07. Integración | Pendiente | fase/07-integracion | Pendiente |
