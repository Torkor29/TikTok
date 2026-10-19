"""Sons supplémentaires de l'épisode Rennes (numpy), même pipeline et même audit que lille_v5/sfx.py."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "lille_v5"))
import sfx as SFXM
from sfx import *
SFXM.OUT = os.path.join(HERE, "sfx")
def fire():
    d = 2.0; t = T(d); x = band(noise(d), 200, 2500)*.35*(1 + .3*np.sin(2*np.pi*3*t))
    cr = (rng.random(len(t)) > .996)*rng.standard_normal(len(t))*3; x += band(cr, 1500, 8000)
    return x*np.minimum(1, t/.2)*np.minimum(1, (d - t)/.3)
def tractor():
    d = 2.2; t = T(d); o = np.zeros(len(t)); tt = 0
    while tt < d - .06:
        p = band(noise(.06), 60, 600)*env(.06, .002, .05, 6) + np.sin(2*np.pi*55*T(.06))*np.exp(-T(.06)*30)
        i = int(SR*tt); o[i:i + len(p)] += p[:len(o) - i]; tt += .085
    return o*np.minimum(1, t/.2)*np.minimum(1, (d - t)/.4)
def wind():
    d = 2.0; t = T(d); return sweep_band(noise(d), 300, 900, .5)*(.5 + .5*np.sin(np.pi*t/d))
def flap():
    d = .09; return band(noise(d), 1500, 7000)*env(d, .0005, .03, 8) + np.sin(2*np.pi*900*T(d))*np.exp(-T(d)*60)*.4
def doorslam():
    return mix(creak()[:int(SR*.35)]*.6, at(boom()*.9, .3, 1.4), at(stamp()*.5, .3, 1.4))
if __name__ == "__main__":
    res = [(n, write(n, f())) for n, f in (("fire", fire), ("tractor", tractor), ("wind", wind), ("flap", flap), ("doorslam", doorslam))]
    p, bad = audit(res); print(p, bad)
