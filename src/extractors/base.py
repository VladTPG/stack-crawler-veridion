from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup

class BaseExtractor(ABC):
    def __init__(self,ruleset):
        self.ruleset = ruleset
    def clean_regex(self, regex):
        return regex.split("\\;")[0]

    def get_confidence(self,regex):
        confidence = 100
        if "confidence" in regex:
            for option in regex.split("\\;"):
                if "confidence" in option:
                    confidence = int(option.split(":")[1])
        return confidence

    def register_match(self,technologies,technology, matches, pattern):
        confidence = self.get_confidence(pattern)
        matched_keyword = "matched_" + self.name
        if technology not in technologies:
            technologies[technology] = {
                "confidence": 0,
                matched_keyword: {}
            }

        technologies[technology][matched_keyword][matches] = pattern
        technologies[technology]["confidence"] += confidence

        if technologies[technology]["confidence"] > 100:
            technologies[technology]["confidence"] = 100

    def normalize_patterns(self, pattern):
        return [pattern] if isinstance(pattern, str) else pattern

    @abstractmethod
    def extract(self, response : requests.Response, soup: BeautifulSoup):
        pass