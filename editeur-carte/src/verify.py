#!/usr/bin/env python3
"""Reimplemente le pipeline de rendu de l'editeur en PIL pour verifier la geometrie."""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont

ROOT = "/sessions/hopeful-eager-lovelace/mnt/Editeur de carte joa"
EDIT = os.path.join(ROOT, "editeur-carte")
ASSETS = os.path.join(EDIT, "assets")
FONTS = os.path.join(ROOT, "Font joa")
cfg = json.load(open(os.path.join(EDIT, "config.json")))
problems = []


def img(tpl, src):
    p = os.path.join(ASSETS, tpl, src.split("/")[-1])
    if not os.path.exists(p):
        problems.append("image manquante: " + p)
        return None
    return Image.open(p).convert("RGBA")


def paste(base, tpl, l):
    if not l:
        return
    im = img(tpl, l["src"])
    if im is None:
        return
    if im.size != (l["w"], l["h"]):
        im = im.resize((l["w"], l["h"]))
    base.alpha_composite(im, (l["x"], l["y"]))


def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, cfg["fonts"][name]), int(round(size)))


def text(d, style, value):
    if not value:
        return
    f = font(style["font"], style["size"])
    w = d.textlength(value, font=f)
    if w > style.get("maxWidth", 1e9):
        f = font(style["font"], style["size"] * style["maxWidth"] / w)
        w = d.textlength(value, font=f)
    x = style["cx"] if style.get("align") == "left" else style["cx"] - w / 2
    d.text((x, style["baseline"]), value, font=f, fill=style["color"], anchor="ls")


def dice(base, tpl, cfgd, colors):
    n = len(colors)
    if n < 1:
        return
    idx = min(n, len(cfgd["supports"])) - 1
    paste(base, tpl, cfgd["supports"][idx])
    sock = cfgd["socketsByCount"][idx]
    ref = cfgd["refSocket"]
    for i in range(min(n, len(sock))):
        dl = cfgd["dice"].get(colors[i])
        if not dl:
            problems.append("couleur de de inconnue: %s (%s)" % (colors[i], tpl))
            continue
        im = img(tpl, dl["src"])
        if im is None:
            continue
        base.alpha_composite(im, (int(round(sock[i][0] + dl["x"] - ref[0])),
                                  int(round(sock[i][1] + dl["y"] - ref[1]))))


