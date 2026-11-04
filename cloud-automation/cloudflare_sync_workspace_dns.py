import json
import os
import sys
import urllib.request

CF_TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN", "").strip()
MISSING_MX_DOMAINS = ["auratetrax.com", "auraintelstudios3d.com", "prophonix.com"]

def cf_api(method: str, endpoint: str, payload: dict | None = None) -> dict:
    url = f"https://api.cloudflare.com/client/v4{endpoint}"
    headers = {
        "Authorization": f"Bearer {CF_TOKEN}",
        "Content-Type": "application/json"
    }
    data = json.dumps(payload).encode("utf-8") if payload else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))

def ensure_google_mx_records():
    if not CF_TOKEN:
        print("================================================================================")
        print(" [MODO GUÍA / DRY-RUN] Variable CLOUDFLARE_API_TOKEN no detectada en entorno.")
        print(" Para aplicar automáticamente vía API en Cloudflare, ejecuta:")
        print("   export CLOUDFLARE_API_TOKEN='tu_token_api_cloudflare'")
        print("   python3 ~/standard1979-ecosystem/cloud-automation/cloudflare_sync_workspace_dns.py")
        print("--------------------------------------------------------------------------------")
        print(" REGISTROS EXACTOS A INYECTAR EN CLOUDFLARE PARA COMPLETAR EL 100%:")
        for d in MISSING_MX_DOMAINS:
            print(f"  * [{d}] -> Tipo: MX | Nombre: @ | Servidor: smtp.google.com | Prioridad: 1")
        print("  * [DKIM en standard1979, auratetrax, auraintelstudios3d, prophonix]:")
        print("    -> En admin.google.com > Autenticar correo > Generar registro nuevo (2048-bit)")
        print("    -> Tipo: TXT | Nombre: google._domainkey | Valor: v=DKIM1; k=rsa; p=MIIBIjANBg...")
        print("================================================================================")
        return

    for domain in MISSING_MX_DOMAINS:
        zones = cf_api("GET", f"/zones?name={domain}")["result"]
        if not zones:
            print(f"[WARN] Zona {domain} no encontrada en este token.")
            continue
        zone_id = zones[0]["id"]
        existing_mx = cf_api("GET", f"/zones/{zone_id}/dns_records?type=MX")["result"]
        if any(r["content"].lower() == "smtp.google.com" for r in existing_mx):
            print(f"[OK] {domain} ya cuenta con MX smtp.google.com")
        else:
            cf_api("POST", f"/zones/{zone_id}/dns_records", {
                "type": "MX",
                "name": domain,
                "content": "smtp.google.com",
                "priority": 1,
                "ttl": 3600
            })
            print(f"[APLICADO] MX smtp.google.com (Prioridad 1) creado en vivo para {domain}")

if __name__ == "__main__":
    ensure_google_mx_records()
