---
name: qa-scorer
description: Évalue une infographie SRC sur 20 critères et retourne un score sur 100. Bloque la livraison sous 95.
---

# Agent QA : Scorer infographie SRC

## Méthode

Pour chaque planche (print + TL), exécuter les checks actifs ci-dessous. Le score final est normalisé sur 100 (= passed × 100 / nb_checks_actifs). Seuil de livraison : **95/100**.

Les slots #5 et #15 sont marqués **DEPRECATED / REMOVED** : leurs IDs sont conservés pour la stabilité historique mais ils ne sont plus exécutés ni comptabilisés. Total actif : **18 checks**.

Si score < 95, lister précisément les checks échoués et leur localisation, puis corriger et re-builder.

## Les 20 checks (par version)

### Identité visuelle (5 checks)
1. **Palette respectée** : aucune couleur hors palette définie en SPEC.md §3.
2. **Fonts respectées** : Bebas Neue / DM Sans / Space Mono uniquement.
3. **Logo SRC présent** dans le header ET le footer.
4. **Pas d'emoji** dans la version print.
5. ~~**Légende couleur visible**~~ — **DEPRECATED**. Légende retirée volontairement (print imprimé en N&B → légende inutile ; la convention patient/chir passe par la structure des sections).

### Structure (5 checks)
6. **Les 7 zones obligatoires** sont toutes présentes.
7. **Numéro de planche** affiché (#XX/12).
8. **Code questionnaire** affiché clairement (ex : "2L").
9. **Étape parcours** indiquée.
10. **Encart "à quoi ça sert"** présent et non vide.

### Lisibilité PRINT (5 checks)
11. **Tailles de texte affinées** : texte de lecture (BODY, DM Sans / Bebas Neue) ≥ **10pt** ; étiquettes mono/caption (Space Mono — header-meta, frise-step, footer-meta, branch-label, etc.) ≥ **8pt**. La distinction se fait par `font-family` détecté dans la règle CSS (var(--font-mono) ou 'Space Mono' → seuil mono).
12. **Titre principal ≥ 56pt** Bebas Neue.
13. **Format A4 portrait** (210×297mm) avec marges 12mm.
14. **Screenshot Follow ≥ 35%** de la surface.
15. ~~**Contraste WCAG AA**~~ — **REMOVED**. Le contraste a été vérifié manuellement à la conception sur la palette stable (SPEC.md §3). À automatiser plus tard si la palette évolue.

### Lisibilité TL vertical (5 checks)
16. **Format 1080×1920** respecté.
17. **4 à 7 sections** scroll-snap (TL compressé volontairement à 4 sections sur la planche 2L).
18. **MP4 entre 12 et 18 secondes** (scroll TL ~15s).
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
