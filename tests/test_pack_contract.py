import json
import zipfile
from pathlib import Path


def test_config_has_unique_categories() -> None:
    config = json.loads(Path("config/categories.json").read_text(encoding="utf-8"))
    assert sum(item["limit"] for item in config["categories"]) == 100
    assert len(config["categories"]) == 10
    assert {item["limit"] for item in config["categories"]} == {10}
    assert all(set(item["names"]) == {"es", "it"} for item in config["categories"])
    assert len({item["slug"] for item in config["categories"]}) == len(config["categories"])


def test_generated_archive_contract_if_present() -> None:
    archive = Path("packs/official-medicines-es-it.zip")
    if not archive.exists():
        return
    with zipfile.ZipFile(archive) as zf:
        names = zf.namelist()
        assert "lastlight-pack.json" in names
        assert any(name.startswith("es/") and name.endswith(".md") for name in names)
        assert any(name.startswith("it/") and name.endswith(".md") for name in names)


def test_generated_documents_match_category_atc_if_present() -> None:
    pack = Path("data/processed/official-medicines-es-it")
    if not pack.exists():
        return
    config = json.loads(Path("config/categories.json").read_text(encoding="utf-8"))
    for language in ("es", "it"):
        for category in config["categories"]:
            documents = list((pack / language / category["slug"]).glob("*.md"))
            assert len(documents) == category["limit"]
            expected = category["atc"]
            label = "- Clasificación ATC:" if language == "es" else "- Codice ATC:"
            for path in documents:
                metadata_line = next(
                    line for line in path.read_text(encoding="utf-8").splitlines()
                    if line.startswith(label)
                )
                assert expected in metadata_line, path

