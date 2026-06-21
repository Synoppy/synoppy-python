"""Official Python SDK for the Synoppy web-data API.

One key for scrape, screenshot, crawl, map, extract, classify, enrich,
and images. Every successful response includes ``creditsUsed`` and
``creditsRemaining`` so you can track metered usage.
"""
from __future__ import annotations

import json as _json
from typing import Any, Dict, List, Optional, Union

import requests

__version__ = "1.0.0"
DEFAULT_BASE_URL = "https://synoppy.com"


class SynoppyError(Exception):
    """Raised when the API returns an error response."""

    def __init__(self, message: str, code: str, status: int) -> None:
        super().__init__(message)
        self.code = code
        self.status = status


class Synoppy:
    """Synoppy API client.

    Example:
        >>> from synoppy import Synoppy
        >>> client = Synoppy(api_key="syn_live_...")
        >>> page = client.read("https://stripe.com/blog", formats=["markdown"])
        >>> print(page["markdown"])
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 60.0,
    ) -> None:
        if not api_key:
            raise ValueError("Synoppy: api_key is required")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": "Bearer " + api_key,
                "Content-Type": "application/json",
                "User-Agent": "synoppy-python/" + __version__,
            }
        )

    def _request(self, path: str, body: Dict[str, Any]) -> Dict[str, Any]:
        resp = self._session.post(
            self.base_url + path, data=_json.dumps(body), timeout=self.timeout
        )
        try:
            data = resp.json()
        except ValueError:
            data = {}
        if not resp.ok or data.get("success") is False:
            raise SynoppyError(
                data.get("error", "HTTP %s" % resp.status_code),
                data.get("code", "ERROR"),
                resp.status_code,
            )
        return data

    # --- Endpoints -----------------------------------------------------------

    def read(
        self,
        url: str,
        formats: Optional[List[str]] = None,
        only_main_content: Optional[bool] = None,
        timeout_ms: Optional[int] = None,
        render: Optional[Union[bool, str]] = None,
        wait_ms: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Read a URL → clean markdown / HTML / text.

        ``render`` may be ``True``/``False`` or ``"auto"`` to control JS
        rendering; ``wait_ms`` adds a settle delay before capture. The
        response includes ``metadata`` (title, description, language,
        siteName, author, ogImage, sourceUrl, statusCode, wordCount,
        fetchedAt, rendered, bytesIn), the requested ``markdown``/``html``/
        ``text``, ``renderMs``, ``latencyMs``, ``creditsUsed``, and
        ``creditsRemaining``.
        """
        body: Dict[str, Any] = {"url": url}
        if formats is not None:
            body["formats"] = formats
        if only_main_content is not None:
            body["onlyMainContent"] = only_main_content
        if timeout_ms is not None:
            body["timeoutMs"] = timeout_ms
        if render is not None:
            body["render"] = render
        if wait_ms is not None:
            body["waitMs"] = wait_ms
        return self._request("/api/scrape", body)

    scrape = read

    def screenshot(
        self,
        url: str,
        full_page: Optional[bool] = None,
        wait_ms: Optional[int] = None,
        timeout_ms: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Capture a PNG screenshot of a URL.

        Returns ``screenshot`` (a PNG data URL) alongside ``sourceUrl``,
        ``statusCode``, ``fullPage``, ``latencyMs``, ``creditsUsed``, and
        ``creditsRemaining``. Raises :class:`SynoppyError` with code
        ``RENDER_UNAVAILABLE`` (status 503) if rendering is unavailable.
        """
        body: Dict[str, Any] = {"url": url}
        if full_page is not None:
            body["fullPage"] = full_page
        if wait_ms is not None:
            body["waitMs"] = wait_ms
        if timeout_ms is not None:
            body["timeoutMs"] = timeout_ms
        return self._request("/api/screenshot", body)

    def crawl(self, url: str, limit: Optional[int] = None) -> Dict[str, Any]:
        """Crawl a site → one clean page per URL discovered (requires a key)."""
        body: Dict[str, Any] = {"url": url}
        if limit is not None:
            body["limit"] = limit
        return self._request("/api/crawl", body)

    def map(self, url: str) -> Dict[str, Any]:
        """Discover every URL on a domain."""
        return self._request("/api/map", {"url": url})

    sitemap = map

    def extract(
        self,
        url: str,
        prompt: Optional[str] = None,
        instruction: Optional[str] = None,
    ) -> Dict[str, Any]:
        """AI-structured JSON extraction (requires a key).

        ``instruction`` is an alias for ``prompt``. The response includes
        ``data``, ``model``, ``metadata``, ``truncated``,
        ``usage`` (``inputTokens``/``outputTokens``), ``latencyMs``,
        ``creditsUsed``, and ``creditsRemaining``.
        """
        body: Dict[str, Any] = {"url": url}
        if prompt is None:
            prompt = instruction
        if prompt is not None:
            body["prompt"] = prompt
        return self._request("/api/extract", body)

    def classify(self, url: str, labels: Optional[List[str]] = None) -> Dict[str, Any]:
        """Classify a company by industry, or your own labels (requires a key).

        Without ``labels``, ``data`` holds the NAICS/SIC industry profile
        (``industry``, ``naics_code``, ``naics_title``, ``naics_sector``,
        ``naics_sector_title``, ``naics_valid``, ``sic_code``,
        ``sic_title``, ``sic_division``, ``sic_division_title``,
        ``sic_valid``, ``categories``, ``confidence``). With ``labels``,
        ``data`` holds ``label``, ``matched``, ``confidence``, and
        ``reasoning``. Both modes include ``creditsUsed`` and
        ``creditsRemaining``.
        """
        body: Dict[str, Any] = {"url": url}
        if labels is not None:
            body["labels"] = labels
        return self._request("/api/classify", body)

    def enrich(
        self,
        url: Optional[str] = None,
        *,
        domain: Optional[str] = None,
        email: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Resolve a brand profile from a URL, domain, or work email.

        Pass exactly one of ``url``, ``domain``, or ``email`` (a work email
        is mapped to its domain server-side). The response includes
        ``name``, ``description``, ``logo``, ``colors``, ``fonts``,
        ``address``, ``socials`` (``label``/``url``), ``bytesIn``,
        ``latencyMs``, ``creditsUsed``, and ``creditsRemaining``.
        """
        body: Dict[str, Any] = {}
        if url is not None:
            body["url"] = url
        if domain is not None:
            body["domain"] = domain
        if email is not None:
            body["email"] = email
        if not body:
            raise ValueError(
                "Synoppy.enrich: one of url, domain, or email is required"
            )
        return self._request("/api/brand", body)

    brand = enrich

    def images(self, url: str) -> Dict[str, Any]:
        """Pull every image off a page.

        Returns ``url``, ``count``, ``images`` (each with ``src``, ``alt``,
        ``width``, ``height``), ``bytesIn``, ``latencyMs``, ``creditsUsed``,
        and ``creditsRemaining``.
        """
        return self._request("/api/images", {"url": url})

    # --- Coming soon ---------------------------------------------------------
    # /api/act is not live yet. It is intentionally not implemented; calling
    # it raises a clear error rather than hitting an endpoint that does not
    # exist.

    def act(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Agentic browser actions — coming soon (not yet live)."""
        raise NotImplementedError(
            "Synoppy.act is coming soon; /api/act is not live yet."
        )


__all__ = ["Synoppy", "SynoppyError", "__version__"]
