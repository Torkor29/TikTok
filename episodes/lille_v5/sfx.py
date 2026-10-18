"""Bruitages LOSC v5 synthétisés en numpy (aucun ElevenLabs). python3 sfx.py -> sfx/*.mp3 + planche d'audit (onde + spectrogramme + niveaux)."""
import os, sys, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "sfx")
SR = 44100
rng = np.random.default_rng(7)

def T(d): return np.arange(int(SR*d))/SR
def noise(d): return rng.standard_normal(int(SR*d))
def band(x, lo, hi):
    """Filtre passe-bande par FFT (bords adoucis)."""
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1/SR)
    m = np.clip((f - lo*.8)/(lo*.2 + 1e-9), 0, 1)*np.clip((hi*1.25 - f)/(hi*.25 + 1e-9), 0, 1) if lo > 0 else np.clip((hi*1.25 - f)/(hi*.25), 0, 1)
    return np.fft.irfft(X*m, len(x))
def sweep_band(x, f0, f1, q=.35, steps=24):
    """Bruit filtré dont la fréquence centrale glisse de f0 à f1 (whoosh)."""
    n = len(x); out = np.zeros(n); win = n//steps*2; hop = n//steps
    for i in range(steps):
        a = i*hop; b = min(n, a + win); fc = f0*(f1/f0)**(i/(steps - 1))
        seg = band(x[a:b], fc*(1 - q), fc*(1 + q))*np.hanning(b - a); out[a:b] += seg
    return out
def env(d, a=.005, r=None, curve=4.0):
    t = T(d); e = np.minimum(1, t/max(a, 1e-4))
    r = d - a if r is None else r
    e *= np.exp(-curve*np.maximum(0, t - a)/max(r, 1e-4)); return e
def fade(x, fi=.003, fo=.02):
    n_i, n_o = int(SR*fi), int(SR*fo); x = x.copy()
    if n_i: x[:n_i] *= np.linspace(0, 1, n_i)
    if n_o: x[-n_o:] *= np.linspace(1, 0, n_o)
    return x
def tone(f, d, wave="sin"):
    t = T(d); ph = 2*np.pi*np.cumsum(np.full(len(t), f) if np.isscalar(f) else f)/SR
    return np.sin(ph) if wave == "sin" else (2*(ph/(2*np.pi) % 1) - 1)
def gliss(f0, f1, d, expo=True):
    t = T(d); f = f0*(f1/f0)**(t/d) if expo else f0 + (f1 - f0)*t/d
    return np.sin(2*np.pi*np.cumsum(f)/SR)
def mix(*parts):
    n = max(len(p) for p in parts); o = np.zeros(n)
    for p in parts: o[:len(p)] += p
    return o
def at(x, t0, total):
    o = np.zeros(int(SR*total)); i = int(SR*t0); o[i:i + len(x)] += x[:len(o) - i]; return o
def norm(x, peak=.89): return fade(x)/(np.max(np.abs(x)) + 1e-9)*peak

S = {}
def snd(fn): S[fn.__name__] = fn; return fn

# ---------------------------------------------------------------- impacts
@snd
def braam():          # nappe grave cinématique : saw désaccordées + sub, filtrées
    d = 1.8; t = T(d); e = np.minimum(1, t/.04)*np.exp(-t*1.6)
    x = sum(tone(55*r, d, "saw") for r in (1, 1.007, .993, 2.002))*.25 + .8*np.sin(2*np.pi*41*t)
    return band(x*e, 0, 900)
@snd
def boom():
    d = 1.2; t = T(d); f = 90*np.exp(-t*3) + 38
    return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*3.2) + band(noise(d), 0, 300)*env(d, .002, .3, 6)*.6
@snd
def stamp():          # tampon : choc sourd + claquement papier
    d = .45; t = T(d)
    return (np.sin(2*np.pi*np.cumsum(140*np.exp(-t*30) + 70)/SR)*np.exp(-t*22)*.9
            + band(noise(d), 800, 5000)*env(d, .001, .06, 8)*.7)
