"""Minutage au mot près + sous-titres « karaoké » (mot courant surligné), pour les formats tactique / storytime.
Words(lignes, voix) : sans voix -> minutage estimé (≈ 16 caractères/s, blanc de .18 s entre phrases) ;
avec voix -> faster-whisper (horodatage des mots, mis en cache dans <voix>.mots.json) aligné mot à mot sur le texte.
  W.t(ligne, "mot", n=1)   instant où le mot (n-ième occurrence dans la ligne) est prononcé
  W.line(i)                (début, fin) de la phrase i
  caption(cv, W, t, y)     sous-titre : 1 à 3 mots à la fois, le mot dit en jaune"""
import os, re, json, math, subprocess, difflib
import numpy as np
from PIL import Image, ImageDraw, ImageFont
FONT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "fonts", "Anton-Regular.ttf")
def norm(x):
    x = x.lower()
    for a, b in (("éèêë", "e"), ("àâä", "a"), ("îï", "i"), ("ôö", "o"), ("ùûü", "u"), ("ç", "c"), ("œ", "oe")):
        for ch in a: x = x.replace(ch, b)
    return re.sub(r"[^a-z0-9]", "", x)
class Words:
    def __init__(self, lines, voice=None, cps=16.0, gap=.18):
        self.lines = lines; self.tok = []                              # (ligne, mot affiché, norm)
        for i, l in enumerate(lines):
            for w in l.split():
                if norm(w): self.tok.append([i, w, norm(w), 0.0, 0.0])
        self.real = bool(voice and os.path.exists(voice))
        if self.real: self._align(voice)
        else:
            t = 0.0
            for i, l in enumerate(lines):
                for tk in [x for x in self.tok if x[0] == i]:
                    d = (len(tk[1]) + 1)/cps; tk[3], tk[4] = t, t + d; t += d
                    if tk[1][-1] in ",;:": t += .12
                t += gap
        self.end = self.tok[-1][4] + .2
    def _align(self, voice):
        cache = voice + ".mots.json"
        if os.path.exists(cache) and os.path.getmtime(cache) > os.path.getmtime(voice): ww = json.load(open(cache))
        else:
            from faster_whisper import WhisperModel
            raw = subprocess.run(["ffmpeg", "-v", "error", "-i", voice, "-ar", "16000", "-ac", "1", "-f", "f32le", "-"], capture_output=True).stdout
            a = np.frombuffer(raw, np.float32); ww = []
            for s in WhisperModel("small", device="cpu", compute_type="int8").transcribe(a, language="fr", word_timestamps=True)[0]:
                ww += [dict(w=w.word, s=w.start, e=w.end) for w in s.words if norm(w.word)]
            json.dump(ww, open(cache, "w"))
        A = [t[2] for t in self.tok]; B = [norm(w["w"]) for w in ww]
        sm = difflib.SequenceMatcher(None, A, B, autojunk=False); m = {}
        for blk in sm.get_matching_blocks():
            for k in range(blk.size): m[blk.a + k] = blk.b + k
        for i, tk in enumerate(self.tok):                               # mots non reconnus : interpolés entre voisins reconnus
            if i in m: tk[3], tk[4] = ww[m[i]]["s"], ww[m[i]]["e"]
        known = [i for i in range(len(self.tok)) if i in m]
        for i, tk in enumerate(self.tok):
            if i in m: continue
            p = max([k for k in known if k < i], default=None); n = min([k for k in known if k > i], default=None)
            t0 = self.tok[p][4] if p is not None else 0.0; t1 = self.tok[n][3] if n is not None else t0 + .4
            kk = [j for j in range(len(self.tok)) if (p is None or j > p) and (n is None or j < n)]; q = kk.index(i)
            tk[3] = t0 + (t1 - t0)*q/len(kk); tk[4] = t0 + (t1 - t0)*(q + 1)/len(kk)
    def line(self, i):
        tk = [x for x in self.tok if x[0] == i]; return tk[0][3], tk[-1][4]
    def t(self, i, word, n=1, end=False):
        w = norm(word); k = 0
        for tk in self.tok:
            if tk[0] == i and (tk[2].startswith(w) or norm(re.split("['’]", tk[1])[-1]).startswith(w)):
                k += 1
                if k == n: return tk[4] if end else tk[3]
        raise KeyError(f"« {word} » absent de la ligne {i} : {self.lines[i]}")
    def chunks(self, maxw=3):
        """Groupes de 1 à 3 mots (coupés à la ponctuation) : [(t0, t1, [tokens])]."""
        out, cur = [], []
        for tk in self.tok:
            if cur and (cur[-1][0] != tk[0] or len(cur) >= maxw): out.append(cur); cur = []
            cur.append(tk)
            if tk[1][-1] in ".,;:!?…": out.append(cur); cur = []
        if cur: out.append(cur)
        res = []
        for k, c in enumerate(out):
            t1 = out[k + 1][0][3] if k + 1 < len(out) else c[-1][4] + .6
            res.append((c[0][3], min(t1, c[-1][4] + .5), c))
        return res
_f = {}
def _font(size):
    if size not in _f: _f[size] = ImageFont.truetype(FONT, size)
    return _f[size]
def caption(cv, W, t, y, size=92, col=(255, 255, 255), hi=(255, 214, 64), stroke=(10, 10, 16), maxw=980):
    """Sous-titre centré : le groupe de mots en cours, le mot dit en jaune qui grossit un peu (pop)."""
    if not hasattr(W, "_ch"): W._ch = W.chunks()
    cur = [c for c in W._ch if c[0] <= t < c[1]]
    if not cur: return
    t0, t1, toks = cur[-1]; f = _font(size); d = ImageDraw.Draw(cv)
    words = [tk[1].upper() for tk in toks]; ws = [f.getlength(w) for w in words]; gap = size*.28
    tot = sum(ws) + gap*(len(ws) - 1); sc = min(1.0, maxw/tot); x = cv.width/2 - tot*sc/2
    for tk, w, wd in zip(toks, words, ws):
        on = tk[3] <= t; now = tk[3] <= t < tk[4] + .05
        if on:
            s = sc*(1 + .12*math.exp(-(t - tk[3])*14)); fs = _font(max(8, int(size*s)))
            d.text((x + wd*sc/2, y), w, font=fs, fill=hi if now else col, anchor="mm", stroke_width=max(3, int(size*.07)), stroke_fill=stroke)
        x += (wd + gap)*sc
