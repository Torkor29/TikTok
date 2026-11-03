#!/usr/bin/env python3
"""Clips GetSaaS : vidéo source du Drive -> clip TikTok 1080x1920 avec titre style Snap.
Règles respectées : pas de musique ajoutée, pas de texte inventé (hooks officiels seulement),
différence visible vs source (accroche + recadrage zoom). Usage: make_clips.py SRC_DIR OUT_DIR"""
import sys, os, glob, re, subprocess
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
EMOJI_DIR = os.path.join(HERE, "..", "emoji")
FONT = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
# Hooks officiels de la campagne (doc « Règles des clips GetSaaS »)
HOOKS = [
    ("Ça fait 5 ans que je travaille au McDo et je découvre ça seulement maintenant ??!", ["1f480", "1f62d"]),
    ("Elon Musk est même pas au courant", ["1f62d", "1f62d"]),
    ("Ça devrait être illégal !!", ["1f631", "1f480"]),
    ("6 ans de galère au smic et JE VOIS ÇA !!", ["1f480", "1f480"]),
]
W, H = 1080, 1920

def caption_png(text, emojis, path):
    font = ImageFont.truetype(FONT, 50)
    d = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) > W - 120: lines.append(cur); cur = w
        else: cur = t
    lines.append(cur)
    es = 56
    lh, pad = 66, 22
    bh = lh * len(lines) + pad * 2
    img = Image.new("RGBA", (W, bh), (0, 0, 0, 150))
    dr = ImageDraw.Draw(img)
    for i, ln in enumerate(lines):
        last = i == len(lines) - 1
        tw = dr.textlength(ln, font=font) + ((len(emojis) * (es + 6) + 8) if last else 0)
        x = (W - tw) / 2; y = pad + i * lh
        dr.text((x, y), ln, font=font, fill="white")
        if last:
            ex = x + dr.textlength(ln, font=font) + 12
            for e in emojis:
                em = Image.open(os.path.join(EMOJI_DIR, e + ".png")).convert("RGBA").resize((es, es), Image.LANCZOS)
                img.alpha_composite(em, (int(ex), int(y + 4))); ex += es + 6
    img.save(path)

def main(src, out):
    os.makedirs(out, exist_ok=True)
    files = sorted(glob.glob(os.path.join(src, "*.mp4")), key=lambda f: int(re.findall(r"(\d+)\.mp4$", f)[0]))
    for i, f in enumerate(files):
        n = re.findall(r"(\d+)\.mp4$", f)[0]
        hook, em = HOOKS[i % len(HOOKS)]
        cap = os.path.join(out, f".cap_{n}.png")
        caption_png(hook, em, cap)
        z = 1.06 + 0.02 * (i % 3)  # recadrage léger, différent d'un clip à l'autre
        vf = (f"[0:v]scale={int(W*z)//2*2}:{int(H*z)//2*2}:flags=lanczos,crop={W}:{H},setsar=1[v];"
              f"[v][1:v]overlay=0:{int(H*0.66)}[o]")
        dst = os.path.join(out, f"getsaas_clip_{n}_hook{i % len(HOOKS) + 1}.mp4")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f, "-i", cap, "-filter_complex", vf,
                        "-map", "[o]", "-map", "0:a?", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
                        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", dst], check=True)
        os.remove(cap); print("ok", dst, flush=True)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
