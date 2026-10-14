"""Photo -> grosse icône ronde « autocollant » (couleurs réhaussées, légère postérisation, grain papier, bord blanc épais).
  python3 scripts/icone_joueur.py in.png out.png x0,y0,x1,y1 (fractions, recadrage carré conseillé)"""
import sys, random
from PIL import Image, ImageDraw, ImageEnhance, ImageOps, ImageFilter
im = Image.open(sys.argv[1]).convert("RGB")
f = [float(v) for v in sys.argv[3].split(",")]
im = im.crop((int(f[0]*im.width), int(f[1]*im.height), int(f[2]*im.width), int(f[3]*im.height)))
S = 820; side = min(im.size); im = im.crop(((im.width - side)//2, (im.height - side)//2, (im.width + side)//2, (im.height + side)//2)).resize((S, S), Image.LANCZOS)
im = ImageEnhance.Color(ImageEnhance.Contrast(im).enhance(1.15)).enhance(1.25)
im = ImageOps.posterize(im, 5)
g = Image.effect_noise((S, S), 30).convert("L").point(lambda v: 128 + (v - 128)//3)
im = Image.blend(im, Image.merge("RGB", (g, g, g)), .08)
B = 44; out = Image.new("RGBA", (S + 2*B, S + 2*B), (0, 0, 0, 0)); d = ImageDraw.Draw(out)
d.ellipse([0, 0, S + 2*B - 1, S + 2*B - 1], fill=(250, 250, 246, 255))
m = Image.new("L", (S, S), 0); ImageDraw.Draw(m).ellipse([0, 0, S - 1, S - 1], fill=255)
ph = im.convert("RGBA"); ph.putalpha(m); out.alpha_composite(ph, (B, B))
d.ellipse([B - 3, B - 3, B + S + 2, B + S + 2], outline=(28, 26, 30), width=6)
out.save(sys.argv[2])
