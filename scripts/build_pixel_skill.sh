#!/bin/bash
# Assemble dist/pixel-fc.skill : SKILL.md pixel.fc + moteurs (pixel, tactique, karaoké, rstyle) + polices pixel + convertisseur de vidéos.
set -e
cd "$(dirname "$0")/.."
T=$(mktemp -d); S=$T/pixel-fc; mkdir -p $S/engine $S/fonts $S/scripts $S/rennes
cp .claude/skills/pixel-fc/SKILL.md $S/
cp engine/pixelart.py engine/pixel.py engine/tactique.py engine/karaoke.py $S/engine/; mkdir -p $S/exemple; cp episodes/rabiot_px/rabiot_px.py $S/exemple/
cp episodes/rennes/rstyle.py $S/rennes/
cp assets/fonts/Silkscreen-*.ttf /tmp/edu-assets/fonts/LilitaOne-Regular.ttf assets/fonts/PressStart2P-Regular.ttf $S/fonts/
cp scripts/pixelize_video.py $S/scripts/
(cd $T && zip -qr pixel-fc.skill pixel-fc) && mv $T/pixel-fc.skill dist/ && rm -rf $T && ls -la dist/pixel-fc.skill
