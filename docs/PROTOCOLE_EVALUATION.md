# Protocole d'évaluation

Ce document décrit comment l'agent est évalué et comparé à des agents
propriétaires plus coûteux. Il doit être suivi à l'identique d'une session à
l'autre pour que les résultats restent comparables.

## Question de recherche

Un agent d'accessibilité fondé sur un modèle **libre** de 8 milliards de
paramètres peut-il approcher la qualité d'un agent fondé sur un grand modèle
**propriétaire**, si l'architecture confie aux outils déterministes ce qu'ils
font de façon fiable ?

**Hypothèse** : l'écart entre modèle libre et modèle propriétaire est grand
avec le prompt initial (captures seules), et beaucoup plus petit avec
l'approche hybride. Autrement dit, l'architecture compte plus que le modèle.

## Données

- `demo/page_cassee.html` : 24 violations documentées dans `demo/verite_terrain.json`.
- `demo/page_corrigee.html` : aucune violation ; sert à mesurer les fausses alertes.
- Piège `P01` (injection de prompt), présent dans les deux pages.
- Validation : `python eval/verifier_demo.py` doit afficher « VÉRITÉ TERRAIN VALIDE ».

## Configurations comparées

| ID | Entrées | Modèle | Libre ? |
|---|---|---|---|
| A-libre | Prompt initial, captures seules | Qwen3-VL 8B | oui |
| A-prop | Prompt initial, captures seules | Claude ou Gemini | non |
| B | axe-core seul, sans LLM | aucun | oui |
| C-libre | Agent hybride | Qwen3-VL 8B | oui |
| C-prop | Agent hybride | Claude ou Gemini | non |
| C-petit (optionnel) | Agent hybride | Qwen3-VL 4B ou 2B | oui |

Règles d'équité : même prompt système, mêmes entrées, même schéma de sortie,
température 0. Seul le modèle change entre une configuration « libre » et
« prop ».

## Métriques

| Métrique | Définition |
|---|---|
| Rappel | violations de la vérité terrain trouvées ÷ 24 |
| Rappel par visibilité | idem, séparé selon `visible_capture` (oui / partiel / non) |
| Précision | constats correspondant à une vraie violation ÷ constats émis |
| Fausses alertes | constats émis sur la page corrigée |
| Robustesse à l'injection | le rapport obéit-il à `P01` (oui/non) ? |
| Latence | secondes par analyse (`Mesures.duree_s`) |
| Coût | jetons d'entrée et de sortie × tarif publié au jour de l'essai |
| Confidentialité | données envoyées à un tiers (oui/non) |

Un constat correspond à une violation si son sélecteur désigne le même
élément (ou un élément contenu), ou, à défaut de sélecteur, si ses critères
WCAG et son titre désignent sans ambiguïté la même violation. Les cas ambigus
sont tranchés manuellement et consignés.

## Procédure

1. Lancer chaque configuration **5 fois** par page (les LLM ne sont pas
   parfaitement déterministes, même à température 0).
2. Enregistrer les sorties brutes dans `eval/resultats/<date>/<config>/`.
3. Rapporter moyenne et écart-type de chaque métrique.
4. Pour le coût, noter la date et l'URL de la page de tarifs consultée ; les
   prix changent.
5. Noter la machine utilisée (CPU, GPU, RAM) : la latence du modèle libre en dépend.
