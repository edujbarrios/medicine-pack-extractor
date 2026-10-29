import json
import zipfile
from pathlib import Path


def test_config_has_unique_categories() -> None:
    config = json.loads(Path("config/categories.json").read_text(encoding="utf-8"))
    assert sum(item["limit"] for item in config["categories"]) == 100
    assert len(config["categories"]) == 10
    assert {item["limit"] for item in config["categories"]} == {10}
    assert len({item["slug"] for item in config["categories"]}) == len(config["categories"])


def test_generated_archive_contract_if_present() -> None:
    archive = Path("packs/cima-medicamentos-es.zip")
    if not archive.exists():
        return
    with zipfile.ZipFile(archive) as zf:
        names = zf.namelist()
        assert "lastlight-pack.json" in names
        assert any(name.startswith("es/") and name.endswith(".md") for name in names)

