"""Contrôle du rythme d'un épisode AVANT de générer/monter : blancs dans les voix, mots-clés dans les 3 premières secondes, longueur du hook.

  python3 scripts/check_rythme.py episodes/<sujet>                 # voix/scene_N.mp3 + textes_voix.json + alignement.json
  python3 scripts/check_rythme.py episodes/<sujet> --mots "Saint-Étienne,ASSE,Verts"

Alerte si : un blanc > 0,35 s dans une voix (à couper ou à réenregistrer sans « … ») ; le hook (scène 1) dépasse 18 mots ;
la 1re phrase dépasse 12 mots ; aucun mot-clé (--mots) n'est prononcé dans les 3 premières secondes ; plus d'un « … » par scène.
"""
import sys, os, json, re, subprocess

def silences(mp3, db=-35, d=.35):
    out = subprocess.run(["ffmpeg", "-nostats", "-i", mp3, "-af", f"silencedetect=noise={db}dB:d={d}", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", out)]
    du = [float(x) for x in re.findall(r"silence_duration: ([\d.]+)", out)]
    dur = float(re.findall(r"Duration: \d+:\d+:([\d.]+)", out)[0]) if "Duration" in out else 0
    return [(s, x) for s, x in zip(st, du) if s > .1 and s + x < dur - .1]      # on ignore début et fin de fichier

def main():
    ep = sys.argv[1]; mots = []
    if "--mots" in sys.argv: mots = [m.strip().lower() for m in sys.argv[sys.argv.index("--mots") + 1].split(",")]
    T = json.load(open(os.path.join(ep, "textes_voix.json")))
    T = T if isinstance(T, list) else list(T.values())
    ok = True
    hook = T[0]; first = re.split(r"[.?!…]", hook)[0]; hook = re.sub(r"\s[!?:;…]", "", hook)
    print(f"Hook : {len(hook.split())} mots, 1re phrase {len(first.split())} mots")
    if len(hook.split()) > 18: print("  ! hook trop long (> 18 mots)"); ok = False
    if len(first.split()) > 12: print("  ! 1re phrase trop longue (> 12 mots)"); ok = False
    for i, t in enumerate(T, 1):
        if t.count("…") > 1: print(f"  ! scène {i} : {t.count('…')} « … » (chaque « … » = un blanc dans la voix)"); ok = False
    al = os.path.join(ep, "alignement.json")
    if mots and os.path.exists(al):
        w = json.load(open(al))["words"]["1"]
        early = " ".join(x[0].lower() for x in w if x[1] < 3.0)
        hit = [m for m in mots if m in early]
        print(f"Mots-clés dits avant 3 s : {hit or 'AUCUN'}")
        if not hit: ok = False
    vdir = os.path.join(ep, "voix")
    if os.path.isdir(vdir):
        for f in sorted(os.listdir(vdir), key=lambda s: [int(x) if x.isdigit() else x for x in re.split(r"(\d+)", s)]):
            if not f.endswith(".mp3"): continue
            for s, d in silences(os.path.join(vdir, f)):
                print(f"  ! {f} : blanc de {d:.2f} s à {s:.2f} s"); ok = False
    print("RYTHME OK" if ok else "À CORRIGER (voir ci-dessus)")

if __name__ == "__main__":
    main()
