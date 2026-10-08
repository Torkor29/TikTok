#!/bin/bash
# Assemble dist/tiktok-foot-viral.skill (version « orientée vues ») : SKILL.md viral + méthode de la série + skill quiz + moteur + contrôle du rythme.
set -e
cd "$(dirname "$0")/.."
T=$(mktemp -d); S=$T/tiktok-foot-viral
mkdir -p $S/scripts $S/references $S/assets
cp .claude/skills/tiktok-foot-viral/SKILL.md $S/
cp SKILL.md $S/references/METHODE_SERIE.md
cp .claude/skills/tiktok-foot-quiz/SKILL.md $S/references/FORMAT_QUIZ.md
cp engine/engine.py engine/foot.py engine/story.py engine/quiz.py scripts/setup.sh scripts/check_rythme.py $S/scripts/
cp -r assets/sfx $S/assets/
mkdir -p dist; rm -f dist/tiktok-foot-viral.skill
(cd $T && zip -qr tiktok-foot-viral.skill tiktok-foot-viral) && mv $T/tiktok-foot-viral.skill dist/
ls -l dist/tiktok-foot-viral.skill
