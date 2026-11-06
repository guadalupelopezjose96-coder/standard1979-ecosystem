#!/usr/bin/env python3
import getpass, json, re, subprocess, sys, time

email = "Guadalupelopezjose96@gmail.com"
raw = getpass.getpass("Pega tu clave de Cloudflare (...aba6) y pulsa Enter: ").strip()
secret = re.sub(r"[^A-Za-z0-9_-]", "", raw)
auth_hdrs = ["-H", f"X-Auth-Email: {email}", "-H", f"X-Auth-Key: {secret}"]

def cf_api(method, path, payload=None):
    cmd = ["curl", "-s", "-X", method, "-A", "Mozilla/5.0"] + auth_hdrs + ["-H", "Content-Type: application/json"]
    if payload is not None:
        cmd += ["-d", json.dumps(payload)]
    cmd.append(f"https://api.cloudflare.com/client/v4{path}")
    out = subprocess.check_output(cmd).decode()
    return json.loads(out)

z_res = cf_api("GET", "/zones?name=auratetrax.com")
if not z_res.get("success") or not z_res.get("result"):
    print("[ERROR] No se encontro la zona auratetrax.com:", z_res)
    sys.exit(1)

zid = z_res["result"][0]["id"]
print(f"[OK] Zona auratetrax.com ID: {zid} | Status: {z_res['result'][0].get('status')}")

# 1. Revisar registros DNS de auratetrax.com (asegurar @ y www proxied y revisar CAA)
dns_res = cf_api("GET", f"/zones/{zid}/dns_records?per_page=100")
records = dns_res.get("result", [])
has_root = False
has_www = False
for r in records:
    print(f"  [DNS] {r['type']} {r['name']} -> {r['content']} (proxied={r.get('proxied')})")
    if r["name"] == "auratetrax.com" and r["type"] in ("A", "AAAA", "CNAME"):
        has_root = True
        if not r.get("proxied"):
            cf_api("PATCH", f"/zones/{zid}/dns_records/{r['id']}", {"proxied": True})
            print("  [FIX] Activado proxy naranja en registro raiz.")
    if r["name"] == "www.auratetrax.com" and r["type"] in ("A", "AAAA", "CNAME"):
        has_www = True

if not has_root:
    cf_api("POST", f"/zones/{zid}/dns_records", {"type": "AAAA", "name": "@", "content": "100::", "proxied": True})
    print("  [FIX] Creado registro raiz AAAA 100:: (Worker originless proxied).")
if not has_www:
    cf_api("POST", f"/zones/{zid}/dns_records", {"type": "AAAA", "name": "www", "content": "100::", "proxied": True})
    print("  [FIX] Creado registro www AAAA 100:: (Worker originless proxied).")

# 2. Revisar estado de Universal SSL y paquetes de certificados
uni = cf_api("GET", f"/zones/{zid}/ssl/universal/settings")
print("[SSL UNIVERSAL SETTINGS]:", uni.get("result"))

packs = cf_api("GET", f"/zones/{zid}/ssl/certificate_packs?status=all")
print("[CERTIFICATE PACKS]:")
for p in packs.get("result", []):
    print(f"  - ID: {p.get('id')} | Type: {p.get('type')} | Status: {p.get('status')} | CA: {p.get('certificate_authority')} | Errors: {p.get('validation_errors')}")

# 3. Forzar re-emision de Universal SSL con Let's Encrypt / Google y activar TLS 1.3 + Min TLS 1.2
cf_api("PATCH", f"/zones/{zid}/settings/tls_1_3", {"value": "on"})
cf_api("PATCH", f"/zones/{zid}/settings/min_tls_version", {"value": "1.2"})
cf_api("PATCH", f"/zones/{zid}/settings/ssl", {"value": "flexible"})

# Si no hay ningun pack 'active', reiniciar Universal SSL cambiando CA a lets_encrypt
active_packs = [p for p in packs.get("result", []) if p.get("status") == "active"]
if not active_packs:
    print("[FIX] No hay certificado de borde activo en auratetrax.com. Reiniciando aprovisionamiento Universal SSL (CA: lets_encrypt)...")
    cf_api("PATCH", f"/zones/{zid}/ssl/universal/settings", {"enabled": False})
    time.sleep(2)
    r_en = cf_api("PATCH", f"/zones/{zid}/ssl/universal/settings", {"enabled": True, "certificate_authority": "lets_encrypt"})
    print("[FIX] Respuesta re-activacion Universal SSL:", r_en.get("result"), r_en.get("errors"))
