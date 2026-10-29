from medicine_pack_extractor.render import html_to_text, render_aifa_medicine, render_medicine, slugify
from medicine_pack_extractor.aifa import AifaClient


def test_html_to_text_removes_markup() -> None:
    assert html_to_text("<p>Dosis <strong>diaria</strong></p><p>Segunda línea</p>") == "Dosis diaria\nSegunda línea"


def test_slugify_is_path_safe() -> None:
    assert slugify("Ácido acetilsalicílico 500 mg") == "acido-acetilsalicilico-500-mg"


def test_render_contains_source_and_sections() -> None:
    text = render_medicine(
        {"nregistro": "123", "nombre": "FÁRMACO", "pactivos": "Principio", "formaFarmaceutica": {"nombre": "Comprimido"}},
        [{"seccion": "4.1", "titulo": "Indicaciones", "contenido": "<p>Texto clínico</p>"}],
        {"slug": "analgesics", "names": {"es": "Analgésicos", "it": "Analgesici"}, "atc": "N02"},
    )
    assert "# FÁRMACO" in text
    assert "language: es" in text
    assert "  - analgesics" in text
    assert "## 4.1 Indicaciones" in text
    assert "https://cima.aemps.es/cima/dochtml/ft/123/FichaTecnica.html" in text


def test_render_aifa_contains_italian_metadata() -> None:
    text = render_aifa_medicine(
        {
            "DENOMINAZIONE": "FARMACO IT",
            "COD_FARMACO": "001234",
            "LINK_RCP": "https://api.aifa.gov.it/example?ts=RCP",
            "CODICE_ATC": "N02AA01",
            "PA_ASSOCIATI": "PRINCIPIO",
            "RAGIONE_SOCIALE": "AZIENDA",
            "FORMA": "Compressa",
        },
        "RIASSUNTO DELLE CARATTERISTICHE DEL PRODOTTO\nTesto ufficiale",
        {"slug": "analgesics", "names": {"es": "Analgésicos", "it": "Analgesici"}, "atc": "N02"},
    )
    assert "language: it" in text
    assert "Categoria del campione: Analgesici (N02)" in text
    assert "Testo ufficiale" in text


def test_aifa_pdf_cleanup_removes_only_watermark_lines() -> None:
    raw = "aco\nRIASSUNTO DELLE CARATTERISTICHE\n\n\nrm\nTesto clinico del farmaco"
    assert AifaClient._clean_pdf_text(raw) == (
        "RIASSUNTO DELLE CARATTERISTICHE\n\nTesto clinico del farmaco"
    )

