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
