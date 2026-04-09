# Stack Crawler Veridion Assignment

## Tech Stack

- `Python 3.x`
- `requests` — HTTP client
- `beautifulsoup4` — HTML parsing
- `dnspython` — DNS record queries
- `pandas` + `pyarrow` — Parquet input
- `concurrent.futures.ProcessPoolExecutor` — parallel domain scanning

## How It Works

The system is built around a **plugin-based extractor architecture** with a central resolver. Each extractor is responsible for one type of signal, and results from all extractors are combined and resolved into a final technology map per domain.

```
domains (parquet)
      │
      ▼
  parser.py  ──  ProcessPoolExecutor (N workers)
      │
      ▼
  scan(domain)
      │
      ├── HTTP/HTTPS request (HTTPS first, fallback to HTTP)
      │
      ▼
  TechnologyResolver.extract(response, soup)
      │
      ├── HeadersExtractor       ← HTTP response headers
      ├── MetaExtractor          ← <meta> tags
      ├── CookiesExtractor       ← response cookies
      ├── DomExtractor           ← CSS selector matching
      ├── ScriptExtractor        ← inline <script> content
      ├── ScriptSrcExtractor     ← external script src URLs
      ├── UrlExtractor           ← final response URL
      ├── HtmlExtractor          ← raw HTML text
      ├── TextExtractor          ← visible page text
      ├── CssExtractor           ← inline + external stylesheets
      ├── JsExtractor            ← JS variable names/values
      ├── XhrExtractor           ← API endpoint patterns in scripts
      ├── RobotsExtractor        ← /robots.txt content
      ├── ProbeExtractor         ← tech-specific probe endpoints
      ├── CertIssuerExtractor    ← SSL certificate issuer
      └── DnsExtractor           ← DNS records (A, MX, TXT, etc.)
              │
              ▼
      _apply_implies()   ← cascade: detected tech implies others
      _apply_requires()  ← prune: remove techs missing required dependencies
              │
              ▼
      { "Technology": { confidence: 0-100, matched_<signal>: { ... } } }
              │
              ▼
      data/output.jsonl  (one JSON object per line)
```

### Extractors

Each extractor receives the full HTTP response and BeautifulSoup-parsed DOM. They match their signal type against patterns from the ruleset and return a dict of detected technologies with confidence scores and match evidence.

| Extractor             | Signal                                                                        |
| --------------------- | ----------------------------------------------------------------------------- |
| `HeadersExtractor`    | HTTP response header names and values                                         |
| `MetaExtractor`       | HTML `<meta>` tag name/content pairs                                          |
| `CookiesExtractor`    | Response cookie names and values                                              |
| `DomExtractor`        | CSS selectors with optional conditions (text, exists, src, class, attributes) |
| `ScriptExtractor`     | Inline `<script>` tag content                                                 |
| `ScriptSrcExtractor`  | `src` attributes of external script tags                                      |
| `UrlExtractor`        | Final URL after redirects                                                     |
| `HtmlExtractor`       | Full raw HTML response body                                                   |
| `TextExtractor`       | Visible text extracted by BeautifulSoup                                       |
| `CssExtractor`        | Inline `<style>` tags + up to 5 fetched external stylesheets                  |
| `JsExtractor`         | JS variable name existence and/or value patterns                              |
| `XhrExtractor`        | API endpoint and XHR patterns in inline scripts                               |
| `RobotsExtractor`     | Content of `/robots.txt`                                                      |
| `ProbeExtractor`      | Tech-specific URLs (e.g. `/magento_version`)                                  |
| `CertIssuerExtractor` | SSL certificate issuer organization (HTTPS only)                              |
| `DnsExtractor`        | DNS records by type (A, MX, TXT, etc.)                                        |

### Rules Format

The technologies.json file is sourced from https://github.com/s0md3v/wappalyzer-next

Patterns are standard regexes with optional inline metadata:

- `\;confidence:75` — override the default confidence level (0–100)
- `\;version:\1` — extract version string from a capture group

Technologies can declare relationships:

- `implies` — detecting this tech also adds another (e.g. Apache implies PHP)
- `requires` — tech is only kept if another specific tech is also detected
- `excludes` — detecting this tech removes another from results

### Proof of Detection

Every detected technology carries the evidence that triggered it. For example:

```json
{
  "domain": "example.com",
  "technologies": {
    "Apache HTTP Server": {
      "confidence": 100,
      "matched_headers": {
        "Server": "(?:Apache(?:$|/([\\d.]+)|[^/-])|(?:^|\\b)HTTPD)"
      }
    },
    "PHP": {
      "confidence": 100,
      "matched_implies": "Apache HTTP Server"
    },
    "Let's Encrypt": {
      "confidence": 100,
      "matched_certIssuer": {
        "Let's Encrypt": "Let's Encrypt"
      }
    }
  }
}
```

The `matched_<signal>` field maps the exact key (header name, cookie name, DOM selector, etc.) to the pattern that matched it, providing a traceable audit trail for every detection.

---

## Output

Results are written to `data/output.jsonl` in [JSON Lines](https://jsonlines.org/) format — one JSON object per domain, per line. This ensures that a malformed or incomplete entry for one domain does not corrupt the rest of the file.

---

## How to run

```bash
pip install -r requirements.txt
python src/parser.py
```

---

## Debate Topics

### What were the main issues with the current implementation and how would you tackle them?

1. Since I am not using a headless browser to render JavaScript code, Client Side Rendered apps mostly remain undetected. The fix would be implementing a headless browser to process these cases such as Playwright.

2. The ruleset is loaded per worker process at startup which with many CPUs can lead to inefficiencies. Fix: load the ruleset once into shared read-only memory using Python's `multiprocessing.shared_memory`, so all workers reference the same allocation instead of holding separate copies.

3. Some websites (almost all problematic ones were running Wix) are really slow to process in my implementation. Most of the sites (approx 90-95%) only took a few seconds to process but Wix websites in particular could even take up to 5-6 minutes. Fix: enforce a strict per-domain wall-clock timeout (e.g. 30 seconds total) so slow sites are abandoned rather than blocking a worker indefinitely.

### How would you scale this solution for millions of domains crawled in a timely manner (1–2 months)?

1. Move from ProcessPoolExecutor on a single machine to a Distributed Message Queue (like RabbitMQ) where workers become stateless Docker containers (horizontally scaling); each worker pulls a domain from a queue, scans it, writes the result, and then acknowledges to the queue. For storage, a partitioned data lake (e.g. S3 + Parquet) is a more natural fit than a relational database since results are append-only and the access pattern is bulk analytical reads rather than row-level updates. Implement a Dead Letter Queue for sites that fail, and a timeout that grows progressively to accommodate slow websites.

2. Implement logging to track current queue position, error rate and hit rates to detect infrastructure issues early

3. Implement unit tests and CI/CD pipeline to ensure that modifying one part the algorithm or adding something new doesn't break the program

### How would you discover new technologies in the future?

1. Monitor the GitHub repo mentioned above for changes in the technology fingerprints; when new fingerprints are added, automatically re-scan a set of known sites to validate that the new patterns match correctly and don't introduce false positives.

2. If new methods arise besides the implemented extractors I can create a new extractor by deriving the BaseExtractor class