@snd
def thud():
    d = .4; t = T(d); return np.sin(2*np.pi*np.cumsum(110*np.exp(-t*18) + 50)/SR)*np.exp(-t*14) + band(noise(d), 100, 900)*env(d, .001, .08, 8)*.4
@snd
def tok():            # objet posé sur une étagère
    d = .25; t = T(d); return (np.sin(2*np.pi*620*t)*.5 + np.sin(2*np.pi*1180*t)*.3)*np.exp(-t*38) + band(noise(d), 1500, 6000)*env(d, .001, .02, 8)*.4
@snd
def bang():           # ballon qui éclate
    d = .6; return band(noise(d), 200, 9000)*env(d, .0005, .12, 9) + boom()[:int(SR*d)]*.5
@snd
def hammer():
    d = .35; t = T(d); return (np.sin(2*np.pi*np.cumsum(260*np.exp(-t*25) + 120)/SR)*np.exp(-t*20)
                              + band(noise(d), 2000, 7000)*env(d, .0005, .03, 8)*.8 + np.sin(2*np.pi*1900*t)*np.exp(-t*40)*.25)
@snd
def kick():           # frappe de balle
    d = .3; t = T(d); return np.sin(2*np.pi*np.cumsum(180*np.exp(-t*40) + 60)/SR)*np.exp(-t*18) + band(noise(d), 600, 3000)*env(d, .0005, .02, 8)*.6
@snd
def glove():          # arrêt du gardien (claquement)
    d = .3; return band(noise(d), 700, 5000)*env(d, .0005, .05, 9) + kick()[:int(SR*d)]*.4
@snd
def net():            # filet qui se gonfle
    d = .7; x = band(noise(d), 300, 4000); t = T(d); return x*np.exp(-t*5)*(1 + .5*np.sin(2*np.pi*14*t))*.6

# ---------------------------------------------------------------- mouvements
def _whoosh(d, f0, f1, seed):
    global rng; rng = np.random.default_rng(seed); t = T(d)
    e = np.sin(np.pi*np.clip(t/d, 0, 1))**1.6
    return sweep_band(noise(d), f0, f1)*e
@snd
def whoosh1(): return _whoosh(.45, 400, 3200, 1)
@snd
def whoosh2(): return _whoosh(.38, 2400, 500, 2)
@snd
def whoosh3(): return _whoosh(.55, 300, 1800, 3)
@snd
def suck():           # aspiration (zoom traversant)
    d = .6; t = T(d); x = sweep_band(noise(d), 300, 5000)*(t/d)**2
    return (x + gliss(120, 900, d)*(t/d)**3*.3)*np.minimum(1, (d - t)/.08)
@snd
def swish():
    d = .2; return _whoosh(d, 1500, 5000, 4)
@snd
def riser():
    d = 1.4; t = T(d); return (gliss(180, 900, d)*.3 + sweep_band(noise(d), 500, 6000)*.8)*(t/d)**2.2
@snd
def rewind():         # rembobinage VHS : glissando qui accélère + bruit de bande
    d = .9; t = T(d); f = 300 + 2600*(t/d)**2
    x = np.sign(np.sin(2*np.pi*np.cumsum(f)/SR))*.25 + band(noise(d), 1500, 6000)*.4
    return band(x, 200, 7000)*np.minimum(1, t/.05)*np.exp(-np.maximum(0, t - .75)*20)
@snd
def scratch():
    d = .35; t = T(d); f = 600 + 900*np.sin(2*np.pi*5*t)
    return band(np.sign(np.sin(2*np.pi*np.cumsum(f)/SR))*.4 + noise(d)*.3, 300, 4000)*env(d, .005, .3, 3)

# ---------------------------------------------------------------- papier
@snd
def page_tear():      # page de calendrier arrachée
    d = .32; x = band(noise(d), 1200, 9000); t = T(d)
    crackle = (rng.random(len(t)) > .985)*rng.standard_normal(len(t))*3
    return (x*.6 + band(crackle, 1000, 8000))*np.sin(np.pi*np.clip(t/d, 0, 1))**.6
