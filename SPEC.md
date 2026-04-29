# SPEC — Infographies SRC

> Document de spécification pour Claude Code. Source de vérité du projet.
> Lis ce fichier intégralement avant toute action. Ne dévie pas des règles verrouillées.

---

## 1. Contexte

La **Spine Research Community (SRC)** est une communauté d'environ 50 chirurgiens du rachis en France. Tous utilisent le logiciel de consultation **Follow** comme base de données commune. Tous les utilisateurs Follow de la SRC sont paramétrés de la même manière pour garder une base propre, mais le remplissage est inégal selon les chirurgiens.

**Objectif de ce projet** : produire une série d'infographies pédagogiques pour **éduquer les chirurgiens au bon remplissage** de chaque questionnaire SRC. Une infographie par questionnaire, ton bienveillant et tutoiement, parfois disruptif pour attirer l'œil. On ne culpabilise pas, on motive.

**Liste exhaustive des questionnaires de la série** :

| Code | Type | Qui remplit | Étape |
|------|------|-------------|-------|
| 1D | Démographie | Patient (tablette) | Commun L+C |
| 2L | Éval lombaire initiale | Patient + chir | T0 lombaire |
| 4L | Diagnostic lombaire | Chir | Pré-op L |
| 5L | Programmation lombaire | Chir | Pré-op L |
| 2C | Éval cervicale initiale | Patient + chir | T0 cervical |
| 4C | Diagnostic cervical | Chir | Pré-op C |
| 5C | Programmation cervicale | Chir | Pré-op C |
| 6a | CRO (Compte-rendu opératoire) | Chir | Per-op (commun L+C) |
| 6b | CRH (Compte-rendu hospit) | Chir | Post-op (commun L+C) |
| 1M / 3M / 6M / 1A / 2A L | Suivi lombaire | Patient + chir | Post-op L |
| 1M / 3M / 6M / 1A / 2A C | Suivi cervical | Patient + chir | Post-op C |
| ODI / NDI | Score fonctionnel | Patient | À chaque suivi |
| 8L / 8C | Suivi médical/non-op | Patient | Continu |

Note : il existe aussi un parcours **scoliose jeune** (2IS, 4IS, 5IS, suivis IS avec SRS + EQ5D + capture EOS) — sera traité dans une seconde série.

**Objectif de cette session Claude Code** : créer le repo, le système de templates, et produire la **première planche : 2L**. Une fois 2L validée, les autres se déclinent avec un nouveau JSON.

---

## 2. Deux livrables par questionnaire

Chaque questionnaire produit **deux versions** issues d'un même JSON source :

1. **Print A4 portrait** (PDF) — pour les bureaux des chirurgiens et secrétaires. Fond clair, dense, lisible imprimé. Usage : affichage mural, classeur, distribution lors de réunions SRC.
2. **TL vertical 1080×1920** (HTML interactif + export MP4) — pour WhatsApp. Fond sombre type newsletter SRC, scrollable façon "story", animations légères. Usage : envoi groupé sur WhatsApp.

Une seule source JSON, deux templates, deux rendus.

---

## 3. Identité visuelle SRC

### Logo
`assets/brand/logo_src.jpeg` — monogramme `C` bleu marine profond avec `SR` encarté, `Spine Research Community` en arc autour.

### Palette PRINT A4 (fond clair)

```css
:root {
  --src-navy: #1E2D3D;     /* identité SRC, structure, titres */
  --action: #00A890;       /* zones que LE CHIR doit remplir */
  --critical: #C48F1A;     /* LE champ critique (variable Y, sans lui la donnée est morte) */
  --passive: #B8BEC7;      /* champs auto / patient / déjà saisis ailleurs */
  --cream: #F8F6F1;        /* fond papier doux */
  --text: #0E1117;         /* corps de texte */
  --muted-text: #5B6470;   /* texte secondaire */
  --border: #E5E2DB;       /* lignes fines */
}
```

### Palette TL vertical (fond sombre, dérivée de la newsletter SRC d'avril 2026)

```css
:root {
  --bg: #080A0F;
  --bg2: #0E1117;
  --bg3: #141820;
  --teal: #00D4B4;         /* action chir */
  --teal-dim: #00A890;
  --gold: #F0B429;         /* critique */
  --gold-dim: #C48F1A;
  --white: #F0EDE8;
  --muted: #6B7280;
  --border: rgba(255,255,255,0.07);
}
```

### Typographie (les deux versions)

```html
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,600;1,9..40,300&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
```

