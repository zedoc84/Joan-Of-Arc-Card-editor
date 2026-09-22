#!/usr/bin/env python3
"""Produit la version anglaise : traduit template.html + config.json, puis assemble."""
import base64, io, json, os, sys
from PIL import Image

BASE = ("/sessions/hopeful-eager-lovelace/mnt/1 DRIVE Personnel/2 \U0001F3E0 DOMAINES/HOBBIES/"
        "JEUX/02.BOARDGAME/05.Joan of arc/Editeur de carte joa")
PKG = os.path.join(BASE, "Editeur cartes JOA")
EDIT = os.path.join(PKG, "editeur-carte")
ASSETS = os.path.join(EDIT, "assets")
FONTS = os.path.join(BASE, "Font joa")
SRC = os.path.join(EDIT, "src", "template.html")
OUT_TPL = os.path.join(EDIT, "src", "template_en.html")
OUT_CFG = os.path.join(EDIT, "config_en.json")
OUT_HTML = os.path.join(PKG, "JOA Card Editor.html")

errors = []

# ===================================================== 1. interface (HTML/JS)
UI = [
    ('<html lang="fr">', '<html lang="en">'),
    ("<title>Éditeur de cartes JOA</title>", "<title>JOA Card Editor</title>"),
    ("<h1>Éditeur de cartes JOA<span>Unité &amp; Tarot — 100 % hors ligne</span></h1>",
     "<h1>JOA Card Editor<span>Unit &amp; Tarot — 100 % offline</span></h1>"),
    ("Images, icônes et cartes générées réservées à un usage personnel et non commercial. "
     "Toute vente ou utilisation à des fins lucratives est interdite.",
     "Images, icons and generated cards are for personal, non-commercial use only. "
     "Any sale or use for profit is prohibited."),
    # sections
    ("<summary>Gabarit &amp; image</summary>", "<summary>Template &amp; artwork</summary>"),
    ("<summary>Identité</summary>", "<summary>Identity</summary>"),
    ("<summary>Faction</summary>", "<summary>Faction</summary>"),
    ("<summary>Type d'unité</summary>", "<summary>Unit type</summary>"),
    ("<summary>Attaque</summary>", "<summary>Attack</summary>"),
    ("<summary>Défense</summary>", "<summary>Defence</summary>"),
    ("<summary>Niveau / Étoiles</summary>", "<summary>Level / Stars</summary>"),
    ("<summary>Vie &amp; commandement</summary>", "<summary>Health &amp; command</summary>"),
    ("<summary>Pouvoirs</summary>", "<summary>Powers</summary>"),
    # gabarit & image
    ('<label class="f">Type de carte</label>', '<label class="f">Card type</label>'),
    ('<label class="f">Image de fond</label>', '<label class="f">Background artwork</label>'),
    ('id="btnPic">Choisir une image…<', 'id="btnPic">Choose an image…<'),
    ('title="Retirer"', 'title="Remove"'),
    ('<label class="f">Zoom de l\'image <b id="zoomVal">', '<label class="f">Artwork zoom <b id="zoomVal">'),
    ('<label class="f">Rotation <b id="rotVal">', '<label class="f">Rotation <b id="rotVal">'),
    ('id="btnFit">Ajuster<', 'id="btnFit">Fit<'),
    ('id="btnFill">Remplir<', 'id="btnFill">Fill<'),
    ('id="btnCenter">Centrer<', 'id="btnCenter">Centre<'),
    ("Glissez sur la carte pour déplacer l'image ; molette pour zoomer.",
     "Drag on the card to move the artwork; scroll to zoom."),
    # attaque / defense
    ('<label class="f">Mode</label>', '<label class="f">Mode</label>'),
    ('<label class="f">Nombre de dés <b id="atkN">', '<label class="f">Number of dice <b id="atkN">'),
    ('<label class="f">Nombre de dés <b id="defN">', '<label class="f">Number of dice <b id="defN">'),
    ("> Afficher l'icône bouclier</label>", "> Show shield icon</label>"),
    # niveau / extras
    ("> Afficher le blason de niveau</label>", "> Show level crest</label>"),
    ('<label class="f">Étoiles</label>', '<label class="f">Stars</label>'),
    ("> Blason points de vie</label>", "> Hit-point crest</label>"),
    ("> Blason commandement</label>", "> Command crest</label>"),
    ("> Lignes de séparation (pouvoirs)</label>", "> Separator lines (powers)</label>"),
    # pouvoirs
    ('id="addText">+ Texte libre<', 'id="addText">+ Free text<'),
    ('id="clrPow">Tout effacer<', 'id="clrPow">Clear all<'),
    ('<label class="f">Éléments placés</label>', '<label class="f">Placed elements</label>'),
    ('<label class="f">Taille <b id="selScaleV">', '<label class="f">Size <b id="selScaleV">'),
    ('<label class="f">Rotation <b id="selRotV">', '<label class="f">Rotation <b id="selRotV">'),
    ('<label class="f">Texte</label>', '<label class="f">Text</label>'),
    ('<label class="f">Taille police</label>', '<label class="f">Font size</label>'),
    ('<label class="f">Couleur</label>', '<label class="f">Colour</label>'),
    ('id="selUp">&#9650; Devant<', 'id="selUp">&#9650; Forward<'),
    ('id="selDown">&#9660; Derrière<', 'id="selDown">&#9660; Back<'),
    ('id="selDel">Supprimer<', 'id="selDel">Delete<'),
    ("Cliquez un symbole pour l'ajouter, puis glissez-le sur la carte.\n"
     "          Molette = redimensionner l'élément sélectionné. <kbd>Suppr</kbd> pour l'effacer, "
     "flèches pour l'ajuster au pixel.",
     "Click a symbol to add it, then drag it onto the card.\n"
     "          Scroll = resize the selected element. <kbd>Del</kbd> to remove it, "
     "arrow keys to nudge it pixel by pixel."),
    # pied de page
    ('id="btnPng">Exporter en PNG<', 'id="btnPng">Export as PNG<'),
    ('id="btnSave">Sauver<', 'id="btnSave">Save<'),
    ('id="btnLoad">Ouvrir<', 'id="btnLoad">Open<'),
    ('id="zFit">Ajuster<', 'id="zFit">Fit<'),
    # JS
    ("b.title=k;",
     "b.title=({noir:'Black',blanc:'White',rouge:'Red',jaune:'Yellow',violet:'Purple'})[k]||k;"),
    ("lb.textContent='Dé '+(i+1);", "lb.textContent='Die '+(i+1);"),
    ("toast(it.label+' ajouté');", "toast(it.label+' added');"),
    ("text:'Texte'", "text:'Text'"),
    ("('« '+(p.text||'')+' »')", "('\\u201C'+(p.text||'')+'\\u201D')"),
    ("(st().texts.name||'carte').replace(/[^\\w\\-À-ÿ ]+/g,'').trim()||'carte'",
     "(st().texts.name||'card').replace(/[^\\w\\-À-ÿ ]+/g,'').trim()||'card'"),
    ("toast('PNG exporté');", "toast('PNG exported');"),
    ("a.download=((st().texts.name||'carte')+'.joa.json');",
     "a.download=((st().texts.name||'card')+'.joa.json');"),
    ("toast('Sauvegardé');", "toast('Saved');"),
    ("toast('Chargé');", "toast('Loaded');"),
    ("alert('Fichier illisible');", "alert('Unreadable file');"),
]