@snd
def rustle():         # froissement de billets (texture longue)
    d = 1.3; t = T(d); x = band(noise(d), 2500, 9000)*(.4 + .6*np.abs(np.sin(2*np.pi*3.3*t)))
    cr = (rng.random(len(t)) > .992)*rng.standard_normal(len(t))*2
    return (x*.5 + band(cr, 1500, 8000))*np.minimum(1, t/.1)*np.minimum(1, (d - t)/.25)
@snd
def marker():         # trait de feutre
    d = .35; t = T(d); x = band(noise(d), 2500, 8000)*(.6 + .4*np.sin(2*np.pi*22*t)); return x*np.sin(np.pi*t/d)**.5
@snd
def pin():
    d = .18; t = T(d); return np.sin(2*np.pi*3100*t)*np.exp(-t*40)*.4 + band(noise(d), 3000, 9000)*env(d, .0005, .02, 8)*.6
@snd
def ribbon():
    d = .5; t = T(d); return band(noise(d), 1800, 7000)*(t/d)*np.exp(-np.maximum(0, t - .4)*30)*.8
@snd
def typewriter():
    d = .9; o = np.zeros(int(SR*d))
    for k in range(7):
        c = band(noise(.05), 1500, 6000)*env(.05, .0005, .02, 8) + np.sin(2*np.pi*np.cumsum(np.full(int(SR*.05), 1800 + 200*k))/SR)*env(.05, .0005, .02, 9)*.3
        i = int(SR*(k*.11 + .01*(k % 2))); o[i:i + len(c)] += c
    return o

# ---------------------------------------------------------------- musique / ambiance
@snd
def ding():           # caisse enregistreuse
    d = 1.0; t = T(d); return sum(np.sin(2*np.pi*f*t)*np.exp(-t*k)*a for f, k, a in ((1568, 3, .6), (2093, 4, .4), (3136, 6, .2)))
@snd
def coins():
    d = .8; o = np.zeros(int(SR*d))
    for k in range(9):
        f = rng.uniform(2800, 5200); c = np.sin(2*np.pi*f*T(.15))*np.exp(-T(.15)*30)*.5
        i = int(SR*rng.uniform(0, .6)); o[i:i + len(c)] += c
    return o
@snd
def heart():
    d = .8; o = np.zeros(int(SR*d))
    for t0, a in ((0, 1), (.2, .7)):
        b = np.sin(2*np.pi*np.cumsum(70*np.exp(-T(.25)*12) + 38)/SR)*np.exp(-T(.25)*16)*a; i = int(SR*t0); o[i:i + len(b)] += b
    return band(o, 0, 400)
@snd
def shimmer():        # transformation / magie
    d = 1.1; t = T(d); o = np.zeros(len(t))
    for k, f in enumerate((1318, 1568, 1976, 2637, 3136)):
        o += np.sin(2*np.pi*f*t)*np.exp(-np.maximum(0, t - k*.09)*5)*(t > k*.09)*.25
    return o*(1 + .3*np.sin(2*np.pi*9*t))
@snd
def sparkle():
    d = .9; o = np.zeros(int(SR*d))
    for k in range(10):
        f = rng.uniform(3000, 7000); c = np.sin(2*np.pi*f*T(.2))*np.exp(-T(.2)*20)*.3; i = int(SR*k*.06); o[i:i + len(c)] += c
    return o
@snd
def fanfare():        # 3 notes cuivrées (saw filtrée)
    o = np.zeros(int(SR*1.3))
    for t0, f, d in ((0, 392, .16), (.18, 523, .16), (.36, 659, .8)):
        x = sum(tone(f*r, d, "saw") for r in (1, 1.004))*.4; x = band(x, 0, 2500)*env(d, .02, d, 2.5); i = int(SR*t0); o[i:i + len(x)] += x
    return o
@snd
def bell():
    d = 1.6; t = T(d); return sum(np.sin(2*np.pi*f*t)*np.exp(-t*k)*a for f, k, a in ((880, 2, .5), (1760*1.01, 3, .3), (2640*1.02, 5, .2), (440, 1.5, .3)))
