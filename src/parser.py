import sys
import os

import json
import requests
import pandas as pd
from bs4 import BeautifulSoup
from concurrent.futures import ProcessPoolExecutor, as_completed

import urllib3
urllib3.disable_warnings()

_resolver = None
_session = None


def _worker_init():
    global _resolver, _session

    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

    from extractors.headers import HeadersExtractor
    from extractors.meta import MetaExtractor
    from extractors.cookies import CookiesExtractor
    from extractors.dom import DomExtractor
    from extractors.script import ScriptExtractor
    from extractors.scriptsrc import ScriptSrcExtractor
    from extractors.url import UrlExtractor
    from extractors.html import HtmlExtractor
    from extractors.text import TextExtractor
    from extractors.css import CssExtractor
    from extractors.js import JsExtractor
    from extractors.xhr import XhrExtractor
    from extractors.robots import RobotsExtractor
    from extractors.probe import ProbeExtractor
    from extractors.certissuer import CertIssuerExtractor
    from extractors.dns import DnsExtractor
    from resolver import TechnologyResolver

    with open("rules/technologies.json") as f:
        ruleset = json.load(f)

    extractors = [
        HeadersExtractor(ruleset),
        MetaExtractor(ruleset),
        CookiesExtractor(ruleset),
        DomExtractor(ruleset),
        ScriptExtractor(ruleset),
        ScriptSrcExtractor(ruleset),
        UrlExtractor(ruleset),
        HtmlExtractor(ruleset),
        TextExtractor(ruleset),
        CssExtractor(ruleset),
        JsExtractor(ruleset),
        XhrExtractor(ruleset),
        RobotsExtractor(ruleset),
        ProbeExtractor(ruleset),
        CertIssuerExtractor(ruleset),
        DnsExtractor(ruleset),
    ]

    _resolver = TechnologyResolver(extractors=extractors, ruleset=ruleset)

    _session = requests.Session()
    _session.verify = False
    _session.max_redirects = 5


def scan(domain):
    for scheme in ("https", "http"):
        try:
            response = _session.get(
                f"{scheme}://{domain}",
                timeout=(5, 10),
                allow_redirects=True,
            )
            soup = BeautifulSoup(response.text, "html.parser")
            technologies = _resolver.extract(response=response, soup=soup)
            return domain, technologies
        except Exception:
            continue
    return domain, {}

import time
if __name__ == "__main__":
    start_time = time.time()
    sites = pd.read_parquet("data/part-00000-66e0628d-2c7f-425a-8f5b-738bcd6bf198-c000.snappy.parquet")
    domains = sites.iloc[:, 0].tolist()

    unique = set()
    total_found = 0
    workers = os.cpu_count()

    output_path = "data/output.jsonl"
    with ProcessPoolExecutor(initializer=_worker_init) as executor, open(output_path, "a", encoding="utf-8") as out_file:
        futures = {executor.submit(scan, domain): domain for domain in domains}
        for i, future in enumerate(as_completed(futures), 1):
            try:
                domain, technologies = future.result()
                unique.update(technologies.keys())
                found = list(technologies.keys())
                total_found += len(found)
                out_file.write(json.dumps({"domain": domain, "technologies": technologies}) + "\n")
                out_file.flush()
                preview = found[:5]
                suffix = "..." if len(found) > 5 else ""
                print(f"[{i:>3}/{len(domains)}] {domain}: {len(found)} techs: {preview}{suffix}", flush=True)
            except Exception as e:
                print(f"[{i:>3}/{len(domains)}] failed: {e}", flush=True)


    print("==================================")
    print(f"Total technologies found: {total_found}")
    print(f"{len(unique)} unique technologies across all sites")
    print(f"Elapsed time: {(time.time() - start_time) / 60:.2f} minutes")