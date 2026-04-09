from extractors.base import *
from urllib.parse import urljoin

class CssExtractor(BaseExtractor):
    def __init__(self, ruleset):
        self.name = "css"
        super().__init__(ruleset)

    def extract(self, response, soup):
        technologies = {}

        css_blocks = [tag.get_text() for tag in soup.find_all("style")]

        for link in soup.find_all("link", rel=lambda r: r and "stylesheet" in r)[:5]:
            href = link.get("href", "")
            if not href or href.startswith("data:"):
                continue
            try:
                r = requests.get(urljoin(response.url, href), timeout=5, verify=False)
                css_blocks.append(r.text)
            except Exception:
                continue

        if not css_blocks:
            return technologies

        css_text = "\n".join(css_blocks)
        for technology, fingerprints in self.ruleset.items():
            for p in self.normalize_patterns(fingerprints.get("css", [])):
                if self.safe_search(p, css_text):
                    self.register_match(technologies, technology, p, p)
                    break
        return technologies
