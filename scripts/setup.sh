#!/bin/bash
# Installe les dépendances du moteur (à relancer à chaque nouveau conteneur).
set -e
A=${EDU_ASSETS:-/tmp/edu-assets}; mkdir -p $A/fonts
python3 -c "import PIL, numpy" 2>/dev/null || pip install pillow numpy --break-system-packages -q
command -v ffmpeg >/dev/null || (apt-get update -qq && apt-get install -y -qq ffmpeg)
for u in ofl/lilitaone/LilitaOne-Regular.ttf ofl/patrickhand/PatrickHand-Regular.ttf ofl/caveatbrush/CaveatBrush-Regular.ttf; do
  [ -f $A/fonts/$(basename $u) ] || curl -sfL -o $A/fonts/$(basename $u) https://raw.githubusercontent.com/google/fonts/main/$u
done
echo "OK -> $A"; ls $A/fonts
