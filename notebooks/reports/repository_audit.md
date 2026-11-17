# Auditoría inicial del repositorio

## Estructura observada

- `notebooks/data/`: siete CSV en cinco subcarpetas.
- `notebooks/exploracion-datasets/`: dos notebooks iniciales; fueron revisados y ampliados. La documentación usa también el nombre erróneo `noteboks/`.
- `ocr-phishing/`: notebook EasyOCR y dos imágenes de prueba.
- `frontend/` y `backend/`: directorios vacíos en esta revisión; no se modificaron.
- `instrucciones/`: documentación local. `PROJECT.md` está realmente nombrado `PROYECT.md`.
- `requirements.txt`: dependencias sin versiones fijadas.
- `.venv/`: entorno local no versionado. Python global no estaba disponible en el sandbox; la auditoría usó el entorno existente con autorización.

## Git inicial

- Rama: `exploracion-dataset-fernando`.
- Árbol inicial: limpio.
- HEAD inicial: `1a5c33f`, también apuntado por `origin/main`.
- `origin/exploracion-dataset-fernando` apuntaba a `0d9c818`.
- Remoto: `origin` en GitHub.
- La rama es apropiada porque contiene el trabajo inicial de exploración y OCR.

## Documentación y trazabilidad

`.gitignore` excluye `/instrucciones`, por lo que `TASKS.md` no estaba versionado. Se actualiza localmente y se debe añadir explícitamente si se requiere conservarlo en Git. No se corrigieron nombres ni se eliminaron archivos para evitar cambios estructurales fuera de alcance.

## Dependencias y ejecución

El entorno contiene pandas, NumPy, scikit-learn, OpenCV, EasyOCR y Jupyter. Las dependencias de `requirements.txt` no están fijadas, por lo que una instalación futura puede no reproducir exactamente las versiones usadas. No se instaló ningún paquete.

## Estado de los notebooks iniciales

Los dos notebooks de datasets sólo mostraban carga, nulos, duplicados y clases. El notebook OCR usaba EasyOCR (`es`, `en`, CPU) sobre una sola imagen y ya conservaba correctamente el correo `contact@growthdot.com`, pero no tenía ground truth, métricas ni comparación de preprocesamiento.

## Inventario

El inventario cuantitativo y los hashes se encuentran en `notebooks/reports/data/dataset_audit.json`; el análisis interpretado está en los informes individuales y comparativo.
