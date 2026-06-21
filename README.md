# synoppy (Python)

[![PyPI](https://img.shields.io/pypi/v/synoppy.svg)](https://pypi.org/project/synoppy/) [![Python](https://img.shields.io/pypi/pyversions/synoppy.svg)](https://pypi.org/project/synoppy/)

**Give your AI agents the whole web.** Synoppy is the web-data layer for AI agents — one key to **read, crawl, map, extract, classify & enrich** any site, plus screenshots and image scraping. Clean, structured, LLM-ready data, with no scraping stack to run.

[**Get a free key →**](https://synoppy.com/dashboard) · [Docs](https://synoppy.com/docs) · [synoppy.com](https://synoppy.com)

```bash
pip install synoppy
```

## Quickstart

```python
import os
from synoppy import Synoppy

client = Synoppy(api_key=os.environ["SYNOPPY_API_KEY"])

# Read any URL → clean markdown (force JS rendering + settle delay)
page = client.read(
    "https://stripe.com/blog",
    formats=["markdown"],
    render="auto",
    wait_ms=500,
)
print(page["markdown"])
print(page["metadata"]["rendered"], page["metadata"]["bytesIn"])

# Screenshot a URL → PNG data URL
shot = client.screenshot("https://stripe.com", full_page=True)
print(shot["screenshot"][:40], shot["statusCode"])

# Crawl a site
site = client.crawl("https://example.com", limit=25)
print(site["count"], "of", site["discovered"], "pages")

# AI structured extraction (prompt, a.k.a. instruction)
result = client.extract("https://news.ycombinator.com", prompt="Return { title, summary, topics }")
print(result["data"], result["usage"])

# Brand intelligence — from a url, a domain, or a work email
brand = client.enrich(domain="linear.app")
print(brand["colors"], brand["fonts"], brand["socials"])
```

## Credits

Every successful response includes `creditsUsed` (number) and
`creditsRemaining` (number or `None`) so you can track metered usage:

```python
page = client.read("https://stripe.com")
print("used", page["creditsUsed"], "remaining", page["creditsRemaining"])
```

## Methods

| Method | Endpoint | Notes |
| --- | --- | --- |
| `read(url, formats=, only_main_content=, timeout_ms=, render=, wait_ms=)` / `scrape(...)` | `POST /api/scrape` | `render` is `True`/`False`/`"auto"` |
| `screenshot(url, full_page=, wait_ms=, timeout_ms=)` | `POST /api/screenshot` | returns a PNG data URL; can 503 `RENDER_UNAVAILABLE` |
| `crawl(url, limit=)` | `POST /api/crawl` | `limit` 1–25 · requires a key |
| `map(url)` / `sitemap(url)` | `POST /api/map` | |
| `extract(url, prompt=, instruction=)` | `POST /api/extract` | `instruction` aliases `prompt` · AI · requires a key |
| `classify(url, labels=)` | `POST /api/classify` | NAICS/SIC by default, or your own `labels` · AI · requires a key |
| `enrich(url=, domain=, email=)` / `brand(...)` | `POST /api/brand` | pass one of url / domain / work email |
| `images(url)` | `POST /api/images` | |

Every response also carries `creditsUsed` and `creditsRemaining`.

`act()` is **coming soon** — `/api/act` is not live yet, and calling this
method raises `NotImplementedError`.

## Errors

```python
from synoppy import SynoppyError

try:
    client.crawl("https://example.com")
except SynoppyError as err:
    print(err.code, err.status, err)
```

MIT licensed.
