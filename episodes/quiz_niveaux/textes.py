"""Textes du quiz « de plus en plus dur » (8 niveaux) + construction de la voix avec un temps de réflexion avant chaque réponse.
  python3 episodes/quiz_niveaux/textes.py   -> voix/voix.mp3 (à partir de voix/voix_rapide.mp3)"""
import os, sys, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "engine"))
TEXTE = ["Ce quiz foot devient de plus en plus dur. Dis-moi à quel niveau tu bloques.",
         "Niveau un. Le club de Mbappé ?", "Le Real Madrid !",
         "Niveau deux. Qui a mis un coup de tête en finale du Mondial deux mille six ?", "Zidane !",
         "Niveau trois. Combien de Ballons d'or pour Messi ?", "Huit !",
         "Niveau quatre. Le seul club français champion d'Europe avant le PSG ?", "L'OM, en quatre-vingt-treize !",
         "Niveau cinq. Le Ballon d'or deux mille vingt-quatre ?", "Rodri !",
         "Niveau six. Le seul gardien Ballon d'or ?", "Lev Yachine !",
         "Niveau sept. Qui a marqué le tout premier but de l'histoire de la Coupe du monde ?", "Lucien Laurent, un Français !",
         "Dernier niveau. Le tout premier club champion d'Europe, en cinquante-six ?", "Le Real Madrid !",
         "Alors, t'as bloqué à quel niveau ? Dis-le en commentaire, et envoie ça à ton pote qui se croit fort."]
THINK = 1.1                                                       # silence ajouté entre chaque question et sa réponse (chrono)
SRC = os.path.join(HERE, "voix", "voix_rapide.mp3"); VOIX = os.path.join(HERE, "voix", "voix.mp3"); CUTS = os.path.join(HERE, "voix", "coupes.json")
def silences():
    import re
    r = subprocess.run(["ffmpeg", "-i", SRC, "-af", "silencedetect=n=-42dB:d=0.12", "-f", "null", "-"], capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", r)]; en = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", r)]
    return list(zip(st, en))
def build():
    import karaoke as KA
    WD = KA.Words(TEXTE, SRC); cuts = []
    for q in range(1, 17, 2):
        a = WD.line(q)[1]; b = WD.line(q + 1)[0]; c = (a + b)/2 if b - a < .5 else a + .2
        sil = silences(); m = min(sil, key=lambda ab: abs((ab[0] + ab[1])/2 - c))      # recalé au milieu du vrai blanc (chiffres mal alignés)
        cuts.append(round((m[0] + m[1])/2, 3))
    parts, filt, prev = [], [], 0.0
    for k, c in enumerate(cuts + [None]):
        tr = f"atrim=start={prev}" + (f":end={c}" if c is not None else "")
        filt.append(f"[0:a]{tr},asetpts=PTS-STARTPTS[p{k}]"); parts.append(f"[p{k}]")
        if c is not None: filt.append(f"anullsrc=r=44100:cl=mono,atrim=duration={THINK}[s{k}]"); parts.append(f"[s{k}]"); prev = c
    fc = ";".join(filt) + ";" + "".join(parts) + f"concat=n={len(parts)}:v=0:a=1[o]"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", SRC, "-filter_complex", fc, "-map", "[o]", "-ac", "1", "-ar", "44100", "-b:a", "192k", VOIX], check=True)
    import json; json.dump(dict(cuts=cuts, think=THINK), open(CUTS, "w")); print("coupes", cuts)
if __name__ == "__main__": build()
