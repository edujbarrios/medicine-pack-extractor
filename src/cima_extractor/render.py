"""Render CIMA records as auditable LastLight Markdown documents."""

from __future__ import annotations

import html
import re
from html.parser import HTMLParser


class _TextExtractor(HTMLParser):
    BLOCKS = {"p", "div", "br", "li", "tr", "h1", "h2", "h3", "h4", "h5", "table"}

    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in self.BLOCKS:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def html_to_text(value: object) -> str:
    parser = _TextExtractor()
    parser.feed(str(value or ""))
    text = html.unescape("".join(parser.parts)).replace("\xa0", " ")
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line)


def slugify(value: str) -> str:
    import unicodedata

    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", normalized.lower()).strip("-")[:80]


def render_medicine(medicine: dict, sections: list[dict], category: dict) -> str:
    registration = str(medicine.get("nregistro", ""))
    name = str(medicine.get("nombre", registration))
    active = medicine.get("pactivos") or ", ".join(
        str(item.get("nombre", "")) for item in medicine.get("principiosActivos", [])
    )
    atcs = ", ".join(str(item.get("codigo") or item.get("nombre", "")) for item in medicine.get("atcs", []))
    source = f"https://cima.aemps.es/cima/dochtml/ft/{registration}/FichaTecnica.html"
    safe_title = name.replace("\n", " ").replace(":", " -")
    lines = [
        "---",
        f"title: {safe_title}",
        "language: es",
        "tags:",
        "  - medicamentos",
        "  - cima",
        f"  - {category.get('slug') or slugify(str(category['name']))}",
        f"  - {str(category['atc']).lower()}",
        "priority: normal",
        "---", "",
        f"# {name}", "", 
        "> Fuente oficial: AEMPS/CIMA. Documento para recuperación de información; no sustituye el criterio médico ni la ficha técnica vigente.", "",
        "## Identificación", "",
        f"- Número de registro: {registration}",
        f"- Categoría de muestra: {category['name']} ({category['atc']})",
        f"- Principios activos: {active or 'No indicado'}",
        f"- Clasificación ATC: {atcs or category['atc']}",
        f"- Laboratorio titular: {medicine.get('labtitular', 'No indicado')}",
        f"- Condiciones de prescripción: {medicine.get('cpresc', 'No indicado')}",
        f"- Forma farmacéutica: {(medicine.get('formaFarmaceutica') or {}).get('nombre', 'No indicada')}",
        f"- Fuente: {source}", "",
    ]
    for section in sections:
        number = section.get("seccion") or section.get("numero") or section.get("id") or ""
        title = html_to_text(section.get("titulo") or section.get("nombre") or "Sección")
        content = html_to_text(section.get("contenido") or section.get("texto") or "")
        if content:
            lines.extend([f"## {number} {title}".strip(), "", content, ""])
    return "\n".join(lines).rstrip() + "\n"

