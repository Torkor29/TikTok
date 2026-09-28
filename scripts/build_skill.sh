#!/bin/bash
# Assemble le skill installable dist/tiktok-foot-legendes.skill à partir du repo.
set -e
cd "$(dirname "$0")/.."
T=$(mktemp -d); S=$T/tiktok-foot-legendes
mkdir -p $S/scripts $S/examples/messi $S/assets
cp SKILL.md $S/
cp engine/engine.py engine/foot.py scripts/setup.sh $S/scripts/
cp episodes/messi/messi.py $S/examples/messi/
cp output/messi/messi_legende_script.md $S/examples/messi/
cp -r assets/sfx $S/assets/
mkdir -p dist; rm -f dist/tiktok-foot-legendes.skill
(cd $T && zip -qr tiktok-foot-legendes.skill tiktok-foot-legendes) && mv $T/tiktok-foot-legendes.skill dist/
rm -rf $T; ls -la dist/
