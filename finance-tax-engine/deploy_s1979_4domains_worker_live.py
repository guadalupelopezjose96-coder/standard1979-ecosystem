#!/usr/bin/env python3
import json, urllib.request, urllib.error

email = "Guadalupelopezjose96@gmail.com"
key = "cfk_PIOCfez2IrQxlmHuP7igv8fHiUSFUAGDc9QMVejkbd0bf36f"
PORTAL = "bpc_1UWnOzFE1PknNS53wBZioc6n"


import pathlib as _pathlib
_ASSETS_DIR = _pathlib.Path(__file__).resolve().parent.parent / "brand-governance" / "assets"
_DOM_MAP = {
    "auratetrax.com": "AuraTetrax.com",
    "auraintelstudios3d.com": "AuraIntelStudios3D.com",
    "fourphonix.com": "fourphonix.com",
    "prophonix.com": "prophonix.com",
}
SVGS = {d: (_ASSETS_DIR / folder / "bimi-logo.svg").read_text(encoding="utf-8") for d, folder in _DOM_MAP.items()}

THEMES = {
  "auratetrax.com": {
    "bg": "#080512", "panel": "#120b24", "border": "#3b1d6e", "accent": "#a855f7", "accent2": "#ec4899",
    "btn": "linear-gradient(135deg,#7e22ce,#db2777)", "font": "'Courier New',monospace",
    "tag": "KUBERNETES mTLS MESH // gVISOR SANDWICH MICROVMs",
    "hero": "AURATETRAX // AUTONOMOUS AGENTIC COMPUTE PaaS",
    "sub": "Orquestación determinista de enjambres de agentes IA sobre MicroVMs aisladas, Cilium eBPF y SPIFFE/SPIRE mTLS.",
    "widget_title": "TOPOLOGIA EN VIVO DE CLUSTERS K8s Y CORTACIRCUITOS SOAR",
    "widget_bars": [("NODOS gVISOR ACTIVOS", "99.99% SLA", "#a855f7"), ("MALLA SPIFFE mTLS", "ROTACION 15m", "#ec4899"), ("CADENA SLSA NIVEL 3", "POL-SEC-OSS-001", "#c084fc")],
    "rate": 0.15, "opco": "Aura Technologies Operating, LLC (15% IRC § 482 Royalty)", "unit": "CLUSTERS / NODOS GPU",
    "plans": [
      ("ATX-PAAS-PRO", "Startup Agentic PaaS", 299.00, "Mensual", "5 Agentes Autónomos + MicroVMs gVisor + Cilium eBPF"),
      ("ATX-EXEC-100K", "Autonomous Workflow Pack", 450.00, "Mensual", "100,000 Ejecuciones Deterministas + Cortacircuitos SOAR"),
      ("ATX-PAAS-ENT", "Enterprise Kubernetes Mesh", 1499.00, "Mensual", "Clúster Dedicado mTLS SPIFFE/SPIRE + SLSA Nivel 3"),
      ("ATX-GPU-NODE", "Dedicated GPU Inference Node", 2950.00, "Mensual", "Nodo Privado H100/L40S Zero Data Retention + OTel"),
    ]
  },
  "auraintelstudios3d.com": {
    "bg": "#120c06", "panel": "#1f140a", "border": "#5c3a18", "accent": "#f59e0b", "accent2": "#ef4444",
    "btn": "linear-gradient(135deg,#d97706,#dc2626)", "font": "system-ui,-apple-system,sans-serif",
    "tag": "ESTUDIO GENERATIVO 3D // PROCEDENCIA CRIPTOGRAFICA C2PA v2.1 Ed25519",
    "hero": "AURA INTEL STUDIOS 3D   RENDERIZADO GPU Y GEMELOS DIGITALES",
    "sub": "Producción de mallas glTF/USDZ/FBX, texturas PBR 8K y gemelos digitales industriales certificados con firma Ed25519.",
    "widget_title": "MOTOR DE VERIFICACION DE ACTIVOS 3D Y MANIFIESTOS C2PA v2.1",
    "widget_bars": [("FORMATOS NATIVOS", "glTF / USDZ / FBX", "#f59e0b"), ("TEXTURAS PBR", "8K HDRI + C2PA", "#ef4444"), ("DERECHOS EULA", "DMCA 17 USC 512", "#fbbf24")],
    "rate": 0.15, "opco": "Aura Technologies Operating, LLC (15% IRC § 482 Royalty)", "unit": "PAQUETES / NODOS RENDER",
    "plans": [
      ("AIS3D-PACK-INDIE", "Commercial 3D Asset Pack", 149.00, "Pago Unico", "Modelos glTF/USDZ/FBX + Texturas PBR 8K + C2PA v2.1"),
      ("AIS3D-GPU-STUDIO", "Cloud GPU 3D Render Studio", 499.00, "Mensual", "Pipeline Text-to-3D + Render Distribuido + DMCA Safe Harbor"),
      ("AIS3D-IND-TWIN", "Industrial 3D Digital Twin", 1850.00, "Mensual", "Gemelo Digital 3D en Tiempo Real para Plantas y Subestaciones"),
      ("AIS3D-ENT-API", "Enterprise 3D & C2PA API", 3500.00, "Mensual", "API Mayorista de Generación 3D y Sellado CriptogrÃfico C2PA"),
    ]
  },
  "fourphonix.com": {
    "bg": "#03111a", "panel": "#072030", "border": "#12496b", "accent": "#06b6d4", "accent2": "#3b82f6",
    "btn": "linear-gradient(135deg,#0891b2,#2563eb)", "font": "system-ui,-apple-system,sans-serif",
    "tag": "CLOUD PBX UCaaS // SIP TLS 1.3 + SRTP // E911 DINAMICO PIDF-LO",
    "hero": "FOURPHONIX   COMUNICACIONES UNIFICADAS EMPRESARIALES Y E911",
    "sub": "Telefonía corporativa en la nube con marcación directa 911 (Kari's Law), geolocalización RAY BAUM'S Act y CPNI AES-256.",
    "widget_title": "MATRIZ TELEFONICA CLOUD PBX, E911 PIDF-LO Y MENSAJERIA 10DLC",
    "widget_bars": [("VOZ HD CIFRADA", "SIP TLS 1.3 + SRTP", "#06b6d4"), ("DESPACHO E911", "KARI + RAY BAUM XML", "#38bdf8"), ("REGISTRO SMS", "TCR 10DLC + STIR A", "#60a5fa")],
    "rate": 0.10, "opco": "Phonix Communications Operating, LLC (10% IRC § 482 Royalty)", "unit": "BLOQUES DE ASIENTOS / DIDs",
    "plans": [
      ("4PHX-E911-DID", "Nationwide DID + E911 Pack", 99.00, "Mensual", "25 Números DID + Marcación Directa 911 + Ubicación PIDF-LO"),
      ("4PHX-UCAAS-BIZ", "Enterprise UCaaS Cloud PBX", 249.00, "Mensual", "10 Asientos Voz HD SIP TLS 1.3 / SRTP + CPNI AES-256"),
      ("4PHX-OMNI-AI", "Omnichannel 10DLC + AI Voice", 399.00, "Mensual", "SMS/MMS Corporativo TCR 10DLC + Recepcionista IA STIR Nivel A"),
      ("4PHX-PBX-ENT50", "Multi-Site PBX Cluster (50)", 1250.00, "Mensual", "50 Asientos Multi-Sede HA + Grabación Inmutable WORM RFC 3161"),
    ]
  },
  "prophonix.com": {
    "bg": "#140508", "panel": "#240a10", "border": "#6b1829", "accent": "#f43f5e", "accent2": "#fb7185",
    "btn": "linear-gradient(135deg,#e11d48,#9f1239)", "font": "system-ui,-apple-system,sans-serif",
    "tag": "WHOLESALE CARRIER SIP // STIR/SHAKEN LEVEL A // TCPA & FL FTSA SAFE HARBOR",
    "hero": "PROPHONIX   INTERCONEXION CARRIER MAYORISTA Y CORTAFUEGOS TCPA/FTSA",
    "sub": "Troncales SIP de alta concurrencia CPS, SBC BGP Anycast y cumplimiento automatizado Fla. Stat. § 501.059 (8AM-8PM, mÃx 3/24h).",
    "widget_title": "MONITOR NOC CARRIER CPS, STIR/SHAKEN STI-CA Y FILTRO DNC/RND",
    "widget_bars": [("ATESTACION FCC", "STIR/SHAKEN NIVEL A", "#f43f5e"), ("REGLA FLORIDA FTSA", "8AM-8PM | MAX 3/24H", "#fb7185"), ("TRAZABILIDAD ITG", "RESPUESTA < 24 HORAS", "#fda4af")],
    "rate": 0.10, "opco": "Phonix Communications Operating, LLC (10% IRC § 482 Royalty)", "unit": "TRONCALES / BLOQUES CPS",
    "plans": [
      ("PPHX-SIP-TRUNK", "Wholesale Carrier SIP Trunk", 199.00, "Mensual+LCR", "Alta Concurrencia CPS + STIR/SHAKEN Nivel A + SBC Anti-Fraude"),
      ("PPHX-TCPA-SAFE", "Carrier Compliance Dialer", 799.00, "Mensual", "Cortafuegos TCPA + Florida FTSA (8AM-8PM / MÃx 3/24h) + DNC/RND"),
      ("PPHX-CARRIER-CPS", "High-CPS Interconnect 100+", 2450.00, "Mensual", "Interconexión Dedicada 100+ CPS + Pasarela ITG Traceback <24h"),
      ("PPHX-SBC-PEER", "Global Carrier SBC Peering", 4900.00, "Mensual", "Clúster SBC Dedicado BGP Anycast + Mitigación DDoS SIP L7"),
    ]
  }
}

