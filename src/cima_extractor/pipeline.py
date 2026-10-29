"""End-to-end extraction and LastLight pack generation."""

from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from datetime import date
from pathlib import Path

from .cima import CimaClient
from .render import render_medicine, slugify


def _load_config(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_project(root: Path, config_path: Path | None = None) -> dict:
    root = Path(root).resolve()
    config = _load_config(config_path or root / "config" / "categories.json")
    client = CimaClient(root / "data" / "raw" / "cima")
    pack = root / "data" / "processed" / "cima-medicamentos-es"
    if pack.exists():
        shutil.rmtree(pack)
    pack.mkdir(parents=True)
    provenance: list[dict] = []
    cases: list[dict] = []
    summary: dict[str, int] = {}

    for category in config["categories"]:
        candidates = client.list_medicines(category["atc"])
        selected: list[dict] = []
        for candidate in candidates:
            registration = str(candidate.get("nregistro", ""))
            if not registration:
                continue
            detail = client.medicine(registration)
            sections = client.technical_sheet(registration)
            if not sections:
                continue
            selected.append(detail)
            rel = Path(config["language"]) / category["slug"] / f"{registration}-{slugify(str(detail.get('nombre', 'medicamento')))}.md"
            target = pack / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            rendered = render_medicine(detail, sections, category)
            target.write_text(rendered, encoding="utf-8")
            provenance.append({
                "path": rel.as_posix(),
                "source": f"https://cima.aemps.es/cima/dochtml/ft/{registration}/FichaTecnica.html",
                "publisher": "Agencia Española de Medicamentos y Productos Sanitarios (AEMPS)",
                "retrieved_at": date.today().isoformat(),
                "sha256": hashlib.sha256(rendered.encode()).hexdigest(),
            })
            cases.extend(_benchmark_cases(detail, rel.as_posix(), category))
            if len(selected) >= int(config["per_category"]):
                break
        summary[category["slug"]] = len(selected)
        if len(selected) < int(config["per_category"]):
            raise RuntimeError(f"Solo se encontraron {len(selected)} fichas utilizables para {category['slug']}")

    manifest = {
        "format_version": 1,
        "name": "CIMA Medicamentos ES",
        "version": "0.1.0",
        "description": "Muestra reproducible de fichas técnicas oficiales de medicamentos de AEMPS/CIMA.",
        "languages": [config["language"]],
        "license": "See AEMPS source terms; extractor code is MPL-2.0",
        "source": "https://cima.aemps.es/cima/publico/home.html",
        "publisher": "AEMPS / cima-extractor (generated derivative)",
        "published_at": date.today().isoformat(),
        "generated_on": date.today().isoformat(),
        "provenance": provenance,
    }
    (pack / "lastlight-pack.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    dataset = root / "data" / "processed" / "eval.jsonl"
    dataset.write_text("".join(json.dumps(case, ensure_ascii=False) + "\n" for case in cases), encoding="utf-8")
    archive = root / "packs" / "cima-medicamentos-es.zip"
    archive.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(pack.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(pack).as_posix())
    return {"pack": str(pack), "archive": str(archive), "dataset": str(dataset), "categories": summary, "cases": len(cases)}


def _benchmark_cases(medicine: dict, path: str, category: dict) -> list[dict]:
    registration = str(medicine.get("nregistro", ""))
    name = str(medicine.get("nombre", registration))
    active = str(medicine.get("pactivos", "")).strip()
    base = f"cima-{category['slug']}-{registration}"
    queries = [f"¿Cuál es la información de la ficha técnica de {name}?"]
    if active:
        queries.append(f"¿Qué medicamento de la muestra contiene {active} y tiene el registro {registration}?")
    return [{
        "id": f"{base}-{index}", "query": query, "language": "es", "category": category["slug"],
        "answerable": True, "expected_path": path, "difficulty": "easy", "tags": ["cima", category["atc"].lower(), "ficha-tecnica"],
    } for index, query in enumerate(queries, 1)]

