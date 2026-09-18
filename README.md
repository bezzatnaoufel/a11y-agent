# a11y-agent : agent libre de droits de test d'accessibilité

[![Tests](../../actions/workflows/tests.yml/badge.svg)](../../actions/workflows/tests.yml)
Licence : Apache 2.0

Agent qui analyse une interface web et produit un rapport d'accessibilité
WCAG 2.2 AA en français, destiné à être publié en commentaire de Pull/Merge
Request. Projet #6 du cours de génie logiciel, conçu pour être repris par les
équipes des sessions suivantes.

## En bref

- **Libre de droits** : modèle Qwen3-VL (Apache 2.0) exécuté localement avec
  Ollama. Aucun coût d'utilisation, aucune donnée envoyée à un tiers.
- **Hybride** : axe-core et un parcours clavier automatisé établissent les
  faits ; le modèle explique, priorise et juge uniquement ce qui est visible.
- **Comparé** à des agents propriétaires (Claude, Gemini) avec le même
  prompt, les mêmes entrées et le même schéma de sortie.

## Démarrage rapide

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
playwright install chromium
npm install
ollama pull qwen3-vl:8b-instruct
python -m pytest -q && python eval/verifier_demo.py
```

## Lancer une analyse

```bash
python -m agent demo/page_cassee.html                 # analyse hybride complète
python -m agent demo/page_cassee.html --sans-modele   # couche déterministe seule
python -m agent demo/page_cassee.html --mode captures # configuration de référence
```

Instructions détaillées : [docs/GUIDE_CONTINUATION.md](docs/GUIDE_CONTINUATION.md).

## Documentation

| Document | Contenu |
|---|---|
| [Guide de continuation](docs/GUIDE_CONTINUATION.md) | Installation, architecture, tâches courantes, avancement, passation |
| [Protocole d'évaluation](docs/PROTOCOLE_EVALUATION.md) | Configurations comparées, métriques, procédure |
| [Décisions d'architecture](docs/decisions/) | Pourquoi des modèles libres, pourquoi l'approche hybride, rôle des modèles propriétaires |
| [Inventaire des licences](docs/LICENCES.md) | Chaque dépendance et sa licence |

## Structure

```
agent/        code de l'agent (collecte axe-core, tests clavier, schéma, modèles)
demo/         page cassée (24 violations), page corrigée, vérité terrain
eval/         vérification de la démo, évaluation comparative
tests/        tests unitaires et tests du module clavier sur la démo
docs/         documentation et décisions d'architecture
```

## Rapport d'équipe

Lien à ajouter à la remise.
