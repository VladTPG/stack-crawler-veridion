from extractors.base import *

class UrlExtractor(BaseExtractor):
    def __init__(self, ruleset):
        self.name = "url"
        super().__init__(ruleset)

    def extract(self, response, soup):
        technologies = {}
        url = response.url
        for technology, fingerprints in self.ruleset.items():
            for p in self.normalize_patterns(fingerprints.get("url", [])):
                if self.safe_search(p, url):
                    self.register_match(technologies, technology, url, p)
                    break
        return technologies
