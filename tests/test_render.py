from cima_extractor.render import html_to_text, render_medicine, slugify


def test_html_to_text_removes_markup() -> None:
    assert html_to_text("<p>Dosis <strong>diaria</strong></p><p>Segunda línea</p>") == "Dosis diaria\nSegunda línea"


def test_slugify_is_path_safe() -> None:
    assert slugify("Ácido acetilsalicílico 500 mg") == "acido-acetilsalicilico-500-mg"


def test_render_contains_source_and_sections() -> None:
    text = render_medicine(
        {"nregistro": "123", "nombre": "FÁRMACO", "pactivos": "Principio", "formaFarmaceutica": {"nombre": "Comprimido"}},
        [{"seccion": "4.1", "titulo": "Indicaciones", "contenido": "<p>Texto clínico</p>"}],
        {"name": "Analgésicos", "atc": "N02"},
    )
    assert "# FÁRMACO" in text
    assert "language: es" in text
    assert "  - analgesicos" in text
    assert "## 4.1 Indicaciones" in text
    assert "https://cima.aemps.es/cima/dochtml/ft/123/FichaTecnica.html" in text

