"""Minutage provisoire d'un QUIZ quand les voix ElevenLabs manquent (crédits épuisés) :
écrit <dossier>/voix/<clé>.mp3 (silence de la durée estimée, ~6 syllabes/s + pauses) pour chaque clé de textes_voix.json
sans voix réelle dans episodes/<quiz>/voix/, copie les vraies voix existantes, et <dossier>/alignement.json (intro, cta, outro).
  python3 scripts/minutage_provisoire_quiz.py episodes/quiz_psg2 <dossier>
  LEGENDES_PROVISOIRE=<dossier> python3 episodes/quiz_psg2/quiz_psg2.py <sortie> --stills | --apercu
"""
import json, os, shutil, subprocess, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "engine"))
from engine import _syll, align_words
RATE = 6.0
PAUSES = (("…", .45), (".", .4), ("!", .4), ("?", .4), (":", .3), (",", .2))

def estimate(text):
    tm, ws = .05, []
    for wd in text.split():
        n = sum(_syll(x) for x in wd.split("-") if x.strip(".,;:!?…'’")) or 1
        ws.append([wd, round(tm, 3), round(tm + n/RATE, 3)]); tm += n/RATE
        tm += next((p for c, p in PAUSES if wd.endswith(c)), 0)
    return ws, tm + .1

if __name__ == "__main__":
    ep, out = sys.argv[1], sys.argv[2]
    T = json.load(open(os.path.join(ep, "textes_voix.json"))); os.makedirs(os.path.join(out, "voix"), exist_ok=True)
    words = {}
    for k, text in T.items():
        real = os.path.join(ep, "voix", f"{k}.mp3"); dst = os.path.join(out, "voix", f"{k}.mp3")
        if os.path.exists(real):
            shutil.copy(real, dst); ws = [list(x) for x in align_words(real, text)]
        else:
            ws, d = estimate(text)
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", f"{d:.2f}", "-q:a", "9", dst], check=True)
        words[k] = ws
        print(k, "réelle" if os.path.exists(real) else "provisoire")
    K = ["intro", "cta", "outro"]
    json.dump({"texts": [T[k] for k in K], "words": {str(i + 1): words[k] for i, k in enumerate(K)}},
              open(os.path.join(out, "alignement.json"), "w"), ensure_ascii=False, indent=0)
