"""Écussons officiels détourés (assets/logos/<club>_sticker.png), mis à l'échelle, ancre au centre."""
import os
from PIL import Image
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
def sticker(name, h):
    im = Image.open(os.path.join(ROOT, "assets", "logos", f"{name}_sticker.png")).convert("RGBA")
    im = im.resize((max(1, int(im.width*h/im.height)), h), Image.LANCZOS); im.info["anchor"] = (im.width/2, im.height/2); return im