```css
--font-display: 'Bebas Neue', sans-serif;   /* titres énormes, chiffres choc */
--font-body: 'DM Sans', sans-serif;          /* corps, descriptions */
--font-mono: 'Space Mono', monospace;        /* étiquettes, métadonnées, accents techniques */
```

### Convention couleur des champs (alignée sur Follow)

Dans Follow, une **case bleue pleine = remplie**, un **cercle blanc vide = à remplir**. On garde cette convention dans nos annotations SVG par-dessus les screenshots :

- **Disque plein `--action`** = le chir doit remplir
- **Disque plein `--critical`** = champ critique (rare, max 1-2 par planche)
- **Disque plein `--passive`** = patient ou auto ou déjà rempli ailleurs

---

## 4. Arborescence du repo

```
src-infographies/
├── SPEC.md                          # ce fichier
├── CLAUDE.md                        # règles d'or pour Claude (à créer)
├── Makefile                         # commandes : make 2L, make qa, make all
├── pyproject.toml                   # deps : jinja2, playwright, pydantic
│
├── .claude/
│   ├── skills/
│   │   └── infographic-build.md     # règles verrouillées de production
│   └── agents/
│       └── qa-scorer.md             # agent QA (boucle qualité)
│
├── assets/
│   ├── brand/
│   │   ├── logo_src.jpeg            # logo SRC (déposé par Jo)
│   │   └── inspiration/             # 3-5 visuels de référence (déposés par Jo)
│   └── screenshots/
│       └── follow/
│           ├── 2L.png               # screenshot brut Follow (déposé par Jo)
│           ├── 2L_part1.png ...     # multi-screens si besoin
│           └── ...
│
├── data/
│   ├── parcours.json                # chronologie globale des questionnaires
│   └── questionnaires/
│       └── 2L.json                  # source de vérité de la planche 2L
│
├── templates/
│   ├── print_a4.html.j2             # template PDF imprimable
│   └── tl_vertical.html.j2          # template TL WhatsApp
│
├── src/
│   ├── __init__.py
│   ├── render.py                    # JSON + template → HTML
│   ├── export.py                    # HTML → PDF / PNG / MP4 via Playwright
│   ├── schema.py                    # validation Pydantic du JSON
│   └── qa.py                        # exécute l'agent QA et calcule le score
│
└── output/
    ├── pdf/                         # 2L_print_v1.pdf, 2L_print_v2.pdf...
    ├── tl/                          # 2L_tl_v1.html + 2L_tl_v1.mp4
    └── qa-reports/                  # rapports JSON du scorer
```

---

## 5. CLAUDE.md à créer

Crée un fichier `CLAUDE.md` à la racine avec les **règles d'or non négociables**. Voici son contenu :

```markdown
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
```

---

## 6. Skill `infographic-build.md` à créer

Crée `.claude/skills/infographic-build.md` avec ce contenu :

```markdown
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
```

---

## 7. Agent QA `qa-scorer.md` à créer

Crée `.claude/agents/qa-scorer.md` avec ce contenu :

```markdown
---
name: qa-scorer
description: Évalue une infographie SRC sur 20 critères et retourne un score sur 100. Bloque la livraison sous 95.
---

# Agent QA : Scorer infographie SRC

## Méthode

Pour chaque planche (print + TL), exécuter les 20 checks ci-dessous. Chaque check vaut 5 points. Score final sur 100. Seuil de livraison : **95/100**.

Si score < 95, lister précisément les checks échoués et leur localisation, puis corriger et re-builder.

## Les 20 checks (par version)

### Identité visuelle (5 checks)
1. **Palette respectée** : aucune couleur hors palette définie en SPEC.md §3.
2. **Fonts respectées** : Bebas Neue / DM Sans / Space Mono uniquement.
3. **Logo SRC présent** dans le header ET le footer.
4. **Pas d'emoji** dans la version print.
5. **Légende couleur visible** (action / critical / passive).

### Structure (5 checks)
6. **Les 7 zones obligatoires** sont toutes présentes.
7. **Numéro de planche** affiché (#XX/12).
8. **Code questionnaire** affiché clairement (ex : "2L").
9. **Étape parcours** indiquée.
10. **Encart "à quoi ça sert"** présent et non vide.

### Lisibilité PRINT (5 checks)
11. **Texte corps ≥ 10pt** partout.
12. **Titre principal ≥ 56pt** Bebas Neue.
13. **Format A4 portrait** (210×297mm) avec marges 12mm.
14. **Screenshot Follow ≥ 35%** de la surface.
15. **Contraste WCAG AA** sur tous les textes (ratio ≥ 4.5).

### Lisibilité TL vertical (5 checks)
16. **Format 1080×1920** respecté.
17. **5 à 7 sections** scroll-snap.
18. **MP4 entre 25 et 35 secondes**.
19. **Animation à l'entrée** de chaque section.
20. **Tutoiement** vérifié partout (aucun "vous" dans les textes).

## Format de sortie

```json
{
  "id": "2L",
  "version": 1,
  "score": 95,
  "passed": true,
  "checks": [
    {"id": 1, "name": "Palette respectée", "passed": true, "details": ""},
    {"id": 12, "name": "Titre principal ≥ 56pt", "passed": false, "details": "Titre actuel à 48pt dans print_a4.html ligne 142. Augmenter à 56pt minimum."}
  ],
  "summary": "1 check échoué sur 20. Score 95/100. Livré."
}
```

## Si score < 95

Lister précisément les checks échoués avec leur ligne/sélecteur, puis corriger le template ou le JSON, re-build, re-score. Ne pas livrer tant que score < 95.
```

