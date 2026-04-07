import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from extractors.headers import HeadersExtractor
from extractors.meta import MetaExtractor
from extractors.cookies import CookiesExtractor

import json
import requests
from bs4 import BeautifulSoup
file = open("rules/technologies.json", "r")
ruleset = json.load(file)

hex = HeadersExtractor(ruleset)
mex = MetaExtractor(ruleset)
cex = CookiesExtractor(ruleset)


response = requests.get("https://gigfinder-nine.vercel.app/signin")
soup = BeautifulSoup(response.text, 'html.parser')



print(hex.extract(response=response,soup=soup))
print(mex.extract(response=response,soup=soup))
print(cex.extract(response=response,soup=soup))
