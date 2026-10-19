"""Filtre « papier découpé » sur une vraie photo de joueur : détourage (rembg), aplats de couleur gouache,
traits de découpe, grain papier, liseré blanc d'autocollant déchiré et ombre portée. Résultat : un sprite RGBA
propre, ancre aux pieds (ou en bas du buste)."""
import os
from functools import lru_cache
import numpy as np
from PIL import Image, ImageFilter, ImageChops, ImageOps

CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "cutouts")
_sess = None

def _seg(im):
    global _sess
    from rembg import remove, new_session
    if _sess is None: _sess = new_session("u2net_human_seg")
    return remove(im, session=_sess, only_mask=True)

def _clean_mask(m):
    """Garde la plus grosse silhouette, bords lissés (pas de franges)."""
    a = np.asarray(m.filter(ImageFilter.GaussianBlur(2)), np.float32)
    b = a > 120
    try:
        from scipy import ndimage
        lab, n = ndimage.label(b)
        if n > 1:
            sizes = ndimage.sum(b, lab, range(1, n + 1)); b = lab == (1 + int(np.argmax(sizes)))
        b = ndimage.binary_fill_holes(b)
    except Exception: pass
    return Image.fromarray((b*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))

def _stylize(rgb, mask, levels=14):
    """Rendu gouache propre : lissage qui préserve les bords (aplats doux, teintes conservées),
    légère postérisation par canal, contours fins sombres, grain papier."""
    import cv2
    a = np.asarray(rgb)[:, :, ::-1].copy()
    for _ in range(2): a = cv2.bilateralFilter(a, 9, 40, 9)
    a = cv2.edgePreservingFilter(a, flags=1, sigma_s=40, sigma_r=.35)
    a = a[:, :, ::-1].astype(np.float32)
    step = 256/levels; a = np.floor(a/step)*step + step/2                       # aplats
    a = cv2.GaussianBlur(a, (0, 0), 1.0)
    g = cv2.cvtColor(np.clip(a, 0, 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
    ed = cv2.Canny(cv2.GaussianBlur(g, (0, 0), 1.6), 40, 110)
    ed = cv2.GaussianBlur(ed.astype(np.float32), (0, 0), .8)/255
    a = a*(1 - .45*np.clip(ed, 0, 1)[..., None])
    m = a.mean(2, keepdims=True); a = m + (a - m)*1.12
    rng = np.random.default_rng(7); n = rng.random(a.shape[:2]).astype(np.float32)
    n = cv2.GaussianBlur(n, (0, 0), 1.1)
    a = a*(.95 + .08*n[..., None])
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

def _rough(mask, px, seed=3):
    """Dilate le masque en liseré à bord légèrement déchiré."""
    d = mask.point(lambda v: 255 if v > 100 else 0).filter(ImageFilter.MaxFilter(2*px + 1))
    rng = np.random.default_rng(seed); n = rng.random((mask.height//6 + 2, mask.width//6 + 2)).astype(np.float32)
    n = Image.fromarray((n*255).astype(np.uint8)).resize(mask.size, Image.BICUBIC)
    d = ImageChops.subtract(d, n.point(lambda v: 255 if v > 235 else 0).filter(ImageFilter.MinFilter(5)))
    d = ImageChops.lighter(d, mask.point(lambda v: 255 if v > 100 else 0).filter(ImageFilter.MaxFilter(2*(px//2) + 1)))
    return d.filter(ImageFilter.GaussianBlur(1))

@lru_cache(maxsize=32)
def paper_player(path, box=None, h=900, border=16, levels=10, shadow=True):
    """Sprite papier découpé d'un joueur depuis une photo (box = recadrage). Ancre : bas-centre de la silhouette."""
    os.makedirs(CACHE, exist_ok=True)
    key = f"{os.path.basename(path)}_{box}_{levels}".replace(" ", "").replace("(", "").replace(")", "").replace(",", "-")
    mp = os.path.join(CACHE, key + "_mask.png")
    src = Image.open(path).convert("RGB")
    if box: src = src.crop(box)
    if os.path.exists(mp): mask = Image.open(mp).convert("L")
    else: mask = _clean_mask(_seg(src)); mask.save(mp)
    bb = mask.point(lambda v: 255 if v > 60 else 0).getbbox()
    pad = border*3
    src = src.crop(bb); mask = mask.crop(bb)
    k = h/src.height; size = (max(1, int(src.width*k)), h)
    src = src.resize(size, Image.LANCZOS); mask = mask.resize(size, Image.LANCZOS)
    W, H = size[0] + 2*pad, size[1] + 2*pad
    body = Image.new("RGB", (W, H)); body.paste(_stylize(src, mask, levels), (pad, pad))
    m = Image.new("L", (W, H), 0); m.paste(mask, (pad, pad))
    rim = _rough(m, border)
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if shadow:
        sh = rim.filter(ImageFilter.GaussianBlur(10)).point(lambda v: int(v*.45))
        s_img = Image.new("RGBA", (W, H), (20, 14, 10, 0)); s_img.putalpha(sh)
        out.alpha_composite(s_img, (8, 12))
    paper = Image.new("RGBA", (W, H), (250, 247, 238, 0)); paper.putalpha(rim); out.alpha_composite(paper)
    b = body.convert("RGBA"); b.putalpha(m.point(lambda v: 255 if v > 128 else int(v*1.6)).filter(ImageFilter.GaussianBlur(.6)))
    out.alpha_composite(b)
    out.info["anchor"] = (W/2, H - pad)
    return out
