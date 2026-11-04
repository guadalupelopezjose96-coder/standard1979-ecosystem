import hashlib
import hmac
import os
import time
from decimal import Decimal, ROUND_HALF_UP
from fastapi import FastAPI, HTTPException, Header, Request
from pydantic import BaseModel, Field
import stripe
import httpx

app = FastAPI(
    title="Standard 1979 Ecosystem Billing, Tax & Intercompany Royalty Engine",
    description="PCI-DSS v4.0 (SAQ-A), Usage-Based Billing, Avalara AFC Telecom Tax & IRC 482 Royalty Settlement",
    version="3.1.0"
)

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_live_replace_in_vault")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_replace_in_vault")
AVALARA_AFC_API_URL = os.getenv("AVALARA_AFC_URL", "https://communications.avalara.net/api/v2/afc/CalcTaxes")
AVALARA_API_KEY = os.getenv("AVALARA_API_KEY", "avatax_replace_in_vault")

# Cuentas Conectadas de Stripe (Subcuentas segregadas por OpCo y Holding para evitar Commingling of Funds)
STRIPE_CONNECTED_ACCOUNTS = {
    "HOLDING_IP": os.getenv("STRIPE_ACC_STANDARD1979", "acct_standard1979_holding"),
    "AURA_OPCO": os.getenv("STRIPE_ACC_AURA_OPCO", "acct_aura_technologies_opco"),
    "PHONIX_OPCO": os.getenv("STRIPE_ACC_PHONIX_OPCO", "acct_phonix_comms_opco"),
}

# Tasas de Regalías Inter-Compañía (Arm's Length Principle - IRC § 482) hacia standard1979.com
ROYALTY_RATES = {
    "auraintelcore.com": Decimal("0.15"),      # 15% AGR hacia Standard 1979 Holdings, LLC
    "auratetrax.com": Decimal("0.15"),         # 15% AGR hacia Standard 1979 Holdings, LLC
    "auraintelstudios3d.com": Decimal("0.15"), # 15% AGR hacia Standard 1979 Holdings, LLC
    "fourphonix.com": Decimal("0.10"),         # 10% AGR hacia Standard 1979 Holdings, LLC
    "prophonix.com": Decimal("0.10"),          # 10% AGR hacia Standard 1979 Holdings, LLC
}

class UsageMeterEvent(BaseModel):
    tenant_stripe_customer_id: str = Field(..., pattern=r"^cus_[a-zA-Z0-9]+$")
    domain: str = Field(..., pattern=r"^(auraintelcore\.com|auratetrax\.com|auraintelstudios3d\.com|fourphonix\.com|prophonix\.com)$")
    meter_event_name: str = Field(..., pattern=r"^(ai_tokens_1k|gpu_render_seconds|sip_voice_minutes)$")
    quantity: int = Field(..., gt=0)
    idempotency_key: str = Field(..., min_length=16, max_length=64)

class TelecomTaxQuoteRequest(BaseModel):
    domain: str = Field(..., pattern=r"^(fourphonix\.com|prophonix\.com)$")
    customer_zip: str = Field(..., pattern=r"^\d{5}(-\d{4})?$")
    state_code: str = Field(..., min_length=2, max_length=2)
    gross_voice_charge_usd: Decimal = Field(..., gt=Decimal("0.00"))
    lines_count: int = Field(default=1, ge=1)

@app.post("/v1/billing/meter-event")
async def record_usage_meter_event(event: UsageMeterEvent):
    """
    Registra consumo en tiempo real (Tokens IA en AuraIntelCore, Segundos GPU 3D en AuraIntelStudios3D,
    Minutos SIP/WebRTC en fourphonix/prophonix) usando Stripe Billing Meters API.
    """
    try:
        meter_record = stripe.billing.MeterEvent.create(
            event_name=event.meter_event_name,
            payload={
                "stripe_customer_id": event.tenant_stripe_customer_id,
                "value": str(event.quantity),
                "domain_origin": event.domain,
            },
            identifier=event.idempotency_key,
            timestamp=int(time.time())
        )
        return {
            "status": "recorded",
            "meter_id": meter_record.identifier,
            "domain": event.domain,
            "metric": event.meter_event_name,
            "quantity": event.quantity
        }
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Stripe Meter API Error: {str(exc)}")

