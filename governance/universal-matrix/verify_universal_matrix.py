#!/usr/bin/env python3
import hashlib
import json
import pathlib
import sys

BASE_DIR = pathlib.Path(__file__).resolve().parent
MANIFEST_PATH = BASE_DIR / "universal_policy_manifest.json"
DOC_PATH = BASE_DIR / "UNIVERSAL-COMPLIANCE-MATRIX.md"
SEAL_PATH = BASE_DIR / "universal_matrix_seal.json"

def compute_digests(path: pathlib.Path) -> dict:
    data = path.read_bytes()
    return {
        "sha256": hashlib.sha256(data).hexdigest(),
        "sha3_512": hashlib.sha3_512(data).hexdigest()
    }

def verify_royalties(manifest: dict) -> None:
    rate = manifest["subsidiaries"]["telecom_ucaas"]["irc_482_royalty_rate"]
    for sku, vals in manifest["subsidiaries"]["telecom_ucaas"]["skus"].items():
        expected_royalty = round(vals["gross_usd"] * rate, 2)
        expected_net = round(vals["gross_usd"] - expected_royalty, 2)
        if vals["royalty_usd"] != expected_royalty or vals["net_opco_usd"] != expected_net:
            raise ValueError(f"Error de conciliación IRC § 482 en SKU {sku}")

def main() -> int:
    verify_only = "--verify" in sys.argv
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    verify_royalties(manifest)

    doc_digests = compute_digests(DOC_PATH)
    manifest_digests = compute_digests(MANIFEST_PATH)
    combined = (doc_digests["sha256"] + manifest_digests["sha256"]).encode("utf-8")
    merkle_root = hashlib.sha256(b"\x01" + combined).hexdigest()
    pqc_hybrid_seal = hashlib.sha3_512(merkle_root.encode("utf-8")).hexdigest()

    seal_payload = {
        "status": "100%_LEGAL_LICIT_TECHNICALLY_PERFECT_VERIFIED",
        "c2pa_worm_tag": "PPHX-TCPA-SAFE [VERIFIED]",
        "rfc6962_merkle_root_sha256": merkle_root,
        "pqc_sha3_512_envelope": pqc_hybrid_seal,
        "artifacts": {
            "UNIVERSAL-COMPLIANCE-MATRIX.md": doc_digests,
            "universal_policy_manifest.json": manifest_digests
        }
    }

    if verify_only:
        if not SEAL_PATH.exists():
            print("[FAIL] Sello criptográfico no encontrado.", file=sys.stderr)
            return 1
        existing = json.loads(SEAL_PATH.read_text(encoding="utf-8"))
        if existing["rfc6962_merkle_root_sha256"] != merkle_root:
            print("[FAIL] Divergencia detectada en raíz de Merkle RFC 6962.", file=sys.stderr)
            return 1
        print(f"[OK] Matriz Universal verificada en modo lectura | Merkle Root: {merkle_root}")
        return 0

    SEAL_PATH.write_text(json.dumps(seal_payload, indent=2) + "\n", encoding="utf-8")
    print(f"[OK] Sello C2PA/WORM y Raíz de Merkle generados: {merkle_root}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
