"""Images libres de droits depuis Wikimedia Commons (API officielle), avec licence et auteur conservés.
  python3 scripts/commons_fetch.py "Harry Kane" assets/photos/commons/kane [--n 4] [--width 1400]
Écrit les images + un credits.json (titre, auteur, licence, url) à citer en description si la licence l'exige (CC BY / BY-SA).
Doucement sur l'API : User-Agent identifié, 1 requête par seconde, peu de fichiers."""
import sys, os, json, time, re, argparse, urllib.parse, urllib.request
API = "https://commons.wikimedia.org/w/api.php"
UA = "papierfc-tiktok-bot/1.0 (montage video perso; contact via github Torkor29)"
OK_LIC = ("cc0", "public domain", "pd", "cc by", "cc-by", "cc by-sa", "cc-by-sa")
def get(params):
    q = API + "?" + urllib.parse.urlencode(dict(params, format="json"))
    req = urllib.request.Request(q, headers={"User-Agent": UA}); time.sleep(1)
    with urllib.request.urlopen(req, timeout=30) as r: return json.load(r)
def clean(html): return re.sub(r"<[^>]+>", "", html or "").strip()
def search(query, n=4, width=1400):
    d = get(dict(action="query", generator="search", gsrsearch=f"{query} filetype:bitmap", gsrnamespace=6, gsrlimit=20,
                 prop="imageinfo", iiprop="url|extmetadata|size|mime", iiurlwidth=width))
    out = []
    for p in sorted(d.get("query", {}).get("pages", {}).values(), key=lambda p: p.get("index", 99)):
        ii = (p.get("imageinfo") or [{}])[0]; md = ii.get("extmetadata", {})
        lic = clean(md.get("LicenseShortName", {}).get("value", "")); mime = ii.get("mime", "")
        if mime not in ("image/jpeg", "image/png") or not any(k in lic.lower() for k in OK_LIC): continue
        if ii.get("height", 0) < 700: continue
        out.append(dict(title=p["title"], url=ii.get("thumburl") or ii["url"], page=ii.get("descriptionurl"), license=lic,
                        author=clean(md.get("Artist", {}).get("value", "")), w=ii.get("width"), h=ii.get("height")))
        if len(out) >= n: break
    return out
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("query"); ap.add_argument("outdir"); ap.add_argument("--n", type=int, default=4); ap.add_argument("--width", type=int, default=1400)
    a = ap.parse_args(); os.makedirs(a.outdir, exist_ok=True); res = search(a.query, a.n, a.width); cred = []
    for i, r in enumerate(res):
        ext = ".png" if r["url"].lower().endswith(".png") else ".jpg"; fn = os.path.join(a.outdir, f"{i}{ext}")
        req = urllib.request.Request(r["url"], headers={"User-Agent": UA}); time.sleep(1)
        with urllib.request.urlopen(req, timeout=60) as resp, open(fn, "wb") as f: f.write(resp.read())
        r["file"] = fn; cred.append(r); print(fn, "|", r["license"], "|", r["author"][:60], "|", r["title"])
    json.dump(cred, open(os.path.join(a.outdir, "credits.json"), "w"), ensure_ascii=False, indent=1)
if __name__ == "__main__": main()
