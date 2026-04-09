from extractors.base import *

class HtmlExtractor(BaseExtractor):
    def __init__(self, ruleset):
        self.name = "html"
        super().__init__(ruleset)

    def extract(self, response, soup):
        technologies = {}
        html = response.text
        for technology, fingerprints in self.ruleset.items():
            for p in self.normalize_patterns(fingerprints.get("html", [])):
                if self.safe_search(p, html):
                    self.register_match(technologies, technology, p, p)
                    break
        return technologies
