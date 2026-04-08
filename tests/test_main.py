import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from extractors.headers import HeadersExtractor
from extractors.meta import MetaExtractor
from extractors.cookies import CookiesExtractor
from extractors.dom import DomExtractor
from extractors.script import ScriptExtractor
from extractors.scriptsrc import ScriptSrcExtractor


import json
import requests
from bs4 import BeautifulSoup
file = open("rules/technologies.json", "r")
ruleset = json.load(file)

hex = HeadersExtractor(ruleset)
mex = MetaExtractor(ruleset)
cex = CookiesExtractor(ruleset)
domex = DomExtractor(ruleset)
script = ScriptExtractor(ruleset)
src = ScriptSrcExtractor(ruleset)


response = requests.get("https://tfm.ro")
soup = BeautifulSoup(response.text, 'html.parser')



print(hex.extract(response=response,soup=soup))
print(mex.extract(response=response,soup=soup))
print(cex.extract(response=response,soup=soup))
print(domex.extract(response=response,soup=soup))
print(script.extract(response=response,soup=soup))
print(src.extract(response=response,soup=soup))