def render_site(dom, t):
    wbars = "".join([f'<div style="background:{t["bg"]};border:1px solid {t["border"]};padding:12px 16px;border-radius:10px;border-left:4px solid {c}"><div style="font-size:11px;color:#94a3b8">{k}</div><div style="font-size:16px;font-weight:800;color:{c};margin-top:4px">{v}</div></div>' for k,v,c in t["widget_bars"]])
    cards = ""
    opts = ""
    for i, (sku, name, pr, bill, desc) in enumerate(t["plans"]):
        cards += f'''<div class="pcard" id="card{i}" onclick="sel({i})">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
            <span style="font-size:11px;padding:3px 8px;border-radius:6px;background:{t["bg"]};color:{t["accent"]};font-family:monospace">{sku}</span>
            <span style="font-size:12px;color:#94a3b8">{bill}</span>
          </div>
          <div style="font-size:17px;font-weight:800;color:#fff;margin-bottom:6px">{name}</div>
          <div style="font-size:26px;font-weight:900;color:{t["accent"]};margin-bottom:8px">USD {pr:,.2f}</div>
          <div style="font-size:13px;color:#cbd5e1;line-height:1.45">{desc}</div>
        </div>'''
        opts += f'<option value="{i}" data-p="{pr}" data-s="{sku}">{name}   USD {pr:,.2f} ({bill})</option>'

    return f'''<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{t["hero"]}</title><link rel="icon" type="image/svg+xml" href="/favicon.svg"><link rel="alternate icon" href="/favicon.ico">
<style>
body{{margin:0;background:{t["bg"]};color:#f1f5f9;font-family:{t["font"]}}}
.bar{{padding:12px 24px;background:#00000066;border-bottom:1px solid {t["border"]};display:flex;justify-content:space-between;font-size:12px;color:{t["accent"]};font-family:monospace}}
.wrap{{max-width:1200px;margin:24px auto;padding:0 18px}}
.hero{{background:radial-gradient(circle at top right,{t["border"]}66,{t["panel"]});border:1px solid {t["border"]};border-radius:16px;padding:28px;margin-bottom:20px}}
.tag{{display:inline-block;padding:4px 10px;border-radius:6px;background:{t["bg"]};color:{t["accent"]};font-size:11px;font-family:monospace;border:1px solid {t["border"]};margin-bottom:10px}}
h1{{margin:0 0 8px 0;font-size:26px;color:#fff;letter-spacing:.3px}}
.sub{{color:#cbd5e1;font-size:14px;margin-bottom:18px}}
.wgrid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}}
.pgrid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(255px,1fr));gap:16px;margin-bottom:20px}}
.pcard{{background:{t["panel"]};border:2px solid {t["border"]};border-radius:14px;padding:20px;cursor:pointer;transition:.2s}}
.pcard.active{{border-color:{t["accent"]};box-shadow:0 0 20px {t["accent"]}33}}
.calc{{background:{t["panel"]};border:1px solid {t["border"]};border-radius:16px;padding:24px}}
.cgrid{{display:grid;grid-template-columns:1.3fr 1fr 1fr;gap:16px;align-items:center;background:{t["bg"]};padding:16px;border-radius:12px;border:1px solid {t["border"]}}}
select,input[type=range]{{width:100%;padding:10px;background:{t["panel"]};color:#fff;border:1px solid {t["border"]};border-radius:8px}}
.btn{{background:{t["btn"]};color:#fff;border:none;padding:14px;border-radius:10px;font-weight:800;cursor:pointer;width:100%;font-size:14px}}
.mgrid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin-top:16px}}
.mcard{{background:{t["bg"]};border:1px solid {t["border"]};padding:14px;border-radius:10px}}
</style></head><body>
<div class="bar"><span style="display:flex;align-items:center;gap:10px"><img src="/favicon.svg" alt="logo" style="width:22px;height:22px;border-radius:4px"><b>{dom.upper()}</b> // {t["opco"]}</span><span>STRIPE TAX & B2B PORTAL: {PORTAL}</span></div>
<div class="wrap">
  <div class="hero">
    <div class="tag">{t["tag"]}</div>
    <h1>{t["hero"]}</h1>
    <div class="sub">{t["sub"]}</div>
    <div style="font-size:11px;color:#94a3b8;margin-bottom:8px;font-family:monospace">{t["widget_title"]}</div>
    <div class="wgrid">{wbars}</div>
  </div>
  <div class="pgrid">{cards}</div>
  <div class="calc">
    <h2 style="margin:0 0 6px 0;font-size:18px;color:{t["accent"]}">Consola de Aprovisionamiento, Regalías IRC § 482 y Checkout Directo</h2>
    <div class="cgrid">
      <div><div style="font-size:11px;color:#94a3b8;margin-bottom:6px">1. PLAN SELECCIONADO:</div><select id="ps" onchange="rc()">{opts}</select></div>
      <div><div style="font-size:11px;color:#94a3b8;margin-bottom:6px">2. {t["unit"]}: (<span id="ql">1</span>)</div><input type="range" id="qr" min="1" max="25" value="1" oninput="rc()"></div>
      <div><a id="pay-btn" class="btn" href="https://buy.stripe.com/5kQ7sL7XAamsgyXavgcjS0A" onclick="pay();return false;" style="display:block;text-align:center;text-decoration:none;line-height:20px">Activar SKU + Checkout &rarr;</a></div>
    </div>
    <div class="mgrid">
      <div class="mcard"><div style="font-size:11px;color:#94a3b8">SUBTOTAL BRUTO</div><div id="mg" style="font-size:22px;font-weight:800;color:#fff;margin-top:4px"></div></div>
      <div class="mcard"><div style="font-size:11px;color:#94a3b8">REGALIA IRC § 482 (HOLDING)</div><div id="mr" style="font-size:22px;font-weight:800;color:{t["accent"]};margin-top:4px"></div></div>
      <div class="mcard"><div style="font-size:11px;color:#94a3b8">RETENCION NETA OPCO</div><div id="mn" style="font-size:22px;font-weight:800;color:{t["accent2"]};margin-top:4px"></div></div>
      <div class="mcard"><div style="font-size:11px;color:#94a3b8">SELLO C2PA / WORM</div><div id="ms" style="font-size:16px;font-weight:800;color:#34d399;margin-top:6px;font-family:monospace"></div></div>
    </div>
    <div style="margin-top:16px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;font-size:12px;color:#94a3b8">
      <span>Facturación electrónica PEPPOL UBL 3.0 | Click-to-Cancel FTC 16 CFR 425 Activo</span>
      <a id="portal-btn" href="https://buy.stripe.com/5kQ7sL7XAamsgyXavgcjS0A" style="color:{t['accent']};border:1px solid {t['accent']};padding:8px 14px;border-radius:8px;text-decoration:none;font-weight:700">Abrir Portal Fiscal Stripe ({PORTAL})</a>
    </div>
  </div>
</div>
<script>
const rate={t["rate"]};
function sel(i){{document.getElementById('ps').selectedIndex=i;rc();}}
function rc(){{
  const s=document.getElementById('ps');const o=s.options[s.selectedIndex];
  const p=parseFloat(o.getAttribute('data-p'));const sku=o.getAttribute('data-s');
  const q=parseInt(document.getElementById('qr').value);document.getElementById('ql').innerText=q;
  for(let i=0;i<4;i++){{const c=document.getElementById('card'+i);if(c)c.className=(i===s.selectedIndex)?'pcard active':'pcard';}}
  const g=p*q;const r=g*rate;const n=g-r;
  document.getElementById('mg').innerText='USD '+g.toLocaleString('en-US',{{minimumFractionDigits:2}});
  document.getElementById('mr').innerText='USD '+r.toLocaleString('en-US',{{minimumFractionDigits:2}});
  document.getElementById('mn').innerText='USD '+n.toLocaleString('en-US',{{minimumFractionDigits:2}});
      document.getElementById('ms').innerText=sku+' [VERIFIED]';const L={{"PPHX-SIP-TRUNK": "https://buy.stripe.com/28Edr9a5I8ek96v8n8cjS0z", "PPHX-TCPA-SAFE": "https://buy.stripe.com/5kQ7sL7XAamsgyXavgcjS0A", "PPHX-CARRIER-CPS": "https://buy.stripe.com/cNibJ1elYdyE1E35aWcjS0B", "PPHX-SBC-PEER": "https://buy.stripe.com/9B67sLa5I52896vdHscjS0C", "4PHX-E911-DID": "https://buy.stripe.com/9B67sL5PsdyE4Qf1YKcjS0D", "4PHX-UCAAS-BIZ": "https://buy.stripe.com/7sY7sLfq2gK0beD320cjS0E", "4PHX-OMNI-AI": "https://buy.stripe.com/dRm28ra5IeCiciHcDocjS0F", "4PHX-PBX-ENT50": "https://buy.stripe.com/aFa5kD0v89iogyXfPAcjS0G", "AIC-LLM-GW": "https://buy.stripe.com/8x24gzgu6fGM3Mb6f0cjS0H", "ATRX-PAAS-NODE": "https://buy.stripe.com/bJeaEXdhUgK082r5aWcjS0I", "AIS3D-H100-C2PA": "https://buy.stripe.com/14A9ATa5I528dmL9rccjS0J", "S1979-IP-LIC": "https://buy.stripe.com/aFaeVdcdQ5280zZ6f0cjS0K", "ATX-PAAS-PRO": "https://buy.stripe.com/14A7sLfq2bqwgyX9rccjS0L", "ATX-EXEC-100K": "https://buy.stripe.com/dRm00j4Lo1PW1E39rccjS0M", "ATX-PAAS-ENT": "https://buy.stripe.com/8x25kD2Dg8ek82rbzkcjS0N", "ATX-GPU-NODE": "https://buy.stripe.com/bJe9AT91EbqwfuTfPAcjS0O", "AIS3D-PACK-INDIE": "https://buy.stripe.com/00waEXb9M7ag6Yn7j4cjS0P", "AIS3D-GPU-STUDIO": "https://buy.stripe.com/6oUaEX7XA3Y44QfgTEcjS0Q", "AIS3D-IND-TWIN": "https://buy.stripe.com/eVq28r5PsbqwbeD8n8cjS0R", "AIS3D-ENT-API": "https://buy.stripe.com/7sY7sL2Dgbqw96v8n8cjS0S"}};const u=L[sku]||'https://buy.stripe.com/5kQ7sL7XAamsgyXavgcjS0A'\\;const pb=document.getElementById('pay-btn');if(pb)pb.href=u;const ptb=document.getElementById('portal-btn');if(ptb)ptb.href=u;
}}
    function pay(){{const pb=document.getElementById('pay-btn');if(pb&&pb.href){{window.location.assign(pb.href);}}}}
sel(1);
</script></body></html>'''

