from extractors.base import *

class MetaExtractor(BaseExtractor):

    def __init__(self, ruleset):
        self.name = "meta"
        super().__init__(ruleset)

    def extract(self, response, soup):
        technologies = {}
        for technology, fingerprints in self.ruleset.items():
            for tag, pattern in fingerprints.get("meta",{}).items():
                metatag = soup.find("meta", attrs={"name": tag}) or soup.find("meta", attrs={"property": tag}) or soup.find("meta", attrs={tag: True})
                if metatag:
                    content = metatag.get("content")
                    pattern = self.normalize_patterns(pattern)
                    for p in pattern:
                        if not p or (content and self.safe_search(pattern=self.clean_regex(p),string=content)):
                            self.register_match(technologies= technologies,technology=technology,matches=tag,pattern=p)
        return technologies