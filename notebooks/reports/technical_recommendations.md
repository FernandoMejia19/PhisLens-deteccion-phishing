# Recomendaciones técnicas para las siguientes fases

## Preparación de datos y Random Forest

- Crear datos derivados fuera de `notebooks/data/` y registrar hash, fuente, versión y transformación.
- Normalizar etiquetas sin perder `target_original`; deduplicar antes de dividir.
- Usar particiones agrupadas por plantilla, mensaje base, destinatario o fuente cuando exista relación.
- Comparar TF-IDF de palabras y caracteres con variables léxicas/estructurales. Para Random Forest, limitar dimensionalidad mediante selección (`chi2`, frecuencia mínima) o reducción; documentar la pérdida de interpretabilidad.
- Establecer baseline lineal (regresión logística o Linear SVM) y evaluar accuracy, precision, recall, F1, matriz de confusión, PR-AUC y métricas por fuente/idioma. Priorizar recall de phishing sin ignorar falsos positivos.
- Calibrar probabilidades antes de llamarlas “confianza”. La salida debe expresar incertidumbre y limitaciones.

## Español e inglés

- Entrenar/evaluar por idioma y reportar resultados separados antes de considerar un modelo conjunto.
- No traducir automáticamente todo el corpus como sustituto de datos naturales; las traducciones de una misma muestra deben quedar en el mismo split.
- Conservar URLs, correos, números, moneda, negaciones y marcas antes de aplicar stemming/stopwords.
- Probar n-gramas de caracteres para errores ortográficos, variantes regionales y texto de OCR.

## Dominios y correo

- Extraer dominio con un parser de direcciones y normalizar IDN/Punycode. Comparar dominio visible, `Reply-To` y dominios de enlaces cuando existan cabeceras.
- Consultar DNS con `dnspython` para MX/SPF/DMARC; no interpretar la mera existencia de registros como legitimidad.
- Preferir RDAP para datos de registro. ICANN describe RDAP como reemplazo estandarizado de WHOIS y advierte que parte de los datos puede estar redactada: [ICANN RDAP](https://www.icann.org/en/contracted-parties/registry-operators/resources/registration-data-access-protocol).
- Google Safe Browsing puede comprobar URLs maliciosas en uso no comercial, requiere proyecto y clave, y exige advertir sobre falsos positivos/negativos. No tiene costo para ese uso: [límites y políticas](https://developers.google.com/safe-browsing/v4/usage-limits), [configuración](https://developers.google.com/safe-browsing/v4/get-started).
- VirusTotal Public API requiere cuenta/clave, limita 500 solicitudes diarias y 4 por minuto y no permite producto comercial; Premium es de pago por licencia: [Public vs Premium](https://docs.virustotal.com/reference/public-vs-premium-api).
- urlscan requiere clave para el flujo normal, aplica cuotas y puede hacer públicos los URLs enviados. Deben quitarse datos personales o usarse scans privados/no listados: [prácticas](https://docs.urlscan.io/pages/api-best-practices), [cuotas](https://docs.urlscan.io/pages/api-rate-limits), [precios](https://urlscan.io/pricing/). No enviar enlaces sospechosos automáticamente durante la tesis.

## Números telefónicos

- `phonenumbers` funciona sin API para parsear, normalizar E.164, comprobar longitud/patrón y asociar prefijo/región. No requiere credenciales ni pago. Su propia documentación aclara que la validación no demuestra que el número esté en uso ni quién es su propietario: [python-phonenumbers](https://github.com/daviddrysdale/python-phonenumbers).
- Mostrar “prefijo asociado a Ecuador” o “estructura posible”, nunca “número legítimo”, “usuario de WhatsApp” o ubicación actual.
- Servicios de lookup comerciales sólo deben evaluarse después por costo, privacidad, cobertura regional y credenciales; no son necesarios para la fase de modelado.

## Noticias y educación

- Priorizar fuentes institucionales con fecha, autor y enlace canónico. CERT-EU ofrece RSS por categoría para advisories, guidance y threat intelligence: [anuncio de feeds](https://cert.europa.eu/blog/read-feed-and-lead-fresh-features-for-our-cyber-fans).
- INCIBE-CERT es una fuente en español y su servicio de alerta temprana dispone de avisos/RSS; se debe filtrar por phishing porque muchos avisos son vulnerabilidades, no campañas de fraude.
- CISA publica advisories y recursos, pero tampoco todo su contenido es phishing. Implementar una lista blanca de fuentes, deduplicación, fecha de publicación y revisión de relevancia.
- RSS suele ser gratuito y sin credenciales; APIs y redistribución pueden tener condiciones propias. Guardar sólo metadatos y extractos permitidos, no copiar artículos completos.

## Orden recomendado

1. Confirmar procedencia/licencias y semántica de etiquetas.
2. Crear manifiesto y pipeline de limpieza/deduplicación.
3. Diseñar splits agrupados y baseline por idioma/fuente.
4. Entrenar Random Forest con conjuntos de características controlados.
5. Integrar OCR sólo después de medir cómo sus errores afectan la clasificación.
6. Evaluar servicios externos al diseñar el backend, con presupuesto, privacidad y términos de uso.
