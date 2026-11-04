import base64
import hashlib
import hmac
import json
import sys
from decimal import Decimal
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization

# Agregar rutas de los módulos del ecosistema
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "phonix-opco" / "telecom-compliance"))
sys.path.insert(0, str(ROOT_DIR / "finance-tax-engine"))
sys.path.insert(0, str(ROOT_DIR / "aura-opco" / "sso-oidc-provider"))

from phonix_telecom_gatekeeper import PhonixComplianceGatekeeper
from s1979_billing_tax_royalty_engine import ROYALTY_RATES, TelecomTaxQuoteRequest, calculate_telecom_taxes
from aura_oidc_sso_server import issue_federated_jwt, TokenExchangeRequest

def test_1_stir_shaken_es256_signature_and_florida_ftsa():
    # Generar llave ECDSA P-256 efímera para prueba STIR/SHAKEN
    priv_key = ec.generate_private_key(ec.SECP256R1())
    pem_bytes = priv_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    gatekeeper = PhonixComplianceGatekeeper(
        sti_ca_cert_url="https://sti-ca.prophonix.com/certs/phonix-opco-2026.cer",
        private_key_pem=pem_bytes
    )

    # 1. Probar generación de cabecera SIP Identity (RFC 8224 / RFC 8225 PASSporT)
    identity_hdr, orig_id = gatekeeper.build_stir_shaken_identity_header(
        orig_e164="+14075550100",
        dest_e164="+13055550199",
        attestation_level="A"
    )
    assert "alg=ES256;ppt=shaken" in identity_hdr
    assert len(orig_id) == 36
    print(f"[PASS] STIR/SHAKEN Attestation 'A' firmada con éxito (origid: {orig_id})")

    # 2. Probar bloqueo por límite de 3 llamadas en 24h en Florida (FTSA - Fla. Stat. § 501.059)
    allowed, reason = gatekeeper.check_calling_window_and_frequency(
        dest_e164="+14075550199",
        recipient_tz_name="America/New_York",
        calls_in_last_24h=3
    )
    # Si estamos fuera de horario (8am-8pm) o en >=3 llamadas, debe bloquear
    assert allowed is False
    print(f"[PASS] Regla Florida FTSA verificada correctamente: {reason}")

    # 3. Probar generación XML E911 PIDF-LO (RAY BAUM's Act & Kari's Law)
    pidf_xml = gatekeeper.build_e911_pidf_lo_xml(
        caller_e164="+14075550100",
        domain="fourphonix.com",
        state="FL",
        city="Orlando",
        street_name="Orange",
        street_suffix="Ave",
        house_number="400",
        building="Tower 1",
        floor="8",
        suite_unit="Suite 820",
        postal_code="32801"
    )
    assert "<ca:FLR>8</ca:FLR>" in pidf_xml and "<ca:UNIT>Suite 820</ca:UNIT>" in pidf_xml
    print("[PASS] Objeto de Ubicación Despachable E911 (PIDF-LO XML) validado.")

async def test_2_telecom_taxes_and_irc482_royalties():
    quote_req = TelecomTaxQuoteRequest(
        domain="prophonix.com",
        customer_zip="32801",
        state_code="FL",
        gross_voice_charge_usd=Decimal("1000.00"),
        lines_count=10
    )
    res = await calculate_telecom_taxes(quote_req)
    assert Decimal(res["taxes_breakdown"]["fcc_universal_service_fund_usf"]) > Decimal("0.00")
    assert Decimal(res["taxes_breakdown"]["e911_emergency_fee"]) == Decimal("4.00")
    print(f"[PASS] Impuestos Telecom (FCC USF + E911 + FL CST) calculados: Total Tax = ${res['total_tax_usd']} USD")

    # Verificar tasas de regalías IRC § 482 para los dominios operativos hacia standard1979.com
    assert ROYALTY_RATES["auraintelcore.com"] == Decimal("0.15")
    assert ROYALTY_RATES["prophonix.com"] == Decimal("0.10")
    print("[PASS] Tabulador de Regalías Inter-Compañía (IRC § 482) hacia standard1979.com verificado.")

async def test_3_oauth21_pkce_sso_jwt():
    verifier = "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk_standard1979_pkce"
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode("ascii")).digest()).rstrip(b"=").decode("ascii")

    req = TokenExchangeRequest(
        client_id="https://auraintelstudios3d.com",
        subject_user_id="usr_1979AURA3D000001",
        tenant_id="tnt_ENTPRISE00000001",
        code_verifier=verifier,
        expected_code_challenge=challenge
    )
    token_resp = await issue_federated_jwt(req)
    assert token_resp["token_type"] == "Bearer"
    assert len(token_resp["access_token"].split(".")) == 3
    print("[PASS] SSO OIDC / OAuth 2.1 (PKCE S256 + RS256 JWT) emitido para AuraIntelStudios3D.com.")

if __name__ == "__main__":
    import asyncio
    print("==================================================================")
    print(" EJECUTANDO SUITE DE AUDITORÍA FUNCIONAL - STANDARD 1979 ECOSYSTEM")
    print("==================================================================")
    test_1_stir_shaken_es256_signature_and_florida_ftsa()
    asyncio.run(test_2_telecom_taxes_and_irc482_royalties())
    asyncio.run(test_3_oauth21_pkce_sso_jwt())
    print("==================================================================")
    print(" 100% DE LAS PRUEBAS TÉCNICAS, LEGALES Y FISCALES APROBADAS")
    print("==================================================================")
