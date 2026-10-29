# CIMA Extractor

Proyecto reproducible en Python y Jupyter para convertir fichas técnicas públicas de medicamentos de [AEMPS/CIMA](https://cima.aemps.es/cima/publico/home.html) en un **Knowledge Pack Format v1** consumible por [LastLight](https://github.com/edujbarrios/lastlight), junto con casos JSONL compatibles con [lastlight-bench](https://github.com/edujbarrios/lastlight-bench).

> **Aviso sanitario:** este repositorio sirve para investigación de recuperación de información. No ofrece consejo médico, no prescribe tratamientos y no sustituye la ficha técnica vigente ni el criterio de profesionales sanitarios. CIMA es la fuente de autoridad; cada documento generado conserva su URL de origen.

## Muestra inicial

La configuración incluida selecciona determinísticamente 10 medicamentos autorizados y comercializados por cada grupo ATC:

| Carpeta | Grupo | ATC | Fichas |
|---|---|---:|---:|
| `analgesicos` | Analgésicos | `N02` | 10 |
| `antibacterianos` | Antibacterianos para uso sistémico | `J01` | 10 |
| `antidiabeticos` | Medicamentos usados en diabetes | `A10` | 10 |

Los grupos y el tamaño se pueden cambiar en [`config/categories.json`](config/categories.json).

## Estructura

```text
config/                 selección de categorías ATC
data/raw/               caché de respuestas CIMA (no versionada)
data/processed/         pack expandido y eval.jsonl (no versionados)
docs/                   metodología y formato de salida
notebooks/              flujo reproducible y explicación paso a paso
packs/                  ZIP final (no versionado)
src/cima_extractor/     cliente, transformación, render y CLI
tests/                  pruebas unitarias y del contrato del pack
```

## Instalación

Requiere Python 3.10 o posterior. No hay dependencias de ejecución; Jupyter y pytest son extras de desarrollo.

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
python -m pip install -e ".[dev]"
jupyter lab
```

Abre `notebooks/01_cima_to_lastlight.ipynb` y ejecuta todas las celdas, o usa la CLI:

```bash
cima-extractor --root .
```

La primera ejecución consulta la API pública y guarda una caché local en `data/raw/cima`. Las siguientes ejecuciones reutilizan esa caché. El resultado contiene:

- `data/processed/cima-medicamentos-es/lastlight-pack.json`
- `data/processed/cima-medicamentos-es/es/<categoria>/*.md`
- `packs/cima-medicamentos-es.zip`
- `data/processed/eval.jsonl`

## Probar con LastLight

```bash
python -m pip install lastlight
python -c "from lastlight import LastLight; e=LastLight('packs/cima-medicamentos-es.zip', language='es'); print(e.query('¿Qué información hay sobre un analgésico de la muestra?'))"
lastlight --knowledge packs/cima-medicamentos-es.zip --validate-pack
```

Para usar el dataset con un checkout de `lastlight-bench`:

```bash
lastlight-bench --corpus ./data/processed/cima-medicamentos-es --cases ./data/processed/eval.jsonl --output ./results/cima.json
```

Las preguntas generadas son una prueba inicial de recuperación por nombre, principio activo y número de registro. No constituyen todavía un benchmark clínico validado. Para resultados publicables, conviene añadir preguntas difíciles, negativas y anotación independiente por profesionales.

## Reproducibilidad y uso responsable

- La extracción usa únicamente endpoints públicos documentados de CIMA.
- Cada Markdown incluye número de registro, metadatos y enlace a la ficha oficial.
- El manifiesto guarda origen y SHA-256 de cada documento.
- Los datos generados se excluyen de Git para evitar copias obsoletas y mantener el repositorio ligero.
- CIMA cambia con el tiempo: antes de publicar un pack, revísalo y fija una versión/fecha de corte.
- Revisa las condiciones y el aviso legal de AEMPS antes de redistribuir contenido generado. La licencia MPL-2.0 de este repositorio cubre el código, no concede derechos adicionales sobre los datos fuente.

## Desarrollo

```bash
python -m pytest
```

Consulta [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md) para conocer las decisiones de muestreo y el mapeo exacto a ambos proyectos.

## Licencia

Código bajo Mozilla Public License 2.0. El contenido extraído conserva la atribución y las condiciones de su fuente AEMPS/CIMA.

