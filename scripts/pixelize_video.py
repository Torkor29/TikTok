"""Convertit N'IMPORTE QUELLE vidéo déjà rendue en DA pixel.fc (gros pixels 4×4 + palette 32 couleurs + lignes de balayage),
le son est copié tel quel. Pour les vidéos refaites « proprement » (textes nets en police pixel), utiliser PIXEL=1 au rendu.
  python3 scripts/pixelize_video.py output/x/x.mp4 [sortie.mp4] [--scale 4] [--dither]"""
import sys, os, subprocess, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "engine"))
a = [x for x in sys.argv[1:] if not x.startswith("--")]
if "--scale" in sys.argv: os.environ["PIXEL_SCALE"] = sys.argv[sys.argv.index("--scale") + 1]; a = [x for x in a if x != os.environ["PIXEL_SCALE"]]
import pixel as PX
from PIL import Image
src = a[0]; dst = a[1] if len(a) > 1 else src.replace(".mp4", "_pixel.mp4")
info = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=width,height,r_frame_rate", "-of", "json", src], capture_output=True, text=True).stdout)["streams"][0]
w, h, fps = info["width"], info["height"], info["r_frame_rate"]
dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
tmp = dst + ".v.mp4"
enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", fps, "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", tmp], stdin=subprocess.PIPE)
n = 0
while True:
    buf = dec.stdout.read(w*h*3)
    if len(buf) < w*h*3: break
    im = PX.pixelate(Image.frombytes("RGB", (w, h), buf), dither="--dither" in sys.argv).convert("RGBA"); PX.scanlines(im)
    enc.stdin.write(im.convert("RGB").tobytes()); n += 1
enc.stdin.close(); enc.wait(); dec.wait()
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", tmp, "-i", src, "-map", "0:v", "-map", "1:a?", "-c:v", "copy", "-c:a", "copy", dst], check=True); os.remove(tmp)
print(dst, n, "images")
