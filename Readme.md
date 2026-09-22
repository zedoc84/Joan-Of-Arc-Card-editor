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


