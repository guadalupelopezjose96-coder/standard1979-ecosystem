#!/usr/bin/env python3
import json
import os
import pathlib
import re
import sys
import urllib.parse
import urllib.request

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
HOME_DIR = pathlib.Path.home()
REGISTRY_PATH = BASE_DIR / "finance-tax-engine" / "stripe_payment_links_registry.json"
PRIMARY_ACCOUNT_ID = "acct_1TGvtcFE1PknNS53"
PORTAL_CONFIG_ID = "bpc_1UWnOzFE1PknNS53wBZloc6n"
LIVE_PUBLISHABLE_KEY = "pk_live_51TGvtcFE1PknNS53eGNgg6EJvR9hvp9gx0cV7Bb91IGkvlnHsxWngDQN0MEkXJaAbgNWR4qmxPdz5Jg8b22rtRt900uN6UCpEs"

CATALOG = [
    {"sku": "PPHX-SIP-TRUNK", "domain": "prophonix.com", "name": "Wholesale Carrier SIP Trunk (PPHX-SIP-TRUNK)", "usd": 19900, "opco": "Phonix Communications Operating, LLC", "royalty_pct": "10%"},
    {"sku": "PPHX-TCPA-SAFE", "domain": "prophonix.com", "name": "Carrier Compliance Dialer TCPA/FTSA (PPHX-TCPA-SAFE)", "usd": 79900, "opco": "Phonix Communications Operating, LLC", "royalty_pct": "10%"},
    {"sku": "PPHX-CARRIER-CPS", "domain": "prophonix.com", "name": "High-CPS Interconnect 100+ (PPHX-CARRIER-CPS)", "usd": 245000, "opco": "Phonix Communications Operating, LLC", "royalty_pct": "10%"},
    {"sku": "PPHX-SBC-PEER", "domain": "prophonix.com", "name": "Global Carrier SBC Peering BGP Anycast (PPHX-SBC-PEER)", "usd": 490000, "opco": "Phonix Communications Operating, LLC", "royalty_pct": "10%"},
    {"sku": "4PHX-E911-DID", "domain": "fourphonix.com", "name": "Nationwide DID + E911 Pack (4PHX-E911-DID)", "usd": 9900, "opco": "Phonix Communications Operating, LLC", "royalty_pct": "10%"},
    {"sku": "4PHX-UCAAS-BIZ", "domain": "fourphonix.com", "name": "Enterprise UCaaS Cloud PBX (4PHX-UCAAS-BIZ)", "usd": 24900, "opco": "Phonix Communications Operating, LLC", "royalty_pct": "10%"},
    {"sku": "4PHX-OMNI-AI", "domain": "fourphonix.com", "name": "Omnichannel 10DLC + AI Voice (4PHX-OMNI-AI)", "usd": 39900, "opco": "Phonix Communications Operating, LLC", "royalty_pct": "10%"},
    {"sku": "4PHX-PBX-ENT50", "domain": "fourphonix.com", "name": "Multi-Site PBX Cluster 50 Seats (4PHX-PBX-ENT50)", "usd": 125000, "opco": "Phonix Communications Operating, LLC", "royalty_pct": "10%"},
    {"sku": "AIC-LLM-GW", "domain": "AuraIntelCore.com", "name": "Enterprise OIDC SSO + vLLM Gateway (AIC-LLM-GW)", "usd": 49900, "opco": "Aura Technologies Operating, LLC", "royalty_pct": "15%"},
    {"sku": "ATRX-PAAS-NODE", "domain": "AuraTetrax.com", "name": "Modular Agentic PaaS Cluster (ATRX-PAAS-NODE)", "usd": 89900, "opco": "Aura Technologies Operating, LLC", "royalty_pct": "15%"},
    {"sku": "AIS3D-H100-C2PA", "domain": "AuraIntelStudios3D.com", "name": "NVIDIA H100 3D Generative C2PA Studio (AIS3D-H100-C2PA)", "usd": 149000, "opco": "Aura Technologies Operating, LLC", "royalty_pct": "15%"},
    {"sku": "S1979-IP-LIC", "domain": "standard1979.com", "name": "Standard 1979 Master IP & Compliance License (S1979-IP-LIC)", "usd": 250000, "opco": "Standard 1979 Holdings, LLC", "royalty_pct": "100%"}
]

