#!/usr/bin/env python3
"""Genere config.json : geometrie exacte issue des PSD pour l'editeur de cartes JOA."""
import json, os

BASE = "/sessions/hopeful-eager-lovelace/mnt/Editeur de carte joa/editeur-carte"
ASSETS = os.path.join(BASE, "assets")
man = json.load(open(os.path.join(ASSETS, "manifest.json")))


def index(tpl):
    """{nom du calque -> entree} en aplatissant les groupes."""
    out = {}
    def w(ls, path):
        for l in ls:
            p = path + [l["name"]]
            if l["type"] == "group":
                w(l["children"], p)
            else:
                out["/".join(p)] = l
    w(man[tpl]["layers"], [])
    return out


IU = index("unite")
IT = index("tarot")


def L(idx, key):
    e = idx[key]
    return {"src": e["file"], "x": e["x"], "y": e["y"], "w": e["w"], "h": e["h"]}


def opts(idx, entries):
    """entries = [(id, label, cle_calque), ...]"""
    return [{"id": i, "label": lab, "layer": L(idx, k)} for i, lab, k in entries]


# ---------------------------------------------------------------- des
def dice_set(idx, prefix, colors):
    return {c: L(idx, prefix + n) for c, n in colors}


UNI_DICE_COLORS = [("noir", "Noir"), ("blanc", "Blanc"), ("rouge", "Rouge"), ("jaune", "Jaune")]


def sockets(centers, die_ref_topleft, ref_center):
    """Convertit des centres d'alveole en liste de centres ; le decalage
    exact du de par rapport a l'alveole est calcule cote JS."""
    return {"centers": centers, "ref": ref_center, "refDie": die_ref_topleft}


cfg = {
    "fonts": {
        "Belwe-Condensed": "Belwe-Condensed.ttf",
        "TraditioAH": "traditio.ttf",
        "BaarSophiaBold": "baarsb__.TTF",
        "BaarSophia": "BAARS___.TTF",
        "BaarSophiaItalic": "baarsi__.TTF",
    },
    "templates": {},
}

# ==================================================================== UNITE
u = {
    "label": "Unité",
    "w": man["unite"]["w"],
    "h": man["unite"]["h"],
    "frame": L(IU, "FRONT / DEVANT"),
    "faction": opts(IU, [
        ("french", "Français", "Factions/FRench/Français"),
        ("english", "Anglais", "Factions/English / Anglais"),
        ("ottoman", "Ottoman", "Factions/Ottoman"),
        ("holy", "Saint / Holy", "Factions/Holy / Saint"),
        ("unholy", "Impie / UnHoly", "Factions/UnHoly / Impie"),
        ("neutral", "Neutre", "Factions/Neutre/Neutral"),
    ]),
    "unitType": opts(IU, [
        ("infanterie", "Infanterie", "Unit Type/Infanterie"),
        ("cavalerie", "Cavalerie", "Unit Type/Cavalerie"),
        ("volant", "Volant", "Unit Type/Volant"),
        ("machine", "Machine", "Unit Type/Machine"),
    ]),
    "attack": {
        "modes": opts(IU, [
            ("melee", "Mêlée", "Attaque/Attack/Mêlée/Mêlée"),
            ("direct", "Tir direct", "Attaque/Attack/Shots/Direct Shot"),
            ("arcing", "Tir courbe", "Attaque/Attack/Shots/Arcing Shot"),
        ]),
        "supports": [
            L(IU, "Attaque/Attack/Support Dé/Dice/Back 1 dé/1dice"),
            L(IU, "Attaque/Attack/Support Dé/Dice/back 2 dés/2dice"),
            L(IU, "Attaque/Attack/Support Dé/Dice/back 3dés/3dices"),
        ],
        "socketsByCount": [
            [[57.5, 504]],
            [[54.5, 504], [54.5, 574]],
            [[57.5, 503], [57.5, 573], [57.5, 642]],
        ],
        "refSocket": [57.5, 504],
        "dice": dice_set(IU, "Attaque/Attack/Dés /", UNI_DICE_COLORS),
        "maxDice": 3,
    },
    "defense": {
        "icon": L(IU, "Defense /Calque 7"),
        "supports": [
            L(IU, "Defense /Support Dé / Dice/Back 1 dé/1dice"),
            L(IU, "Defense /Support Dé / Dice/back 2 dés/2dice"),
            L(IU, "Defense /Support Dé / Dice/back 3dés/3dices"),
        ],
        "socketsByCount": [
            [[458.5, 500]],
            [[455.5, 500], [455.5, 570]],
            [[458.5, 499], [458.5, 569], [458.5, 638]],
        ],
        "refSocket": [458.5, 500],
        "dice": dice_set(IU, "Defense /Dés/", UNI_DICE_COLORS),
        "maxDice": 3,
    },
    "skillBand": L(IU, "SKILL / TRAIT/Back for Skill / Fond"),
    "texts": {
        "name":  {"label": "Nom", "value": "Nom - Name", "cx": 257, "baseline": 71,
                  "size": 41.34, "font": "Belwe-Condensed", "color": "#12100 9".replace(" ", ""),
                  "maxWidth": 345, "align": "center"},
        "skill": {"label": "Trait / Skill", "value": "Skill here", "cx": 258, "baseline": 538,
                  "size": 35.43, "font": "Belwe-Condensed", "color": "#ffffff",
                  "maxWidth": 480, "align": "center"},
        "range": {"label": "Portée", "value": "2", "cx": 80.5, "baseline": 375,
                  "size": 41.34, "font": "Belwe-Condensed", "color": "#ffffff",
                  "maxWidth": 60, "align": "center", "onlyWhen": {"field": "attackMode", "in": ["direct", "arcing"]}},
    },
    "powersOrigin": "Pouvoir / Power/",
}
cfg["templates"]["unite"] = u

