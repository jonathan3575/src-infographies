---
name: infographic-build
description: Construire une infographie SRC à partir d'un JSON de questionnaire. Utiliser ce skill pour toute génération de planche print A4 ou TL vertical.
---

# Skill : Construction d'une infographie SRC

## Étapes obligatoires (dans cet ordre)

1. **Charger** le JSON `data/questionnaires/{ID}.json`.
2. **Valider** avec le schema Pydantic (`src/schema.py`). Si invalide, stopper et corriger le JSON.
3. **Vérifier** la présence des assets : `assets/brand/logo_src.jpeg`, `assets/screenshots/follow/{ID}.png`.
4. **Rendre** le HTML via Jinja2 (`src/render.py`).
5. **Exporter** via Playwright (`src/export.py`) : PDF pour print, MP4 pour TL.
6. **Versionner** : si une version existe déjà, incrémenter (v1 → v2 → v3).
7. **Lancer le QA** systématiquement après chaque build.

## Anatomie obligatoire d'une planche (les 7 zones)

1. **Bandeau header** — numéro de planche (#XX/12), code questionnaire + nom long, logo SRC.
2. **Carte d'identité** — qui remplit (patient/chir avec picto), étape parcours, durée estimée chir, fréquence.
3. **Hero visuel** — screenshot Follow + annotations SVG superposées (action / critical / passive) + légende.
4. **Disrupteur** — UN chiffre choc plein largeur en Bebas Neue, accroche courte.
5. **À quoi ça sert** — encart explicatif (3-5 puces) sur la valeur clinique/recherche.
6. **Mini-frise parcours** — situe la planche dans le flow SRC global.
7. **Footer** — logo SRC, version, date.

## Convention de nommage des fichiers

- JSON source : `data/questionnaires/{ID}.json`
- Screenshot : `assets/screenshots/follow/{ID}.png` (ou `{ID}_partN.png` si multi)
- PDF : `output/pdf/{ID}_print_v{N}.pdf`
- TL HTML : `output/tl/{ID}_tl_v{N}.html`
- TL MP4 : `output/tl/{ID}_tl_v{N}.mp4`
- QA report : `output/qa-reports/{ID}_v{N}.json`

## Si le screenshot Follow est multi-pages

Si plusieurs screenshots existent (`2L_part1.png`, `2L_part2.png`...), les empiler verticalement dans le hero visuel avec un séparateur fin `--border`.

## Itération

Après chaque correction, **toujours re-build et re-QA**. Ne pas modifier le HTML directement, toujours passer par le template + JSON.
