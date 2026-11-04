#!/usr/bin/env python3
import argparse, hashlib, json
from datetime import datetime, timezone
from pathlib import Path

PORTAL = "bpc_1UWnOzFE1PknNS53wBZioc6n"
CATALOG = [
    ("ATX-PAAS-PRO", "auratetrax.com", "Aura Technologies Operating, LLC", "1. Startup Agentic PaaS (5 Agents + Cilium eBPF MicroVMs)", 299.00, "Mensual", 0.15, "SAAS"),
    ("ATX-EXEC-100K", "auratetrax.com", "Aura Technologies Operating, LLC", "2. Autonomous Workflow Pack (100k Tool Executions + SOAR)", 450.00, "Mensual", 0.15, "SAAS"),
    ("ATX-PAAS-ENT", "auratetrax.com", "Aura Technologies Operating, LLC", "3. Enterprise Kubernetes Mesh (Dedicated mTLS + SLSA L3)", 1499.00, "Mensual", 0.15, "SAAS"),
    ("ATX-GPU-NODE", "auratetrax.com", "Aura Technologies Operating, LLC", "4. Dedicated GPU Inference Node (Zero Data Retention)", 2950.00, "Mensual", 0.15, "SAAS"),
    ("AIS3D-PACK-INDIE", "auraintelstudios3d.com", "Aura Technologies Operating, LLC", "1. Commercial 3D Asset Pack (glTF/USDZ/FBX + C2PA v2.1)", 149.00, "Pago Unico", 0.15, "FL7"),
    ("AIS3D-GPU-STUDIO", "auraintelstudios3d.com", "Aura Technologies Operating, LLC", "2. Cloud GPU 3D Render Studio (Text-to-3D & Render Cluster)", 499.00, "Mensual", 0.15, "SAAS"),
    ("AIS3D-IND-TWIN", "auraintelstudios3d.com", "Aura Technologies Operating, LLC", "3. Industrial 3D Digital Twin Suite (Real-Time Plant Twin)", 1850.00, "Mensual", 0.15, "SAAS"),
    ("AIS3D-ENT-API", "auraintelstudios3d.com", "Aura Technologies Operating, LLC", "4. Enterprise 3D & Bulk C2PA v2.1 Notary API", 3500.00, "Mensual", 0.15, "SAAS"),
    ("4PHX-E911-DID", "fourphonix.com", "Phonix Communications Operating, LLC", "1. Nationwide DID Pack (25 DIDs) + Dynamic E911 PIDF-LO", 99.00, "Mensual", 0.10, "TEL"),
    ("4PHX-UCAAS-BIZ", "fourphonix.com", "Phonix Communications Operating, LLC", "2. Enterprise UCaaS Cloud PBX (10 Seats + SIP TLS 1.3/SRTP)", 249.00, "Mensual", 0.10, "TEL"),
    ("4PHX-OMNI-AI", "fourphonix.com", "Phonix Communications Operating, LLC", "3. Omnichannel 10DLC Business SMS/MMS + AI Receptionist", 399.00, "Mensual", 0.10, "TEL"),
    ("4PHX-PBX-ENT50", "fourphonix.com", "Phonix Communications Operating, LLC", "4. Multi-Site Enterprise PBX Cluster (50 Seats + WORM)", 1250.00, "Mensual", 0.10, "TEL"),
    ("PPHX-SIP-TRUNK", "prophonix.com", "Phonix Communications Operating, LLC", "1. Wholesale Carrier SIP Trunk (High-CPS + STIR/SHAKEN A)", 199.00, "Mensual+LCR", 0.10, "TEL"),
    ("PPHX-TCPA-SAFE", "prophonix.com", "Phonix Communications Operating, LLC", "2. Carrier Compliance Dialer Suite (TCPA + FL FTSA Safe Harbor)", 799.00, "Mensual", 0.10, "TEL"),
    ("PPHX-CARRIER-CPS", "prophonix.com", "Phonix Communications Operating, LLC", "3. High-CPS Wholesale Interconnect (100+ CPS + ITG Traceback)", 2450.00, "Mensual", 0.10, "TEL"),
    ("PPHX-SBC-PEER", "prophonix.com", "Phonix Communications Operating, LLC", "4. Global Carrier Peering & Dedicated SBC Cluster", 4900.00, "Mensual", 0.10, "TEL"),
]

def generate_quote(*args):
    toks = [str(a) for a in args if not str(a).startswith("-")]
    sku = toks[0] if toks else "ATX-PAAS-ENT"
    qty = int(toks[1]) if len(toks) > 1 and toks[1].isdigit() else 1
    row = next((r for r in CATALOG if r[0].upper() == sku.upper() or r[1] == sku.lower()), CATALOG[2])
    gross = round(row[4] * qty, 2)
    roy = round(gross * row[6], 2)
    tax = round(gross * 0.4204 + 0.40 * qty, 2) if row[7] == "TEL" else (round(gross * 0.07, 2) if row[7] == "FL7" else 0.0)
    tot = round(gross + tax, 2)
    inv = f"INV-{row[0]}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M')}"
    return {"invoice_id": inv, "domain": row[1], "opco": row[2], "sku": row[0], "product": row[3], "qty": qty, "gross_usd": gross, "royalty_to_standard1979_usd": roy, "tax_usd": tax, "total_usd": tot, "stripe_portal": PORTAL, "checkout_url": f"https://pay.{row[1]}/checkout/{inv}?portal={PORTAL}&pci=saq_a_3ds2"}

def main():
    print("=" * 100)
    print(" STANDARD 1979 HOLDINGS, LLC — CATALOGO EXCLUSIVO DE LOS 4 DOMINIOS RESTANTES (16 SKUs)")
    print(" * INTACTOS Y SEPARADOS: standard1979.com y auraintelcore.com (ya tienen sus propios servicios)")
    print("=" * 100)
    quotes = []
    for d in ["auratetrax.com", "auraintelstudios3d.com", "fourphonix.com", "prophonix.com"]:
        rows = [r for r in CATALOG if r[1] == d]
        print(f"\n[{d.upper()}] -> {rows[0][2]} (Regalia IRC 482: {int(rows[0][6]*100)}%)")
        for r in rows:
            print(f"  * {r[0]:<17} | USD {r[4]:>8,.2f} ({r[5]:<11}) | {r[3]}")
        quotes.append(generate_quote(rows[2][0], 1))
    qp = Path(__file__).resolve().parent / "quotes-and-invoices" / "active_commercial_quotes.json"
    if qp.parent.exists():
        qp.write_text(json.dumps(quotes, indent=2) + "\n")
    print("\n" + "=" * 100)
    for q in quotes:
        print(f" * {q['domain']:<22} | {q['invoice_id']} | Total: USD {q['total_usd']:>8,.2f} | Regalia: USD {q['royalty_to_standard1979_usd']:>6,.2f}\n   Checkout: {q['checkout_url']}")
    print("=" * 100)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--sku")
    p.add_argument("--qty", type=int, default=1)
    a, u = p.parse_known_args()
    print(json.dumps(generate_quote(a.sku, a.qty), indent=2)) if a.sku else (print(json.dumps(generate_quote(*u), indent=2)) if u else main())
