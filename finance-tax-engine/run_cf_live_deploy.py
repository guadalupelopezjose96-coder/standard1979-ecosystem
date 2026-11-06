#!/usr/bin/env python3
"""
Despliegue Oficial en Vivo hacia Cloudflare Edge Worker (s1979-4domains-portal)
Acepta y prueba automáticamente tokens 'cfk_...', Bearer Tokens de 40 chars y Global API Keys de 37 chars hex.
"""

import getpass
import json
import os
import pathlib
import re
import subprocess
import sys

HOME = pathlib.Path("/data/data/com.termux/files/home")
ECOSYSTEM_DIR = HOME / "proyectos" / "standard1979_web_ecosystem"
EMAIL = "Guadalupelopezjose96@gmail.com"

DOMAINS = {
    "standard1979.com": "standard1979",
    "auraintelcore.com": "auraintelcore",
    "auratetrax.com": "auratetrax",
    "auraintelstudios3d.com": "auraintelstudios3d",
    "fourphonix.com": "fourphonix",
    "prophonix.com": "prophonix",
}

def test_auth_variants(secret: str):
    variants = []
    # 1. Si empieza con cfk_, probar sin prefijo cfk_ como Bearer y como X-Auth-Key
    if secret.startswith("cfk_"):
        stripped = secret[4:]
        variants.append(("Bearer (sin cfk_)", ["-H", f"Authorization: Bearer {stripped}"]))
        variants.append(("Bearer (con cfk_)", ["-H", f"Authorization: Bearer {secret}"]))
        variants.append(("X-Auth-Key (sin cfk_)", ["-H", f"X-Auth-Email: {EMAIL}", "-H", f"X-Auth-Key: {stripped}"]))
        # También probar primeros 40 chars después de cfk_ (si los últimos 8 son checksum hex)
        if len(stripped) == 48:
            variants.append(("Bearer (40 chars core)", ["-H", f"Authorization: Bearer {stripped[:40]}"]))
    else:
        if re.fullmatch(r"[0-9a-fA-F]{37}", secret):
            variants.append(("Global API Key (37 hex)", ["-H", f"X-Auth-Email: {EMAIL}", "-H", f"X-Auth-Key: {secret.lower()}"]))
        variants.append(("Bearer Token directo", ["-H", f"Authorization: Bearer {secret}"]))
        variants.append(("X-Auth-Key directo", ["-H", f"X-Auth-Email: {EMAIL}", "-H", f"X-Auth-Key: {secret}"]))

    for label, hdrs in variants:
        try:
            raw_out = subprocess.check_output(
                ["curl", "-s", "-A", "Mozilla/5.0"] + hdrs + ["https://api.cloudflare.com/client/v4/zones?per_page=50"],
                text=True
            )
            res = json.loads(raw_out)
            if res.get("success") and res.get("result") is not None:
                print(f" [OK] ¡Autenticación exitosa usando formato: {label}!")
                return hdrs, res.get("result", [])
            else:
                errs = res.get("errors", [])
                print(f"   [-] Variante '{label}' rechazada: {errs}")
        except Exception as e:
            print(f"   [!] Error probando {label}: {e}")
    return None, None