---

## 8. Schema JSON et données 2L

### Schema Pydantic à créer dans `src/schema.py`

```python
from pydantic import BaseModel, Field
from typing import Literal

class QuiRemplit(BaseModel):
    role: Literal["patient", "chirurgien"]
    support: str  # "Tablette", "Ordi"
    pourcentage: int = Field(ge=0, le=100)

class SectionChamps(BaseModel):
    section: str
    qui: Literal["patient", "chirurgien"]
    criticite: Literal["normale", "haute", "critique"] = "normale"
    items: list[str]

class Disrupteur(BaseModel):
    chiffre: str
    unite: str
    phrase_principale: str
    phrase_secondaire: str

class AQuoiCaSert(BaseModel):
    titre: str
    points: list[str]  # 3 à 5 puces

class Questionnaire(BaseModel):
    id: str
    titre: str
    sous_titre: str
    numero_planche: str
    total_planches: int
    rachis: Literal["lombaire", "cervical", "scoliose", "commun"]
    etape_parcours: str
    qui_remplit: list[QuiRemplit]
    duree_estimee_chir: str
    screenshot_follow: list[str]  # liste des chemins (multi-pages possibles)
    champs: list[SectionChamps]
    disrupteur: Disrupteur
    a_quoi_ca_sert: AQuoiCaSert
```

### Le JSON `data/questionnaires/2L.json` à créer

```json
{
  "id": "2L",
  "titre": "Évaluation lombaire initiale",
  "sous_titre": "Première consultation rachis lombaire",
  "numero_planche": "01",
  "total_planches": 12,
  "rachis": "lombaire",
  "etape_parcours": "T0 — Première consultation",
  "qui_remplit": [
    {"role": "patient", "support": "Tablette", "pourcentage": 80},
    {"role": "chirurgien", "support": "Ordi", "pourcentage": 20}
  ],
  "duree_estimee_chir": "≈ 2 minutes",
  "screenshot_follow": [
    "assets/screenshots/follow/2L_part1.png",
    "assets/screenshots/follow/2L_part2.png",
    "assets/screenshots/follow/2L_part3.png",
    "assets/screenshots/follow/2L_part4.png",
    "assets/screenshots/follow/2L_part5.png"
  ],
  "champs": [
    {
      "section": "Le patient remplit sur tablette en salle d'attente",
      "qui": "patient",
      "criticite": "normale",
      "items": [
        "Motif principal de consultation",
        "Trajet de la douleur",
        "Symptômes associés",
        "Côté principal des symptômes",
        "Moment le plus difficile de la journée",
        "Position la plus douloureuse",
        "Ancienneté des symptômes",
        "Traitements déjà entrepris",
        "Antécédents (chirurgie lombaire, accident travail)",
        "Médicaments en cours",
        "EVA dos / EVA jambe (0 à 10)"
      ]
    },
    {
      "section": "Tu complètes sur ordi pendant la consultation",
      "qui": "chirurgien",
      "criticite": "haute",
      "items": [
        "Imagerie disponible (standards / dynamiques / IRM / scanner)",
        "Niveau diagnostic lombaire principal",
        "Diagnostic neurologique principal + détail",
        "Muscle touché + cotation",
        "Diagnostic qui explique la symptomatologie principale",
        "Si HDL : type et côté de hernie, récidive éventuelle",
        "Stade de Pfirmann",
        "Type Modic",
        "Grade Schizas (sténose) + côté",
        "Grade Méyerding (SPL)",
        "Classification MSU"
      ]
    },
    {
      "section": "Le champ qui définit toute la suite",
      "qui": "chirurgien",
      "criticite": "critique",
      "items": [
        "PROJET THÉRAPEUTIQUE LOMBAIRE — médical ou chirurgical"
      ]
    }
  ],
  "disrupteur": {
    "chiffre": "10",
    "unite": "cases",
    "phrase_principale": "Le patient en fait déjà 80%.",
    "phrase_secondaire": "Il te reste 10 cases. Pas une de plus."
  },
  "a_quoi_ca_sert": {
    "titre": "Pourquoi ce 2L bien rempli change tout",
    "points": [
      "C'est le T0 de chaque patient. Sans lui, aucune comparaison post-op n'est possible.",
      "Le PROJET THÉRAPEUTIQUE est la variable cible Y de toutes nos études (médical vs chirurgical).",
      "Les grades radiologiques (Pfirmann, Modic, Schizas, Méyerding) alimentent la stratification de gravité.",
      "Études en cours qui en dépendent : ACCEPT (1 000 patients hernie), CLE 2023/2024.",
      "Sans le 2L de référence, le patient n'entre dans aucune étude SRC."
    ]
  }
}
```

