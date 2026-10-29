# Contributing

Open an issue before making substantial changes. Keep download, transformation, and rendering logic separate, and add tests for every fix. Do not commit caches, generated packs, or personal information.

Before proposing changes, run:

```bash
python -m pytest
medicine-pack-extractor --root .
lastlight --knowledge packs/cima-medicines-es.zip --validate-pack
lastlight --knowledge packs/aifa-medicinali-it.zip --validate-pack
lastlight --knowledge packs/official-medicines-es-it.zip --validate-pack
```

Changes that affect sampling or generated text must explain their impact on reproducibility and benchmark metrics.