def discover_live_key() -> str:
    env_key = os.environ.get("STRIPE_LIVE_KEY", "") or os.environ.get("STRIPE_SECRET_KEY", "")
    if env_key.startswith("sk_live_") or env_key.startswith("rk_live_"):
        return env_key.strip()
    pattern = re.compile(r"\b(sk_live_51TGvtcFE1PknNS53[A-Za-z0-9]+)\b")
    for search_root in [BASE_DIR, HOME_DIR]:
        for path in search_root.rglob("*"):
            if ".git" in path.parts or not path.is_file():
                continue
            try:
                if path.stat().st_size > 2_000_000:
                    continue
                txt = path.read_text(encoding="utf-8", errors="ignore")
                m = pattern.search(txt)
                if m:
                    return m.group(1)
            except Exception:
                continue
    return ""

def stripe_get(endpoint: str, api_key: str) -> dict:
    url = f"https://api.stripe.com/v1/{endpoint}"
    req = urllib.request.Request(url, method="GET")
    req.add_header("Authorization", f"Bearer {api_key}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))

def stripe_post(endpoint: str, data: dict, api_key: str) -> dict:
    url = f"https://api.stripe.com/v1/{endpoint}"
    encoded = urllib.parse.urlencode(data).encode("utf-8")
    req = urllib.request.Request(url, data=encoded, method="POST")
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))

def patch_all_web_files(sku_to_url: dict, portal_url: str) -> int:
    patched = 0
    js_router = (
        "\n<script id=\"s1979-stripe-live-router\">\n"
        f"window.S1979_STRIPE_LINKS = {json.dumps(sku_to_url)};\n"
        f"window.S1979_PORTAL_URL = {json.dumps(portal_url)};\n"
        "document.addEventListener('click', function(e) {\n"
        "  const btn = e.target.closest('button, a');\n"
        "  if (!btn) return;\n"
        "  const txt = (btn.innerText || btn.textContent || '').trim();\n"
        "  if (txt.includes('Activar SKU') || txt.includes('Checkout')) {\n"
        "    const sel = document.querySelector('select');\n"
        "    const bodyTxt = document.body.innerText || '';\n"
        "    for (const [sku, url] of Object.entries(window.S1979_STRIPE_LINKS)) {\n"
        "      if ((sel && sel.value && sel.value.includes(sku)) || bodyTxt.includes(sku + ' [VERIFIED]')) {\n"
        "        e.preventDefault();\n"
        "        window.location.assign(url);\n"
        "        return;\n"
        "      }\n"
        "    }\n"
        "    const fallback = Object.values(window.S1979_STRIPE_LINKS)[0];\n"
        "    if (fallback) { e.preventDefault(); window.location.assign(fallback); }\n"
        "  } else if (txt.includes('Abrir Portal Fiscal Stripe')) {\n"
        "    e.preventDefault();\n"
        "    window.location.assign(window.S1979_PORTAL_URL);\n"
        "  }\n"
        "}, true);\n"
        "</script>\n"
    )
    for root_dir in [BASE_DIR, HOME_DIR]:
        for html_file in root_dir.rglob("*.html"):
            if ".git" in html_file.parts or "node_modules" in html_file.parts:
                continue
            try:
                content = html_file.read_text(encoding="utf-8")
                if "Activar SKU" not in content and "bpc_1UWnOzFE1PknNS53wBZloc6n" not in content:
                    continue
                content = re.sub(r'<script id="s1979-stripe-live-router">.*?</script>\s*', '', content, flags=re.DOTALL)
                if "</body>" in content:
                    content = content.replace("</body>", js_router + "</body>")
                    html_file.write_text(content, encoding="utf-8")
                    patched += 1
                    print(f"  [HTML ACTUALIZADO] {html_file}")
            except Exception:
                continue
    return patched

