"""Schéma de sortie structurée, identique pour tous les fournisseurs de modèles.

Utiliser le même schéma pour le modèle libre et les modèles propriétaires
est ce qui rend la comparaison équitable et l'évaluation automatisable.
"""
from __future__ import annotations

import copy
from typing import Literal, Optional

from pydantic import BaseModel, Field


class Constat(BaseModel):
    titre: str = Field(description="Intitulé court du problème, en français.")
    criteres_wcag: list[str] = Field(description="Critères WCAG concernés, ex. ['1.4.3'].")
    selecteur: Optional[str] = Field(
        default=None,
        description="Sélecteur CSS de l'élément fautif s'il est connu, sinon null.",
    )
    gravite: Literal["bloquante", "majeure", "mineure"]
    source: Literal["axe", "clavier", "capture"] = Field(
        description="Origine du constat : résultats axe, test clavier, ou observation de la capture."
    )
    explication: str = Field(description="Impact concret pour l'utilisateur, en français.")
    piste_correction: str = Field(description="Concept ou technique à explorer, sans code complet.")


class Analyse(BaseModel):
    resume: str = Field(description="Synthèse en 2 à 4 phrases.")
    constats: list[Constat]


def schema_json_aplati(modele: type[BaseModel] = Analyse) -> dict:
    """Schéma JSON sans $ref/$defs, accepté tel quel par Ollama, Claude et Gemini."""
    schema = modele.model_json_schema()
    definitions = schema.pop("$defs", {})

    def resoudre(noeud):
        if isinstance(noeud, dict):
            if "$ref" in noeud:
                nom = noeud["$ref"].split("/")[-1]
                return resoudre(copy.deepcopy(definitions[nom]))
            return {cle: resoudre(val) for cle, val in noeud.items()}
        if isinstance(noeud, list):
            return [resoudre(x) for x in noeud]
        return noeud

    return resoudre(schema)