# ==================================================================== TAROT
TAR_DICE_COLORS = [("noir", "Noir"), ("blanc", "Blanc"), ("rouge", "Rouge"), ("jaune", "Jaune")]
t = {
    "label": "Tarot",
    "w": man["tarot"]["w"],
    "h": man["tarot"]["h"],
    "frame": L(IT, "Calque 6"),
    "faction": opts(IT, [
        ("french", "Français", "FACTION/French / Français"),
        ("english", "Anglais", "FACTION/English / Anglais"),
        ("ottoman", "Ottoman", "FACTION/Ottoman"),
        ("holy", "Saint / Holy", "FACTION/Holy / Saint"),
        ("unholy", "Impie / UnHoly", "FACTION/UUnHoly / Impie"),
        ("neutral", "Neutre", "FACTION/Neutral / Neutre"),
        ("vlad", "Vlad", "FACTION/Vlad"),
    ]),
    "unitType": opts(IT, [
        ("infanterie", "Infanterie", "Type unité / Unity/Infanterie"),
        ("cavalerie", "Cavalerie", "Type unité / Unity/cavalerie"),
        ("volant", "Volant", "Type unité / Unity/Volant / Flying"),
        ("machine", "Machine", "Type unité / Unity/Machine"),
    ]),
    "attack": {
        "modes": opts(IT, [("melee", "Mêlée", "ATTAQUE/attaque mêlée")]),
        "supports": [
            L(IT, "ATTAQUE/Support Dés / Dice copie/support 1 Dé / Dice"),
            L(IT, "ATTAQUE/Support Dés / Dice copie/support 2 dés / Dice"),
            L(IT, "ATTAQUE/Support Dés / Dice copie/support 3 dés / Dice"),
            L(IT, "ATTAQUE/Support Dés / Dice copie/support 4 dés/dice"),
            L(IT, "ATTAQUE/Support Dés / Dice copie/support 5 dés / dice"),
        ],
        "socketsByCount": [
            [[68, 874]],
            [[68, 874], [68, 970.5]],
            [[68, 874], [68, 970.5], [68, 1064.5]],
            [[68, 874], [68, 970.5], [68, 1064.5], [68, 1159.5]],
            [[68, 874], [68, 970.5], [68, 1064.5], [68, 1159.5], [68, 1254.5]],
        ],
        # les des du groupe ATTAQUE ont ete copies : ils portent les coords
        # de la DEFENSE dans le PSD -> on les recale sur l'alveole 1 defense
        "refSocket": [753, 866],
        "dice": dice_set(IT, "ATTAQUE/Dés / Dice/", TAR_DICE_COLORS),
        "maxDice": 5,
    },
    "defense": {
        "icon": L(IT, "DEFENSE/defense"),
        "supports": [
            L(IT, "DEFENSE/Support Dés / Dice copie 2/support 1 Dé / Dice"),
            L(IT, "DEFENSE/Support Dés / Dice copie 2/support 2 dés / Dice"),
            L(IT, "DEFENSE/Support Dés / Dice copie 2/support 3 dés / Dice"),
            L(IT, "DEFENSE/Support Dés / Dice copie 2/support 4 dés/dice"),
            L(IT, "DEFENSE/Support Dés / Dice copie 2/support 5 dés / dice"),
        ],
        "socketsByCount": [
            [[753, 866]],
            [[753, 866], [753, 962.5]],
            [[753, 866], [753, 962.5], [753, 1056.5]],
            [[753, 866], [753, 962.5], [753, 1056.5], [753, 1151.5]],
            [[753, 866], [753, 962.5], [753, 1056.5], [753, 1151.5], [753, 1246.5]],
        ],
        "refSocket": [753, 866],
        "dice": dice_set(IT, "DEFENSE/Dés / Dice/", TAR_DICE_COLORS),
        "maxDice": 5,
    },
    "skillBand": L(IT, "Skill / Traits/SKILL SUPPORT"),
    "level": {
        "support": L(IT, "Level / Niveau/support level"),
        "arrow": L(IT, "Level / Niveau/fleche level"),
        "stars": [
            L(IT, "Level / Niveau/1 etoile/star"),
            L(IT, "Level / Niveau/2 etoiles/stars "),
            L(IT, "Level / Niveau/3 etoiles /stars "),
        ],
    },
    "hit": {"support": L(IT, "Hit / Vie/Hit Point")},
    "command": {"support": L(IT, "COMMAND / Commandement/commandement")},
    "lines": [L(IT, "Pouvoirs / Powers/Ligne 1 "), L(IT, "Pouvoirs / Powers/Ligne 2")],
    "texts": {
        "name":    {"label": "Nom", "value": "Nom - Name", "cx": 415, "baseline": 115,
                    "size": 70.87, "font": "Belwe-Condensed", "color": "#000000",
                    "maxWidth": 470, "align": "center"},
        "skill":   {"label": "Trait / Skill", "value": "Skill", "cx": 410, "baseline": 953,
                    "size": 47.24, "font": "Belwe-Condensed", "color": "#ffffff",
                    "maxWidth": 570, "align": "center"},
        "hit":     {"label": "Points de vie", "value": "4", "cx": 103.5, "baseline": 1340,
                    "size": 82.68, "font": "TraditioAH", "color": "#ffffff",
                    "maxWidth": 110, "align": "center"},
        "level":   {"label": "Niveau (chiffre)", "value": "4", "cx": 758.5, "baseline": 183,
                    "size": 47.24, "font": "TraditioAH", "color": "#ffffff",
                    "maxWidth": 60, "align": "center"},
        "command": {"label": "Commandement", "value": "2", "cx": 709.5, "baseline": 1358,
                    "size": 59.06, "font": "TraditioAH", "color": "#010101",
                    "maxWidth": 70, "align": "center"},
        "command2": {"label": "Commandement (petit)", "value": "1", "cx": 761, "baseline": 1352,
                     "size": 47.24, "font": "TraditioAH", "color": "#ffffff",
                     "maxWidth": 50, "align": "center"},
    },
    "powersOrigin": "Pouvoirs / Powers/",
}
cfg["templates"]["tarot"] = t