html = open(SRC, encoding="utf-8").read()
for fr, en in UI:
    n = html.count(fr)
    if n != 1:
        errors.append("UI x%d : %r" % (n, fr[:70]))
        continue
    html = html.replace(fr, en, 1)
open(OUT_TPL, "w", encoding="utf-8").write(html)

# ===================================================== 2. config (libelles)
LBL = {
    # gabarits
    "Unité": "Unit", "Tarot": "Tarot",
    # factions
    "Français": "French", "Anglais": "English", "Ottoman": "Ottoman",
    "Saint / Holy": "Holy", "Impie / UnHoly": "Unholy", "Neutre": "Neutral", "Vlad": "Vlad",
    # types
    "Infanterie": "Infantry", "Cavalerie": "Cavalry", "Volant": "Flying", "Machine": "Machine",
    # modes d'attaque
    "Mêlée": "Melee", "Tir direct": "Direct shot", "Tir courbe": "Arcing shot",
    # champs texte
    "Nom": "Name", "Trait / Skill": "Skill", "Portée": "Range",
    "Points de vie": "Hit points", "Niveau (chiffre)": "Level (number)",
    "Commandement": "Command", "Commandement (petit)": "Command (small)",
    # groupes de palette
    "Cartes": "Cards", "Dés 3D": "3D dice", "Jetons": "Tokens",
    "Faces rouges": "Red faces", "Faces noires": "Black faces",
    "Faces blanches": "White faces", "Faces jaunes": "Yellow faces",
    "Symboles": "Symbols", "Divers": "Misc",
    # elements de palette
    "Carte Tour": "Round card", "Carte Conseil": "Council card", "Carte Mythe": "Myth card",
    "Dé noir": "Black die", "Dé blanc": "White die", "Dé rouge": "Red die",
    "Dé jaune": "Yellow die", "Dé violet": "Purple die",
    "Jeton Mythe": "Myth token", "Jeton XP": "XP token",
    "Kill": "Kill", "Disrupt": "Disrupt", "Push": "Push", "Tramp": "Tramp",
    "Bouclier": "Shield", "Vierge": "Blank",
    "Face 3": "Face 3", "Face 4": "Face 4",
    "Flèche": "Arrow", "Ligne": "Line",
}
VALUES = {"Nom - Name": "Name", "Skill here": "Skill here", "Skill": "Skill"}

