#!/usr/bin/env python3
"""Assemble l'editeur en un seul fichier HTML autonome (images + polices en base64)."""
import base64, io, json, os, re, sys
from PIL import Image

ROOT = "/sessions/hopeful-eager-lovelace/mnt/Editeur de carte joa"
EDIT = os.path.join(ROOT, "editeur-carte")
ASSETS = os.path.join(EDIT, "assets")
FONTS = os.path.join(ROOT, "Font joa")
TPL = "/sessions/hopeful-eager-lovelace/mnt/outputs/build/template.html"
OUT = os.path.join(ROOT, "Editeur de cartes JOA.html")

cfg = json.load(open(os.path.join(EDIT, "config.json")))

# ---- fichiers image reellement references par la config -------------------
used = set()
def scan(o, tpl=None):
    if isinstance(o, dict):
        for k, v in o.items():
            if k == "src" and isinstance(v, str):
                used.add((tpl, v))
            else:
                scan(v, tpl)
    elif isinstance(o, list):
        for v in o:
            scan(v, tpl)

for tpl in cfg["templates"]:
    scan(cfg["templates"][tpl], tpl)

# on prefixe les src par le dossier du gabarit pour eviter les collisions
def rewrite(o, tpl):
    if isinstance(o, dict):
        for k, v in o.items():
            if k == "src" and isinstance(v, str) and not v.startswith(tpl + "/"):
                o[k] = tpl + "/" + v
            else:
                rewrite(v, tpl)
    elif isinstance(o, list):
        for v in o:
            rewrite(v, tpl)

for tpl in cfg["templates"]:
    rewrite(cfg["templates"][tpl], tpl)

assets = {}
total_raw = 0
for tpl, f in sorted(used):
    p = os.path.join(ASSETS, tpl, f)
    if not os.path.exists(p):
        print("!! manquant:", p, file=sys.stderr)
        continue
    im = Image.open(p).convert("RGBA")
    buf = io.BytesIO()
    im.save(buf, "WEBP", lossless=True, quality=100, method=6)
    total_raw += buf.tell()
    assets[tpl + "/" + f] = "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()

# ---- polices --------------------------------------------------------------
fontdata, faces = {}, []
for name, fn in cfg["fonts"].items():
    p = os.path.join(FONTS, fn)
    if not os.path.exists(p):
        print("!! police manquante:", p, file=sys.stderr)
        continue
    b64 = base64.b64encode(open(p, "rb").read()).decode()
    url = "data:font/ttf;base64," + b64
    fontdata[name] = url
    faces.append("@font-face{font-family:'%s';src:url(%s) format('truetype');font-display:block}" % (name, url))

html = open(TPL, encoding="utf-8").read()
html = html.replace("/*__FONTS__*/", "\n".join(faces))
html = html.replace("/*__ASSETS__*/{}", json.dumps(assets))
html = html.replace("/*__CONFIG__*/{}", json.dumps(cfg, ensure_ascii=False))
html = html.replace("/*__FONTDATA__*/{}", json.dumps(fontdata))

open(OUT, "w", encoding="utf-8").write(html)
print("images embarquees :", len(assets), "(%.2f Mo webp)" % (total_raw / 1e6))
print("polices           :", len(fontdata))
print("fichier           :", OUT, "%.2f Mo" % (os.path.getsize(OUT) / 1e6))