# ============================================================ palette pouvoirs
PALETTE = [
    ("Cartes", [
        ("Carte Tour", "Cartes/Carte Round / Tour"),
        ("Carte Conseil", "Cartes/Carte Council / Conseil"),
        ("Carte Mythe", "Cartes/Carte Mythe / Tactic"),
    ]),
    ("Dés 3D", [
        ("Dé noir", "Dés 3D / 3D Dice/Noir"),
        ("Dé blanc", "Dés 3D / 3D Dice/Blanc"),
        ("Dé rouge", "Dés 3D / 3D Dice/Rouge"),
        ("Dé jaune", "Dés 3D / 3D Dice/Jaune"),
        ("Dé violet", "Dés 3D / 3D Dice/Violet"),
    ]),
    ("Jetons", [
        ("Jeton Mythe", "Tokens/Myth token"),
        ("Jeton XP", "Tokens/XP token"),
    ]),
    ("Faces rouges", [
        ("Kill", "Faces Red/Rouge/Kill"),
        ("Disrupt", "Faces Red/Rouge/Disrupt"),
        ("Push", "Faces Red/Rouge/Push"),
        ("Face 4", "Faces Red/Rouge/Calque 13"),
    ]),
    ("Faces noires", [
        ("Kill", "Face Black/Noir/Kill"),
        ("Disrupt", "Face Black/Noir/Disrupt"),
        ("Bouclier", "Face Black/Noir/Shield/Bouclier"),
    ]),
    ("Faces blanches", [
        ("Vierge", "Faces White / Blanc/Blank White / Blanc vierge"),
        ("Disrupt", "Faces White / Blanc/Disrupt White / disrupt Blanc"),
        ("Push", "Faces White / Blanc/Push White / Push Blanc"),
        ("Bouclier", "Faces White / Blanc/Shield White / Bouclier Blanc"),
    ]),
    ("Faces jaunes", [
        ("Vierge", "Face Yellow / Jaune/Blank / vierge"),
        ("Disrupt", "Face Yellow / Jaune/Disrupt"),
        ("Face 3", "Face Yellow / Jaune/Calque 11"),
        ("Face 4", "Face Yellow / Jaune/Calque 12"),
    ]),
    ("Symboles", [
        ("Bouclier", "Dice symbol / symbole dé/Shield"),
        ("Push", "Dice symbol / symbole dé/push"),
        ("Kill", "Dice symbol / symbole dé/Kill"),
        ("Tramp", "Dice symbol / symbole dé/Tramp"),
        ("Disrupt", "Dice symbol / symbole dé/Disrupt"),
    ]),
]

