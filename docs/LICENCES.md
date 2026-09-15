# Inventaire des licences

Objectif : prouver que l'agent est « libre de droits ». Toute nouvelle
dépendance doit être ajoutée ici **avant** d'être fusionnée dans `main`.

## Agent (production)

| Composant | Rôle | Licence | Remarque |
|---|---|---|---|
| Qwen3-VL (2B à 32B) | Modèle de vision | Apache 2.0 | Vérifié sur la page Ollama du modèle |
| Ollama | Exécution locale du modèle | MIT | |
| ollama (Python) | Client Ollama | MIT | |
| Playwright (Python) | Pilotage du navigateur | Apache 2.0 | |
| Chromium | Navigateur | BSD et autres licences libres | Téléchargé par Playwright |
| axe-core | Règles WCAG | MPL 2.0 | Téléchargé via npm, non modifié, non redistribué dans le dépôt. Toute modification d'un de ses fichiers devrait rester sous MPL 2.0. |
| Pydantic | Schéma de sortie | MIT | |

## Développement

| Composant | Licence |
|---|---|
| pytest | MIT |

## Évaluation comparative seulement

Ces SDK sont libres, mais les **services** qu'ils appellent sont propriétaires
et payants. Ils ne doivent jamais devenir une dépendance de l'agent.

| Composant | Licence du SDK | Service |
|---|---|---|
| anthropic (Python) | MIT | API Claude, payante |
| google-genai (Python) | Apache 2.0 | API Gemini, payante |

## Licence du projet

Apache 2.0 (voir `LICENSE` et `NOTICE`).
