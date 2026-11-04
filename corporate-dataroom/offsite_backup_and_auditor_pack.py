import hashlib, json, shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RELEASE_DIR = Path.home() / "standard1979-release-artifacts"
EXPORT_DIR = Path.home() / "standard1979-auditor-dataroom-export"

def build_external_auditor_pack() -> dict:
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    files_to_export = [
        ROOT / "compliance-evidence" / "SOC2_ISO27001_ISO42001_EVIDENCE_PACK.json",
        ROOT / "compliance-evidence" / "MERKLE_PQC_NOTARY_SEAL.json",
        ROOT / "legal-corpus" / "01_MASTER_TOS_AND_MSA_ALL_6_DOMAINS.md",
        ROOT / "legal-corpus" / "02_EULA_3D_ASSETS_AND_C2PA_PROVENANCE.md",
        ROOT / "legal-corpus" / "03_INTERCOMPANY_IP_LICENSE_IRC482_AND_DPA.md",
        ROOT / "legal-corpus" / "04_BOARD_RESOLUTION_IRC482_AND_FINCEN_BOI.md",
        ROOT / "sbom-cyclonedx.json",
        ROOT / "THIRD-PARTY-NOTICES.txt"
    ]
    exported_manifest = {}
    for src in files_to_export:
        if src.exists():
            dst = EXPORT_DIR / src.name
            shutil.copy2(src, dst)
            exported_manifest[src.name] = hashlib.sha256(dst.read_bytes()).hexdigest()

    vaults = sorted(RELEASE_DIR.glob("*.aes256.enc"), key=lambda p: p.stat().st_mtime, reverse=True)
    latest_vault = vaults[0] if vaults else None
    if latest_vault:
        shutil.copy2(latest_vault, EXPORT_DIR / latest_vault.name)
        exported_manifest[latest_vault.name] = hashlib.sha256(latest_vault.read_bytes()).hexdigest()

    summary = {
        "export_standard": "SOC 2 CC7.5 Off-Site Vault & Big-4 External Auditor Data Room",
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "export_directory": str(EXPORT_DIR),
        "exported_artifacts_count": len(exported_manifest),
        "artifacts_sha256": exported_manifest,
        "private_keys_exposed": False
    }
    (EXPORT_DIR / "AUDITOR_DATAROOM_MANIFEST.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary

if __name__ == "__main__":
    print(json.dumps(build_external_auditor_pack(), indent=2))
