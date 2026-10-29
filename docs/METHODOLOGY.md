# Metodología

## Objetivo

Construir dos corpus nacionales comparables de información oficial sobre medicamentos y un pack combinado para recuperación offline con LastLight. La unidad de comparación es la categoría ATC, no la identidad exacta del medicamento.

## Diseño del corpus

La configuración común contiene diez prefijos ATC: `A02`, `A10`, `B01`, `C07`, `H02`, `J01`, `M01`, `N02`, `N05` y `R03`. Se seleccionan diez medicamentos autorizados con documentación utilizable por categoría y país.

El resultado esperado es:

- España: 100 fichas técnicas en español.
- Italia: 100 RCP en italiano.
- Pack combinado: 200 documentos organizados bajo `es/` e `it/`.

No se fuerza que un medicamento español tenga un equivalente italiano. Esto evita emparejamientos farmacológicos dudosos y mantiene una estratificación comparable por categoría.

## España: AEMPS/CIMA

La URL base es `https://cima.aemps.es/cima/rest`. Por cada prefijo ATC se consulta `medicamentos` con `comerc=1` y `autorizados=1`. Para cada número de registro se descargan:

1. `medicamento?nregistro=...`, con identidad y metadatos.
2. `docSegmentado/contenido/1?nregistro=...`, con la ficha técnica segmentada.

El HTML se convierte a texto sin resumir ni reinterpretar el contenido clínico. Las respuestas originales se guardan en `data/raw/cima`.

## Italia: AIFA

AIFA publica diariamente `https://drive.aifa.gov.it/farmaci/confezioni_fornitura.csv`. El catálogo incluye AIC, código de medicamento, estado administrativo, ATC, principio activo y enlaces a Foglio Illustrativo y RCP.

El extractor procesa el CSV en streaming, conserva medicamentos con estado `Autorizzata`, agrupa por prefijo ATC y deduplica por `COD_FARMACO`. Descarga el `LINK_RCP` desde `api.aifa.gov.it` y extrae el texto del PDF:

1. Preferentemente con `pdftotext -layout` de Poppler.
2. Como alternativa portable, con `pypdf`.

Los CSV y PDF originales se guardan en `data/raw/aifa`. El RCP no se traduce, resume ni combina con el Foglio Illustrativo.

## Rutas y metadatos

Las rutas son estables y paralelas:

```text
es/<categoria-comun>/<registro>-<nombre>.md
it/<categoria-comun>/<cod-farmaco>-<nombre>.md
```

Cada documento declara `title`, `language`, `tags` y `priority` en front matter. Cada manifiesto declara fuente, editor, idiomas, fecha de generación y una cadena de procedencia con URL y SHA-256 por documento.

## Packs

Se publican tres artefactos independientes:

- `cima-medicines-es.zip`: evaluación monolingüe española.
- `aifa-medicinali-it.zip`: evaluación monolingüe italiana.
- `official-medicines-es-it.zip`: recuperación y enrutamiento bilingüe.

Las preguntas de benchmark no se generan aquí. Deben mantenerse en `lastlight-bench` para separar el corpus de su evaluación y evitar contaminación entre construcción y ground truth.

## Licencias y atribución

AIFA indica CC BY 4.0 para sus open data. Cada documento italiano atribuye AIFA y enlaza su RCP. Los documentos españoles conservan atribución y enlace a AEMPS/CIMA. La MPL-2.0 cubre el código del extractor, no reemplaza las condiciones de los organismos fuente.

## Limitaciones

- Los catálogos nacionales y sus documentos cambian con el tiempo.
- Una misma categoría ATC no implica equivalencia entre dos medicamentos concretos.
- La extracción de PDF puede conservar encabezados, pies o marcas de agua del documento oficial.
- Algunos PDF pueden carecer de una capa de texto utilizable; el extractor los omite y prueba candidatos posteriores.
- El corpus permite evaluar recuperación documental, no seguridad clínica ni corrección terapéutica.
- Un benchmark robusto requiere preguntas negativas, paráfrasis difíciles, control de fugas léxicas y revisión especializada.

## Publicación reproducible

Para una versión citable se recomienda conservar las cachés de corte fuera de Git, registrar sus hashes, fijar la versión del pack y validar los tres ZIP con la misma versión de LastLight usada en la evaluación.
