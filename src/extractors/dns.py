from extractors.base import *
import dns.resolver
from urllib.parse import urlparse

class DnsExtractor(BaseExtractor):
    def __init__(self, ruleset):
        self.name = "dns"
        super().__init__(ruleset)

    def extract(self, response, soup):
        technologies = {}
        hostname = urlparse(response.url).hostname
        if not hostname:
            return technologies

        record_cache = {}
        for technology, fingerprints in self.ruleset.items():
            for record_type, patterns in fingerprints.get("dns", {}).items():
                if record_type not in record_cache:
                    try:
                        answers = dns.resolver.resolve(hostname, record_type)
                        record_cache[record_type] = [str(r) for r in answers]
                    except Exception:
                        record_cache[record_type] = []
                for record in record_cache[record_type]:
                    for p in self.normalize_patterns(patterns):
                        if self.safe_search(p, record):
                            self.register_match(technologies, technology, record, p)
        return technologies
