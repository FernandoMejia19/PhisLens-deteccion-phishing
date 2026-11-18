Spear-Phishing en español: dataset de correos dirigidos con señales de personalización (SpearPhishMX)
=====================================================================================================

Descripción
-----------
Este dataset contiene correos electrónicos en español etiquetados para clasificación binaria:
- etiqueta=1: spear-phishing
- etiqueta=0: legítimo

El objetivo es soportar investigación reproducible en detección de spear-phishing y explicabilidad (XAI).
Para reducir riesgos, esta versión pública incluye el campo 'cuerpo_sanitizado' con anonimización de PII
y URLs desactivadas (defanged).

Contenido del paquete
---------------------
- SpearPhishMX_dataset_publico.csv
  CSV UTF-8 separado por punto y coma (;).
- SpearPhishMX_schema_es.json
  Esquema del dataset (tipos, nulos, ejemplos y descripción de columnas).
- README.txt
  Este documento.

Privacidad, seguridad y uso responsable
---------------------------------------
- El campo 'cuerpo_sanitizado' reemplaza información sensible (por ejemplo, correos/telefonía/RFC/CLABE)
  con marcadores como <EMAIL>, <TELEFONO>, <RFC>, <CLABE>.
- Las URLs están desactivadas (por ejemplo, hxxp:// y [.] ) para evitar clics accidentales.
- Este dataset se publica con fines de investigación defensiva. No debe utilizarse para campañas ofensivas.

Notas metodológicas
-------------------
- 'dirigido_a_persona_v2' y campos relacionados reflejan heurísticas de detección de saludos y nombres
  para caracterizar personalización del mensaje.
- Algunas columnas relacionadas con adjuntos y ruteo ('conteo_adjuntos', 'conteo_saltos', etc.) se incluyen
  como placeholders para compatibilidad con pipelines, pero no siempre contienen información observada.

Citación (plantilla)
-------------------
Al publicar en Mendeley Data, se asignará un DOI. Reemplaza el DOI aquí:
@dataset{DiazZeferino_SpearPhishMX_2026,
  author    = {Díaz Zeferino, Juan Manuel},
  title     = {SpearPhishMX (Core público): correos en español para detección de spear-phishing},
  year      = {2026},
  publisher = {Mendeley Data},
  doi       = {10.17632/XXXXX.1}
}

Contacto
--------
Si deseas acceder a una versión con mayor detalle (por ejemplo, texto sin sanitizar o URLs originales),
considera publicar una versión 'restricted-access' o bajo embargo, según políticas institucionales.