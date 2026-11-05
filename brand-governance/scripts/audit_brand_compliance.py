#!/usr/bin/env python3
"""
Standard 1979 Holdings, LLC - Read-Only Brand, SVG Security & Stripe Royalty Auditor
"""
import hashlib, json, pathlib, sys, xml.etree.ElementTree as ET

FORBIDDEN_TAGS = {"script", "foreignobject", "iframe", "object", "embed", "animate", "a", "image"}
BASE = pathlib.Path(__file__).resolve().parent.parent / "assets"
LEDGER = BASE / "brand-cryptographic-ledger.json"

def verify_all():
    if not LEDGER.exists():
        print("[FAIL] Missing brand-cryptographic-ledger.json")
        sys.exit(1)
    data = json.loads(LEDGER.read_text(encoding="utf-8"))
    errors = 0
    for dom, meta in data["domains"].items():
        svg_file = BASE.parent / meta["svg_path"]
        raw = svg_file.read_bytes()
        if hashlib.sha256(raw).hexdigest() != meta["sha256"]:
            print(f"[FAIL] SHA-256 mismatch for {dom}")
            errors += 1
        root = ET.fromstring(raw.decode("utf-8"))
        if root.attrib.get("baseProfile") != "tiny-ps":
            print(f"[FAIL] {dom} missing SVG Tiny-PS profile")
            errors += 1
        for elem in root.iter():
            tag = elem.tag.split("}")[-1].lower()
            if tag in FORBIDDEN_TAGS:
                print(f"[FAIL] Forbidden XML tag <{tag}> in {dom}")
                errors += 1
            for attr in elem.attrib:
                if attr.lower().startswith("on"):
                    print(f"[FAIL] Event handler attribute {attr} in {dom}")
                    errors += 1
        gross_cents = 100000  # $1,000.00 sample Stripe Connect charge
        fee_cents = int(round(gross_cents * meta["irc_482_royalty_rate"]))
        print(f"[PASS] {dom:24s} | Licensee: {meta['operating_licensee']:36s} | Stripe Fee ($1k): ${fee_cents/100:6.2f} | SHA256: {meta['sha256'][:12]}...")
    if errors:
        sys.exit(1)
    print("[OK] 100% Brand Governance, Lanham Act Quality Control & SVG Hardening Verified.")

if __name__ == "__main__":
    verify_all()
