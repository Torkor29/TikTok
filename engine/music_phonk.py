"""Musique ORIGINALE de la chaîne (signature sonore) : phonk / drift phonk, 129 BPM, ré# mineur.
Tout est synthétisé ici (aucun sample externe, zéro droit) : cowbell 808 mélodique, basse 808 avec glissandos, kick, clap, hi-hats en rafales.
  python3 engine/music_phonk.py [sortie.wav] [durée_s]
BPM / BEAT exportés pour caler le montage sur les temps (beat_times())."""
import sys, math
import numpy as np
SR = 44100; BPM = 129.0; BEAT = 60/BPM; S16 = BEAT/4
rng = np.random.default_rng(29)
def env(n, a=.002, d=.2, sus=0.0):
    t = np.arange(n)/SR; e = np.minimum(1, t/max(a, 1e-4))*((1 - sus)*np.exp(-t/max(d, 1e-4)) + sus); return e
def hz(midi): return 440*2**((midi - 69)/12)
def bp(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1/SR); X[(f < lo) | (f > hi)] *= .03; return np.fft.irfft(X, len(x))
def cowbell(f0, dur=.32):
    """Cowbell 808 : deux carrés (rapport 1,48) filtrés passe-bande, attaque sèche, déclin court + queue."""
    n = int(dur*SR); t = np.arange(n)/SR
    sq = np.sign(np.sin(2*math.pi*f0*t)) + .8*np.sign(np.sin(2*math.pi*f0*1.48*t))
    x = bp(sq, f0*.7, f0*5) * (env(n, .001, .05)*.7 + env(n, .001, .22)*.3)
    return np.tanh(x*1.6)*.5
def kick808(f_from, f_to, dur, glide_t=None):
    """Basse 808 : sinus avec chute de pitch à l'attaque, tenue, glissando optionnel vers f_to, saturation."""
    n = int(dur*SR); t = np.arange(n)/SR
    f = f_from*(1 + 3*np.exp(-t/.018))
    if glide_t is not None:
        g = np.clip((t - glide_t)/.09, 0, 1); f = f*(1 - g) + f_to*g*(1 + 0*t)
    ph = 2*math.pi*np.cumsum(f)/SR; x = np.sin(ph)*env(n, .001, dur*.9, .55)
    x[-int(.02*SR):] *= np.linspace(1, 0, int(.02*SR))
    return np.tanh(x*2.2)*.75
def clap(dur=.25):
    n = int(dur*SR); x = rng.standard_normal(n); e = np.zeros(n)
    for k, d in enumerate((0, .011, .022)): i = int(d*SR); e[i:] += env(n - i, .0005, .012 if k < 2 else .12)
    return bp(x*e, 900, 6000)*.55
def hat(dur=.05, op=False):
    n = int((.22 if op else dur)*SR); x = bp(rng.standard_normal(n), 7000, 16000)
    return x*env(n, .0005, .09 if op else .018)*.32
def place(buf, x, t, g=1.0):
    i = int(t*SR); j = min(len(buf), i + len(x))
    if i < len(buf): buf[i:j] += x[:j - i]*g
def render(dur=64.0):
    n = int(dur*SR); mix = np.zeros(n); bass = np.zeros(n); drums = np.zeros(n)
    R = 51                                                   # ré#3 (D#)
    # mélodie cowbell originale : 2 mesures × 16 doubles-croches, degrés (demi-tons au-dessus de ré#4), None = silence
    A = [0, None, 3, 0, 5, None, 3, 7, None, 5, 3, None, 10, 8, 7, 5]
    B = [0, None, 3, 0, 5, None, 3, 7, None, 8, 7, 5, 3, None, 2, 3]
    C = [12, None, 10, 8, 10, None, 7, 8, None, 7, 5, None, 3, 5, 7, None]
    bar = 4*BEAT; nb = int(dur/bar) + 1
    for b in range(nb):
        t0 = b*bar; sect = (b//8) % 4                         # 8 mesures intro/couplet, puis montée
        mel = (A, B, A, C)[b % 4]
        if not (sect == 0 and b < 2):
            for k, d in enumerate(mel):
                if d is not None: place(mix, cowbell(hz(R + 12 + d)*2, .3), t0 + k*S16, .9 if k % 4 == 0 else .7)
        if b < 2: continue                                    # 2 mesures d'intro : cowbell seule (hook immédiat)
        # 808 : notes longues + glissandos (le « slide » phonk)
        prog = [(0, 0, 2.0, None), (2.0, 0, 1.0, 3), (3.0, -2, 1.0, None)] if b % 2 == 0 else [(0, 5, 1.5, None), (1.5, 3, 1.0, 0), (2.5, 0, 1.5, -5)]
        for (bt, deg, ln, gl) in prog:
            f1 = hz(R - 24 + deg); f2 = hz(R - 24 + gl) if gl is not None else None
            place(bass, kick808(f1, f2, ln*BEAT, ln*BEAT*.6 if gl is not None else None), t0 + bt*BEAT, .95)
        # clap sur le 3e temps (half-time) + petit clap fantôme
        place(drums, clap(), t0 + 2*BEAT, 1.0)
        if b % 4 == 3: place(drums, clap(), t0 + 3.75*BEAT, .5)
        # hi-hats : croches, rafales de triples-croches en fin de mesure paire
        for k in range(8): place(drums, hat(), t0 + k*BEAT/2, .9 if k % 2 == 0 else .6)
        if b % 2 == 1:
            for k in range(8): place(drums, hat(.03), t0 + 3*BEAT + k*BEAT/8, .45 + .05*k)
        place(drums, hat(op=True), t0 + 1.5*BEAT, .5)
    # sidechain : la 808 et la mélodie respirent sous chaque kick/note de basse
    duck = np.ones(n); step = int(BEAT*SR)
    for i in range(0, n, step): k = min(n - i, int(.12*SR)); duck[i:i + k] = .55 + .45*np.linspace(0, 1, k)
    out = mix*duck*.8 + bass + drums
    fade = int(1.5*SR); out[-fade:] *= np.linspace(1, 0, fade)
    out = np.tanh(out*1.2); out /= np.abs(out).max() + 1e-9
    return (out*.92).astype(np.float32)
def beat_times(dur): return [k*BEAT for k in range(int(dur/BEAT) + 1)]
if __name__ == "__main__":
    import wave
    path = sys.argv[1] if len(sys.argv) > 1 else "assets/music/phonk_papierfc.wav"; dur = float(sys.argv[2]) if len(sys.argv) > 2 else 64
    x = render(dur); st = np.stack([x, x], 1)
    st[:, 1] = np.roll(x, int(.006*SR))                       # léger élargissement stéréo
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st*32767).astype(np.int16).tobytes())
    print(path)
