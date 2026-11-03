#!/usr/bin/env python3
"""Montage piloté par une liste de plans (EDL) choisis à la main après analyse de la vidéo.
EDL JSON : {"hook": n°, "segs": [[début, fin, vitesse, zoom_début, zoom_fin, focus_y], ...]}
[..., focus_x optionnel] focus : 0 = haut/gauche de l'image, 0.5 = centre. Pas de son. Usage: edit_clip.py SRC EDL.json OUT.mp4"""
import sys, json, os, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_clips import caption_png, HOOKS, EMOJIS, W, H

src, edl, out = sys.argv[1:4]
e = json.load(open(edl))
h = e["hook"] - 1
cap = out + ".cap.png"
caption_png(HOOKS[h], EMOJIS[h % len(EMOJIS)], cap)
parts, labels = [], []
shake_ids = set(e.get("shake", []))
for i, sg in enumerate(e["segs"]):
    a, b, sp, z0, z1, fy = sg[:6]; fx = sg[6] if len(sg) > 6 else 0.5
    d = (b - a) / sp
    # zoom continu + "punch" à l'entrée du plan (transition)
    punch = "" if i == 0 else "*(1+0.18*exp(-t*14))"
    z = f"({z0}+({z1}-{z0})*min(t/{d:.3f},1)){punch}"
    sh = i in shake_ids
    ox = "+18*sin(t*47)*sin(t*13)" if sh else ""
    oy = "+14*sin(t*39+1)*sin(t*11)" if sh else ""
    flash = "" if i == 0 else ",eq=brightness='0.55*exp(-t*22)':eval=frame"
    parts.append(f"[0:v]trim={a}:{b},setpts=(PTS-STARTPTS)/{sp},fps=30,"
                 f"scale=w='trunc({W}*{z}*1.04/2)*2':h='trunc({H}*{z}*1.04/2)*2':eval=frame:flags=bicubic,"
                 f"crop={W}:{H}:'(iw-{W})*{fx}{ox}':'(ih-{H})*{fy}{oy}',setsar=1{flash}[s{i}]")
    labels.append(f"[s{i}]")
CY = int(H * e.get("cap_y", 0.66))
fc = ";".join(parts) + f";{''.join(labels)}concat=n={len(labels)}:v=1:a=0[v];[1:v]format=rgba,fade=in:st=0:d=0.2:alpha=1[c];[v][c]overlay=0:'{CY}+60*exp(-t*14)':shortest=1[o]"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-loop", "1", "-framerate", "30", "-i", cap, "-filter_complex", fc, "-map", "[o]",
                "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
                "-movflags", "+faststart", out], check=True)
os.remove(cap); print("ok", out)
