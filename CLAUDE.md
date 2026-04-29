# CLAUDE.md — Règles d'or du projet Infographies SRC

## Ton
- Tutoyer le lecteur (Spine Surgeon membre de la SRC).
- Bienveillant, jamais culpabilisant.
- Disruptif sur UN seul élément par planche (le chiffre choc).

## Identité visuelle (verrouillée)
- Palettes : voir SPEC.md §3. Aucun ajout de couleur hors palette. Le mot-clé CSS `white` est toléré (la regex QA ne flaggue que les hex 6-digits).
- Fonts : Bebas Neue (display), DM Sans (body), Space Mono (mono). Aucune autre font.
- Logo SRC : présent dans le header ET le footer de chaque planche (print + TL).

## Règles de mise en page PRINT A4
- Format : 210×297mm, marges 12mm.
- Texte BODY (DM Sans, Bebas Neue) : minimum 10pt.
- Texte MONO/CAPTION (Space Mono) : minimum 8pt (étiquettes discrètes : header-meta, frise-step, footer-meta, branch-label).
- Le titre principal utilise Bebas Neue, taille 56pt minimum (var `--title-size`).
- Le hero (screenshot ou SVG) doit porter `data-screenshot-area-min="35"`.
- L'encart "à quoi ça sert" est OBLIGATOIRE.
- Pied de page : logo SRC + numéro de planche + date (la version a été retirée).
- **La planche DOIT tenir sur 1 page A4.** En cas de débordement, compresser en priorité : padding, font-sizes des sections (en respectant les minima ci-dessus), max-height du hero.

## Règles de mise en page TL vertical
- Format de référence : 1080×1920px, mais le template doit être **responsive** (vw, vh, clamp) pour fonctionner en mobile DevTools (~400px) sans débordement horizontal.
- 4 à 7 sections scroll-snap (Jo a accepté 4 sections sur 2L et 00).
- IntersectionObserver pour fade-in à l'entrée de chaque section.
- Durée du scroll automatique pour l'export MP4 : **12 à 18 secondes** (`TL_SCROLL_DURATION_MS = 15_000` dans `src/export.py`).

## Code couleur des annotations sur screenshots Follow
- `--action` : le chir doit remplir activement.
- `--critical` : champ critique (ex : variable Y projet thérapeutique). Max 2 par planche.
- `--passive` : déjà rempli par le patient ou auto.
- La légende dédiée a été supprimée des planches finales (slot QA #5 deprecated) ; la convention reste utilisée en interne dans les SVG.

## Les 7 zones obligatoires (data-zone)
Chaque planche (print + TL) doit contenir : `header`, `identity`, `hero`, `disrupteur`, `valeur`, `frise`, `footer`. Vérifié par le check QA #6.

## Pipeline de build
```
make {ID}        # render + export print + export TL pour la planche {ID}
                 # → output/{pdf,tl}/{ID}_{print,tl}_v{N}.{html,pdf,mp4,webm}
make qa          # QA score sur la 2L (cible historique)
make qa-{ID}     # QA score sur une planche précise
make all-planches    # build toutes les planches détectées dans data/questionnaires/
make publish-all     # publie les dernières versions dans docs/ pour GitHub Pages
make deploy          # publish-all + git add docs/ + commit + push
```

`make` utilise `.venv/bin/python` automatiquement (pas de `python` système sur cette machine). Le PATH des subprocess n'inclut pas `/opt/homebrew/bin` — `find_tool()` dans `export.py`/`qa.py` fait le fallback pour `ffmpeg`/`ffprobe`.

## Routing des templates
Dans `src/render.py` :
- `q.id == "00"` → `templates/print_a4_manifeste.html.j2` + `templates/tl_vertical_manifeste.html.j2`
- Sinon → `templates/print_a4.html.j2` + `templates/tl_vertical.html.j2`

Le manifeste a sa propre structure : pas de Follow screenshot, hero = double timeline SVG inline, encart valeur = "Mot du bureau" avec photo.

## Versioning
`src/render.py:next_version()` scanne `output/{pdf,tl}/{ID}_{print,tl}_v*.html` et incrémente automatiquement. Les versions précédentes ne sont JAMAIS supprimées (debug + historique).

## Système QA (src/qa.py + .claude/agents/qa-scorer.md)
- 18 checks actifs (slots #5 "légende" et #15 "contraste WCAG" sont DEPRECATED, non comptabilisés).
- Score normalisé : `round(passed × 100 / 18)`.
- Seuil de livraison : **95/100**.
- Check #11 affiné : distingue body (≥10pt) vs mono (≥8pt) via `font-family` détecté dans la règle CSS.

## Photos institutionnelles
- `assets/brand/logo_src.jpeg` : header + footer partout.
- `assets/brand/bureau_src.jpg` : photo institutionnelle restaurant, utilisée dans le **mot du bureau de la planche 00**.
- `assets/brand/bureau_src_rooftop.jpg` : photo communauté rooftop, utilisée dans l'**encart "À propos" de la page d'accueil**.

Les 3 sont listés dans `BRAND_ASSETS` (publish.py) et copiés systématiquement dans `docs/assets/brand/` à chaque `make publish-all`.

## Pitfalls connus (à savoir avant de toucher le code)
- **Jinja2 `s.items` est masqué par `dict.items()`** → toujours utiliser `s["items"]` (cf. v2 print template).
- **`ffmpeg`/`ffprobe` à `/opt/homebrew/bin/`** ne sont pas dans le PATH du subprocess `make` → utiliser `find_tool()` qui fallback sur les chemins Homebrew + /usr/local/bin.
- **Couleurs SVG inline** : la regex QA `#[0-9A-Fa-f]{6}\b` détecte les hex hors palette. Utiliser uniquement les hex de SPEC §3, ou `white` (mot-clé) pour les fonds clairs.
- **Mix-blend-mode sur le logo** : `multiply` sur fond clair (cream/white), `screen` sur fond sombre (page d'accueil dark). Le JPEG du logo a un fond blanc ; sur fond cream, l'inclure dans une `.logo-chip` cream + `mix-blend-mode: multiply` pour intégrer sans halo.
- **Path SVG en équerre** : pour les branches non-op (8L/8C), utiliser `Q ... Q ...` ou cubic Bézier avec contrôle agressif vers l'extérieur. Le tracé doit visuellement DIVERGER, pas converger.

## Workflow type pour une nouvelle planche
1. Créer `data/questionnaires/{ID}.json` (schema Pydantic dans `src/schema.py`).
2. Déposer les screenshots Follow dans `assets/screenshots/follow/`.
3. `make {ID}` → produit v1 (PDF + TL).
4. Itérer le contenu (JSON) + ajustements visuels (templates) → v2, v3...
5. Validation visuelle Jo après chaque itération significative.
6. `make qa-{ID}` → score ≥ 95.
7. `make publish-all && make deploy` après accord explicite.

## Interdits
- Pas d'emoji dans les planches imprimées.
- Pas de capture d'écran retouchée (annoter en SVG par-dessus, ne jamais modifier le PNG source).
- Pas de mention nominative d'un chir ou d'une marque industrielle.
- Pas de "vous" — toujours "tu".
- Pas de rebuild ni de push sans permission explicite (cf. memory/feedback_workflow).
