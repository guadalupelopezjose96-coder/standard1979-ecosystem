import json
from pathlib import Path

DOMAINS = [
    ("standard1979.com", "Standard 1979 Holdings, LLC"),
    ("auraintelcore.com", "Aura Technologies Operating, LLC"),
    ("auratetrax.com", "Aura Technologies Operating, LLC"),
    ("auraintelstudios3d.com", "Aura Technologies Operating, LLC"),
    ("fourphonix.com", "Phonix Communications Operating, LLC"),
    ("prophonix.com", "Phonix Communications Operating, LLC"),
]

BASE_DIR = Path(__file__).resolve().parent / "generated-portals"

for domain, entity in DOMAINS:
    well_known = BASE_DIR / domain / ".well-known"
    well_known.mkdir(parents=True, exist_ok=True)

    # RFC 9116 Mandatory security.txt for SOC 2 & ISO 27001 Vulnerability Disclosure
    security_txt = (
        f"# RFC 9116 Security Disclosure Policy - {domain} ({entity})\n"
        f"Contact: mailto:security-soc@standard1979.com\n"
        f"Contact: https://{domain}/.well-known/security-contact\n"
        f"Expires: 2027-12-31T23:59:59.000Z\n"
        f"Encryption: https://standard1979.com/.well-known/pgp-key.txt\n"
        f"Preferred-Languages: en, es\n"
        f"Canonical: https://{domain}/.well-known/security.txt\n"
        f"Policy: https://standard1979.com/legal/vulnerability-disclosure-policy\n"
    )
    (well_known / "security.txt").write_text(security_txt, encoding="utf-8")

    # Estricta protección de Propiedad Intelectual contra AI Scrapers externos
    robots_txt = (
        f"# Intellectual Property & Anti-AI Scraping Policy for {domain}\n"
        f"# Copyright (c) Standard 1979 Holdings, LLC. All Rights Reserved.\n"
        f"User-agent: GPTBot\nDisallow: /\n\n"
        f"User-agent: ChatGPT-User\nDisallow: /\n\n"
        f"User-agent: CCBot\nDisallow: /\n\n"
        f"User-agent: ClaudeBot\nDisallow: /\n\n"
        f"User-agent: anthropic-ai\nDisallow: /\n\n"
        f"User-agent: Bytespider\nDisallow: /\n\n"
        f"User-agent: Google-Extended\nDisallow: /\n\n"
        f"User-agent: *\nDisallow: /v1/secure-inference\nDisallow: /oauth2/token\n"
    )
    (BASE_DIR / domain / "robots.txt").write_text(robots_txt, encoding="utf-8")

print(f"[OK] Archivos RFC 9116 (security.txt) y Anti-Scraping (robots.txt) generados para los 6 dominios.")
