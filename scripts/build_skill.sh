#!/bin/bash
# Assemble le skill installable dist/tiktok-foot-legendes.skill à partir du repo.
set -e
cd "$(dirname "$0")/.."
T=$(mktemp -d); S=$T/tiktok-foot-legendes
mkdir -p $S/scripts $S/examples/messi $S/examples/ronaldo $S/examples/zidane $S/examples/om $S/examples/neymar $S/examples/lemans $S/examples/dijon $S/examples/psg $S/examples/liverpool $S/assets
cp SKILL.md $S/
cp .claude/skills/tiktok-foot-legendes/SKILL.md $S/FINIR_UN_EPISODE.md
cp engine/engine.py engine/foot.py engine/story.py scripts/setup.sh scripts/minutage_provisoire.py $S/scripts/
cp episodes/messi/messi.py output/messi/messi_legende_script.md $S/examples/messi/
cp episodes/ronaldo/ronaldo.py episodes/ronaldo/alignement.json output/ronaldo/ronaldo_legende_script.md $S/examples/ronaldo/
cp episodes/zidane/zidane.py episodes/zidane/alignement.json output/zidane/zidane_legende_script.md $S/examples/zidane/
cp episodes/om/om.py episodes/om/alignement.json output/om/om_legende_script.md $S/examples/om/
cp episodes/neymar/neymar.py episodes/neymar/alignement.json output/neymar/neymar_legende_script.md $S/examples/neymar/
cp episodes/lemans/lemans.py episodes/lemans/alignement.json output/lemans/lemans_legende_script.md $S/examples/lemans/
cp episodes/dijon/dijon.py episodes/dijon/textes_voix.json output/dijon/dijon_legende_script.md $S/examples/dijon/
cp episodes/psg/psg.py episodes/psg/textes_voix.json output/psg/psg_legende_script.md $S/examples/psg/
cp episodes/liverpool/liverpool.py episodes/liverpool/textes_voix.json output/liverpool/liverpool_legende_script.md $S/examples/liverpool/
cp -r assets/sfx $S/assets/
mkdir -p dist; rm -f dist/tiktok-foot-legendes.skill
(cd $T && zip -qr tiktok-foot-legendes.skill tiktok-foot-legendes) && mv $T/tiktok-foot-legendes.skill dist/
rm -rf $T; ls -la dist/
