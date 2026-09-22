# Éditeur de cartes JOA — notes techniques

Le fichier livré est **`../Editeur de cartes JOA.html`** : un seul fichier autonome
(4,7 Mo) qui contient les 133 calques extraits des deux PSD (en WebP sans perte,
base64) et les 5 polices du dossier `Font joa`. Il fonctionne hors ligne, sans
serveur, par simple double-clic. Ce dossier-ci n'est **pas** nécessaire pour
l'utiliser — il sert uniquement à le régénérer.

## Contenu

| Dossier / fichier | Rôle |
|---|---|
| `assets/unite/`, `assets/tarot/` | un PNG transparent par calque des PSD |
| `assets/manifest.json` | arborescence des calques + coordonnées d'origine |
| `config.json` | géométrie de l'éditeur (options, alvéoles de dés, styles de texte) |
| `src/mkconfig.py` | génère `config.json` à partir du manifeste |
| `src/template.html` | le code de l'éditeur, sans les assets |
| `src/build.py` | assemble `template.html` + assets + polices → le HTML final |
| `src/verify.py` | rejoue le pipeline de rendu en Python (contrôle de la géométrie) |

## Régénérer après modification

```bash
python3 src/mkconfig.py      # si la géométrie change
python3 src/build.py         # produit "Editeur de cartes JOA.html"
python3 src/verify.py        # rendu de contrôle dans outputs/verif/
```

Les chemins sont en dur en haut de chaque script.

## Points de calage relevés dans les PSD

* **Textes** — police, corps, couleur et ligne de base repris de l'*engine data*
  Photoshop ; la ligne de base correspond au bas de la boîte du calque texte
  d'origine (vérifié à ±1 px sur 12 des 14 calques).
* **Dés** — les alvéoles des supports ont été détectées par analyse des zones
  sombres opaques de chaque image de support. Le décalage exact d'un dé par
  rapport à son alvéole est repris du PSD (alvéole n°1) puis appliqué aux
  autres. Unité : 3 dés max, Tarot : 5.
* **Groupe ATTAQUE du tarot** — les calques de dés y sont un copier-coller du
  groupe DEFENSE et portent ses coordonnées ; l'éditeur les recale sur
  l'alvéole n°1 de la défense (`refSocket`).
* **Image de fond** — dessinée sous le cadre, exactement comme le calque
  « Your PIC / Votre Image » du PSD : elle apparaît partout où le cadre est
  transparent.
