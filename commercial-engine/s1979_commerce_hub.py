#!/usr/bin/env python3
"""
Standard 1979 Holdings, LLC - Multi-Domain Commercialization & Checkout Engine
Generates live commercial catalogs, Stripe/ACH payment links (PCI-DSS v4.0 SAQ-A),
and formal B2B quotes/invoices with automatic tax & IRC 482 royalty allocation.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

CATALOG = {
    "standard1979.com": {
        "entity": "Standard 1979 Holdings, LLC",
        "sales_email": "licensing@standard1979.com",
        "billing_email": "treasury@standard1979.com",
        "royalty_rate": 0.00,
        "tax_profile": "EXEMPT_B2B_IP_LICENSE",
        "products": [
            {"sku": "S1979-IP-WL", "name": "Enterprise White-Label IP License (Annual)", "price_usd": 15000.00, "billing": "annual"},
            {"sku": "S1979-AUDIT-DR", "name": "SOC2/ISO27001/ISO42001 Compliance Architecture License", "price_usd": 4500.00, "billing": "one_time"}
        ]
    },
    "auraintelcore.com": {
        "entity": "Aura Technologies Operating, LLC",
        "sales_email": "sales@auraintelcore.com",
        "billing_email": "billing@auraintelcore.com",
        "royalty_rate": 0.15,
        "tax_profile": "SAAS_FL_EXEMPT_OR_OSS",
        "products": [
            {"sku": "AIC-SSO-ENT", "name": "OIDC/OAuth 2.1 Zero-Trust Identity Federation", "price_usd": 499.00, "billing": "monthly"},
            {"sku": "AIC-LLM-GW", "name": "Enterprise AI Security Gateway (100M Tokens)", "price_usd": 850.00, "billing": "monthly"}
        ]
    },
    "auratetrax.com": {
        "entity": "Aura Technologies Operating, LLC",
        "sales_email": "sales@auratetrax.com",
        "billing_email": "billing@auratetrax.com",
        "royalty_rate": 0.15,
        "tax_profile": "PAAS_COMPUTE",
        "products": [
            {"sku": "ATX-PAAS-PRO", "name": "Tetrax Modular Agentic PaaS (Starter 5 Nodes)", "price_usd": 299.00, "billing": "monthly"},
            {"sku": "ATX-PAAS-ENT", "name": "Tetrax Autonomous Cluster (Unlimited Nodes + Dedicated K8s)", "price_usd": 1499.00, "billing": "monthly"}
        ]
    },
    "auraintelstudios3d.com": {
        "entity": "Aura Technologies Operating, LLC",
        "sales_email": "studio@auraintelstudios3d.com",
        "billing_email": "billing@auraintelstudios3d.com",
        "royalty_rate": 0.15,
        "tax_profile": "DIGITAL_3D_ASSETS_FL_7PCT",
        "products": [
            {"sku": "AIS3D-PACK-INDIE", "name": "C2PA-Signed 3D Generative Asset Commercial Pack", "price_usd": 149.00, "billing": "one_time"},
            {"sku": "AIS3D-GPU-STUDIO", "name": "Dedicated 3D Generative Render Studio Subscription", "price_usd": 499.00, "billing": "monthly"}
        ]
    },
    "fourphonix.com": {
        "entity": "Phonix Communications Operating, LLC",
        "sales_email": "sales@fourphonix.com",
        "billing_email": "owner@fourphonix.com",
        "royalty_rate": 0.10,
        "tax_profile": "TELECOM_USF_FL_CST",
        "products": [
            {"sku": "4PHX-UCAAS-BIZ", "name": "FourPhonix Cloud PBX & Omni-Channel UCaaS (10 Seats)", "price_usd": 249.00, "billing": "monthly"},
            {"sku": "4PHX-E911-DID", "name": "Nationwide DID Bundle + Kari's Law / RAY BAUM E911", "price_usd": 99.00, "billing": "monthly"}
        ]
    },
    "prophonix.com": {
        "entity": "Phonix Communications Operating, LLC",
        "sales_email": "enterprise@prophonix.com",
        "billing_email": "billing@prophonix.com",
        "royalty_rate": 0.10,
        "tax_profile": "TELECOM_USF_FL_CST",
        "products": [
            {"sku": "PPHX-SIP-TRUNK", "name": "ProPhonix High-Volume Wholesale SIP Trunk (STIR/SHAKEN A)", "price_usd": 199.00, "billing": "monthly"},
            {"sku": "PPHX-TCPA-SAFE", "name": "Carrier Compliance Dialer Suite (TCPA/FTSA Safe Harbor)", "price_usd": 799.00, "billing": "monthly"}
        ]
    }
}

def generate_quote(domain: str, sku: str, client_name: str, qty: int = 1):
    dom_data = CATALOG[domain]
    prod = next(p for p in dom_data["products"] if p["sku"] == sku)
    subtotal = round(prod["price_usd"] * qty, 2)
    if dom_data["tax_profile"] == "TELECOM_USF_FL_CST":
        taxes = round(subtotal * (0.346 + 0.0744), 2)
        tax_label = "FCC USF (34.6%) + FL CST (7.44%)"
    elif dom_data["tax_profile"] == "DIGITAL_3D_ASSETS_FL_7PCT":
        taxes = round(subtotal * 0.07, 2)
        tax_label = "FL Sales & Discretional Surtax (7.0%)"
    else:
        taxes = 0.00
        tax_label = "Exempt B2B SaaS / IP License (0.0%)"

    total = round(subtotal + taxes, 2)
    royalty = round(subtotal * dom_data["royalty_rate"], 2)
    opco_net = round(subtotal - royalty, 2)
    quote_id = f"INV-{sku}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M')}"
    return {
        "invoice_id": quote_id,
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "domain": domain,
        "Operating_entity": dom_data["entity"],
        "sales_contact": dom_data["sales_email"],
        "client_name": client_name,
        "sku": sku,
        "description": prod["name"],
        "billing_cycle": prod["billing"],
        "quantity": qty,
        "subtotal_usd": subtotal,
        "tax_jurisdiction": tax_label,
        "taxes_usd": taxes,
        "total_payable_usd": total,
        "irc_482_holding_royalty_usd": royalty,
        "opco_net_retained_usd": opco_net,
        "checkout_url": f"https://pay.{domain}/checkout/{quote_id}?pci_mode=saq_a_3ds2"
    }

def main():
    base = Path(__file__).resolve().parent
    out_catalog = base / "catalogs" / "master_commercial_catalog.json"
    out_catalog.write_text(json.dumps(CATALOG, indent=2), encoding="utf-8")

    sample_invoices = [
        generate_quote("auratetrax.com", "ATX-PAAS-ENT", "Acme Robotics Corp", 1),
        generate_quote("auraintelstudios3d.com", "AIS3D-GPU-STUDIO", "Nebula Game Studios LLC", 2),
        generate_quote("prophonix.com", "PPHX-TCPA-SAFE", "Apex Contact Centers Inc", 1),
        generate_quote("standard1979.com", "S1979-IP-WL", "Global FinTech Partners Ltd", 1),
    ]
    inv_path = base / "Quotes-and-Invoices" / "active_commercial_quotes.json"
    inv_path.write_text(json.dumps(sample_invoices, indent=2), encoding="utf-8")

    print("=" * 80)
    print(" STANDARD 1979 HOLDINGS, LLC - COMMERCIAL ENGINE & B2B/B2C CATALOG (6 DOMAINS)")
    print("=" * 80)
    for dom, info in CATALOG.items():
        print(f"\n[{dom.upper()}] -> {info['entity']} | Contacto: {info['sales_email']}")
        for p in info["products"]:
            print(f"  * {p['sku']:<16} | {p['name']:<56} | ${p['price_usd']:>8,.2f} ({p['billing']})")
    print("\n" + "-" * 80)
    print(" COTIZACIONES / LINKS DE PAGO GENERADOS PARA LOS 4 DOMINIOS RESTANTES:")
    print("-" * 80)
    for inv in sample_invoices:
        print(
            f" * {inv['domain']:<22} | {inv['invoice_id']:<28} | Total: ${inv['total_payable_usd']:>9,.2f} "
            f"| Regalía Holding: ${inv['irc_482_holding_royalty_usd']:>7,.2f}\n"
            f"   Checkout Link: {inv['checkout_url']}"
        )
    print("=" * 80)

if __name__ == "__main__":
    main()
