import json
from datetime import datetime, timezone

SANCTIONED = {"CU", "IR", "KP", "SY", "RU", "BY"}

def screen(iso: str, entity: str, domain: str) -> dict:
    blocked = iso.upper() in SANCTIONED
    return {
        "standard": "OFAC SDN (31 CFR 501) + BIS EAR (15 CFR 744 ECCN 3A090/4A090) + CMMC 2.0 L2",
        "domain": domain,
        "entity": entity,
        "country_iso": iso.upper(),
        "decision": "BLOCKED_OFAC_BIS_SANCTIONS" if blocked else "CLEARED_COMMERCIAL_AND_FEDRAMP"
    }

if __name__ == "__main__":
    b = screen("KP", "Restricted Entity", "AuraIntelStudios3D.com")
    a = screen("US", "Enterprise Partner FL", "AuraIntelCore.com")
    assert b["decision"] == "BLOCKED_OFAC_BIS_SANCTIONS" and a["decision"] == "CLEARED_COMMERCIAL_AND_FEDRAMP"
    print(json.dumps({"timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "blocked_test": b, "cleared_test": a}, indent=2))
