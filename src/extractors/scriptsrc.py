from extractors.base import *

class ScriptSrcExtractor(BaseExtractor):
    def __init__(self, ruleset):
        self.name = "src"
        super().__init__(ruleset)

    def extract(self, response, soup):
        technologies = {}
        script_tags = soup.find_all("script")
        for technology, fingerprints in self.ruleset.items():
            patterns = self.normalize_patterns(fingerprints.get("scriptSrc",[]))
            for p in patterns:
                for tag in script_tags:
                    src = tag.get("src")
                    if src and self.safe_search(self.clean_regex(p),src):
                        self.register_match(technologies=technologies,technology=technology,matches=src,pattern=p)
                        break


        return technologies