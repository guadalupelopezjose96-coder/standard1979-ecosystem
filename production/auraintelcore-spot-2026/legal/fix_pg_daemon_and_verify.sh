#!/usr/bin/env bash
set -euo pipefail

SV_POSTGRES_DIR="/data/data/com.termux/files/usr/var/service/postgres"

echo "=== 1. DESACTIVANDO BANDERA 'NORMALLY DOWN' ==="
if [ -f "${SV_POSTGRES_DIR}/down" ]; then
    rm -f "${SV_POSTGRES_DIR}/down"
    echo "[OK] Bandera 'down' eliminada."
fi

echo "=== 2. INICIANDO Y ASEGURANDO POSTGRESQL ==="
sv up postgres || true
sleep 2

sv status postgres

echo "=== 3. PRUEBA DE CONEXIÓN CON EL MOTOR ==="
if pg_isready -q; then
    echo "[OK] PostgreSQL activo y aceptando conexiones."
    psql -d postgres -c "SELECT version();" || psql -c "SELECT version();" || true
else
    echo "[INFO] Iniciando via pg_ctl si runsv no lo levanta directamente..."
    pg_ctl -D "${PREFIX}/var/lib/postgresql" start || true
    sleep 2
    pg_isready
fi

echo "=== 4. AUDITORIA DE REPOSITORIO GIT ==="
git status -s
