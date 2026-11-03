#!/usr/bin/env python3
"""Clips GetSaaS : vidéo source du Drive -> clip TikTok 1080x1920 avec titre style Snap.
Règles respectées : pas de musique ajoutée, pas de texte inventé (hooks officiels seulement),
différence visible vs source (accroche + recadrage zoom). Usage: make_clips.py SRC_DIR OUT_DIR [num ...]"""
import sys, os, glob, re, subprocess
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
EMOJI_DIR = os.path.join(HERE, "..", "emoji")
FONT = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
# Hooks officiels de la campagne (doc « Règles des clips GetSaaS »)
HOOKS = [  # 4 officiels + variantes demandées
    "Ça fait 5 ans que je travaille au McDo et je découvre ça seulement maintenant ??!",
    "Elon Musk est même pas au courant",
    "Ça devrait être illégal !!",
    "6 ans de galère au smic et JE VOIS ÇA !!",
    "Putain si j'avais su ça en tant qu'étudiant",
    "Putain j'aurais pu me payer des vacances beaucoup plus tôt",
    "Pourquoi personne m'a montré ça avant ??",
    "Mes potes vont jamais me croire",
    "J'ai passé 3 ans en fac pour rien",
    "Mon patron va pas aimer cette vidéo",
]
EMOJIS = [["1f480", "1f62d"], ["1f62d", "1f62d"], ["1f631", "1f480"], ["1f480", "1f480"],
          ["1f602", "1f480"], ["1f633", "1f62d"], ["1f62d", "1f602"], ["1f631", "1f631"]]
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

def first_cut(f):
    """Premier changement de plan (fin de la face cam), sinon 3 s."""
    r = subprocess.run(["ffmpeg", "-i", f, "-vf", "select='gt(scene,0.08)',showinfo", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    ts = [float(x) for x in re.findall(r"pts_time:([0-9.]+)", r)]
    ts = [t for t in ts if 1.0 < t < 8.0]
    return round(ts[0], 2) if ts else 3.0

def main(src, out):
    os.makedirs(out, exist_ok=True)
    files = sorted(glob.glob(os.path.join(src, "*.mp4")), key=lambda f: int(re.findall(r"(\d+)\.mp4$", f)[0]))
    only = set(sys.argv[3:])  # numéros optionnels à (re)monter
    for f in files:
        n = re.findall(r"(\d+)\.mp4$", f)[0]
        if only and n not in only: continue
        i = int(n)
        hook, em = HOOKS[(i * 7) % len(HOOKS)], EMOJIS[(i * 3) % len(EMOJIS)]
        cap = os.path.join(out, f".cap_{n}.png")
        caption_png(hook, em, cap)
        cut = first_cut(f)  # fin de la réaction face cam
        SP = 1.5            # démo accélérée pour garder le rythme
        zexpr = "if(lt(t,{c}),1.10,if(mod(floor((t-{c})/1.6),2),1.22,1.04))".format(c=cut)
        vf = (f"[0:v]trim=0:{cut},setpts=PTS-STARTPTS[a];"
              f"[0:v]trim=start={cut},setpts=(PTS-STARTPTS)/{SP}[b];"
              f"[a][b]concat=n=2:v=1:a=0,fps=30,"
              f"scale=w='trunc({W}*{zexpr}/2)*2':h='trunc({H}*{zexpr}/2)*2':eval=frame:flags=lanczos,"
              f"crop={W}:{H},setsar=1[v];[v][1:v]overlay=0:{int(H*0.66)}[o]")
        dst = os.path.join(out, f"getsaas_clip_{n}_hook{(i * 7) % len(HOOKS) + 1}.mp4")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f, "-i", cap, "-filter_complex", vf,
                        "-map", "[o]", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
                        "-pix_fmt", "yuv420p", "-an", "-movflags", "+faststart", dst], check=True)
        os.remove(cap); print("ok", dst, flush=True)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
