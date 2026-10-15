"""Analyse des exports TikTok Studio (Analyses > Contenu > Télécharger) croisés avec data/videos_meta.csv.
  python3 scripts/analyse_tiktok.py data/export_AAAA-MM-JJ.xlsx [output/analyse]
Sortie : rapport.md (tableau, médianes par format/sujet, tendance) + vues.png (vues par vidéo dans l'ordre de publication)."""
import sys, os, csv, math, zipfile, statistics, xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont
NS = {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}; T = "{%s}t" % NS["a"]
MOIS = "janvier février mars avril mai juin juillet août septembre octobre novembre décembre".split()

def read_xlsx(p):
    z = zipfile.ZipFile(p); ss = []
    if "xl/sharedStrings.xml" in z.namelist():
        ss = ["".join(t.text or "" for t in si.iter(T)) for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("a:si", NS)]
    rows = []
    for r in ET.fromstring(z.read("xl/worksheets/sheet1.xml")).iter("{%s}row" % NS["a"]):
        row = []
        for c in r.findall("a:c", NS):
            v = c.find("a:v", NS); t = c.get("t")
            row.append(ss[int(v.text)] if t == "s" else "".join(x.text or "" for x in c.iter(T)) if t == "inlineStr" else (v.text if v is not None else ""))
        rows.append(row)
    return [dict(zip(rows[0], r)) for r in rows[1:]]

def day(s):  # « 5 octobre » -> (10, 5)
    d, m = s.split(); return (MOIS.index(m) + 1, int(d))

def main(xlsx, out):
    os.makedirs(out, exist_ok=True)
    meta = {r["id"]: r for r in csv.DictReader(open(os.path.join(os.path.dirname(__file__), "..", "data", "videos_meta.csv")))}
    vids = []
    for r in read_xlsx(xlsx):
        vid = r["Video link"].rstrip("/").split("/")[-1]; m = meta.get(vid, {})
        v = int(r["Total views"]); L, C, S = int(r["Total likes"]), int(r["Total comments"]), int(r["Total shares"])
        vids.append(dict(id=vid, date=day(r["Post time"]), datestr=r["Post time"], titre=r["Video title"][:70], vues=v, likes=L, coms=C, partages=S,
                         eng=(L + C + S)/max(v, 1)*100, promo=int(float(m.get("promo_vues") or 0)), org=v - int(float(m.get("promo_vues") or 0)), com=C/max(v, 1)*100, format=m.get("format", "?"), sujet=m.get("sujet", "?"), mascotte=m.get("mascotte", "?")))
    vids.sort(key=lambda x: (x["date"], x["id"]))
    L = ["# Analyse TikTok @papierfc", "", f"Source : {os.path.basename(xlsx)} — {len(vids)} vidéos", "",
         "| Date | Format | Sujet | Vues | dont payées | Organiques | Likes | Coms | % com | % engagement | Titre |", "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|"]
    for v in vids:
        L.append(f"| {v['datestr']} | {v['format']} | {v['sujet']} | {v['vues']:,} | {v['promo']:,} | {v['org']:,} | {v['likes']:,} | {v['coms']:,} | {v['com']:.1f} | {v['eng']:.1f} | {v['titre']} |".replace(",", " "))
    def group(key):
        g = {}
        for v in vids: g.setdefault(v[key], []).append(v["org"])
        return sorted(g.items(), key=lambda kv: -statistics.median(kv[1]))
    for key, lab in (("format", "format"), ("sujet", "sujet"), ("mascotte", "mascotte")):
        L += ["", f"## Vues ORGANIQUES médianes par {lab}", "", f"| {lab} | nb | médiane | max |", "|---|---:|---:|---:|"]
        L += [f"| {k} | {len(x)} | {int(statistics.median(x)):,} | {max(x):,} |".replace(",", " ") for k, x in group(key)]
    # tendance : médiane des 5 premières vs 5 dernières
    a, b = [v["org"] for v in vids[:5]], [v["org"] for v in vids[-5:]]
    L += ["", "## Tendance", "", f"(vues organiques = total - vues payées) Médiane des 5 premières vidéos : {int(statistics.median(a)):,} vues — des 5 dernières : {int(statistics.median(b)):,} vues.".replace(",", " ")]
    open(os.path.join(out, "rapport.md"), "w").write("\n".join(L) + "\n")
    # graphique (échelle log) : une barre par vidéo, couleur = format
    W, H, P = 1600, 800, 90; im = Image.new("RGB", (W, H), (250, 250, 246)); d = ImageDraw.Draw(im)
    try: f = ImageFont.truetype("DejaVuSans.ttf", 16)
    except OSError: f = ImageFont.load_default()
    col = {"quiz": (214, 40, 46), "histoire": (30, 80, 160), "vote": (40, 150, 80), "autre": (130, 130, 130), "?": (180, 180, 180)}
    vmax = max(v["vues"] for v in vids); y = lambda n: H - P - (math.log10(max(n, 1))/math.log10(vmax*1.3))*(H - 2*P)
    for e in range(0, 7):
        if 10**e > vmax*1.3: break
        d.line([(P, y(10**e)), (W - 20, y(10**e))], fill=(220, 220, 220)); d.text((10, y(10**e) - 8), f"{10**e:,}".replace(",", " "), fill=(90, 90, 90), font=f)
    bw = (W - P - 40)/len(vids)
    for i, v in enumerate(vids):
        x0 = P + i*bw + 6; d.rectangle([x0, y(v["vues"]), x0 + bw - 12, H - P], fill=col.get(v["format"], (180, 180, 180)))
        d.text((x0, y(v["vues"]) - 20), f"{v['vues']:,}".replace(",", " "), fill=(30, 30, 30), font=f)
        d.text((x0, H - P + 8), v["datestr"].replace("octobre", "oct").replace("septembre", "sept"), fill=(60, 60, 60), font=f)
        d.text((x0, H - P + 30), v["sujet"][:10], fill=(60, 60, 60), font=f)
    for k, (lab, c) in enumerate(col.items()):
        if lab != "?": d.rectangle([P + k*150, 20, P + k*150 + 20, 40], fill=c); d.text((P + k*150 + 28, 22), lab, fill=(30, 30, 30), font=f)
    for i, v in enumerate(vids):                                      # part payée hachurée en noir
        if v["promo"]: x0 = P + i*bw + 6; d.rectangle([x0, y(v["vues"]), x0 + bw - 12, y(max(v["org"], 1))], outline=(0, 0, 0), width=3)
    im.save(os.path.join(out, "vues.png")); print(os.path.join(out, "rapport.md"))

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "output/analyse")
