"""Fournisseurs de modèles d'IA générative.

Règle du projet : l'agent utilise EXCLUSIVEMENT des modèles libres de droits
(voir docs/decisions/0001-modeles-libres.md). Les fournisseurs propriétaires
(Claude, Gemini) existent uniquement pour l'évaluation comparative et ne
peuvent être instanciés qu'avec autoriser_proprietaire=True.

Ajouter un fournisseur : créer une sous-classe de Fournisseur, implémenter
analyser(), puis l'enregistrer dans FOURNISSEURS. Voir docs/GUIDE_CONTINUATION.md.
"""
from __future__ import annotations

import base64
import json
import os
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass

from agent.schema import Analyse, schema_json_aplati


@dataclass
class Mesures:
    """Coût d'un appel, pour comparer modèle libre et modèles propriétaires."""
    fournisseur: str
    modele: str
    duree_s: float
    jetons_entree: int
    jetons_sortie: int
    donnees_envoyees_a_un_tiers: bool


class ErreurLicence(RuntimeError):
    """Levée quand on tente d'utiliser un modèle propriétaire hors évaluation."""


class Fournisseur(ABC):
    nom: str = ""
    libre: bool = False
    modele_par_defaut: str = ""

    def __init__(self, modele: str | None = None):
        self.modele = modele or self.modele_par_defaut

    @abstractmethod
    def analyser(self, systeme: str, texte: str, images: list[bytes]) -> tuple[Analyse, Mesures]:
        """Envoie le prompt et les captures, retourne l'analyse validée et les mesures."""


class FournisseurOllama(Fournisseur):
    """Modèle libre exécuté localement. Fournisseur par défaut et seul utilisé en production."""
    nom = "ollama"
    libre = True
    modele_par_defaut = os.getenv("A11Y_MODELE_LIBRE", "qwen3-vl:8b-instruct")

    def analyser(self, systeme, texte, images):
        import ollama

        client = ollama.Client(host=os.getenv("OLLAMA_HOST", "http://localhost:11434"))
        debut = time.perf_counter()
        reponse = client.chat(
            model=self.modele,
            messages=[
                {"role": "system", "content": systeme},
                {"role": "user", "content": texte, "images": images},
            ],
            format=schema_json_aplati(),
            options={"temperature": 0, "seed": 42},
        )
        duree = time.perf_counter() - debut
        analyse = Analyse.model_validate_json(reponse.message.content)
        return analyse, Mesures(
            self.nom, self.modele, duree,
            reponse.prompt_eval_count or 0, reponse.eval_count or 0,
            donnees_envoyees_a_un_tiers=False,
        )


class FournisseurAnthropic(Fournisseur):
    """Claude, via l'API Anthropic. Comparaison uniquement."""
    nom = "anthropic"
    libre = False
    modele_par_defaut = os.getenv("A11Y_MODELE_ANTHROPIC", "claude-sonnet-5")

    def analyser(self, systeme, texte, images):
        import anthropic

        client = anthropic.Anthropic()  # lit ANTHROPIC_API_KEY
        contenu = [
            {"type": "image", "source": {"type": "base64", "media_type": "image/png",
                                          "data": base64.b64encode(img).decode()}}
            for img in images
        ] + [{"type": "text", "text": texte}]
        outil = {
            "name": "rapport_accessibilite",
            "description": "Enregistre le rapport d'accessibilité structuré.",
            "input_schema": schema_json_aplati(),
        }
        debut = time.perf_counter()
        reponse = client.messages.create(
            model=self.modele,
            max_tokens=4096,
            temperature=0,
            system=systeme,
            tools=[outil],
            tool_choice={"type": "tool", "name": outil["name"]},
            messages=[{"role": "user", "content": contenu}],
        )
        duree = time.perf_counter() - debut
        bloc = next(b for b in reponse.content if b.type == "tool_use")
        analyse = Analyse.model_validate(bloc.input)
        return analyse, Mesures(
            self.nom, self.modele, duree,
            reponse.usage.input_tokens, reponse.usage.output_tokens,
            donnees_envoyees_a_un_tiers=True,
        )


class FournisseurGemini(Fournisseur):
    """Gemini, via l'API Google. Comparaison uniquement."""
    nom = "gemini"
    libre = False
    # Pas de valeur par défaut codée en dur : les noms de modèles Gemini changent souvent.
    modele_par_defaut = os.getenv("A11Y_MODELE_GEMINI", "")

    def analyser(self, systeme, texte, images):
        if not self.modele:
            raise ValueError("Définissez A11Y_MODELE_GEMINI (voir .env.example).")
        from google import genai
        from google.genai import types

        client = genai.Client()  # lit GEMINI_API_KEY
        parties = [types.Part.from_bytes(data=img, mime_type="image/png") for img in images]
        debut = time.perf_counter()
        reponse = client.models.generate_content(
            model=self.modele,
            contents=[*parties, texte],
            config=types.GenerateContentConfig(
                system_instruction=systeme,
                temperature=0,
                response_mime_type="application/json",
                response_json_schema=schema_json_aplati(),
            ),
        )
        duree = time.perf_counter() - debut
        analyse = Analyse.model_validate(json.loads(reponse.text))
        usage = reponse.usage_metadata
        return analyse, Mesures(
            self.nom, self.modele, duree,
            usage.prompt_token_count or 0, usage.candidates_token_count or 0,
            donnees_envoyees_a_un_tiers=True,
        )


FOURNISSEURS: dict[str, type[Fournisseur]] = {
    f.nom: f for f in (FournisseurOllama, FournisseurAnthropic, FournisseurGemini)
}


def creer_fournisseur(nom: str = "ollama", modele: str | None = None,
                      autoriser_proprietaire: bool = False) -> Fournisseur:
    """Point d'entrée unique. Refuse les modèles propriétaires sauf demande explicite."""
    if nom not in FOURNISSEURS:
        raise ValueError(f"Fournisseur inconnu : {nom}. Choix : {', '.join(FOURNISSEURS)}")
    classe = FOURNISSEURS[nom]
    if not classe.libre and not autoriser_proprietaire:
        raise ErreurLicence(
            f"« {nom} » n'est pas un modèle libre de droits. Il n'est permis que pour "
            f"l'évaluation comparative (eval/), avec autoriser_proprietaire=True."
        )
    return classe(modele)
