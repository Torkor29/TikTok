#!/bin/bash
# Assemble le skill installable dist/tiktok-foot-quiz.skill (format quiz « T'es un vrai fan de X ? ») à partir du repo.
set -e
cd "$(dirname "$0")/.."
T=$(mktemp -d); S=$T/tiktok-foot-quiz
mkdir -p $S/scripts $S/examples/quiz_psg $S/examples/quiz_psg2 $S/assets
cp .claude/skills/tiktok-foot-quiz/SKILL.md $S/
cp SKILL.md $S/METHODE_SERIE.md
cp engine/engine.py engine/foot.py engine/story.py engine/quiz.py scripts/setup.sh scripts/minutage_provisoire_quiz.py $S/scripts/
cp -r episodes/quiz_psg/quiz_psg.py episodes/quiz_psg/textes_voix.json episodes/quiz_psg/alignement.json episodes/quiz_psg/voix \
      output/quiz_psg/quiz_psg_script.md $S/examples/quiz_psg/
cp episodes/quiz_psg2/quiz_psg2.py episodes/quiz_psg2/textes_voix.json episodes/quiz_psg2/alignement.json \
      output/quiz_psg2/quiz_psg2_script.md $S/examples/quiz_psg2/
cp -r assets/sfx $S/assets/
mkdir -p dist; rm -f dist/tiktok-foot-quiz.skill
(cd $T && zip -qr tiktok-foot-quiz.skill tiktok-foot-quiz) && mv $T/tiktok-foot-quiz.skill dist/
rm -rf $T; ls -la dist/
