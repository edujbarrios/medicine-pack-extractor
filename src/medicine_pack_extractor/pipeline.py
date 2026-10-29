"""Build Spanish, Italian and bilingual LastLight knowledge packs."""

from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from datetime import date
from pathlib import Path

from .aifa import AifaClient, AifaError
from .cima import CimaClient
from .render import render_aifa_medicine, render_medicine, slugify


def _load_config(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _provenance(path: Path, pack: Path, source: str, publisher: str) -> dict:
    return {
        "path": path.relative_to(pack).as_posix(),
        "source": source,
        "publisher": publisher,
        "retrieved_at": date.today().isoformat(),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def _manifest(*, name: str, languages: list[str], source: str, publisher: str, provenance: list[dict]) -> dict:
    return {
        "format_version": 1,
        "name": name,
        "version": "0.2.0",
        "description": "Official medicine product information prepared for offline retrieval research.",
        "languages": languages,
        "license": "Source data terms apply; extractor code is MPL-2.0",
        "source": source,
        "publisher": publisher,
        "published_at": date.today().isoformat(),
        "generated_on": date.today().isoformat(),
        "provenance": provenance,
    }


def _write_manifest(pack: Path, manifest: dict) -> None:
    (pack / "lastlight-pack.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def _archive(pack: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(pack.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(pack).as_posix())


def _build_cima(root: Path, config: dict, pack: Path) -> dict[str, int]:
    client = CimaClient(root / "data" / "raw" / "cima")
    provenance: list[dict] = []
    summary: dict[str, int] = {}
    publisher = "Agencia Española de Medicamentos y Productos Sanitarios (AEMPS)"
    for category in config["categories"]:
        target_count = int(category["limit"])
        selected = 0
        seen: set[str] = set()
        page = 1
        while selected < target_count:
            candidates = client.list_medicines(category["atc"], page=page)
            if not candidates:
                break
            for candidate in candidates:
                registration = str(candidate.get("nregistro", ""))
                if not registration or registration in seen:
                    continue
                seen.add(registration)
                detail = client.medicine(registration)
                atc_codes = {
                    str(item.get("codigo", "")).upper()
                    for item in detail.get("atcs", [])
                    if isinstance(item, dict)
                }
                if not any(code.startswith(category["atc"]) for code in atc_codes):
                    continue
                sections = client.technical_sheet(registration)
                if not sections:
                    continue
                rel = Path("es") / category["slug"] / f"{registration}-{slugify(str(detail.get('nombre', 'medicamento')))}.md"
                target = pack / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(render_medicine(detail, sections, category), encoding="utf-8")
                provenance.append(_provenance(target, pack, f"https://cima.aemps.es/cima/dochtml/ft/{registration}/FichaTecnica.html", publisher))
                selected += 1
                if selected >= target_count:
                    break
            page += 1
        summary[category["slug"]] = selected
        if selected < target_count:
            raise RuntimeError(f"Solo se encontraron {selected} fichas CIMA para {category['slug']}")
    _write_manifest(pack, _manifest(name="CIMA Medicines ES", languages=["es"], source="https://cima.aemps.es/cima/publico/home.html", publisher=publisher, provenance=provenance))
    return summary


def _build_aifa(root: Path, config: dict, pack: Path) -> dict[str, int]:
    client = AifaClient(root / "data" / "raw" / "aifa")
    provenance: list[dict] = []
    summary: dict[str, int] = {}
    publisher = "Agenzia Italiana del Farmaco (AIFA)"
    for category in config["categories"]:
        selected = 0
        target_count = int(category["limit"])
        for medicine in client.select_medicines(category["atc"], target_count * 3):
            try:
                rcp_text = client.rcp_text(medicine)
            except AifaError:
                continue
            code = medicine["COD_FARMACO"].strip()
            rel = Path("it") / category["slug"] / f"{code}-{slugify(medicine['DENOMINAZIONE'])}.md"
            target = pack / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(render_aifa_medicine(medicine, rcp_text, category), encoding="utf-8")
            provenance.append(_provenance(target, pack, medicine["LINK_RCP"].strip(), publisher))
            selected += 1
            if selected >= target_count:
                break
        summary[category["slug"]] = selected
        if selected < target_count:
            raise RuntimeError(f"Solo se extrajeron {selected} RCP AIFA para {category['slug']}")
    _write_manifest(pack, _manifest(name="AIFA Medicinali IT", languages=["it"], source="https://medicinali.aifa.gov.it/it/", publisher=publisher, provenance=provenance))
    return summary


def _build_combined(spanish: Path, italian: Path, combined: Path) -> None:
    shutil.copytree(spanish / "es", combined / "es")
    shutil.copytree(italian / "it", combined / "it")
    es_manifest = json.loads((spanish / "lastlight-pack.json").read_text(encoding="utf-8"))
    it_manifest = json.loads((italian / "lastlight-pack.json").read_text(encoding="utf-8"))
    _write_manifest(combined, _manifest(
        name="Official Medicines ES-IT",
        languages=["es", "it"],
        source="https://cima.aemps.es/ | https://medicinali.aifa.gov.it/",
        publisher="AEMPS and AIFA; assembled by medicine-pack-extractor",
        provenance=es_manifest["provenance"] + it_manifest["provenance"],
    ))


def build_project(root: Path, config_path: Path | None = None) -> dict:
    root = Path(root).resolve()
    config = _load_config(config_path or root / "config" / "categories.json")
    output = root / "data" / "processed"
    packs_dir = root / "packs"
    paths = {
        "es": output / "cima-medicines-es",
        "it": output / "aifa-medicinali-it",
        "es_it": output / "official-medicines-es-it",
    }
    for path in paths.values():
        if path.exists():
            shutil.rmtree(path)
        path.mkdir(parents=True)
    summaries = {"es": _build_cima(root, config, paths["es"]), "it": _build_aifa(root, config, paths["it"])}
    _build_combined(paths["es"], paths["it"], paths["es_it"])
    archives = {
        "es": packs_dir / "cima-medicines-es.zip",
        "it": packs_dir / "aifa-medicinali-it.zip",
        "es_it": packs_dir / "official-medicines-es-it.zip",
    }
    for key, archive in archives.items():
        _archive(paths[key], archive)
    return {
        "packs": {key: str(path) for key, path in paths.items()},
        "archives": {key: str(path) for key, path in archives.items()},
        "categories": summaries,
        "documents": {"es": sum(summaries["es"].values()), "it": sum(summaries["it"].values())},
    }