@snd
def notif():
    d = .5; o = np.zeros(int(SR*d))
    for t0, f in ((0, 1320), (.12, 1760)):
        c = np.sin(2*np.pi*f*T(.3))*np.exp(-T(.3)*14); i = int(SR*t0); o[i:i + len(c)] += c*.6
    return o
@snd
def pop():
    d = .15; t = T(d); return gliss(500, 1400, d)*np.exp(-t*30)
@snd
def zap():            # éclair
    d = .5; t = T(d); x = np.sign(np.sin(2*np.pi*np.cumsum(1800*np.exp(-t*6) + 80)/SR))*.4 + band(noise(d), 3000, 9000)*.5
    return band(x, 100, 9000)*env(d, .001, .4, 5)
@snd
def flashfx():
    d = .7; t = T(d); return (sweep_band(noise(d), 6000, 800)*.6 + gliss(2000, 200, d)*.2)*np.exp(-t*4)
@snd
def tick():
    d = .05; return band(noise(d), 2500, 8000)*env(d, .0005, .01, 8)
@snd
def tictac():
    o = np.zeros(int(SR*1.4))
    for k in range(10):
        c = tick()*(1 if k % 2 else .6); i = int(SR*k*.14); o[i:i + len(c)] += c
    return o
@snd
def paws():           # pas de pattes
    o = np.zeros(int(SR*1.2))
    for k in range(6):
        c = band(noise(.08), 200, 1500)*env(.08, .002, .05, 8); i = int(SR*k*.18); o[i:i + len(c)] += c*(.7 + .3*(k % 2))
    return o
@snd
def waves():
    d = 2.2; t = T(d); return band(noise(d), 150, 1800)*(.4 + .6*np.sin(np.pi*t/1.1)**2)*np.minimum(1, (d - t)/.3)
@snd
def bubbles():
    d = 1.0; o = np.zeros(int(SR*d))
    for k in range(12):
        f0 = rng.uniform(300, 900); dd = rng.uniform(.05, .1); c = gliss(f0, f0*2.2, dd)*np.exp(-T(dd)*25)*.5
        i = int(SR*rng.uniform(0, .9)); o[i:i + len(c)] += c[:len(o) - i]
    return o
@snd
def crank():          # cliquetis de manivelle
    o = np.zeros(int(SR*1.6))
    for k in range(14):
        c = band(noise(.03), 1500, 6000)*env(.03, .0005, .01, 8) + np.sin(2*np.pi*900*T(.03))*np.exp(-T(.03)*80)*.4
        i = int(SR*k*.11); o[i:i + len(c)] += c
    return o
@snd
def creak():          # grincement (balance / corde)
    d = .8; t = T(d); f = 180 + 60*np.sin(2*np.pi*1.5*t)
    x = np.sign(np.sin(2*np.pi*np.cumsum(f)/SR))*(rng.random(len(t)) > .3)
    return band(x, 300, 3000)*np.sin(np.pi*t/d)*.5
@snd
def drumroll():
    d = 1.4; t = T(d); o = np.zeros(len(t)); k = 0; tt = 0.0
    while tt < d - .05:
        c = band(noise(.04), 150, 2500)*env(.04, .001, .03, 8); i = int(SR*tt); o[i:i + len(c)] += c*(.5 + .5*tt/d); tt += .045
    return o
@snd
def fall():           # chute (glissando + thud)
    return mix(gliss(700, 150, .35)*np.exp(-T(.35)*3)*.4, at(thud(), .32, .8))
@snd
def siren():
    d = 1.6; t = T(d); f = 700 + 250*np.sin(2*np.pi*1.5*t); return np.sin(2*np.pi*np.cumsum(f)/SR)*.35*np.minimum(1, t/.1)*np.minimum(1, (d - t)/.3)
@snd
def inflate():        # ballon qui gonfle (souffle + couinement montant)
    d = .5; t = T(d); return (band(noise(d), 600, 3000)*.5*(t/d) + gliss(250, 600, d)*.15*(t/d))*np.minimum(1, (d - t)/.06)
