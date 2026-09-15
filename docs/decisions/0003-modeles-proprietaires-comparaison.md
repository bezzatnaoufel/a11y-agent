# ADR 0003 : Modèles propriétaires limités à l'évaluation comparative

**Statut** : accepté
**Date** : 2026-09

## Contexte

L'énoncé demande de comparer le résultat de l'agent libre avec un agent plus
poussé et coûteux (Claude, Gemini…), sans remettre en cause la règle de
l'ADR 0001.

## Décision

- Une interface unique `Fournisseur` (`agent/fournisseurs.py`) avec trois
  implémentations : Ollama (libre), Anthropic (Claude) et Google (Gemini).
- Les trois reçoivent **exactement** le même prompt système, les mêmes
  entrées et le même schéma de sortie (`agent/schema.py`), à température 0.
- `creer_fournisseur()` lève `ErreurLicence` pour un fournisseur non libre,
  sauf si `autoriser_proprietaire=True`. Seuls les scripts de `eval/` passent
  ce paramètre.
- Les SDK propriétaires sont dans `requirements-comparaison.txt`, jamais dans
  `requirements.txt`.
- Les clés d'API vivent dans `.env` (ignoré par Git) ou dans les secrets du
  dépôt ; aucun workflow déclenché par une PR externe n'y a accès.

## Conséquences

- La comparaison est équitable : seule la variable « modèle » change.
- Impossible d'utiliser un modèle propriétaire en production par accident.
- La comparaison envoie la page de démo (fictive) à des tiers ; ne jamais
  lancer les configurations propriétaires sur du code réel d'une organisation
  sans autorisation.