def main() -> int:
    api_key = discover_live_key()
    if not api_key:
        print("[AVISO] No se encontró sk_live_... en archivos locales.")
        print("Para sincronizar en Modo Vivo: en Firefox haz clic en '+ Crear clave secreta' o en 'Revelar clave activa' (Clave restringida) y ejecuta:")
        print("export STRIPE_LIVE_KEY='sk_live_...' && python3 finance-tax-engine/sync_live_stripe_production.py")
        return 0

    print(f"[*] Clave LIVE detectada ({api_key[:16]}...{api_key[-4:]}). Sincronizando catálogo LIVE de {PRIMARY_ACCOUNT_ID}...")
    plinks_resp = stripe_get("payment_links?limit=100&active=true", api_key)
    prices_resp = stripe_get("prices?limit=100&active=true&expand[]=data.product", api_key)

    sku_to_url = {}
    for pl in plinks_resp.get("data", []):
        meta_sku = pl.get("metadata", {}).get("sku", "")
        if meta_sku:
            sku_to_url[meta_sku] = pl["url"]

    existing_prices_by_sku = {}
    for price in prices_resp.get("data", []):
        prod = price.get("product", {})
        if not isinstance(prod, dict):
            continue
        prod_name = prod.get("name", "")
        meta_sku = prod.get("metadata", {}).get("sku", "") or price.get("metadata", {}).get("sku", "")
        for item in CATALOG:
            if meta_sku == item["sku"] or item["sku"].lower() in prod_name.lower() or item["name"].lower() in prod_name.lower():
                existing_prices_by_sku[item["sku"]] = price["id"]

    for item in CATALOG:
        sku = item["sku"]
        if sku in sku_to_url:
            print(f"  [LIVE ACTIVO] {sku} ({item['domain']}) -> {sku_to_url[sku]}")
            continue

        price_id = existing_prices_by_sku.get(sku)
        if not price_id:
            prod = stripe_post("products", {
                "name": item["name"],
                "metadata[sku]": sku,
                "metadata[domain]": item["domain"],
                "metadata[operating_entity]": item["opco"],
                "metadata[irc_482_royalty]": item["royalty_pct"],
                "metadata[holding_beneficiary]": "Standard 1979 Holdings, LLC"
            }, api_key)
            price = stripe_post("prices", {
                "product": prod["id"],
                "unit_amount": str(item["usd"]),
                "currency": "usd",
                "recurring[interval]": "month",
                "metadata[sku]": sku
            }, api_key)
            price_id = price["id"]

        pl = stripe_post("payment_links", {
            "line_items[0][price]": price_id,
            "line_items[0][quantity]": "1",
            "line_items[0][adjustable_quantity][enabled]": "true",
            "line_items[0][adjustable_quantity][minimum]": "1",
            "line_items[0][adjustable_quantity][maximum]": "100",
            "allow_promotion_codes": "true",
            "billing_address_collection": "required",
            "metadata[sku]": sku,
            "metadata[domain]": item["domain"],
            "metadata[irc_482_royalty]": item["royalty_pct"]
        }, api_key)
        sku_to_url[sku] = pl["url"]
        print(f"  [LIVE CREADO] {sku} ({item['domain']}) -> {pl['url']}")

    portal_url = f"https://dashboard.stripe.com/{PRIMARY_ACCOUNT_ID}/settings/billing/portal"
    registry = {
        "mode": "LIVE_PRODUCTION",
        "primary_stripe_account_id": PRIMARY_ACCOUNT_ID,
        "account_name": "Standard 1979 Holdings, LLC",
        "live_publishable_key": LIVE_PUBLISHABLE_KEY,
        "billing_portal_config_id": PORTAL_CONFIG_ID,
        "billing_portal_url": portal_url,
        "sku_payment_links": sku_to_url
    }
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    patched = patch_all_web_files(sku_to_url, portal_url)
    print(f"\n[EXITO LIVE] {len(sku_to_url)} Payment Links LIVE sincronizados y {patched} archivos HTML actualizados.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
