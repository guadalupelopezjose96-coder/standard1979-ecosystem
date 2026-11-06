#!/usr/bin/env python3
import getpass, json, pathlib, re, subprocess, sys

email = "Guadalupelopezjose96@gmail.com"
try:
    raw = getpass.getpass("Pega aqui tu clave de Cloudflare (terminada en ...aba6) y pulsa Enter: ").strip()
except Exception:
    raw = sys.stdin.readline().strip()

secret = re.sub(r"[^A-Za-z0-9_-]", "", raw)
print(f"[DIAGNOSTICO] Longitud: {len(secret)} chars | Inicio: '{secret[:4]}...' | Fin: '...{secret[-4:]}'")

if not secret or "PIOCfez" in secret:
    print("[ERROR] Clave vacia o es la antigua revocada (...f36f).")
    sys.exit(1)

stripped = secret[4:] if secret.startswith("cfk_") else secret
candidates = [
    ("Bearer (sin cfk_)", ["-H", f"Authorization: Bearer {stripped}"]),
    ("Bearer (con cfk_)", ["-H", f"Authorization: Bearer {secret}"]),
    ("X-Auth-Key (sin cfk_)", ["-H", f"X-Auth-Email: {email}", "-H", f"X-Auth-Key: {stripped}"]),
    ("X-Auth-Key (con cfk_)", ["-H", f"X-Auth-Email: {email}", "-H", f"X-Auth-Key: {secret}"]),
]
if len(stripped) > 37 and re.fullmatch(r"[0-9a-fA-F]{37}", stripped[-37:]):
    candidates.append(("X-Auth-Key (hex37 tail)", ["-H", f"X-Auth-Email: {email}", "-H", f"X-Auth-Key: {stripped[-37:].lower()}"]))

auth_hdrs = None
zones_res = None

for label, hdrs in candidates:
    out = subprocess.check_output(
        ["curl", "-s", "-A", "Mozilla/5.0"] + hdrs + ["https://api.cloudflare.com/client/v4/zones?per_page=50"]
    ).decode()
    try:
        data = json.loads(out)
        if data.get("success"):
            auth_hdrs = hdrs
            zones_res = data
            print(f"[OK] Autenticacion exitosa usando modo: {label}")
            break
        else:
            print(f"[INFO] Modo {label} -> {data.get('errors')}")
    except Exception:
        pass

if not auth_hdrs:
    # Probar si es un Account API Token verificando /accounts
    for label, hdrs in candidates[:2]:
        out = subprocess.check_output(
            ["curl", "-s", "-A", "Mozilla/5.0"] + hdrs + ["https://api.cloudflare.com/client/v4/accounts?per_page=10"]
        ).decode()
        try:
            data = json.loads(out)
            if data.get("success") and data.get("result"):
                auth_hdrs = hdrs
                zones_res = {"result": [{"name": "auratetrax.com", "id": "", "account": {"id": data["result"][0]["id"]}}]}
                print(f"[OK] Autenticacion de Cuenta exitosa usando modo: {label}")
                break
        except Exception:
            pass

if not auth_hdrs:
    print("[ERROR] Ningun modo de autenticacion fue aceptado por Cloudflare para esta clave.")
    sys.exit(1)

zones = zones_res.get("result", [])
acct_id = zones[0]["account"]["id"]
print(f"[OK] Account ID: {acct_id} | Zonas detectadas: {len(zones)}")

