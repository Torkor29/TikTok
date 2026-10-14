"""Écusson -> autocollant (fond retiré par remplissage depuis les coins, bord blanc épais).
  python3 scripts/make_sticker.py in.png out_sticker.png"""
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageChops
im = Image.open(sys.argv[1]).convert("RGBA"); im.thumbnail((900, 900), Image.LANCZOS)
if im.getchannel("A").getextrema()[0] < 250: a = im.getchannel("A")
else:
    rgb = im.convert("RGB"); W, H = rgb.size; mark = (255, 0, 255)
    for p in [(0, 0), (W-1, 0), (0, H-1), (W-1, H-1)]: ImageDraw.floodfill(rgb, p, mark, thresh=60)
    a = Image.eval(ImageChops.difference(rgb, Image.new("RGB", rgb.size, mark)).convert("L"), lambda v: 255 if v > 8 else 0)
im.putalpha(a); im = im.crop(a.getbbox())
pad = max(im.size)//14; W, H = im.width + 2*pad, im.height + 2*pad
c = Image.new("RGBA", (W, H)); c.paste(im, (pad, pad), im)
b = c.getchannel("A").filter(ImageFilter.MaxFilter(2*(pad*2//3)//2*2+1)).filter(ImageFilter.GaussianBlur(2)).point(lambda v: 255 if v > 100 else 0)
out = Image.new("RGBA", (W, H), (250, 250, 246, 0)); out.putalpha(b)
out.alpha_composite(c); out.save(sys.argv[2])
