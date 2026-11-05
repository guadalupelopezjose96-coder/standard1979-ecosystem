#!/usr/bin/env python3
"""
Standard 1979 Holdings, LLC - Deterministic Brand & Logo Generator
Standards: SVG Tiny-PS (BIMI), DMCA 17 USC 1202 CMI, WCAG 2.2 AAA, C2PA v2.1
"""
import hashlib, json, pathlib

DOMAINS = [
    ("standard1979.com", "Standard 1979 Holdings, LLC", "S1979", "#0A192F", "#D4AF37", "0.00"),
    ("AuraIntelCore.com", "Aura Technologies Operating, LLC", "AIC", "#0F172A", "#38BDF8", "0.15"),
    ("AuraTetrax.com", "Aura Technologies Operating, LLC", "ATX", "#111827", "#818CF8", "0.15"),
    ("AuraIntelStudios3D.com", "Aura Technologies Operating, LLC", "A3D", "#1E1B4B", "#C084FC", "0.15"),
    ("fourphonix.com", "Phonix Communications Operating, LLC", "4PX", "#064E3B", "#34D399", "0.10"),
    ("prophonix.com", "Phonix Communications Operating, LLC", "PPX", "#042F2E", "#2DD4BF", "0.10"),
]

BASE = pathlib.Path(__file__).resolve().parent.parent / "assets"
BASE.mkdir(parents=True, exist_ok=True)
manifest = {"copyright_owner": "Standard 1979 Holdings, LLC", "statute": "17 U.S.C. 1202 & Lanham Act", "domains": {}}

for dom, entity, code, bg, fg, royalty in DOMAINS:
    d_dir = BASE / dom
    d_dir.mkdir(parents=True, exist_ok=True)
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" version="1.2" baseProfile="tiny-ps" viewBox="0 0 1000 1000" width="1000" height="1000">
  <title>{dom} - Official Verified Brand Asset of Standard 1979 Holdings, LLC</title>
  <desc>Copyright (c) 2026 Standard 1979 Holdings, LLC. Licensed to {entity} under IRC Sec 482. CMI Protected under 17 USC 1202.</desc>
  <rect width="1000" height="1000" fill="{bg}"/>
  <circle cx="500" cy="440" r="290" fill="{bg}" stroke="{fg}" stroke-width="28"/>
  <text x="500" y="485" font-family="sans-serif" font-weight="bold" font-size="160" fill="{fg}" text-anchor="middle">{code}</text>
  <text x="500" y="845" font-family="sans-serif" font-weight="bold" font-size="46" fill="#FFFFFF" text-anchor="middle">{dom.upper()}™</text>
  <text x="500" y="910" font-family="sans-serif" font-size="24" fill="{fg}" text-anchor="middle">© 2026 STANDARD 1979 HOLDINGS, LLC</text>
</svg>
'''
    svg_path = d_dir / "bimi-logo.svg"
    svg_path.write_text(svg, encoding="utf-8")
    digest = hashlib.sha256(svg.encode("utf-8")).hexdigest()
    sha3_digest = hashlib.sha3_512(svg.encode("utf-8")).hexdigest()
    manifest["domains"][dom] = {
        "legal_owner": "Standard 1979 Holdings, LLC",
        "operating_licensee": entity,
        "irc_482_royalty_rate": float(royalty),
        "asc_606_classification": "Symbolic IP (Over-Time Recognition)",
        "svg_path": f"assets/{dom}/bimi-logo.svg",
        "sha256": digest,
        "sha3_512_pqc": sha3_digest,
        "sri_integrity": "sha256-" + hashlib.sha256(svg.encode("utf-8")).digest().hex()
    }

(BASE / "brand-cryptographic-ledger.json").write_text(
    json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
)
print("[OK] Generated 6 BIMI/SVG Tiny-PS logos and cryptographic ledger.")