@snd
def whistle():
    d = .5; t = T(d); f = 2800 + 120*np.sin(2*np.pi*28*t); return np.sin(2*np.pi*np.cumsum(f)/SR)*np.minimum(1, t/.02)*np.minimum(1, (d - t)/.05)*.5
@snd
def touch():          # touche de balle légère
    d = .15; t = T(d); return np.sin(2*np.pi*np.cumsum(220*np.exp(-t*50) + 90)/SR)*np.exp(-t*30)*.8
@snd
def breath():         # souffle (l'impossible)
    d = 1.3; t = T(d); return sweep_band(noise(d), 300, 1200)*np.sin(np.pi*t/d)**2*.7
@snd
def crowd():          # foule (synthèse : bruit rose modulé + « voix » formantes)
    d = 2.5; t = T(d); x = band(noise(d), 250, 3500)
    for f in (450, 700, 1100):
        x += band(noise(d), f*.9, f*1.1)*(1 + .5*np.sin(2*np.pi*rng.uniform(2, 5)*t))
    return x*np.minimum(1, t/.25)*np.minimum(1, (d - t)/.6)

def write(name, x):
    os.makedirs(OUT, exist_ok=True); x = norm(np.nan_to_num(x)).astype(np.float32)
    wav = os.path.join(OUT, name + ".wav"); mp3 = os.path.join(OUT, name + ".mp3")
    import wave
    with wave.open(wav, "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR); f.writeframes((x*32767).astype(np.int16).tobytes())
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-b:a", "192k", mp3], check=True); os.remove(wav)
    return x

def audit(res):
    """Planche : nom, durée, pic, RMS, forme d'onde + spectrogramme ; drapeaux : clic de fin, DC, trop court."""
    cols, cw, ch = 4, 600, 300; rows = (len(res) + cols - 1)//cols
    sheet = Image.new("RGB", (cols*cw, rows*ch), (18, 18, 22)); d = ImageDraw.Draw(sheet)
    fnt = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20); bad = []
    for i, (nm, x) in enumerate(res):
        X, Y = (i % cols)*cw, (i//cols)*ch
        rms = 20*math.log10(np.sqrt(np.mean(x**2)) + 1e-9); tail = np.max(np.abs(x[-200:])); dc = abs(np.mean(x))
        flags = [f for f, c in (("CLIC FIN", tail > .05), ("DC", dc > .02), ("SOURD", rms < -38)) if c]
        if flags: bad.append((nm, flags))
        d.text((X + 8, Y + 4), f"{nm}  {len(x)/SR:.2f}s  RMS {rms:.0f}dB {' '.join(flags)}", font=fnt, fill=(255, 90, 90) if flags else (220, 220, 220))
        n = len(x); step = max(1, n//(cw - 20))
        for k in range(0, cw - 20):
            seg = x[k*step:(k + 1)*step]
            if len(seg): a = np.max(np.abs(seg)); d.line([(X + 10 + k, Y + 80 - a*48), (X + 10 + k, Y + 80 + a*48)], fill=(110, 200, 255))
        nfft = 512; hop = max(64, n//(cw - 20)); spec = []
        for k in range(0, max(1, n - nfft), hop): spec.append(np.abs(np.fft.rfft(x[k:k + nfft]*np.hanning(nfft)))[:200])
        if spec:
            S_ = np.log10(np.array(spec).T + 1e-6); S_ = np.clip((S_ - S_.max() + 4)/4, 0, 1)
            im = Image.fromarray((S_[::-1]*255).astype(np.uint8)).resize((cw - 20, 150)).convert("RGB")
            sheet.paste(im, (X + 10, Y + 140))
    p = "/tmp/claude-0/aud/sfx_audit.jpg"; sheet.save(p, quality=85); return p, bad

if __name__ == "__main__":
    res = [(nm, write(nm, fn())) for nm, fn in S.items()]
    p, bad = audit(res); print(p); print("DRAPEAUX:", bad)
