# Contribuir

Abre una incidencia antes de cambios grandes. Mantén separadas la lógica de descarga, transformación y presentación; añade pruebas para cada corrección. No incluyas en commits cachés, packs generados ni información personal.

Antes de proponer cambios ejecuta:

```bash
python -m pytest
cima-extractor --root .
lastlight --knowledge packs/cima-medicamentos-es.zip --validate-pack
```

Los cambios que alteren el muestreo o el texto generado deben explicar su impacto en la reproducibilidad y en las métricas del benchmark.

