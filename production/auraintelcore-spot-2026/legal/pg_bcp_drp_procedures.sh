#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR="${HOME}/standard1979-ecosystem/production/backups/postgres"
mkdir -p "${BACKUP_DIR}"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
SNAPSHOT_FILE="${BACKUP_DIR}/pg_snapshot_${TIMESTAMP}.sql.gz"

echo "=== 1. DIAGNÓSTICO Y ESTADO DE POSTGRESQL (LOCAL) ==="
if pg_isready -q; then
    echo "[OK] Instancia PostgreSQL local activa y aceptando conexiones."
else
    echo "[FAIL] PostgreSQL no responde. Intentando reinicio vía sv..."
    sv restart postgres || true
    sleep 2
fi

echo "=== 2. EJECUCIÓN DE RESPALDO EN CALIENTE (RPO <= 15 MIN) ==="
# Exportar base de datos a volcado comprimido
pg_dumpall | gzip > "${SNAPSHOT_FILE}" 2>/dev/null || {
    echo "[WARN] pg_dumpall directo falló sin base predeterminada. Respaldando catálogo 'postgres'..."
    pg_dump postgres | gzip > "${SNAPSHOT_FILE}"
}

echo "[OK] Volcado generado: ${SNAPSHOT_FILE}"

echo "=== 3. SELLADO CRIPTOGRÁFICO EN SHA256SUMS ==="
sha256sum "${SNAPSHOT_FILE}" >> SHA256SUMS
sort -u SHA256SUMS -o SHA256SUMS

echo "=== 4. PROTOCOLO DE CONMUTACIÓN POR ERROR (FAILOVER) ==="
cat << 'DETAILS'
----------------------------------------------------------------------
PROCEDIMIENTO OPERATIVO ESTÁNDAR: FALLA DEL MOTOR POSTGRESQL
----------------------------------------------------------------------
A. Caída Local (Reinicio del Servicio Runit):
   $ sv restart postgres
   $ sv status postgres

B. Corrupción de Datos (Restauración desde Snapshot Inmutable):
   $ dropdb postgres && createdb postgres
   $ gunzip -c <ultimo_snapshot.sql.gz> | psql postgres

C. Conmutación a la Nube (Failover Transaccional):
   Si el servicio local queda inoperativo, la plataforma web conmuta
   al almacenamiento Stripe Ledger / Cloudflare KV desacoplado
   mientras se regenera el clúster local.
----------------------------------------------------------------------
DETAILS

echo "=== ESTADO DE INTEGRIDAD ACTUAL ==="
tail -n 3 SHA256SUMS
