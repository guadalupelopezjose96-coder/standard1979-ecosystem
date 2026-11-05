#!/usr/bin/env python3
"""
Standard 1979 Holdings, LLC - Deterministic Pure-Python PNG Generator for Stripe Connect
Generates sRGB PNGs: icon-512x512.png and logo-1200x300.png with tEXt Copyright CMI (17 USC 1202)
"""
import hashlib, json, pathlib, struct, zlib

DOMAINS = {
    "standard1979.com":       ((10, 25, 47),   (212, 175, 55),  "Standard 1979 Holdings, LLC"),
    "AuraIntelCore.com":      ((15, 23, 42),   (56, 189, 248),  "Aura Technologies Operating, LLC"),
    "AuraTetrax.com":         ((17, 24, 39),   (129, 140, 248), "Aura Technologies Operating, LLC"),
    "AuraIntelStudios3D.com": ((30, 27, 75),   (192, 132, 252), "Aura Technologies Operating, LLC"),
    "fourphonix.com":         ((6, 78, 59),    (52, 211, 153),  "Phonix Communications Operating, LLC"),
    "prophonix.com":          ((4, 47, 46),    (45, 212, 191),  "Phonix Communications Operating, LLC"),
}

def make_chunk(chunk_type: bytes, data: bytes) -> bytes:
    crc = zlib.crc32(chunk_type + data) & 0xFFFFFFFF
    return struct.pack(">I", len(data)) + chunk_type + data + struct.pack(">I", crc)

def build_png(width: int, height: int, bg: tuple, fg: tuple, domain: str, licensee: str) -> bytes:
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    srgb = struct.pack(">B", 0)
    cmi = f"Copyright\x00(c) 2026 Standard 1979 Holdings, LLC. Licensed to {licensee} ({domain}). Protected under 17 USC 1202.".encode("latin-1")
    rows = bytearray()
    border = max(6, min(width, height) // 32)
    cx, cy = width // 2, height // 2
    r_outer = (min(width, height) * 36) // 100
    r_inner = r_outer - border
    r_out_sq, r_in_sq = r_outer * r_outer, r_inner * r_inner

    for y in range(height):
        rows.append(0)
        dy_sq = (y - cy) * (y - cy)
        is_edge_y = (y < border) or (y >= height - border)
        for x in range(width):
            is_edge_x = (x < border) or (x >= width - border)
            dist_sq = (x - cx) * (x - cx) + dy_sq
            if is_edge_x or is_edge_y or (r_in_sq <= dist_sq <= r_out_sq):
                rows.extend(fg)
            else:
                rows.extend(bg)

    compressed = zlib.compress(bytes(rows), level=9)
    return (
        b"\x89PNG\r\n\x1a\n"
        + make_chunk(b"IHDR", ihdr)
        + make_chunk(b"sRGB", srgb)
        + make_chunk(b"tEXt", cmi)
        + make_chunk(b"IDAT", compressed)
        + make_chunk(b"IEND", b"")
    )

base = pathlib.Path(__file__).resolve().parent.parent / "assets"
ledger_path = base / "brand-cryptographic-ledger.json"
ledger = json.loads(ledger_path.read_text(encoding="utf-8"))

for dom, (bg, fg, licensee) in DOMAINS.items():
    d_dir = base / dom
    icon_bytes = build_png(512, 512, bg, fg, dom, licensee)
    logo_bytes = build_png(1200, 300, bg, fg, dom, licensee)
    (d_dir / "stripe-icon-512x512.png").write_bytes(icon_bytes)
    (d_dir / "stripe-logo-1200x300.png").write_bytes(logo_bytes)
    ledger["domains"][dom]["stripe_icon_sha256"] = hashlib.sha256(icon_bytes).hexdigest()
    ledger["domains"][dom]["stripe_logo_sha256"] = hashlib.sha256(logo_bytes).hexdigest()
    print(f"[OK] {dom:24s} -> stripe-icon-512x512.png & stripe-logo-1200x300.png")

ledger_path.write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n", encoding="utf-8")
