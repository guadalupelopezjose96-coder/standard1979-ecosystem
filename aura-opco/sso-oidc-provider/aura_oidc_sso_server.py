import base64
import hashlib
import json
import time
import uuid
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa

app = FastAPI(
    title="AuraIntelCore Central OIDC / OAuth 2.1 Federated IdP",
    description="Single Sign-On (SSO) Provider for standard1979.com, AuraIntelCore.com, AuraTetrax.com, AuraIntelStudios3D.com, fourphonix.com & prophonix.com",
    version="2.2.0"
)

_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
_public_key = _private_key.public_key()
KEY_ID = "s1979-oidc-rs256-2026-11"
ISSUER_URL = "https://auraintelcore.com"

ALLOWED_ECOSYSTEM_AUDIENCES = {
    "https://standard1979.com",
    "https://auraintelcore.com",
    "https://auratetrax.com",
    "https://auraintelstudios3d.com",
    "https://fourphonix.com",
    "https://prophonix.com"
}

class TokenExchangeRequest(BaseModel):
    client_id: str = Field(..., description="Dominio cliente registrado en el ecosistema")
    subject_user_id: str = Field(..., pattern=r"^usr_[a-zA-Z0-9]{16}$")
    tenant_id: str = Field(..., pattern=r"^tnt_[a-zA-Z0-9]{16}$")
    code_verifier: str = Field(..., min_length=43, max_length=128, description="RFC 7636 PKCE Verifier")
    expected_code_challenge: str = Field(..., description="SHA256 Base64URL PKCE Challenge guardado en sesión")
    scopes: list[str] = Field(default=["openid", "profile", "email", "aura:inference", "phonix:sip"])

def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")

def _int_to_b64url(val: int) -> str:
    byte_length = (val.bit_length() + 7) // 8
    return _b64url_encode(val.to_bytes(byte_length, "big"))

def _sign_rs256_jwt(header: dict, payload: dict, priv_key: rsa.RSAPrivateKey) -> str:
    h_b64 = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    p_b64 = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{h_b64}.{p_b64}".encode("ascii")
    signature = priv_key.sign(
        signing_input,
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    s_b64 = _b64url_encode(signature)
    return f"{h_b64}.{p_b64}.{s_b64}"

@app.get("/.well-known/openid-configuration")
async def openid_discovery():
    return {
        "issuer": ISSUER_URL,
        "authorization_endpoint": f"{ISSUER_URL}/oauth2/authorize",
        "token_endpoint": f"{ISSUER_URL}/oauth2/token",
        "jwks_uri": f"{ISSUER_URL}/.well-known/jwks.json",
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code", "refresh_token"],
        "code_challenge_methods_supported": ["S256"],
        "id_token_signing_alg_values_supported": ["RS256"]
    }

@app.get("/.well-known/jwks.json")
async def jwks_endpoint():
    pub_numbers = _public_key.public_numbers()
    return {
        "keys": [
            {
                "kty": "RSA",
                "use": "sig",
                "alg": "RS256",
                "kid": KEY_ID,
                "n": _int_to_b64url(pub_numbers.n),
                "e": _int_to_b64url(pub_numbers.e)
            }
        ]
    }

@app.post("/oauth2/token")
async def issue_federated_jwt(req: TokenExchangeRequest):
    if req.client_id not in ALLOWED_ECOSYSTEM_AUDIENCES:
        raise HTTPException(status_code=403, detail="Unauthorized domain audience.")

    computed_challenge = _b64url_encode(hashlib.sha256(req.code_verifier.encode("ascii")).digest())
    if computed_challenge != req.expected_code_challenge:
        raise HTTPException(status_code=400, detail="PKCE S256 verification failed.")

    now = int(time.time())
    jwt_header = {"alg": "RS256", "typ": "JWT", "kid": KEY_ID}
    jwt_claims = {
        "iss": ISSUER_URL,
        "sub": req.subject_user_id,
        "aud": req.client_id,
        "iat": now,
        "nbf": now,
        "exp": now + 900,
        "jti": str(uuid.uuid4()),
        "tenant_id": req.tenant_id,
        "scope": " ".join(req.scopes),
        "amr": ["pwd", "mfa", "hwk"]
    }

    signed_jwt = _sign_rs256_jwt(jwt_header, jwt_claims, _private_key)

    return {
        "access_token": signed_jwt,
        "id_token": signed_jwt,
        "token_type": "Bearer",
        "expires_in": 900,
        "scope": " ".join(req.scopes)
    }
