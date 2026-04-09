from extractors.base import *

class TextExtractor(BaseExtractor):
    def __init__(self, ruleset):
        self.name = "text"
        super().__init__(ruleset)

    def extract(self, response, soup):
        technologies = {}
        text = soup.get_text(separator=" ", strip=True)
        for technology, fingerprints in self.ruleset.items():
            for p in self.normalize_patterns(fingerprints.get("text", [])):
                if self.safe_search(p, text):
                    self.register_match(technologies, technology, p, p)
                    break
        return technologies
