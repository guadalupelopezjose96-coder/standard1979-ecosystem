#!/usr/bin/env bash
set -euo pipefail

INPUT_PRORES="${1:-../assets/master_prores422hq.mov}"
OUTPUT_4K="../deliverables/auraintelcore_4k_master.mp4"
OUTPUT_1080P="../deliverables/auraintelcore_1080p_master.mp4"

mkdir -p ../deliverables

echo "=== [1/3] Verificando Parámetros ITU-R BS.1770-4 (-14 LUFS / -1.0 dBTP) ==="
AUDIO_FILTER="loudnorm=I=-14.0:TP=-1.0:LRA=7.0"

echo "=== [2/3] Renderizando Master 4K UHD (3840x2160, 24fps CFR, 45 Mbps) ==="
# Pase 1
ffmpeg -y -i "${INPUT_PRORES}" -c:v libx264 -preset slow -b:v 45M -maxrate 60M -bufsize 90M \
  -profile:v high -level 5.1 -pix_fmt yuv420p -r 24 -g 48 -keyint_min 48 -sc_threshold 0 \
  -pass 1 -an -f null /dev/null

# Pase 2 con Audio Masterizado
ffmpeg -y -i "${INPUT_PRORES}" -c:v libx264 -preset slow -b:v 45M -maxrate 60M -bufsize 90M \
  -profile:v high -level 5.1 -pix_fmt yuv420p -r 24 -g 48 -keyint_min 48 -sc_threshold 0 \
  -pass 2 -c:a aac -b:a 320k -ar 48000 -af "${AUDIO_FILTER}" \
  -movflags +faststart "${OUTPUT_4K}"

rm -f ffmpeg2pass-0.log*

echo "=== [3/3] Generando Versión 1080p Web (18 Mbps) ==="
ffmpeg -y -i "${OUTPUT_4K}" -vf "scale=1920:1080" -c:v libx264 -preset slow -b:v 18M \
  -maxrate 24M -bufsize 36M -profile:v high -level 4.2 -pix_fmt yuv420p -r 24 -g 48 \
  -c:a copy -movflags +faststart "${OUTPUT_1080P}"

echo "=== Renderizado completado exitosamente ==="
