"""Raccourcit les blancs d'une voix : tout blanc > 0,25 s (sous -35 dB) est ramené à 0,15 s. Garde début et fin.
  python3 scripts/trim_blancs.py in.mp3 out.mp3
À lancer AVANT align_episode (l'alignement est recalculé sur la voix raccourcie)."""
import sys, subprocess, numpy as np
SR = 44100
def main(src, dst, thr_db=-35, maxgap=.25, keep=.15, win=.01):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", src, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True).stdout
    a = np.frombuffer(raw, np.float32); n = int(win*SR)
    rms = np.sqrt(np.array([np.mean(a[i:i+n]**2) for i in range(0, len(a), n)]) + 1e-12)
    quiet = 20*np.log10(rms) < thr_db
    out = []; i = 0; last = 0; k = 0
    while k < len(quiet):
        if quiet[k]:
            j = k
            while j < len(quiet) and quiet[j]: j += 1
            if k > 0 and j < len(quiet) and (j - k)*win > maxgap:      # blanc intérieur trop long
                cut0 = k*n + int(keep/2*SR); cut1 = j*n - int(keep/2*SR)
                out.append(a[last:cut0]); last = cut1
            k = j
        else: k += 1
    out.append(a[last:]); b = np.concatenate(out)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-b:a", "192k", dst], input=b.tobytes(), check=True)
    print(f"{src}: {len(a)/SR:.2f} s -> {len(b)/SR:.2f} s")
if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
