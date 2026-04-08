from extractors.base import *

class ScriptExtractor(BaseExtractor):
    def __init__(self, ruleset):
        self.name = "script"
        super().__init__(ruleset)

    def extract(self, response, soup):
        technologies = {}

        script_tags = soup.find_all("script")
        for technology, fingerprints in self.ruleset.items():
            patterns = self.normalize_patterns(fingerprints.get("scripts",[]))
            for p in patterns:
                for tag in script_tags:
                    text = tag.get_text()
                    if text and self.safe_search(self.clean_regex(p),text):
                        self.register_match(technologies=technologies,technology=technology,matches=p,pattern=p)

        return technologies