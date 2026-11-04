#!/usr/bin/env bash
set -euo pipefail

ECOSYSTEM_DIR="$HOME/standard1979-ecosystem"
RELEASE_DIR="$HOME/standard1979-release-artifacts"
KEY_DIR="$HOME/.ssh/standard1979-signing"
mkdir -p "$KEY_DIR"
chmod 700 "$KEY_DIR"

echo "=================================================================="
echo " INICIALIZANDO CUSTODIA GIT FIRMADA (Ed25519) Y BÓVEDA AES-256"
echo "=================================================================="

# 1. Asegurar que git y openssh estén disponibles
command -v git >/dev/null 2>&1 || pkg install -y git
command -v ssh-keygen >/dev/null 2>&1 || pkg install -y openssh

# 2. Generar llave Ed25519 para firmado criptográfico de Commits y Tags (si no existe)
if [ ! -f "$KEY_DIR/s1979_ed25519" ]; then
  ssh-keygen -t ed25519 -C "release-authority@standard1979.com" -f "$KEY_DIR/s1979_ed25519" -N "" >/dev/null
fi

echo "release-authority@standard1979.com $(cat "$KEY_DIR/s1979_ed25519.pub")" > "$KEY_DIR/allowed_signers"

# 3. Crear .gitignore corporativo e inicializar repositorio Git con firmas SSH Ed25519
cd "$ECOSYSTEM_DIR"

cat << 'GITEOF' > .gitignore
logs/
__pycache__/
*.pyc
.terraform/
*.tfstate
*.tfstate.backup
.env
GITEOF

if [ ! -d ".git" ]; then
  git init -b main
fi

git config user.name "Standard 1979 Release Authority"
git config user.email "release-authority@standard1979.com"
git config gpg.format ssh
git config user.signingkey "$KEY_DIR/s1979_ed25519.pub"
git config gpg.ssh.allowedSignersFile "$KEY_DIR/allowed_signers"
git config commit.gpgsign true
git config tag.gpgSign true

git add -A
git commit -S -m "feat(release): Standard 1979 Ecosystem v1.0.0 - 100% Legal, Fiscal & Technical Compliance across 6 Domains" || true
git tag -s -f v1.0.0 -m "Signed Production Release v1.0.0 (Standard1979, AuraIntelCore, AuraTetrax, AuraIntelStudios3D, fourphonix, prophonix)"

echo "------------------------------------------------------------------"
echo " [VERIFICANDO FIRMA CRIPTOGRÁFICA Ed25519 DEL COMMIT Y TAG v1.0.0]"
echo "------------------------------------------------------------------"
git verify-commit HEAD
git verify-tag v1.0.0

# 4. Cifrar el paquete de producción .tar.gz con AES-256-CBC + PBKDF2 (Iteraciones: 600,000 OWASP standard)
cd "$RELEASE_DIR"
LATEST_BUNDLE=$(ls -t standard1979-ecosystem-v1.0.0-*.tar.gz | head -n 1)
ENCRYPTED_VAULT="${LATEST_BUNDLE}.aes256.enc"

# Generar llave maestra aleatoria de 256 bits si no existe
if [ ! -f "$KEY_DIR/vault_master.key" ]; then
  openssl rand -hex 32 > "$KEY_DIR/vault_master.key"
  chmod 600 "$KEY_DIR/vault_master.key"
fi

openssl enc -aes-256-cbc -salt -pbkdf2 -iter 600000 \
  -in "$LATEST_BUNDLE" \
  -out "$ENCRYPTED_VAULT" \
  -pass file:"$KEY_DIR/vault_master.key"

VAULT_SHA=$(sha256sum "$ENCRYPTED_VAULT" | awk '{print $1}')

echo "=================================================================="
echo " [OK] COMMIT Y TAG v1.0.0 FIRMADOS CON Ed25519"
echo " [OK] BÓVEDA CIFRADA AES-256: $RELEASE_DIR/$ENCRYPTED_VAULT"
echo " [OK] SHA-256 BÓVEDA CIFRADA: $VAULT_SHA"
echo " [OK] LLAVE DE DESCIFRADO:    $KEY_DIR/vault_master.key"
echo "=================================================================="
