# ADR 0001 : Utiliser uniquement des modèles libres de droits, famille Qwen3-VL

**Statut** : accepté
**Date** : 2026-09

## Contexte

L'équipe d'AQL doit développer et maintenir plusieurs agents (revue de code,
tests d'API, de performance, de sécurité, d'accessibilité…), et les étudiants
des sessions suivantes doivent pouvoir reprendre le travail. L'énoncé impose
des modèles d'IA générative « libres de droits seulement », pour garantir une
uniformité et une réutilisation des connaissances.

L'agent d'accessibilité a besoin d'un modèle de **vision** (il lit des captures
d'écran) capable de produire une **sortie JSON structurée**.

## Décision

- Modèle par défaut : `qwen3-vl:8b-instruct` via Ollama (licence Apache 2.0,
  environ 6 Go en quantification Q4_K_M).
- Modèles de repli de la même famille, même licence : `qwen3-vl:4b` et
  `qwen3-vl:2b` pour les machines modestes et le CI sans GPU ;
  `qwen3-vl:32b` si une machine de laboratoire le permet.
- Exécution locale uniquement, via Ollama (licence MIT).
- Le modèle est configurable (`A11Y_MODELE_LIBRE`), mais tout remplacement doit
  rester sous licence permissive (Apache 2.0, MIT) et être consigné dans
  `docs/LICENCES.md`.

## Conséquences

- Aucun coût d'utilisation, aucune donnée envoyée à un tiers.
- Une seule famille de modèles à maîtriser pour l'équipe.
- Les modèles sous licences « communautaires » ou avec conditions d'usage
  propres (Llama, Gemma, etc.) sont exclus. Attention : la licence peut varier
  selon la **taille** au sein d'une même famille ; vérifier la page du modèle
  exact avant tout changement.
- Performance inférieure aux grands modèles propriétaires : mesurée
  explicitement dans l'évaluation comparative (ADR 0003).
