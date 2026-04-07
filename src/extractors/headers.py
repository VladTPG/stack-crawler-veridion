from extractors.base import BaseExtractor
import re
class HeadersExtractor(BaseExtractor):

    def __init__(self, ruleset):
        self.name = "headers"
        super().__init__(ruleset)

    def extract(self, response, soup):
        headers = response.headers
        technologies ={}
        for technology, fingerprints in self.ruleset.items():
            for header_name, pattern in fingerprints.get("headers",{}).items():
                if header_name in headers:
                    pattern = self.normalize_patterns(pattern)
                    for p in pattern:
                        if not p or re.search(pattern=self.clean_regex(p),string=headers[header_name]):

                            self.register_match(technologies=technologies,technology=technology,matches=header_name,pattern = self.clean_regex(p))

        return technologies