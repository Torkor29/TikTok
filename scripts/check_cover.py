"""Aperçu d'une couverture avec la zone visible TikTok (bande 3:4 centrale y 240..1680) : python3 scripts/check_cover.py cover.jpg out.jpg"""
import sys
from PIL import Image, ImageDraw
im = Image.open(sys.argv[1]).convert("RGB"); d = ImageDraw.Draw(im, "RGBA")
d.rectangle([0, 0, im.width, 240], fill=(0, 0, 0, 150)); d.rectangle([0, 1680, im.width, im.height], fill=(0, 0, 0, 150))
im.resize((im.width//4, im.height//4)).save(sys.argv[2])
