"""Collecte déterministe : exécute axe-core dans une page chargée par Playwright.

Le JSON brut d'axe est très verbeux. On n'en garde que l'essentiel pour
éviter de saturer le contexte du LLM plus tard.
"""
from __future__ import annotations

from pathlib import Path

from playwright.sync_api import Page

RACINE = Path(__file__).resolve().parent.parent
AXE_JS = RACINE / "node_modules" / "axe-core" / "axe.min.js"

# Règles WCAG 2.0 / 2.1 / 2.2, niveaux A et AA.
TAGS_WCAG = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"]


def _criteres_depuis_tags(tags: list[str]) -> list[str]:
    """Convertit les tags axe ('wcag143') en critères lisibles ('1.4.3')."""
    criteres = []
    for tag in tags:
        chiffres = tag.removeprefix("wcag")
        if tag.startswith("wcag") and chiffres.isdigit() and len(chiffres) >= 3:
            criteres.append(f"{chiffres[0]}.{chiffres[1]}.{chiffres[2:]}")
    return criteres


def executer_axe(page: Page, inclure_bonnes_pratiques: bool = False) -> list[dict]:
    """Injecte axe-core dans la page et retourne une liste de violations simplifiées.

    Chaque violation contient : regle, impact, criteres_wcag, aide, url_aide,
    bonne_pratique (bool) et noeuds (selecteur, extrait html, resume).
    """
    if not AXE_JS.exists():
        raise FileNotFoundError(f"axe-core introuvable ({AXE_JS}). Lancez « npm install ».")
    page.add_script_tag(path=str(AXE_JS))

    tags = TAGS_WCAG + (["best-practice"] if inclure_bonnes_pratiques else [])
    brut = page.evaluate(
        """async (tags) => await axe.run(document, {
               runOnly: { type: 'tag', values: tags },
               resultTypes: ['violations']
           })""",
        tags,
    )

    violations = []
    for v in brut["violations"]:
        criteres = _criteres_depuis_tags(v["tags"])
        violations.append({
            "regle": v["id"],
            "impact": v["impact"],
            "criteres_wcag": criteres,
            "bonne_pratique": not criteres,
            "aide": v["help"],
            "url_aide": v["helpUrl"],
            "noeuds": [
                {
                    "selecteur": " ".join(map(str, n["target"])),
                    "html": n["html"][:300],
                    "resume": n.get("failureSummary", "")[:400],
                }
                for n in v["nodes"]
            ],
        })
    return violations
