import base64
import hashlib
import json
import time
import uuid
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec

FLORIDA_AREA_CODES = {
    "239", "305", "321", "324", "352", "386", "407", "448",
    "561", "645", "656", "689", "727", "754", "772", "786",
    "813", "850", "863", "904", "941", "954"
}

class PhonixComplianceGatekeeper:
    """
    Motor de cumplimiento FCC / TCPA / FTSA / STIR-SHAKEN / E911
    para fourphonix.com y prophonix.com.
    """
    def __init__(self, sti_ca_cert_url: str, private_key_pem: bytes):
        self.sti_ca_cert_url = sti_ca_cert_url
        self.private_key = serialization.load_pem_private_key(private_key_pem, password=None)

    @staticmethod
    def _b64url_encode(data: bytes) -> str:
        return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")

    @staticmethod
    def _get_local_datetime(tz_name: str) -> datetime:
        try:
            return datetime.now(ZoneInfo(tz_name))
        except ZoneInfoNotFoundError:
            # Fallback seguro a Eastern Standard Time (UTC-5) para entornos aislados sin tzdata
            return datetime.now(timezone(timedelta(hours=-5)))

    def check_calling_window_and_frequency(
        self,
        dest_e164: str,
        recipient_tz_name: str,
        calls_in_last_24h: int
    ) -> tuple[bool, str]:
        digits = dest_e164.lstrip("+")
        area_code = digits[1:4] if digits.startswith("1") and len(digits) == 11 else ""
        is_florida = area_code in FLORIDA_AREA_CODES

        local_now = self._get_local_datetime(recipient_tz_name)
        hour = local_now.hour

        if is_florida:
            if hour < 8 or hour >= 20:
                return False, "BLOCKED_FL_FTSA_HOURS: Florida calls allowed strictly between 08:00 and 20:00 local time."
            if calls_in_last_24h >= 3:
                return False, "BLOCKED_FL_FTSA_FREQUENCY: Maximum 3 calls per 24-hour period reached for Florida number."
        else:
            if hour < 8 or hour >= 21:
                return False, "BLOCKED_TCPA_FEDERAL_HOURS: Calls allowed strictly between 08:00 and 21:00 local time."

        return True, "ALLOWED"

    def build_stir_shaken_identity_header(
        self,
        orig_e164: str,
        dest_e164: str,
        attestation_level: str = "A"
    ) -> tuple[str, str]:
        if attestation_level not in ("A", "B", "C"):
            raise ValueError("Invalid STIR/SHAKEN attestation level. Must be A, B, or C.")

        orig_id = str(uuid.uuid4())
        header = {
            "alg": "ES256",
            "ppt": "shaken",
            "typ": "passport",
            "x5u": self.sti_ca_cert_url
        }
        payload = {
            "attest": attestation_level,
            "dest": {"tn": [dest_e164]},
            "iat": int(time.time()),
            "orig": {"tn": orig_e164},
            "origid": orig_id
        }

        h_b64 = self._b64url_encode(json.dumps(header, separators=(",", ":")).encode())
        p_b64 = self._b64url_encode(json.dumps(payload, separators=(",", ":")).encode())
        signing_input = f"{h_b64}.{p_b64}".encode("ascii")

        signature_der = self.private_key.sign(signing_input, ec.ECDSA(hashes.SHA256()))
        s_b64 = self._b64url_encode(signature_der)

        identity_header = (
            f"{h_b64}.{p_b64}.{s_b64};"
            f"info=<{self.sti_ca_cert_url}>;alg=ES256;ppt=shaken"
        )
        return identity_header, orig_id

    @staticmethod
    def build_e911_pidf_lo_xml(
        caller_e164: str,
        domain: str,
        state: str,
        city: str,
        street_name: str,
        street_suffix: str,
        house_number: str,
        building: str,
        floor: str,
        suite_unit: str,
        postal_code: str
    ) -> str:
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<presence xmlns="urn:ietf:params:xml:ns:pidf"
          xmlns:gp="urn:ietf:params:xml:ns:pidf:geopriv10"
          xmlns:ca="urn:ietf:params:xml:ns:pidf:geopriv10:civicAddr"
          entity="pres:{caller_e164}@{domain}">
  <tuple id="phonix-e911-dispatchable-location">
    <status>
      <gp:geopriv>
        <gp:location-info>
          <ca:civicAddress>
            <ca:country>US</ca:country>
            <ca:A1>{state}</ca:A1>
            <ca:A3>{city}</ca:A3>
            <ca:RD>{street_name}</ca:RD>
            <ca:STS>{street_suffix}</ca:STS>
            <ca:HNO>{house_number}</ca:HNO>
            <ca:BLD>{building}</ca:BLD>
            <ca:FLR>{floor}</ca:FLR>
            <ca:UNIT>{suite_unit}</ca:UNIT>
            <ca:PC>{postal_code}</ca:PC>
          </ca:civicAddress>
        </gp:location-info>
        <gp:usage-rules/>
      </gp:geopriv>
    </status>
  </tuple>
</presence>"""