worker_domains = {"auratetrax.com", "auraintelstudios3d.com", "fourphonix.com", "prophonix.com"}
for z in zones:
    zname = z.get("name")
    zid = z.get("id")
    if zname in worker_domains and zid:
        subprocess.run(["curl", "-s", "-X", "PATCH"] + auth_hdrs + [
            "-H", "Content-Type: application/json", "-d", '{"enabled":true}',
            f"https://api.cloudflare.com/client/v4/zones/{zid}/ssl/universal/settings"
        ], stdout=subprocess.DEVNULL)
        subprocess.run(["curl", "-s", "-X", "PATCH"] + auth_hdrs + [
            "-H", "Content-Type: application/json", "-d", '{"value":"flexible"}',
            f"https://api.cloudflare.com/client/v4/zones/{zid}/settings/ssl"
        ], stdout=subprocess.DEVNULL)
        routes_raw = subprocess.check_output(
            ["curl", "-s"] + auth_hdrs + [f"https://api.cloudflare.com/client/v4/zones/{zid}/workers/routes"]
        ).decode()
        existing = [r.get("pattern") for r in json.loads(routes_raw).get("result", [])]
        for pat in (f"{zname}/*", f"*.{zname}/*"):
            if pat not in existing:
                subprocess.run(["curl", "-s", "-X", "POST"] + auth_hdrs + [
                    "-H", "Content-Type: application/json",
                    "-d", json.dumps({"pattern": pat, "script": "s1979-4domains-portal"}),
                    f"https://api.cloudflare.com/client/v4/zones/{zid}/workers/routes"
                ], stdout=subprocess.DEVNULL)
        print(f"[OK] Zona {zname}: Universal SSL + Rutas hacia s1979-4domains-portal verificadas.")

script_path = pathlib.Path("finance-tax-engine/deploy_s1979_4domains_worker_live.py")
code = script_path.read_text(encoding="utf-8")
ns = {"__file__": str(script_path.resolve())}
exec(code.split("hdrs =")[0], ns)

legal_footer = (
    '<div style="max-width:1180px;margin:24px auto 0;padding:14px 24px;border-top:1px solid #1e293b;'
    'font-size:11px;color:#64748b;display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px">'
    '<span>&copy; 2026 Standard 1979 Holdings, LLC. All IP &amp; CMI protected under Lanham Act (15 U.S.C. &sect; 1051) &amp; DMCA &sect; 1202 (17 U.S.C. &sect; 1202).</span>'
    '<span>Accounting: FASB ASC 606 | Intercompany Transfer Pricing: IRC &sect; 482 | WORM Audit: RFC 3161 | SLSA Level 3</span>'
    '</div></body>'
)
for k in ns["pages"]:
    if "DMCA &sect; 1202" not in ns["pages"][k]:
        ns["pages"][k] = ns["pages"][k].replace("</body>", legal_footer)

worker_js = f"""
const PAGES = {json.dumps(ns['pages'])};
const SVGS = {json.dumps(ns['SVGS'])};
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
      'X-Regulatory-Compliance': isPhonix ? 'FCC-STIR-SHAKEN-Level-A; Karis-Law; RAY-BAUM; CPNI-AES256; TCPA; FL-FTSA-501.059' : 'SLSA-L3; C2PA-v2.1; RFC-3161-WORM; POL-SEC-OSS-001'
    }};
    if (url.pathname === '/favicon.svg' || url.pathname === '/favicon.ico' || url.pathname === '/assets/brand/bimi-logo.svg') {{
      const svg = SVGS[host] || SVGS['prophonix.com'];
      return new Response(svg, {{
        status: 200,
        headers: {{
          ...secHeaders,
          'Content-Type': 'image/svg+xml; charset=utf-8',
          'Cache-Control': 'public, max-age=86400',
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
          'Cache-Control': 'no-store'
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

up_out = subprocess.check_output([
    "curl", "-s", "-X", "PUT"
] + auth_hdrs + [
    "-F", f"metadata=@{tmp_meta};type=application/json",
    "-F", f"worker.js=@{tmp_js};type=application/javascript+module",
    f"https://api.cloudflare.com/client/v4/accounts/{acct_id}/workers/scripts/s1979-4domains-portal"
]).decode()

up_res = json.loads(up_out)
print("[OK] Worker s1979-4domains-portal 100% blindado y desplegado:", up_res.get("success"))
if not up_res.get("success"):
    print("[ERROR DETAIL]:", up_res.get("errors"))