def render(tplkey, state):
    t = cfg["templates"][tplkey]
    base = Image.new("RGBA", (t["w"], t["h"]), (255, 255, 255, 0))
    ph = Image.new("RGBA", (t["w"], t["h"]), (58, 78, 96, 255))
    dd = ImageDraw.Draw(ph)
    for i in range(0, max(t["w"], t["h"]), 40):
        dd.line([(i, 0), (0, i)], fill=(84, 108, 128, 255), width=6)
    base.alpha_composite(ph)
    paste(base, tplkey, t["frame"])
    d = ImageDraw.Draw(base)
    text(d, t["texts"]["name"], state["name"])

    order = (["skill", "powers", "defense", "attack", "faction", "type"] if tplkey == "unite"
             else ["defense", "attack", "hit", "type", "powers", "command", "skill", "level", "faction"])
    for step in order:
        if step == "skill":
            paste(base, tplkey, t["skillBand"]); d = ImageDraw.Draw(base)
            text(d, t["texts"]["skill"], state["skill"])
        elif step == "powers":
            for l in t.get("lines", []):
                paste(base, tplkey, l)
            for p in state.get("powers", []):
                item = None
                for g in t["palette"]:
                    for it in g["items"]:
                        if it["label"] == p[0] and g["group"] == p[1]:
                            item = it
                if item is None:
                    problems.append("symbole introuvable: %s / %s" % p[:2]); continue
                im = img(tplkey, item["src"])
                base.alpha_composite(im, (int(p[2] - item["w"] / 2), int(p[3] - item["h"] / 2)))
        elif step == "defense":
            dice(base, tplkey, t["defense"], state["def"])
            paste(base, tplkey, t["defense"]["icon"])
        elif step == "attack":
            dice(base, tplkey, t["attack"], state["atk"])
            m = [o for o in t["attack"]["modes"] if o["id"] == state["mode"]]
            if not m:
                problems.append("mode d'attaque inconnu: " + state["mode"]); m = t["attack"]["modes"][:1]
            paste(base, tplkey, m[0]["layer"])
            rt = t["texts"].get("range")
            if rt and (not rt.get("onlyWhen") or state["mode"] in rt["onlyWhen"]["in"]):
                d = ImageDraw.Draw(base); text(d, rt, state.get("range", ""))
        elif step == "faction":
            o = [o for o in t["faction"] if o["id"] == state["faction"]]
            if not o: problems.append("faction inconnue: " + state["faction"]); o = t["faction"][:1]
            paste(base, tplkey, o[0]["layer"])
        elif step == "type":
            o = [o for o in t["unitType"] if o["id"] == state["type"]]
            if not o: problems.append("type inconnu: " + state["type"]); o = t["unitType"][:1]
            paste(base, tplkey, o[0]["layer"])
        elif step == "hit" and t.get("hit"):
            paste(base, tplkey, t["hit"]["support"])
            d = ImageDraw.Draw(base); text(d, t["texts"]["hit"], state.get("hit", ""))
        elif step == "command" and t.get("command"):
            paste(base, tplkey, t["command"]["support"])
            d = ImageDraw.Draw(base)
            text(d, t["texts"]["command"], state.get("cmd", ""))
            text(d, t["texts"]["command2"], state.get("cmd2", ""))
        elif step == "level" and t.get("level"):
            paste(base, tplkey, t["level"]["support"])
            paste(base, tplkey, t["level"]["arrow"])
            paste(base, tplkey, t["level"]["stars"][state.get("stars", 1) - 1])
            d = ImageDraw.Draw(base); text(d, t["texts"]["level"], state.get("lvl", ""))
    return base


U = dict(name="Grenadiers", skill="Tir en salve", faction="english", type="infanterie",
         mode="arcing", range="3", atk=["rouge", "noir", "blanc"], **{"def": ["blanc", "jaune"]},
         powers=[("Kill", "Faces rouges", 190, 630), ("Flèche", "Divers", 277, 653),
                 ("Jeton XP", "Jetons", 340, 635)])
T = dict(name="Vlad Tepes", skill="Terreur nocturne", faction="vlad", type="cavalerie",
         mode="melee", atk=["rouge", "noir", "blanc", "jaune"], **{"def": ["blanc", "noir", "rouge"]},
         hit="6", cmd="3", cmd2="2", lvl="5", stars=3,
         powers=[("Kill", "Faces noires", 300, 1180), ("Flèche", "Divers", 400, 1180),
                 ("Jeton Mythe", "Jetons", 500, 1180)])

os.makedirs("/sessions/hopeful-eager-lovelace/mnt/outputs/verif", exist_ok=True)
for k, s in (("unite", U), ("tarot", T)):
    im = render(k, s)
    im.convert("RGB").save("/sessions/hopeful-eager-lovelace/mnt/outputs/verif/%s.png" % k)
    print("rendu", k, im.size)

# controle d'exhaustivite : tous les calques du manifeste sont-ils utilises ?
man = json.load(open(os.path.join(ASSETS, "manifest.json")))
used = set()
def scan(o):
    if isinstance(o, dict):
        for k, v in o.items():
            if k == "src": used.add(v)
            else: scan(v)
    elif isinstance(o, list):
        for v in o: scan(v)
for k in cfg["templates"]: scan(cfg["templates"][k])

for k in man:
    def w(ls, path=""):
        for l in ls:
            if l["type"] == "group": w(l["children"], path + l["name"] + "/")
            elif l.get("file") and l["file"] not in used and "text" not in l:
                print("  NON UTILISE [%s] %s%s" % (k, path, l["name"]))
    w(man[k]["layers"])

print("\nPROBLEMES:", problems if problems else "aucun")
