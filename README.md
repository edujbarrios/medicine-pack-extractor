# Medicine Pack Extractor

Proyecto reproducible en Python y Jupyter para convertir información oficial de medicamentos de España e Italia en knowledge packs compatibles con [LastLight](https://github.com/edujbarrios/lastlight).

Fuentes:

- **España (`es`)**: fichas técnicas de [AEMPS/CIMA](https://cima.aemps.es/cima/publico/home.html).
- **Italia (`it`)**: RCP y catálogo abierto de [AIFA Medicinali](https://medicinali.aifa.gov.it/it/).

> **Aviso sanitario:** este repositorio sirve para investigación de recuperación de información. No ofrece consejo médico, no prescribe tratamientos y no sustituye los documentos oficiales vigentes ni el criterio de profesionales sanitarios.

## Corpus comparable por idioma

Cada país aporta 100 medicamentos: 10 documentos de cada una de las mismas 10 categorías ATC. Los medicamentos concretos pueden ser diferentes porque proceden de registros nacionales distintos.

| Categoría común | ATC | España | Italia |
|---|---:|---:|---:|
| Analgésicos / Analgesici | `N02` | 10 | 10 |
| Antibacterianos / Antibatterici | `J01` | 10 | 10 |
| Antidiabéticos / Farmaci usati nel diabete | `A10` | 10 | 10 |
| Trastornos de la acidez / Disturbi correlati all'acidità | `A02` | 10 | 10 |
| Antitrombóticos / Antitrombotici | `B01` | 10 | 10 |
| Betabloqueantes / Beta-bloccanti | `C07` | 10 | 10 |
| Corticosteroides sistémicos / Corticosteroidi sistemici | `H02` | 10 | 10 |
| Antiinflamatorios / Antinfiammatori | `M01` | 10 | 10 |
| Psicolépticos / Psicolettici | `N05` | 10 | 10 |
| Enfermedades obstructivas respiratorias / Vie respiratorie | `R03` | 10 | 10 |

La selección se define una sola vez en [`config/categories.json`](config/categories.json), con nombres localizados en español e italiano.

## Artefactos generados

Una ejecución produce tres packs, todos con manifiesto, procedencia y SHA-256:

```text
packs/
├── cima-medicines-es.zip          # 100 documentos, solo español
├── aifa-medicinali-it.zip         # 100 documentos, solo italiano
└── official-medicines-es-it.zip   # 200 documentos, corpus bilingüe
```

El pack combinado queda organizado así:

```text
official-medicines-es-it/
├── lastlight-pack.json
├── es/<categoria>/*.md
└── it/<categoria>/*.md
```

Este repositorio no contiene preguntas, etiquetas de relevancia ni datasets de evaluación. Esos artefactos pertenecen a [lastlight-bench](https://github.com/edujbarrios/lastlight-bench).

## Estructura del proyecto

```text
config/                         categorías ATC comunes y nombres localizados
data/raw/cima/                  caché de respuestas CIMA (no versionada)
data/raw/aifa/                  CSV y RCP de AIFA (no versionados)
data/processed/                 packs expandidos (no versionados)
docs/                           metodología y procedencia
notebooks/                      flujo reproducible
packs/                          ZIP finales (no versionados)
src/medicine_pack_extractor/    clientes, transformación y CLI
tests/                          pruebas unitarias y de contrato
```

## Instalación

Requiere Python 3.10 o posterior. Para la mejor extracción de los RCP italianos se recomienda tener `pdftotext` de Poppler disponible; si no está instalado se usa `pypdf` como alternativa.

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
python -m pip install -e ".[dev]"
jupyter lab
```

Abre `notebooks/01_build_medicine_packs.ipynb` o usa la CLI:

```bash
medicine-pack-extractor --root .
```

La primera ejecución descarga las fuentes públicas y las guarda en `data/raw`. Las ejecuciones posteriores reutilizan la caché.

## Probar con LastLight

```bash
python -m pip install lastlight
lastlight --knowledge packs/cima-medicines-es.zip --validate-pack
lastlight --knowledge packs/aifa-medicinali-it.zip --validate-pack
lastlight --knowledge packs/official-medicines-es-it.zip --validate-pack
```

```python
from lastlight import LastLight

engine = LastLight("packs/official-medicines-es-it.zip", strategy="bm25")
result = engine.query("Quali informazioni contiene il RCP del medicinale?")
print(result.passage if result.accepted else result.refusal_reason)
```

## Reproducibilidad y licencias

- CIMA se consulta mediante su API pública y cada documento conserva la URL de su ficha técnica.
- AIFA se consulta mediante su CSV abierto diario y los enlaces oficiales a los RCP.
- AIFA publica sus open data bajo CC BY 4.0; se conserva atribución a la agencia y al documento fuente.
- El código del extractor se distribuye bajo MPL-2.0. Esa licencia no sustituye las condiciones de las fuentes.
- El contenido puede cambiar con el tiempo. Para publicar una versión estable conviene conservar la caché usada, fijar una versión del pack y registrar la fecha de corte.

## Desarrollo

```bash
python -m pytest
```

Consulta [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md) para ver el muestreo, la transformación de RCP/PDF y las limitaciones.

## Licencia

Código bajo Mozilla Public License 2.0. Los documentos generados mantienen atribución y enlaces a AEMPS/CIMA y AIFA.
