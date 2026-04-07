from extractors.base import BaseExtractor
import re

class CookiesExtractor(BaseExtractor):
    def __init__(self, ruleset):
        self.name = "cookies"
        super().__init__(ruleset)

    def extract(self, response, soup):
        cookies = response.cookies
        technologies ={}
        for technology, fingerprints in self.ruleset.items():
            for cookie_name, pattern in fingerprints.get("cookies",{}).items():
                if cookie_name in cookies:
                    pattern = self.normalize_patterns(pattern)
                    for p in pattern:
                        if not p or re.search(pattern=self.clean_regex(p),string=cookies[cookie_name]):
                            self.register_match(technologies=technologies,technology=technology,matches=cookie_name,pattern = self.clean_regex(p))
        return technologies