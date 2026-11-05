#!/usr/bin/env python3
import json
import pathlib
import re
import subprocess
import sys

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
HOME_DIR = pathlib.Path.home()
REGISTRY_PATH = BASE_DIR / "finance-tax-engine" / "stripe_payment_links_registry.json"

LIVE_SKU_LINKS = {
    "PPHX-SIP-TRUNK": "https://buy.stripe.com/28Edr9a5I8ek96v8n8cjS0z",
    "PPHX-TCPA-SAFE": "https://buy.stripe.com/5kQ7sL7XAamsgyXavgcjS0A",
    "PPHX-CARRIER-CPS": "https://buy.stripe.com/cNibJ1elYdyE1E35aWcjS0B",
    "PPHX-SBC-PEER": "https://buy.stripe.com/9B67sLa5I52896vdHscjS0C",
    "4PHX-E911-DID": "https://buy.stripe.com/9B67sL5PsdyE4Qf1YKcjS0D",
    "4PHX-UCAAS-BIZ": "https://buy.stripe.com/7sY7sLfq2gK0beD320cjS0E",
    "4PHX-OMNI-AI": "https://buy.stripe.com/dRm28ra5IeCiciHcDocjS0F",
    "4PHX-PBX-ENT50": "https://buy.stripe.com/aFa5kD0v89iogyXfPAcjS0G",
    "AIC-LLM-GW": "https://buy.stripe.com/8x24gzgu6fGM3Mb6f0cjS0H",
    "ATRX-PAAS-NODE": "https://buy.stripe.com/bJeaEXdhUgK082r5aWcjS0I",
    "AIS3D-H100-C2PA": "https://buy.stripe.com/14A9ATa5I528dmL9rccjS0J",
    "S1979-IP-LIC": "https://buy.stripe.com/aFaeVdcdQ5280zZ6f0cjS0K"
}

PORTAL_FALLBACK_URL = "https://buy.stripe.com/5kQ7sL7XAamsgyXavgcjS0A"

ROUTER_SNIPPET = (
    "<script id=\"s1979-stripe-live-router\">"
    f"window.S1979_LIVE_LINKS={json.dumps(LIVE_SKU_LINKS)};"
    "document.addEventListener('click',function(e){"
    "var b=e.target.closest('button,a');"
    "if(!b)return;"
    "var t=(b.innerText||b.textContent||'').trim();"
    "if(t.indexOf('Activar SKU')!==-1||t.indexOf('Checkout')!==-1||t.indexOf('Abrir Portal Fiscal Stripe')!==-1){"
    "var s=document.querySelector('select');"
    "var sv=s?(s.value||s.options[s.selectedIndex].text||''):'';"
    "var bt=document.body.innerText||'';"
    "for(var k in window.S1979_LIVE_LINKS){"
    "if(sv.indexOf(k)!==-1||bt.indexOf(k+' [VERIFIED]')!==-1){"
    "e.preventDefault();e.stopPropagation();window.location.href=window.S1979_LIVE_LINKS[k];return;"
    "}}"
    "var h=window.location.hostname.toLowerCase();"
    "if(h.indexOf('prophonix')!==-1){e.preventDefault();window.location.href=window.S1979_LIVE_LINKS['PPHX-TCPA-SAFE'];return;}"
    "if(h.indexOf('fourphonix')!==-1){e.preventDefault();window.location.href=window.S1979_LIVE_LINKS['4PHX-UCAAS-BIZ'];return;}"
    "if(h.indexOf('auraintelcore')!==-1){e.preventDefault();window.location.href=window.S1979_LIVE_LINKS['AIC-LLM-GW'];return;}"
    "if(h.indexOf('auratetrax')!==-1){e.preventDefault();window.location.href=window.S1979_LIVE_LINKS['ATRX-PAAS-NODE'];return;}"
    "if(h.indexOf('auraintelstudios3d')!==-1){e.preventDefault();window.location.href=window.S1979_LIVE_LINKS['AIS3D-H100-C2PA'];return;}"
    "e.preventDefault();window.location.href=window.S1979_LIVE_LINKS['S1979-IP-LIC'];"
    "}},true);"
    "</script>"
)

def main() -> int:
    patched_files = []
    for root in [BASE_DIR, HOME_DIR]:
        for path in root.rglob("*"):
            if ".git" in path.parts or not path.is_file():
                continue
            if path.name in {"wire_live_stripe_to_workers.py", "sync_live_stripe_production.py", "find_valid_live_key_and_sync.py", "bind_stripe_buttons_and_links.py", "sync_existing_stripe_catalog.py", "provision_stripe_live_links.py"}:
                continue
            try:
                if path.stat().st_size > 2_000_000:
                    continue
                txt = path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            if ("Activar SKU" in txt or "bpc_1UWnOzFE1PknNS53wBZloc6n" in txt or "buy.stripe.com/" in txt) and "</body>" in txt:
                new_txt = re.sub(r'<script id="s1979-stripe-live-router">.*?</script>', '', txt, flags=re.DOTALL)
                for sku, url in LIVE_SKU_LINKS.items():
                    new_txt = re.sub(rf'("{sku}"[^}}]*?"url"\s*:\s*")https://buy\.stripe\.com/[A-Za-z0-9_]+(")', rf'\g<1>{url}\g<2>', new_txt)
                new_txt = new_txt.replace("</body>", ROUTER_SNIPPET + "</body>")
                if new_txt != txt:
                    path.write_text(new_txt, encoding="utf-8")
                    patched_files.append(str(path))
                    print(f"  [INYECTADO EN CODIGO WEB/WORKER] {path}")

    print(f"[*] Total de archivos de interfaz/worker actualizados: {len(patched_files)}")

    # Buscar si existe un script de despliegue a Cloudflare Workers/Pages en el entorno
    for candidate in sorted(HOME_DIR.glob("*cloudflare*.sh")) + sorted(HOME_DIR.glob("*deploy*.sh")) + sorted(BASE_DIR.rglob("*cloudflare*.py")) + sorted(BASE_DIR.rglob("*cloudflare*.sh")):
        if ".git" in candidate.parts:
            continue
        print(f"  [SCRIPT CLOUDFLARE DETECTADO] {candidate}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
