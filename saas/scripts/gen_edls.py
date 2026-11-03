#!/usr/bin/env python3
"""Génère les EDL à partir des repères notés à la main pour chaque vidéo (analyse image par image).
Repères (secondes) : fin face cam, curseur [a,b], banque, ventes, IA, résultat [a,b], génération [a,b],
site [a,b], vidéos/vues [a,b], clics, paiements [a,b], logo début, cadrage."""
import json, os, random
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "edl")
M = {  # n: (face, slider, bank, sales, ia, result, gen, site, vids, clicks, pay, logo, cadrage)
 12: (2.0, (3, 6), 7, 9, 12, (14, 16.5), (17, 21.5), (22, 26.5), (27, 30.5), 31, (32, 34.8), 35, "phone"),
 13: (2.0, (3, 7.5), 8, 12, 15, (17.8, 19.9), (20, 24), (26, 30), (30.5, 34), 34.6, (36, 37.9), 38.5, "wide"),
 14: (3.0, (4, 7.5), 8.5, 12, 16.5, (18.8, 20.9), (21, 25.5), (27, 31), (31, 35), 35, (36, 38.9), 39, "wide"),
 15: (3.0, (4, 7.5), 8.3, 11.5, 14.3, (16.8, 19), (19, 23.5), (25, 29), (30, 33), 33.3, (35, 37), 38, "wide"),
 16: (1.9, (5, 8), 9, 12.5, 16.3, (19, 21.9), (22, 26.5), (27, 32), (32, 36), 36.2, (38, 39.9), 41, "mid"),
 19: (3.0, (3, 7), 8, 11.5, 14.3, (16.8, 19), (19, 23), (24, 29), (29, 33), 33, (35, 37), 38, "wide"),
 20: (3.0, (3, 8), 8.5, 12.3, 15.3, (17.8, 20), (20, 24.8), (25, 30), (30, 34), 34, (35, 37.9), 38, "wide"),
 21: (3.0, (3, 7), 7.5, 10.5, 14.2, (16.5, 19), (19, 23.8), (24, 29), (29, 33), 33, (34, 36.9), 37, "wide"),
 22: (3.0, (3, 6.8), 7.5, 11.3, 14.3, (17, 19.9), (20, 24.8), (25, 29.9), (30, 33.9), 34, (35, 37.9), 38, "wide"),
 25: (3.0, (4, 6.9), 8, 11, 15, (18, 19.9), (20, 24.8), (26, 29.9), (31, 34), 35, (36, 37.9), 39, "wide"),
 26: (3.0, (4, 7.5), 8, 12, 15, (18, 19.9), (20, 24.8), (25, 29.9), (30, 33.9), 34, (35, 37.9), 38, "wide"),
 27: (3.0, (3, 6.8), 7.3, 10.3, 13, (16, 17.9), (18, 22.8), (23, 27.9), (28, 31.9), 32, (33, 35.9), 36.5, "wide"),
 32: (3.0, (3, 6.8), 7.3, 10.3, 13.3, (16, 17.9), (18.5, 22.8), (24, 27.9), (29, 32), 32.5, (34, 36.5), 37, "wide"),
 33: (1.9, (3, 6.8), 7.3, 10.3, 13, (16, 16.9), (17, 21.8), (22, 26.9), (27, 30.9), 31, (33, 34.9), 36, "wide"),
 34: (1.9, (3, 6.8), 7.3, 10.3, 13, (16, 17.9), (18, 22.8), (23, 27.9), (28, 31.9), 32, (34, 35.9), 37, "wide"),
 35: (3.0, (3, 6.9), 8, 11.3, 15, (17, 18.9), (19, 23.9), (25, 28.9), (30, 33), 33.5, (35, 37.5), 38, "wide"),
 36: (3.0, (3, 5.9), 7.3, 10.3, 13.3, (16, 17.9), (18, 22.9), (24, 28.9), (29, 32.9), 33, (34, 36.9), 37, "wide"),
 37: (3.0, (3, 6.9), 7.3, 10.3, 13, (15, 16.9), (17, 21.9), (22, 26.9), (27, 30.9), 31, (32, 34.9), 35, "wide"),
 38: (1.9, (3, 6.9), 8, 11.3, 14, (17.5, 18.9), (19, 23.9), (25, 29.9), (30, 33.9), 34, (35, 37.9), 38, "wide"),
 39: (3.0, (4, 6.9), 8, 12, 15, (17, 17.9), (18, 22.9), (24, 27.9), (29, 32.9), 33, (34, 35.9), 37, "wide"),
 40: (3.0, (4, 7), 9, 11.5, 16, (19, 22.9), (23, 25), (28, 31.9), (32, 35.9), 37, (38, 40.9), 41, "room"),
 41: (3.8, (4, 9), 10.5, 14.5, 18.5, (21.5, 24.9), (25, 29.9), (30, 34.9), (35, 38.9), 39, (40, 42.9), 43, "mid"),
 42: (3.8, (4, 9.8), 10.5, 14.5, 19, (23, 25.9), (26, 31), (32, 36.9), (37, 40.9), 41, (42, 44.9), 45, "mid"),
}
DUR = {}
FR = {  # cadrage : (zoom de base, focus_y, focus_x pour les questions)
 "phone": (1.0, 0.3, 0.5), "wide": (1.0, 0.3, 0.5), "mid": (1.3, 0.3, 0.5), "room": (1.45, 0.28, 0.42)}
TRANS_SETS = [["punch", "whip", "glitch"], ["drop", "dark", "punch"], ["whip", "whip", "glitch", "drop"],
              ["punch", "dark", "glitch"], ["drop", "punch", "whip", "dark"]]
def build(n, end):
    f, sl, bank, sales, ia, res, gen, site, vids, clicks, pay, logo, fr = M[n]
    z, fy, fx = FR[fr]
    r = random.Random(n)
    S = [[0.0, f, 1.0, 1.0, 1.08, 0.5]]
    S.append([sl[0], sl[1], max((sl[1] - sl[0]) / 1.8, 1.0), z, z * 1.04, fy, fx])
    for t in (bank, sales, ia):
        S.append([t, t + 1.2, 1.0, z, z, fy, fx])
    S.append([res[0], res[1], 1.0, z, z * 1.3, fy, fx]); ires = len(S) - 1
    S.append([gen[0], gen[1], 1.6, z * 1.05, z * 1.2, fy])
    S.append([site[0], site[1], 1.4, z, z * 1.15, fy])
    S.append([vids[0], vids[1], 1.1, z, z * 1.2, fy])
    S.append([clicks, clicks + 1.3, 1.0, z * 1.1, z * 1.1, fy])
    S.append([pay[0], pay[1], 1.0, z, z * 1.3, fy]); ipay = len(S) - 1
    S.append([logo, min(logo + 1.6, end - 0.05), 1.0, z, z * 1.1, 0.4])
    S = [[round(v, 3) if isinstance(v, float) else v for v in s] for s in S]
    return {"hook": (n * 7) % 10 + 1, "cap_y": 0.72, "shake": [ires, ipay],
            "trans": r.choice(TRANS_SETS), "segs": S}
if __name__ == "__main__":
    import subprocess, sys
    src = sys.argv[1]
    for n in M:
        end = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                    os.path.join(src, f"Video_{n}.mp4")], capture_output=True, text=True).stdout)
        json.dump(build(n, end), open(os.path.join(D, f"{n}.json"), "w"), indent=1)
    print(len(M), "EDL")