---

## 9. Stack technique

### Dépendances Python (`pyproject.toml`)

```toml
[project]
name = "src-infographies"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
  "jinja2>=3.1",
  "playwright>=1.45",
  "pydantic>=2.7",
  "click>=8.1",
]
```

Après installation : `playwright install chromium`.

### `src/render.py`

Charge le JSON, valide via Pydantic, charge le template Jinja2, écrit le HTML dans `output/tl/{id}_tl_v{n}.html` (ou un fichier intermédiaire pour le print).

### `src/export.py`

Utilise Playwright Python pour :
- **Print A4** : `page.pdf(format='A4', margin={...}, print_background=True)`
- **TL vertical** : 
  - Charge le HTML, fixe le viewport à 1080×1920.
  - Lance un scroll automatique programmé (scroll de 0 à `document.body.scrollHeight` sur 30 secondes, easing).
  - Enregistre la vidéo via `browser.new_context(record_video_dir='output/tl/', record_video_size={'width': 1080, 'height': 1920})`.
  - Convertit le `.webm` produit en `.mp4` via ffmpeg si dispo, sinon garde `.webm`.

### Makefile

```makefile
.PHONY: install 2L all qa clean

install:
	pip install -e .
	playwright install chromium

2L:
	python -m src.render --questionnaire 2L
	python -m src.export --questionnaire 2L --format print
	python -m src.export --questionnaire 2L --format tl

qa:
	python -m src.qa --questionnaire 2L

all: 2L qa

clean:
	rm -rf output/pdf/* output/tl/* output/qa-reports/*
```

---

## 10. Workflow attendu

1. Tu lis ce SPEC.md intégralement.
2. Tu crées toute l'arborescence et les fichiers ci-dessus.
3. Tu vérifies que les assets sont présents :
   - `assets/brand/logo_src.jpeg` (déposé par Jo)
   - `assets/screenshots/follow/2L_part1.png` à `2L_part5.png` (déposés par Jo)
   Si un asset manque, tu stoppes et tu listes ce qui manque.
4. Tu codes les deux templates Jinja2 en respectant les 7 zones obligatoires et les palettes.
5. Tu lances `make install` puis `make 2L`.
6. Tu lances `make qa` et tu corriges en boucle jusqu'à score ≥ 95.
7. Tu présentes les livrables finaux : `output/pdf/2L_print_v1.pdf` et `output/tl/2L_tl_v1.mp4`.

---

## 11. Inspiration visuelle de référence

La newsletter SRC d'avril 2026 (`assets/brand/inspiration/SRC_Newsletter_Avril2026.html` si Jo la dépose) est la **référence absolue** pour le ton et le style du TL vertical : magazine sombre, accents teal et gold, typographie Bebas Neue dominante, accroches percutantes, espaces respirés.

Pour le print A4, l'inspiration est différente : reste sobre, médical, dense mais aéré, lisible imprimé en n&b si jamais. Pense "fiche pratique de cabinet" plus que "magazine".

---

## 12. Questions à poser à Jo si besoin

Si en cours de route tu rencontres une ambiguïté **bloquante** (pas une préférence esthétique mineure), pose-la directement. Sinon, applique le SPEC et présente le résultat. Pour les choix esthétiques mineurs, fais ton meilleur jugement et signale-les en commentaire dans le code.

Bonne construction.