pages = {d: render_site(d, t) for d, t in THEMES.items()}

hdrs = {"X-Auth-Email": email, "X-Auth-Key": key, "Content-Type": "application/json"}
zones = json.loads(urllib.request.urlopen(urllib.request.Request("https://api.cloudflare.com/client/v4/zones?per_page=50", headers=hdrs)).read().decode())["result"]
acct_id = zones[0]["account"]["id"]

worker_js = f"""
const PAGES = {json.dumps(pages)};
const SVGS = {json.dumps(SVGS)};
export default {{
  async fetch(request) {{
    const url = new URL(request.url);
    if (url.hostname.startsWith('pay.')) {{
      return Response.redirect('https://buy.stripe.com/28Edr9a5I8ek96v8n8cjS0z', 302);
    }}
    const preview = url.searchParams.get('preview');
    const host = (preview && PAGES[preview]) ? preview : url.hostname.toLowerCase().replace(/^www\\./, '');
    if (url.pathname === '/favicon.svg' || url.pathname === '/favicon.ico' || url.pathname === '/assets/brand/bimi-logo.svg') {{
      const svg = SVGS[host] || SVGS['prophonix.com'];
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
          'Content-Type': 'text/html; charset=utf-8',
          'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
          'X-Frame-Options': 'DENY',
          'X-Content-Type-Options': 'nosniff',
          'Cache-Control': 'no-store'
        }}
      }});
    }}
    return fetch(request);
  }}
}};
"""

boundary = "----S1979UniqueThemes"
meta = json.dumps({"main_module": "worker.js", "compatibility_date": "2026-01-01"})
body = (
    f"--{boundary}\r\nContent-Disposition: form-data; name=\"metadata\"; filename=\"blob\"\r\nContent-Type: application/json\r\n\r\n{meta}\r\n"
    f"--{boundary}\r\nContent-Disposition: form-data; name=\"worker.js\"; filename=\"worker.js\"\r\nContent-Type: application/javascript+module\r\n\r\n{worker_js}\r\n"
    f"--{boundary}--\r\n"
).encode("utf-8")

req = urllib.request.Request(
    f"https://api.cloudflare.com/client/v4/accounts/{acct_id}/workers/scripts/s1979-4domains-portal",
    data=body,
    headers={"X-Auth-Email": email, "X-Auth-Key": key, "Content-Type": f"multipart/form-data; boundary={boundary}"},
    method="PUT"
)
res = json.loads(urllib.request.urlopen(req).read().decode())
print("Worker con 4 disenos e identidades visuales unicas desplegado:", res.get("success"))
