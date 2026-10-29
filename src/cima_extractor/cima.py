"""Small, dependency-free client for the public AEMPS CIMA REST API."""

from __future__ import annotations

import json
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE_URL = "https://cima.aemps.es/cima/rest"
USER_AGENT = "cima-extractor/0.1 (+https://github.com/edujbarrios)"


class CimaError(RuntimeError):
    """Raised when CIMA cannot provide a usable response."""


class CimaClient:
    def __init__(self, cache_dir: Path, timeout: int = 45, retries: int = 3) -> None:
        self.cache_dir = Path(cache_dir)
        self.timeout = timeout
        self.retries = retries
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get(self, endpoint: str, params: dict[str, object]) -> object:
        query = urlencode(sorted(params.items()))
        safe_name = endpoint.strip("/").replace("/", "_") + "__" + query.replace("&", "__").replace("=", "-")
        cache = self.cache_dir / f"{safe_name}.json"
        if cache.exists():
            return json.loads(cache.read_text(encoding="utf-8"))
        url = f"{BASE_URL}/{endpoint}?{query}"
        request = Request(url, headers={"Accept": "application/json", "User-Agent": USER_AGENT})
        last_error: Exception | None = None
        for attempt in range(self.retries):
            try:
                with urlopen(request, timeout=self.timeout) as response:
                    payload = json.loads(response.read().decode("utf-8-sig"))
                cache.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
                return payload
            except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
                last_error = exc
                time.sleep(0.5 * (2**attempt))
        raise CimaError(f"No se pudo consultar {url}: {last_error}")

    def list_medicines(self, atc: str, page: int = 1) -> list[dict]:
        payload = self._get(
            "medicamentos",
            {"atc": atc, "comerc": 1, "autorizados": 1, "pagina": page},
        )
        if isinstance(payload, dict):
            return list(payload.get("resultados", payload.get("medicamentos", [])))
        return list(payload) if isinstance(payload, list) else []

    def medicine(self, registration: str) -> dict:
        payload = self._get("medicamento", {"nregistro": registration})
        if not isinstance(payload, dict):
            raise CimaError(f"Respuesta inesperada para el medicamento {registration}")
        return payload

    def technical_sheet(self, registration: str) -> list[dict]:
        payload = self._get("docSegmentado/contenido/1", {"nregistro": registration})
        if isinstance(payload, dict):
            for key in ("secciones", "resultados"):
                if isinstance(payload.get(key), list):
                    return payload[key]
            return [payload]
        return list(payload) if isinstance(payload, list) else []

