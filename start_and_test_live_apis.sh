#!/usr/bin/env bash
set -euo pipefail

LOG_DIR="$HOME/standard1979-ecosystem/logs"
mkdir -p "$LOG_DIR"

echo "=================================================================="
echo " INICIANDO MICROSERVICIOS EN VIVO - STANDARD 1979 ECOSYSTEM"
echo "=================================================================="

# Detener instancias previas si existen
pkill -f "aura_oidc_sso_server:app" 2>/dev/null || true
pkill -f "s1979_billing_tax_royalty_engine:app" 2>/dev/null || true

# 1. Levantar SSO OIDC Provider (Puerto 8001)
cd "$HOME/standard1979-ecosystem/aura-opco/sso-oidc-provider"
nohup python3 -m uvicorn aura_oidc_sso_server:app --host 127.0.0.1 --port 8001 > "$LOG_DIR/s1979_sso.log" 2>&1 &
SSO_PID=$!

# 2. Levantar Finance, Tax & IRC 482 Royalty Engine (Puerto 8003)
cd "$HOME/standard1979-ecosystem/finance-tax-engine"
nohup python3 -m uvicorn s1979_billing_tax_royalty_engine:app --host 127.0.0.1 --port 8003 > "$LOG_DIR/s1979_fin.log" 2>&1 &
FIN_PID=$!

# Esperar a que ambos sockets HTTP estén listos
for i in {1..15}; do
  if curl -s http://127.0.0.1:8001/.well-known/openid-configuration >/dev/null 2>&1 && \
     curl -s http://127.0.0.1:8003/openapi.json >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

echo "[LIVE 1/3] Consultando OpenID Discovery en AuraIntelCore.com (127.0.0.1:8001)..."
curl -s http://127.0.0.1:8001/.well-known/openid-configuration | python3 -m json.tool

echo "[LIVE 2/3] Consultando JWKS (Llave Pública RSA RS256) en 127.0.0.1:8001..."
curl -s http://127.0.0.1:8001/.well-known/jwks.json | python3 -m json.tool

echo "[LIVE 3/3] Cotizando Impuestos Telecom (FCC USF + E911 + FL CST) en 127.0.0.1:8003..."
curl -s -X POST http://127.0.0.1:8003/v1/tax/telecom-afc-quote \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "fourphonix.com",
    "customer_zip": "32801",
    "state_code": "FL",
    "gross_voice_charge_usd": "500.00",
    "lines_count": 5
  }' | python3 -m json.tool

# Cerrar procesos de prueba limpiamente
kill "$SSO_PID" "$FIN_PID" 2>/dev/null || true

echo "=================================================================="
echo " AUDITORÍA DE ENDPOINTS HTTP EN VIVO COMPLETADA AL 100%"
echo "=================================================================="