for tpl, idx in (("unite", IU), ("tarot", IT)):
    origin = cfg["templates"][tpl]["powersOrigin"]
    groups = []
    for gname, items in PALETTE:
        its = []
        for label, key in items:
            full = origin + key
            if full in idx:
                e = idx[full]
                its.append({"id": e["file"][:-5], "label": label,
                            "src": e["file"], "w": e["w"], "h": e["h"]})
        if its:
            groups.append({"group": gname, "items": its})
    # fleche
    arrow_key = origin + ("Fleche / Arrow" if tpl == "unite" else "Flèche / Arrow")
    extra = []
    if arrow_key in idx:
        e = idx[arrow_key]
        extra.append({"id": e["file"][:-5], "label": "Flèche", "src": e["file"], "w": e["w"], "h": e["h"]})
    for lk, lab in ((origin + "Ligne 1 ", "Ligne"), (origin + "Ligne 2", "Ligne")):
        if lk in idx:
            e = idx[lk]
            extra.append({"id": e["file"][:-5], "label": lab, "src": e["file"], "w": e["w"], "h": e["h"]})
    if extra:
        groups.append({"group": "Divers", "items": extra})
    cfg["templates"][tpl]["palette"] = groups

    # position de depart des pouvoirs (centre de la zone pouvoirs du PSD)
    cfg["templates"][tpl]["powersDefault"] = {
        "unite": {"x": 258, "y": 630}, "tarot": {"x": 413, "y": 1160}}[tpl]

    # style de texte libre pour la zone pouvoirs
    cfg["templates"][tpl]["powerTextStyle"] = {
        "unite": {"size": 35.43, "font": "BaarSophiaBold", "color": "#20120c"},
        "tarot": {"size": 35.43, "font": "BaarSophiaBold", "color": "#000000"},
    }[tpl]

json.dump(cfg, open(os.path.join(BASE, "config.json"), "w"), ensure_ascii=False, indent=1)

# liste des fichiers reellement utilises
used = set()
def scan(o):
    if isinstance(o, dict):
        for k, v in o.items():
            if k == "src" and isinstance(v, str):
                used.add(v)
            else:
                scan(v)
    elif isinstance(o, list):
        for v in o:
            scan(v)
for tpl in cfg["templates"]:
    s = set()
    scan(cfg["templates"][tpl])
    print(tpl, len(s))
scan(cfg)
print("assets utilises:", len(used))
missing = []
for tpl in ("unite", "tarot"):
    for f in used:
        pass
print("OK -> config.json")
