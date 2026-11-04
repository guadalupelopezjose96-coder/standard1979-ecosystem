import json
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timezone

DOMAIN_LEDGER_SPECS = {
    "AuraIntelCore.com": {
        "opco": "Aura Technologies Operating, LLC",
        "royalty_rate": Decimal("0.15"),
        "unit_metric": "1M AI Tokens ( Safetensors vLLM )",
        "unit_cost_usd": Decimal("0.18"),
        "unit_price_usd": Decimal("1.50"),
        "monthly_units": 45000
    },
    "AuraTetrax.com": {
        "opco": "Aura Technologies Operating, LLC",
        "royalty_rate": Decimal("0.15"),
        "unit_metric": "Modular PaaS Node-Hour",
        "unit_cost_usd": Decimal("0.09"),
        "unit_price_usd": Decimal("0.85"),
        "monthly_units": 60000
    },
    "AuraIntelStudios3D.com": {
        "opco": "Aura Technologies Operating, LLC",
        "royalty_rate": Decimal("0.15"),
        "unit_metric": "NVIDIA H100 GPU Render Minute (C2PA)",
        "unit_cost_usd": Decimal("0.06"),
        "unit_price_usd": Decimal("0.45"),
        "monthly_units": 120000
    },
    "fourphonix.com": {
        "opco": "Phonix Communications Operating, LLC",
        "royalty_rate": Decimal("0.10"),
        "unit_metric": "STIR/SHAKEN SIP + AI Voice Minute",
        "unit_cost_usd": Decimal("0.004"),
        "unit_price_usd": Decimal("0.035"),
        "monthly_units": 850000
    },
    "prophonix.com": {
        "opco": "Phonix Communications Operating, LLC",
        "royalty_rate": Decimal("0.10"),
        "unit_metric": "Enterprise UCaaS Seat (E911 + CPNI)",
        "unit_cost_usd": Decimal("3.20"),
        "unit_price_usd": Decimal("29.00"),
        "monthly_units": 2500
    }
}

def generate_asc606_and_irc482_report() -> dict:
    q = Decimal("0.01")
    total_agr = Decimal("0.00")
    total_cogs = Decimal("0.00")
    total_holding_royalties = Decimal("0.00")
    breakdown = {}

    for domain, cfg in DOMAIN_LEDGER_SPECS.items():
        units = Decimal(str(cfg["monthly_units"]))
        agr = (units * cfg["unit_price_usd"]).quantize(q, rounding=ROUND_HALF_UP)
        cogs = (units * cfg["unit_cost_usd"]).quantize(q, rounding=ROUND_HALF_UP)
        royalty = (agr * cfg["royalty_rate"]).quantize(q, rounding=ROUND_HALF_UP)
        opco_net_margin = (agr - cogs - royalty).quantize(q, rounding=ROUND_HALF_UP)
        gross_margin_pct = (((agr - cogs) / agr) * Decimal("100")).quantize(q, rounding=ROUND_HALF_UP)

        total_agr += agr
        total_cogs += cogs
        total_holding_royalties += royalty

        breakdown[domain] = {
            "operating_subsidiary": cfg["opco"],
            "metric": cfg["unit_metric"],
            "recognized_revenue_asc606_usd": str(agr),
            "cloud_gpu_telecom_cogs_usd": str(cogs),
            "gross_margin_percent": f"{gross_margin_pct}%",
            "irc482_royalty_to_standard1979_usd": str(royalty),
            "opco_net_operating_income_usd": str(opco_net_margin)
        }

    return {
        "accounting_standard": "FASB ASC 606 & IRS IRC Section 482 Transfer Pricing",
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "holding_beneficiary": "Standard 1979 Holdings, LLC (standard1979.com)",
        "consolidated_summary_usd": {
            "total_ecosystem_agr_usd": str(total_agr),
            "total_cloud_and_carrier_cogs_usd": str(total_cogs),
            "total_royalties_settled_to_standard1979_usd": str(total_holding_royalties),
            "consolidated_ebitda_pre_opex_usd": str(total_agr - total_cogs)
        },
        "domain_unit_economics": breakdown
    }

if __name__ == "__main__":
    report = generate_asc606_and_irc482_report()
    print("================================================================================")
    print(" FINOPS UNIT ECONOMICS, ASC 606 REVENUE & IRC § 482 ROYALTY LEDGER (6 DOMAINS) ")
    print("================================================================================")
    print(json.dumps(report, indent=2))
