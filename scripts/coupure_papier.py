"""Photo -> coupure de journal papier (style collage) : recadrage, trame de points bichrome, bords déchirés, scotch.
  python3 scripts/coupure_papier.py in.jpg out.png [encre r,g,b] [crop x0,y0,x1,y1 en fractions]"""
import sys, random, math
from PIL import Image, ImageDraw, ImageFilter, ImageOps, ImageEnhance
src, dst = sys.argv[1], sys.argv[2]
ink = tuple(int(v) for v in (sys.argv[3] if len(sys.argv) > 3 else "28,26,30").split(","))
im = Image.open(src).convert("RGB")
if len(sys.argv) > 4:
    f = [float(v) for v in sys.argv[4].split(",")]; im = im.crop((int(f[0]*im.width), int(f[1]*im.height), int(f[2]*im.width), int(f[3]*im.height)))
im = im.resize((800, int(800*im.height/im.width)), Image.LANCZOS)
g = ImageOps.autocontrast(ImageEnhance.Contrast(im.convert("L")).enhance(1.25), cutoff=2)
cell = 6; W, H = g.size; dots = Image.new("L", (W, H), 255); d = ImageDraw.Draw(dots)
sm = g.resize((W//cell + 1, H//cell + 1), Image.BILINEAR)
for j in range(sm.height):
    for i in range(sm.width):
        v = 1 - sm.getpixel((i, j))/255; r = cell*.72*math.sqrt(v)
        if r > .4:
            x, y = i*cell + (cell/2 if j % 2 else 0), j*cell
            d.ellipse([x - r, y - r, x + r, y + r], fill=0)
tone = Image.blend(g, dots, .5)
paper = (244, 238, 222)
col = Image.merge("RGB", [tone.point(lambda v, a=a, b=b: int(a + (b - a)*v/255)) for a, b in zip(ink, paper)])
rnd = random.Random(7); m = Image.new("L", (W, H), 0); md = ImageDraw.Draw(m); pts = []
for x in range(0, W, 14): pts.append((x, rnd.randint(0, 14)))
for y in range(0, H, 14): pts.append((W - rnd.randint(0, 14), y))
for x in range(W, 0, -14): pts.append((x, H - rnd.randint(0, 14)))
for y in range(H, 0, -14): pts.append((rnd.randint(0, 14), y))
md.polygon(pts, fill=255)
pad = 30; out = Image.new("RGBA", (W + 2*pad, H + 2*pad), (0, 0, 0, 0))
bg = Image.new("RGBA", (W, H), paper + (255,)); bg.putalpha(m)
out.alpha_composite(bg, (pad, pad))
inner = Image.new("L", (W, H), 0); ImageDraw.Draw(inner).rectangle([22, 22, W - 22, H - 22], fill=255)
ph = col.convert("RGBA"); ph.putalpha(inner); out.alpha_composite(ph, (pad, pad))
tape = Image.new("RGBA", (220, 60), (236, 226, 190, 175)).rotate(-8, expand=True, resample=Image.BICUBIC)
out.alpha_composite(tape, (W//2 - 80, 0))
out.save(dst)
