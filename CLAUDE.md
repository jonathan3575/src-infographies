# CLAUDE.md — Règles d'or du projet Infographies SRC

## Ton
- Tutoyer le lecteur (chirurgien membre de la SRC).
- Bienveillant, jamais culpabilisant.
- Disruptif sur UN seul élément par planche (le chiffre choc).

## Identité visuelle (verrouillée)
- Palettes : voir SPEC.md §3. Aucun ajout de couleur hors palette.
- Fonts : Bebas Neue (display), DM Sans (body), Space Mono (mono). Aucune autre font.
- Logo SRC : présent en footer de chaque planche (print + TL).

## Règles de mise en page PRINT A4
- Format : 210×297mm, marges 12mm.
- Texte corps : minimum 10pt (jamais en dessous).
- Le titre principal utilise Bebas Neue, taille 56pt minimum.
- Le screenshot Follow occupe au moins 35% de la surface.
- L'encart "à quoi ça sert" est OBLIGATOIRE, en bas de planche.
- Pied de page : logo SRC + numéro de planche + version.

## Règles de mise en page TL vertical
- Format : 1080×1920px, scroll vertical avec scroll-snap par section.
- 5 à 7 sections maximum.
- Une section = un message. Pas de mur de texte.
- Animation à l'entrée de chaque section (intersection observer).
- Durée du scroll automatique pour l'export MP4 : 25 à 35 secondes.

## Code couleur des annotations sur screenshots Follow
- `--action` : le chir doit remplir activement.
- `--critical` : champ critique (ex : variable Y projet thérapeutique). Max 2 par planche.
- `--passive` : déjà rempli par le patient ou auto.
Toujours ajouter une légende visible sur la planche.

## Workflow
1. Build : `make 2L` → produit `output/pdf/2L_print_vN.pdf` et `output/tl/2L_tl_vN.mp4`.
2. QA : `make qa` → lance l'agent qa-scorer, retourne un score sur 100.
3. Si score < 95 : Claude Code corrige automatiquement et re-build.
4. Boucle jusqu'à score ≥ 95.

## Interdits
- Pas d'emoji dans les planches imprimées.
- Pas de capture d'écran retouchée (on annote en SVG par-dessus, on ne modifie pas le screenshot).
- Pas de mention nominative d'un chir ou d'une marque industrielle.
- Pas de "vous" — toujours "tu".
