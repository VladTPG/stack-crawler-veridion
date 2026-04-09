from extractors.base import *
import ssl
import socket
from urllib.parse import urlparse

class CertIssuerExtractor(BaseExtractor):
    def __init__(self, ruleset):
        self.name = "certIssuer"
        super().__init__(ruleset)

    def extract(self, response, soup):
        technologies = {}
        parsed = urlparse(response.url)
        if parsed.scheme != "https":
            return technologies
        hostname = parsed.hostname
        port = parsed.port or 443
        try:
            context = ssl.create_default_context()
            with socket.create_connection((hostname, port), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
            issuer = dict(x[0] for x in cert.get("issuer", []))
            issuer_org = issuer.get("organizationName", "")
        except Exception:
            return technologies
        for technology, fingerprints in self.ruleset.items():
            for p in self.normalize_patterns(fingerprints.get("certIssuer", [])):
                if self.safe_search(p, issuer_org):
                    self.register_match(technologies, technology, issuer_org, p)
                    break
        return technologies
