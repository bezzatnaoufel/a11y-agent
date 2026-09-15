# ADR 0002 : Approche hybride (tests déterministes + LLM)

**Statut** : accepté
**Date** : 2026-09

## Contexte

Le prompt initial fourni demande au LLM d'évaluer, **à partir d'une capture
d'écran seulement**, des éléments invisibles sur une image : aria-labels,
navigation au clavier, structure sémantique. Le modèle ne peut que deviner.
Sur notre page de démo, 16 des 24 violations sont invisibles sur une capture.

## Décision

Répartir les rôles selon ce que chaque outil fait de façon fiable :

| Composant | Rôle | Fiabilité |
|---|---|---|
| axe-core (dans Playwright) | Règles WCAG vérifiables dans le DOM (contraste calculé, noms accessibles, ARIA, etc.) | Déterministe |
| Module clavier (Playwright) | Comportement : atteignabilité, pièges, focus visible, modales | Déterministe |
| LLM de vision | Expliquer, prioriser, relier aux critères ; juger **uniquement** ce qui est visible (texte dans une image, hiérarchie, couleur seule) | Probabiliste |

Le LLM reçoit les résultats déterministes comme **faits établis** et a
l'interdiction de se prononcer sur le DOM ou le clavier à partir de l'image.

## Conséquences

- Moins d'hallucinations, résultats reproductibles pour la majorité des constats.
- Le modèle libre a moins de travail difficile à faire, ce qui réduit l'écart
  avec les modèles propriétaires (hypothèse testée dans l'évaluation).
- Plus de code à maintenir que le prompt seul.
