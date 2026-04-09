from extractors.base import *

class XhrExtractor(BaseExtractor):
    def __init__(self, ruleset):
        self.name = "xhr"
        super().__init__(ruleset)

    def extract(self, response, soup):
        technologies = {}
        script_blocks = [tag.get_text() for tag in soup.find_all("script") if not tag.get("src")]
        if not script_blocks:
            return technologies
        js_text = "\n".join(script_blocks)

        for technology, fingerprints in self.ruleset.items():
            for p in self.normalize_patterns(fingerprints.get("xhr", [])):
                if p and self.safe_search(p, js_text):
                    self.register_match(technologies, technology, p, p)
                    break
        return technologies
