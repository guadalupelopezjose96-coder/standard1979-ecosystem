#!/usr/bin/env bash
set -euo pipefail

cd "$HOME/standard1979-ecosystem"
RELEASE_DIR="$HOME/standard1979-release-artifacts"
mkdir -p "$RELEASE_DIR"

TIMESTAMP=$(date -u +"%Y%m%dT%H%M%SZ")
BUNDLE_NAME="standard1979-ecosystem-v1.0.0-${TIMESTAMP}.tar.gz"
MANIFEST_FILE="$RELEASE_DIR/SHA256SUMS-${TIMESTAMP}.txt"

echo "=================================================================="
echo " GENERANDO MANIFIESTO CRIPTOGRÁFICO SHA-256 Y PAQUETE DE PRODUCCIÓN"
echo "=================================================================="

# 1. Generar hash SHA-256 de cada archivo de código, infraestructura y legal
find . -maxdepth 4 -type f \
  -not -path '*/.*' \
  -not -path './logs/*' \
  -not -name '*.pyc' \
  | sort | xargs sha256sum > "$MANIFEST_FILE"

cat "$MANIFEST_FILE"

# 2. Empaquetar todo el ecosistema excluyendo cachés temporales
tar --exclude='./logs' --exclude='__pycache__' -czf "$RELEASE_DIR/$BUNDLE_NAME" .

BUNDLE_HASH=$(sha256sum "$RELEASE_DIR/$BUNDLE_NAME" | awk '{print $1}')

echo "=================================================================="
echo " PAQUETE SELLADO: $RELEASE_DIR/$BUNDLE_NAME"
echo " SHA-256 DEL BUNDLE: $BUNDLE_HASH"
echo " MANIFIESTO AUDITORÍA: $MANIFEST_FILE"
echo "=================================================================="
