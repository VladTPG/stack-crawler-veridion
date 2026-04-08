from extractors.base import *

class DomExtractor(BaseExtractor):
    def __init__(self, ruleset):
        self.name = "dom_element"
        super().__init__(ruleset)
    def extract(self, response, soup):
        technologies = {}
        handlers = {
            "text": lambda el, p: self.safe_search(p, el.get_text()),
            "exists": lambda el, p: True,
            "src": lambda el, p: self.safe_search(p, el.get("src", "")),
            "class": lambda el, p: self.safe_search(p, " ".join(el.get("class", []))),
            "attributes": lambda el, p: any(
                self.safe_search(pattern, " ".join(el.get(attr, "")) if isinstance(el.get(attr), list) else el.get(attr, ""))
                for attr, pattern in p.items()
            )
        }

        for technology, fingerprints in self.ruleset.items():
            dom = fingerprints.get("dom")
            if not dom:
                continue
            if isinstance(dom,str):
                dom = {dom:{}}

            elif isinstance(dom,list):
                dom = {selector: {} for selector in dom}

            for selector, conditions in dom.items():
                try:
                    elements = soup.select(selector)
                except:
                    continue

                if not elements:
                    continue

                if not conditions:
                    self.register_match(technologies,technology,selector,"")

                for el in elements:
                    for condition_type, pattern in conditions.items():
                        handler = handlers.get(condition_type)
                        if handler and handler(el,pattern):
                            self.register_match(technologies, technology, condition_type, pattern)

        return technologies