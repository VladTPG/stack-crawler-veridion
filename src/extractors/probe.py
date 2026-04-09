from extractors.base import *
from urllib.parse import urljoin

class ProbeExtractor(BaseExtractor):
    def __init__(self, ruleset):
        self.name = "probe"
        super().__init__(ruleset)

    def extract(self, response, soup):
        technologies = {}
        base_url = response.url
        for technology, fingerprints in self.ruleset.items():
            for path, pattern in fingerprints.get("probe", {}).items():
                try:
                    r = requests.get(urljoin(base_url, path), timeout=5, verify=False)
                    content = r.text
                except Exception:
                    continue
                for p in self.normalize_patterns(pattern):
                    if not p or self.safe_search(p, content):
                        self.register_match(technologies, technology, path, p)
                        break
        return technologies
