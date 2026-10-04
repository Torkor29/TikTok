"""Minutage provisoire d'un épisode quand les voix ElevenLabs ne sont pas encore générées (crédits épuisés…).

  python3 scripts/minutage_provisoire.py episodes/<club>/textes_voix.json <dossier_scratch>
  LEGENDES_PROVISOIRE=<dossier_scratch> python3 episodes/<club>/<club>.py output/<club> --stills

Écrit <dossier>/voix/scene_N.mp3 (silence de la durée estimée) et <dossier>/alignement.json (mots répartis à ~6 syllabes/s,
pauses de ponctuation), au même format que story.align_episode : les scènes s'écrivent et se contrôlent comme d'habitude.
Une fois les vraies voix téléchargées dans episodes/<club>/voix/, refaire l'alignement avec story.align_episode et relancer sans la variable.
"""
import json, os, re, subprocess, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "engine"))
from engine import _syll

RATE = 6.0                                     # syllabes par seconde hors pauses (voix Léo ≈ 5,2 syll/s pauses comprises)
PAUSES = (("…", .45), (".", .4), ("!", .4), ("?", .4), (":", .3), (",", .2))

def build(texts, out):
    os.makedirs(os.path.join(out, "voix"), exist_ok=True)
    words = {}
    for i, text in enumerate(texts, 1):
        tm, ws = .05, []
        for wd in text.split():
            n = sum(_syll(x) for x in wd.split("-") if x.strip(".,;:!?…'’")) or 1
            ws.append([wd, round(tm, 3), round(tm + n/RATE, 3)]); tm += n/RATE
            tm += next((p for c, p in PAUSES if wd.endswith(c)), 0)
        words[str(i)] = ws
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", f"{tm + .1:.2f}",
                        "-q:a", "9", os.path.join(out, "voix", f"scene_{i}.mp3")], check=True)
        print(f"scène {i} : {tm + .1:.1f} s")
    json.dump({"texts": texts, "words": words}, open(os.path.join(out, "alignement.json"), "w"), ensure_ascii=False, indent=0)

if __name__ == "__main__":
    build(json.load(open(sys.argv[1])), sys.argv[2])
