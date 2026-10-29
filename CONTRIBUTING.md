# Contribuir

Abre una incidencia antes de cambios grandes. Mantén separadas la lógica de descarga, transformación y presentación; añade pruebas para cada corrección. No incluyas en commits cachés, packs generados ni información personal.

Antes de proponer cambios ejecuta:

```bash
python -m pytest
medicine-pack-extractor --root .
lastlight --knowledge packs/cima-medicines-es.zip --validate-pack
lastlight --knowledge packs/aifa-medicinali-it.zip --validate-pack
lastlight --knowledge packs/official-medicines-es-it.zip --validate-pack
```

Los cambios que alteren el muestreo o el texto generado deben explicar su impacto en la reproducibilidad y en las métricas del benchmark.