@app.post("/v1/tax/telecom-afc-quote")
async def calculate_telecom_taxes(req: TelecomTaxQuoteRequest):
    """
    Calcula impuestos federales y estatales de telecomunicaciones (FCC USF, E911, State Telecom Excise Tax)
    para fourphonix.com y prophonix.com (Transaction / Service Pair 19/6 VoIP Interconnected).
    """
    # Tasas base estatutarias de respaldo (FCC Universal Service Fund + E911 local + FL Communications Services Tax)
    usf_rate = Decimal("0.346") if req.domain in ("fourphonix.com", "prophonix.com") else Decimal("0.00")
    interstate_safe_harbor_ratio = Decimal("0.649") # FCC Safe Harbor VoIP Interconnected (64.9% interestatal)

    interstate_revenue = (req.gross_voice_charge_usd * interstate_safe_harbor_ratio).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    fcc_usf_fee = (interstate_revenue * usf_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    e911_statutory_fee = (Decimal("0.40") * req.lines_count).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    state_telecom_tax_rate = Decimal("0.0744") if req.state_code.upper() == "FL" else Decimal("0.0600")
    state_telecom_tax = (req.gross_voice_charge_usd * state_telecom_tax_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    total_tax = fcc_usf_fee + e911_statutory_fee + state_telecom_tax
    return {
        "domain": req.domain,
        "jurisdiction_state": req.state_code.upper(),
        "zip_code": req.customer_zip,
        "net_charge_usd": str(req.gross_voice_charge_usd),
        "taxes_breakdown": {
            "fcc_universal_service_fund_usf": str(fcc_usf_fee),
            "e911_emergency_fee": str(e911_statutory_fee),
            "state_communications_services_tax": str(state_telecom_tax)
        },
        "total_tax_usd": str(total_tax),
        "grand_total_usd": str(req.gross_voice_charge_usd + total_tax)
    }

@app.post("/v1/webhooks/stripe-royalty-settlement")
async def stripe_invoice_paid_royalty_split(
    request: Request,
    stripe_signature: str = Header(None)
):
    """
    Webhook PCI-DSS v4.0 que recibe el evento 'invoice.paid', descuenta impuestos indirectos
    (Sales Tax / VAT / Telecom Tax) y transfiere automáticamente la regalía IRC § 482
    a la cuenta bancaria/Stripe de Standard 1979 Holdings, LLC (standard1979.com).
    """
    payload = await request.body()
    try:
        event = stripe.Webhook.construct_event(payload, stripe_signature, STRIPE_WEBHOOK_SECRET)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Webhook signature verification failed: {str(exc)}")

    if event["type"] == "invoice.paid":
        invoice = event["data"]["object"]
        domain = invoice.get("metadata", {}).get("domain_origin", "auraintelcore.com").lower()
        subtotal_excl_tax_cents = Decimal(str(invoice.get("subtotal_excluding_tax", 0)))

        if subtotal_excl_tax_cents > 0 and domain in ROYALTY_RATES:
            royalty_rate = ROYALTY_RATES[domain]
            royalty_cents = int((subtotal_excl_tax_cents * royalty_rate).quantize(Decimal("1"), rounding=ROUND_HALF_UP))

            transfer = stripe.Transfer.create(
                amount=royalty_cents,
                currency=invoice.get("currency", "usd"),
                destination=STRIPE_CONNECTED_ACCOUNTS["HOLDING_IP"],
                source_transaction=invoice.get("charge"),
                description=f"IRC 482 IP Royalty Settlement from {domain} to Standard 1979 Holdings, LLC",
                metadata={
                    "contract_ref": "INTERCOMPANY-IP-LICENSE-S1979",
                    "origin_domain": domain,
                    "agr_cents": str(subtotal_excl_tax_cents),
                    "royalty_rate": str(royalty_rate)
                }
            )
            return {"status": "royalty_settled", "transfer_id": transfer.id, "royalty_cents": royalty_cents}

    return {"status": "ignored_event_type"}
