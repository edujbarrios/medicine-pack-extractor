"""Client for AIFA's official open CSV and RCP document service."""

from __future__ import annotations

import csv
import shutil
import subprocess
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

AIFA_CSV_URL = "https://drive.aifa.gov.it/farmaci/confezioni_fornitura.csv"
USER_AGENT = "medicine-pack-extractor/0.2 (+https://github.com/edujbarrios)"


class AifaError(RuntimeError):
    """Raised when an AIFA resource cannot be downloaded or parsed."""


class AifaClient:
    def __init__(self, cache_dir: Path, timeout: int = 90) -> None:
        self.cache_dir = Path(cache_dir)
        self.timeout = timeout
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.pdf_dir = self.cache_dir / "rcp"
        self.pdf_dir.mkdir(exist_ok=True)

    def catalogue(self) -> Path:
        target = self.cache_dir / "confezioni_fornitura.csv"
        if not target.exists() or target.stat().st_size == 0:
            self._download(AIFA_CSV_URL, target, accept="text/csv")
        return target

    def select_medicines(self, atc_prefix: str, limit: int) -> list[dict[str, str]]:
        selected: list[dict[str, str]] = []
        seen: set[str] = set()
        with self.catalogue().open("r", encoding="utf-8-sig", newline="") as stream:
            rows = csv.DictReader(stream, delimiter=";")
            for row in rows:
                medicine_code = row.get("COD_FARMACO", "").strip()
                if (
                    not medicine_code
                    or medicine_code in seen
                    or not row.get("CODICE_ATC", "").startswith(atc_prefix)
                    or row.get("STATO_AMMINISTRATIVO", "").casefold() != "autorizzata"
                    or not row.get("LINK_RCP", "").startswith("https://api.aifa.gov.it/")
                ):
                    continue
                seen.add(medicine_code)
                selected.append(row)
                if len(selected) >= limit:
                    break
        if len(selected) < limit:
            raise AifaError(f"Solo se encontraron {len(selected)} RCP para ATC {atc_prefix}")
        return selected

    def rcp_text(self, medicine: dict[str, str]) -> str:
        code = medicine["COD_FARMACO"].strip()
        pdf = self.pdf_dir / f"{code}.pdf"
        if not pdf.exists() or pdf.stat().st_size == 0:
            self._download(medicine["LINK_RCP"], pdf, accept="application/pdf")
        text = self._extract_pdf_text(pdf)
        if len(text) < 500:
            raise AifaError(f"El RCP {code} no contiene texto suficiente")
        return text

    def _download(self, url: str, target: Path, accept: str) -> None:
        request = Request(
            url,
            headers={
                "Accept": accept,
                "User-Agent": USER_AGENT,
                "Origin": "https://medicinali.aifa.gov.it",
                "Referer": "https://medicinali.aifa.gov.it/it/",
            },
        )
        temporary = target.with_suffix(target.suffix + ".part")
        try:
            with urlopen(request, timeout=self.timeout) as response, temporary.open("wb") as output:
                shutil.copyfileobj(response, output)
            temporary.replace(target)
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            temporary.unlink(missing_ok=True)
            raise AifaError(f"No se pudo descargar {url}: {exc}") from exc

    @staticmethod
    def _extract_pdf_text(pdf: Path) -> str:
        executable = shutil.which("pdftotext")
        if executable:
            try:
                completed = subprocess.run(
                    [executable, "-layout", str(pdf), "-"],
                    check=True,
                    capture_output=True,
                )
                text = completed.stdout.decode("utf-8", errors="replace")
            except (subprocess.CalledProcessError, OSError):
                text = AifaClient._extract_with_pypdf(pdf)
        else:
            text = AifaClient._extract_with_pypdf(pdf)
        return AifaClient._clean_pdf_text(text)

    @staticmethod
    def _extract_with_pypdf(pdf: Path) -> str:
        try:
            from pypdf import PdfReader
            return "\n\n".join(page.extract_text() or "" for page in PdfReader(pdf).pages)
        except Exception as exc:
            raise AifaError(f"No se pudo extraer texto de {pdf.name}: {exc}") from exc

    @staticmethod
    def _clean_pdf_text(text: str) -> str:
        # AIFA PDFs carry a diagonal agency watermark. Poppler exposes it as
        # recurring isolated fragments; remove only those complete lines.
        watermark_fragments = {
            "ag", "aco", "rm", "fa", "ita", "na", "lia", "del", "enz",
            "ia", "zia", "en", "el", "ian", "tal", "i", "ai", "ad", "f", "arm",
        }
        cleaned: list[str] = []
        blank = False
        for raw_line in text.replace("\x00", "").splitlines():
            line = raw_line.rstrip()
            if line.strip().casefold() in watermark_fragments:
                continue
            if not line.strip():
                if not blank:
                    cleaned.append("")
                blank = True
                continue
            blank = False
            cleaned.append(line)
        return "\n".join(cleaned).strip()

