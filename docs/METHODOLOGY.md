# Metodología

## Objetivo

Construir un corpus español, auditable y reproducible de fichas técnicas que LastLight pueda montar como Knowledge Pack v1 y que `lastlight-bench` pueda evaluar sin adaptadores especiales.

## Fuente y selección

La URL base oficial es `https://cima.aemps.es/cima/rest`. Para cada prefijo ATC configurado se consulta `medicamentos` con `comerc=1` y `autorizados=1`. Se recorren las páginas y los resultados en el orden que entrega CIMA hasta alcanzar el límite configurado de medicamentos con ficha técnica: 34 analgésicos, 33 antibacterianos y 33 antidiabéticos.

Para cada número de registro se descargan:

1. `medicamento?nregistro=...`, con identidad y metadatos.
2. `docSegmentado/contenido/1?nregistro=...`, con las secciones de ficha técnica (`tipoDoc=1`).

Las respuestas originales quedan en la caché local `data/raw/cima`. Esto permite inspección y repetición sin cargar innecesariamente el servicio.

## Transformación

El HTML de cada sección se convierte en texto conservando saltos de bloque. No se resume ni se reescribe el contenido clínico. Se antepone una cabecera con metadatos, aviso sanitario y enlace canónico. La ruta estable es:

```text
es/<categoria>/<nregistro>-<nombre-normalizado>.md
```

El manifiesto usa `format_version: 1`, idioma `es`, versión de contenido y una entrada de procedencia con URL y SHA-256 por documento. El ZIP sitúa el manifiesto en su raíz, tal como requiere LastLight.

## Casos de benchmark

`data/processed/eval.jsonl` sigue el esquema observado en `lastlight-bench`:

```json
{"id":"...","query":"...","language":"es","category":"...","answerable":true,"expected_path":"es/...md","difficulty":"easy","tags":["cima","n02","ficha-tecnica"]}
```

Se crean hasta dos consultas por ficha: una por nombre y otra por principio activo/número de registro. Son casos de humo (`easy`) para verificar integración y ranking, no una evaluación clínica completa.

## Limitaciones

- El orden del API puede cambiar y, por tanto, también la muestra si se elimina la caché.
- El prefijo ATC agrupa medicamentos heterogéneos; no es una taxonomía diseñada para este benchmark.
- El corpus puede quedar desactualizado respecto a CIMA.
- La ficha técnica informa sobre medicamentos, pero su recuperación automática no equivale a consejo seguro para un paciente.
- Un benchmark robusto necesita negativos plausibles, paráfrasis difíciles, control de fugas léxicas y revisión humana especializada.

## Extensiones recomendadas

- Guardar una lista fija de números de registro para una versión publicada.
- Añadir fecha de actualización del documento a la procedencia.
- Crear casos de rechazo y consultas con nombres comerciales parecidos.
- Ejecutar una matriz lexical/BM25/adaptive de `lastlight-bench` y versionar solo los resultados resumidos.
- Incorporar validación clínica independiente antes de cualquier uso fuera de investigación.

