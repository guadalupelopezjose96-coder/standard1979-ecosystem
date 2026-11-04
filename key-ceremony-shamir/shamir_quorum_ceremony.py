import hashlib
import json
import secrets
from datetime import datetime, timezone
from pathlib import Path

# Aritmética sobre Campo de Galois GF(2^8) con polinomio irreducible AES (0x11B)
def _gf256_add(a: int, b: int) -> int:
    return a ^ b

def _gf256_mul(a: int, b: int) -> int:
    p = 0
    for _ in range(8):
        if b & 1:
            p ^= a
        hi = a & 0x80
        a = (a << 1) & 0xFF
        if hi:
            a ^= 0x1B
        b >>= 1
    return p

def _gf256_pow(a: int, exp: int) -> int:
    res = 1
    base = a
    while exp > 0:
        if exp & 1:
            res = _gf256_mul(res, base)
        base = _gf256_mul(base, base)
        exp >>= 1
    return res

def _gf256_inv(a: int) -> int:
    if a == 0:
        raise ZeroDivisionError("Cannot invert 0 in GF(256)")
    return _gf256_pow(a, 254)

def split_secret_gf256(secret: bytes, threshold_k: int = 3, total_n: int = 5) -> list[tuple[int, str]]:
    shares_bytes = [bytearray() for _ in range(total_n)]
    for byte_val in secret:
        # Polinomio aleatorio grado k-1 donde f(0) = byte_val
        coeffs = [byte_val] + [secrets.randbelow(255) + 1 for _ in range(threshold_k - 1)]
        for idx in range(1, total_n + 1):
            x = idx
            y = 0
            x_pow = 1
            for c in coeffs:
                y = _gf256_add(y, _gf256_mul(c, x_pow))
                x_pow = _gf256_mul(x_pow, x)
            shares_bytes[idx - 1].append(y)
    return [(i + 1, bytes(shares_bytes[i]).hex()) for i in range(total_n)]

def reconstruct_secret_gf256(shares: list[tuple[int, str]]) -> bytes:
    parsed = [(x, bytes.fromhex(y_hex)) for x, y_hex in shares]
    secret_len = len(parsed[0][1])
    out = bytearray()

    for byte_idx in range(secret_len):
        # Interpolación de Lagrange en x = 0 sobre GF(256)
        f_0 = 0
        for i, (xi, yi_bytes) in enumerate(parsed):
            yi = yi_bytes[byte_idx]
            num = 1
            den = 1
            for j, (xj, _) in enumerate(parsed):
                if i != j:
                    num = _gf256_mul(num, xj)
                    den = _gf256_mul(den, _gf256_add(xi, xj))
            lagrange_basis = _gf256_mul(num, _gf256_inv(den))
            f_0 = _gf256_add(f_0, _gf256_mul(yi, lagrange_basis))
        out.append(f_0)
    return bytes(out)

def run_key_ceremony() -> dict:
    key_file = Path.home() / ".ssh" / "standard1979-signing" / "vault_master.key"
    raw_secret = key_file.read_bytes().strip()
    original_sha256 = hashlib.sha256(raw_secret).hexdigest()

    custodians = [
        "Custodian-1 (Managing Member - Standard 1979 Holdings, LLC)",
        "Custodian-2 (General Counsel & Corporate Secretary)",
        "Custodian-3 (CISO - Aura Technologies Operating, LLC)",
        "Custodian-4 (VP Telecom Compliance - Phonix Communications Operating, LLC)",
        "Custodian-5 (Offline Bank Safety Deposit Box - Orlando, FL)"
    ]

    shares = split_secret_gf256(raw_secret, threshold_k=3, total_n=5)

    # Verificar matemáticamente que cualesquiera 3 custodios (ej. Custodios 1, 3 y 5) reconstruyen el 100% de la llave
    quorum_subset = [shares[0], shares[2], shares[4]]
    recovered = reconstruct_secret_gf256(quorum_subset)
    recovered_sha256 = hashlib.sha256(recovered).hexdigest()
    assert original_sha256 == recovered_sha256, "Shamir GF(256) reconstruction mismatch!"

    ceremony_manifest = {
        "ceremony_standard": "Shamir Secret Sharing Scheme (GF(256) Galois Field) - SOC2 CC6.1 / ISO 27001 A.8.24",
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "quorum_policy": "3-of-5 Executive Fiduciaries Required for Vault Decryption",
        "master_key_sha256_fingerprint": original_sha256,
        "quorum_reconstruction_test_3_of_5": "PASSED_100_PERCENT_BIT_IDENTICAL",
        "custodian_shares_metadata": [
            {
                "share_index": idx,
                "assigned_fiduciary": custodians[idx - 1],
                "share_commitment_sha256": hashlib.sha256(share_hex.encode()).hexdigest()
            }
            for idx, share_hex in shares
        ]
    }
    return ceremony_manifest

if __name__ == "__main__":
    print(json.dumps(run_key_ceremony(), indent=2))
