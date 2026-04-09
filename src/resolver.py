from extractors.base import BaseExtractor


class TechnologyResolver(BaseExtractor):
    def __init__(self, extractors, ruleset):
        self.name = ""
        self.extractors = extractors
        self.ruleset = ruleset

    def extract(self, response, soup):
        technologies = {}

        for extractor in self.extractors:
            try:
                technologies.update(extractor.extract(response=response, soup=soup))
            except Exception:
                pass

        self._apply_implies(technologies)
        self._apply_requires(technologies)

        return technologies

    def _apply_implies(self, technologies):
        changed = True
        while changed:
            changed = False
            for tech in list(technologies.keys()):
                fp = self.ruleset.get(tech, {})
                for entry in self.normalize_patterns(fp.get("implies", [])):
                    name = self.clean_regex(entry)
                    confidence = self.get_confidence(entry)
                    if name and name not in technologies:
                        technologies[name] = {"confidence": confidence, "matched_implies": tech}
                        changed = True

    def _apply_requires(self, technologies):
        for tech in list(technologies.keys()):
            fp = self.ruleset.get(tech, {})
            for entry in self.normalize_patterns(fp.get("requires", [])):
                name = self.clean_regex(entry)
                if name and name not in technologies:
                    technologies.pop(tech, None)
                    break