def main():
    print("==========================================================================")
    print(" DESPLIEGUE MULTI-FORMATO CLOUDFLARE WORKER: s1979-4domains-portal (v1.4) ")
    print("==========================================================================")
    try:
        raw = getpass.getpass(" -> Pega tu clave/token de Cloudflare y pulsa Enter: ").strip()
    except Exception:
        raw = sys.stdin.readline().strip()

    secret = re.sub(r"[^A-Za-z0-9_-]", "", raw)
    print(f" [DIAGNÓSTICO] Longitud: {len(secret)} chars | Inicio: '{secret[:4]}...' | Fin: '...{secret[-4:]}'")

    if not secret:
        print(" [ERROR] No se ingresó ninguna clave.")
        sys.exit(1)

    auth_hdrs, zones = test_auth_variants(secret)
    if not auth_hdrs or not zones:
        print("\n [!] Ninguna variante autenticó en Cloudflare.")
        print("     En https://dash.cloudflare.com/profile/api-tokens baja hasta la sección 'API Keys'")
        print("     -> En 'Global API Key' toca 'View' (son exactamente 37 letras a-f y números 0-9).")
        sys.exit(1)

    acct_id = zones[0]["account"]["id"]
    print(f" [OK] Account ID: {acct_id} | Zonas encontradas: {len(zones)}")

    pages_dict = {}
    for dom, folder in DOMAINS.items():
        html_path = ECOSYSTEM_DIR / folder / "index.html"
        html_str = html_path.read_text(encoding="utf-8")
        pages_dict[dom] = html_str
        pages_dict[f"www.{dom}"] = html_str
        print(f" [+] HTML v1.4 listo para {dom:<24} ({len(html_str):,} bytes)")

    svgs_dict = {}
    old_script = HOME / "standard1979-ecosystem" / "finance-tax-engine" / "deploy_s1979_4domains_worker_live.py"
    if old_script.exists():
        try:
            ns = {"__file__": str(old_script.resolve())}
            exec(old_script.read_text(encoding="utf-8").split("hdrs =")[0], ns)
            svgs_dict = ns.get("SVGS", {})
        except Exception:
            pass

    worker_js = f"""const PAGES = {json.dumps(pages_dict)};
const SVGS = {json.dumps(svgs_dict)};
export default {{
  async fetch(request) {{
    const url = new URL(request.url);
    if (url.hostname.startsWith('pay.')) {{
      return Response.redirect('https://buy.stripe.com/28Edr9a5I8ek96v8n8cjS0z', 302);
    }}
    const preview = url.searchParams.get('preview');
    const host = (preview && PAGES[preview]) ? preview : url.hostname.toLowerCase().replace(/^www\\./, '');
    const isPhonix = (host === 'fourphonix.com' || host === 'prophonix.com');
    const secHeaders = {{
      'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
      'X-Frame-Options': 'DENY',
      'X-Content-Type-Options': 'nosniff',
      'Referrer-Policy': 'strict-origin-when-cross-origin',
      'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
      'Cross-Origin-Opener-Policy': 'same-origin',
      'X-IP-Holder': 'Standard 1979 Holdings, LLC',
      'X-CMI-Protection': '17-USC-1202; Lanham-Act-15-USC-1051',
      'X-Tax-Governance': isPhonix ? 'ASC-606; IRC-482-Royalty-10pct-AGR; Phonix-Communications-Operating-LLC' : 'ASC-606; IRC-482-Royalty-15pct-AGR; Aura-Technologies-Operating-LLC',
      'X-Regulatory-Compliance': isPhonix ? 'FCC-STIR-SHAKEN-Level-A; Karis-Law; RAY-BAUM; CPNI-AES256; TCPA; FL-FTSA-501.059' : 'SLSA-Level-3; C2PA-v2.1-Ed25519; RFC-3161-WORM; Fla-Admin-Code-12A-1.032'
    }};
    if (url.pathname === '/favicon.svg' || url.pathname === '/favicon.ico' || url.pathname === '/assets/brand/bimi-logo.svg') {{
      const svg = SVGS[host] || SVGS['prophonix.com'] || '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="12" fill="#090d16"/><text x="50%" y="56%" text-anchor="middle" fill="#f59e0b" font-family="monospace" font-weight="bold" font-size="24">S79</text></svg>';
      return new Response(svg, {{
        status: 200,
        headers: {{
          'Content-Type': 'image/svg+xml; charset=utf-8',
          'Cache-Control': 'public, max-age=86400',
          'X-Content-Type-Options': 'nosniff',
          'Cross-Origin-Resource-Policy': 'cross-origin'
        }}
      }});
    }}
    const html = PAGES[host];
    if (html) {{
      return new Response(html, {{
        status: 200,
        headers: {{
          ...secHeaders,
          'Content-Type': 'text/html; charset=utf-8',
          'Cache-Control': 'no-store, no-cache, must-revalidate, max-age=0'
        }}
      }});
    }}
    return fetch(request);
  }}
}};
"""

    tmp_js = pathlib.Path("/data/data/com.termux/files/usr/tmp/worker.js")
    tmp_meta = pathlib.Path("/data/data/com.termux/files/usr/tmp/meta.json")
    tmp_js.write_text(worker_js, encoding="utf-8")
    tmp_meta.write_text(json.dumps({"main_module": "worker.js", "compatibility_date": "2026-01-01"}), encoding="utf-8")

    up_out = subprocess.check_output(
        ["curl", "-s", "-X", "PUT", "-A", "Mozilla/5.0"] + auth_hdrs + [
            "-F", f"metadata=@{tmp_meta};type=application/json",
            "-F", f"worker.js=@{tmp_js};type=application/javascript+module",
            f"https://api.cloudflare.com/client/v4/accounts/{acct_id}/workers/scripts/s1979-4domains-portal"
        ],
        text=True
    )
    up_res = json.loads(up_out)
    print(" [OK] Worker s1979-4domains-portal desplegado con éxito:", up_res.get("success"))
    if not up_res.get("success"):
        print(" [ERROR DETAIL]:", up_res.get("errors"))
        sys.exit(1)

    for z in zones:
        zname = z["name"]
        zid = z["id"]
        if zname in DOMAINS:
            subprocess.run(
                ["curl", "-s", "-X", "POST", "-A", "Mozilla/5.0"] + auth_hdrs + [
                    "-H", "Content-Type: application/json",
                    "-d", '{"purge_everything":true}',
                    f"https://api.cloudflare.com/client/v4/zones/{zid}/purge_cache"
                ],
                stdout=subprocess.DEVNULL
            )
            print(f" [OK] Caché global purgada en: https://{zname}")

    print("==========================================================================")
    print(" ¡LOS 6 PORTALES CORPORATIVOS v1.4 ESTÁN 100% EN VIVO EN CLOUDFLARE EDGE! ")
    print("==========================================================================")

if __name__ == "__main__":
    main()
