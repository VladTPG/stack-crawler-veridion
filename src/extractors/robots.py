from extractors.base import *
from urllib.parse import urljoin

class RobotsExtractor(BaseExtractor):
    def __init__(self, ruleset):
        self.name = "robots"
        super().__init__(ruleset)

    def extract(self, response, soup):
        technologies = {}
        try:
            r = requests.get(urljoin(response.url, "/robots.txt"), timeout=5, verify=False)
            robots_text = r.text
        except Exception:
            return technologies
        for technology, fingerprints in self.ruleset.items():
            for p in self.normalize_patterns(fingerprints.get("robots", [])):
                if self.safe_search(p, robots_text):
                    self.register_match(technologies, technology, p, p)
                    break
        return technologies