cfg = json.load(open(os.path.join(EDIT, "config.json"), encoding="utf-8"))
untranslated = set()


def walk(o):
    if isinstance(o, dict):
        for k, v in list(o.items()):
            if k in ("label", "group") and isinstance(v, str):
                if v in LBL:
                    o[k] = LBL[v]
                else:
                    untranslated.add(v)
            elif k == "value" and isinstance(v, str):
                o[k] = VALUES.get(v, v)
            else:
                walk(v)
    elif isinstance(o, list):
        for v in o:
            walk(v)


walk(cfg["templates"])
if untranslated:
    errors.append("libelles sans traduction : " + repr(sorted(untranslated)))
json.dump(cfg, open(OUT_CFG, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

if errors:
    print("ECHEC :")
    for e in errors:
        print("  -", e)
    sys.exit(1)

# ===================================================== 3. assemblage
used = set()


def collect(o, tpl):
    if isinstance(o, dict):
        for k, v in o.items():
            if k == "src" and isinstance(v, str):
                used.add((tpl, v))
            else:
                collect(v, tpl)
    elif isinstance(o, list):
        for v in o:
            collect(v, tpl)


def prefix(o, tpl):
    if isinstance(o, dict):
        for k, v in o.items():
            if k == "src" and isinstance(v, str) and not v.startswith(tpl + "/"):
                o[k] = tpl + "/" + v
            else:
                prefix(v, tpl)
    elif isinstance(o, list):
        for v in o:
            prefix(v, tpl)


for tpl in cfg["templates"]:
    collect(cfg["templates"][tpl], tpl)
    prefix(cfg["templates"][tpl], tpl)

assets = {}
for tpl, f in sorted(used):
    p = os.path.join(ASSETS, tpl, f)
    if not os.path.exists(p):
        print("!! image manquante:", p, file=sys.stderr)
        continue
    buf = io.BytesIO()
    Image.open(p).convert("RGBA").save(buf, "WEBP", lossless=True, quality=100, method=6)
    assets[tpl + "/" + f] = "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()

# polices : reprises telles quelles depuis le HTML francais deja construit
# (les .ttf du dossier "Font joa" ne sont pas toujours descendus d'iCloud)
FR_HTML = os.path.join(PKG, "Editeur de cartes JOA.html")
_fr = open(FR_HTML, encoding="utf-8").read()
_i = _fr.index("const FONTDATA = ")
fontdata = json.loads(_fr[_fr.index("{", _i):_fr.index(";\n", _i)])
if sorted(fontdata) != sorted(cfg["fonts"]):
    print("!! polices divergentes:", sorted(fontdata), sorted(cfg["fonts"]), file=sys.stderr)
    sys.exit(1)
faces = ["@font-face{font-family:'%s';src:url(%s) format('truetype');font-display:block}" % (n, u)
         for n, u in fontdata.items()]

html = html.replace("/*__FONTS__*/", "\n".join(faces))
html = html.replace("/*__ASSETS__*/{}", json.dumps(assets))
html = html.replace("/*__CONFIG__*/{}", json.dumps(cfg, ensure_ascii=False))
html = html.replace("/*__FONTDATA__*/{}", json.dumps(fontdata))
open(OUT_HTML, "w", encoding="utf-8").write(html)

print("traductions interface :", len(UI))
print("images embarquees     :", len(assets))
print("fichier               :", OUT_HTML, "%.2f Mo" % (os.path.getsize(OUT_HTML) / 1e6))
