# Medicine Pack Extractor

Reproducible Python and Jupyter project for converting official medicine information from Spain and Italy into knowledge packs compatible with [LastLight](https://github.com/edujbarrios/lastlight).

Sources:

- **España (`es`)**: Fichas técnicas de medicamentos publicadas por [AEMPS/CIMA](https://cima.aemps.es/cima/publico/home.html).
- **Italia (`it`)**: Riassunti delle Caratteristiche del Prodotto e catalogo aperto pubblicati da [AIFA Medicinali](https://medicinali.aifa.gov.it/it/).

> **Medical disclaimer:** this repository is intended for information-retrieval research. It does not provide medical advice, prescribe treatment, or replace current official documents or professional clinical judgment.

## Comparable corpora by language

Each country contributes 100 medicines: 10 documents from each of the same 10 ATC categories. The specific medicines may differ because they come from separate national registries.

| Shared category | ATC | Spain | Italy |
|---|---:|---:|---:|
| Analgesics | `N02` | 10 | 10 |
| Antibacterials for systemic use | `J01` | 10 | 10 |
| Medicines used in diabetes | `A10` | 10 | 10 |
| Medicines for acid-related disorders | `A02` | 10 | 10 |
| Antithrombotic agents | `B01` | 10 | 10 |
| Beta blockers | `C07` | 10 | 10 |
| Corticosteroids for systemic use | `H02` | 10 | 10 |
| Anti-inflammatory and antirheumatic products | `M01` | 10 | 10 |
| Psycholeptics | `N05` | 10 | 10 |
| Medicines for obstructive airway diseases | `R03` | 10 | 10 |

The selection is defined once in [`config/categories.json`](config/categories.json), with localized Spanish and Italian names.

## Generated artifacts

One run produces three packs, each with a manifest, provenance records, and SHA-256 hashes:

```text
packs/
├── cima-medicines-es.zip          # 100 documents, Spanish only
├── aifa-medicinali-it.zip         # 100 documents, Italian only
└── official-medicines-es-it.zip   # 200 documents, bilingual corpus
```

The combined pack is organized as follows:

```text
official-medicines-es-it/
├── lastlight-pack.json
├── es/<category>/*.md
└── it/<category>/*.md
```

This repository does not contain benchmark questions, relevance labels, or evaluation datasets. Those artifacts belong in [lastlight-bench](https://github.com/edujbarrios/lastlight-bench).

## Project structure

```text
config/                         shared ATC categories and localized names
data/raw/cima/                  CIMA response cache (not versioned)
data/raw/aifa/                  AIFA CSV and RCP cache (not versioned)
data/processed/                 expanded packs (not versioned)
docs/                           methodology and provenance
notebooks/                      reproducible workflow
packs/                          final ZIP files (not versioned)
src/medicine_pack_extractor/    clients, transformations, and CLI
tests/                          unit and contract tests
```

## Installation

Python 3.10 or later is required. For the best extraction quality from Italian RCP files, Poppler's `pdftotext` is recommended. If it is unavailable, the extractor falls back to `pypdf`.

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
python -m pip install -e ".[dev]"
jupyter lab
```

Open `notebooks/01_build_medicine_packs.ipynb` or use the CLI:

```bash
medicine-pack-extractor --root .
```

The first run downloads the public sources and stores them under `data/raw`. Later runs reuse the cache.

## Test with LastLight

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

## Reproducibility and licensing

- CIMA is accessed through its public API, and each document retains the URL of its official technical sheet.
- AIFA is accessed through its daily open CSV catalogue and official RCP links.
- AIFA publishes its open data under CC BY 4.0; attribution to the agency and source document is preserved.
- The extractor code is distributed under MPL-2.0. This license does not replace the source agencies' terms.
- Source content changes over time. For a stable release, retain the source cache, assign a pack version, and record the cutoff date.

## Development

```bash
python -m pytest
```

See [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md) for sampling details, RCP/PDF transformation, and limitations.

## Acknowledgments

The Italian benchmark variant was proposed by **Carrots Studio** through the [Campanile project](https://github.com/Carrotstudiosoftwarehouse/campanile), an offline-first neighborhood information and mutual-aid platform designed to keep working when internet connectivity is unavailable.

## License

Code is licensed under the Mozilla Public License 2.0. Generated documents retain attribution and links to AEMPS/CIMA and AIFA.
