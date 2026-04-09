from extractors.base import *
import re

class JsExtractor(BaseExtractor):
    def __init__(self, ruleset):
        self.name = "js"
        super().__init__(ruleset)

    def extract(self, response, soup):
        technologies = {}
        script_blocks = [tag.get_text() for tag in soup.find_all("script") if not tag.get("src")]
        if not script_blocks:
            return technologies
        js_text = "\n".join(script_blocks)

        for technology, fingerprints in self.ruleset.items():
            js_checks = fingerprints.get("js", {})
            if not isinstance(js_checks, dict):
                continue
            for js_path, pattern in js_checks.items():
                var_name = re.escape(js_path)
                clean_pat = self.clean_regex(pattern) if pattern else None
                try:
                    if clean_pat:
                        m = re.search(rf"{var_name}.*?{clean_pat}", js_text, re.IGNORECASE | re.DOTALL)
                    else:
                        m = re.search(var_name, js_text, re.IGNORECASE)
                except re.error:
                    m = None
                if m:
                    self.register_match(technologies, technology, js_path, pattern or js_path)
                    break
        return technologies
