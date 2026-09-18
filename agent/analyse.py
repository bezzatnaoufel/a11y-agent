"""Analyse complète d'une page : collecte déterministe puis appel au modèle.

Deux modes :
  - « hybride »  : axe-core + clavier + capture, faits transmis au modèle
  - « captures » : capture seule, prompt de l'énoncé (configuration de référence)
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field

from playwright.sync_api import Page

from agent.clavier import executer_clavier
from agent.collect import executer_axe
from agent.fournisseurs import Fournisseur, Mesures, creer_fournisseur
from agent.prompts import (
    SYSTEME_CAPTURES, SYSTEME_HYBRIDE, message_captures, message_hybride,
)
from agent.schema import Analyse

MODES = ("hybride", "captures")


@dataclass
class Resultat:
    mode: str
    url: str
    axe: list[dict] = field(default_factory=list)
    clavier: list[dict] = field(default_factory=list)
    analyse: Analyse | None = None
    mesures: Mesures | None = None
    duree_collecte_s: float = 0.0
    taille_capture_ko: int = 0
    erreur_modele: str | None = None

    @property
    def nombre_faits(self) -> int:
        return sum(len(v["noeuds"]) for v in self.axe + self.clavier)


def collecter(page: Page, url: str, mode: str = "hybride",
              pleine_page: bool = True) -> tuple[list[dict], list[dict], bytes, float]:
    """Retourne (violations axe, violations clavier, capture PNG, durée)."""
    debut = time.perf_counter()
    page.goto(url)
    axe: list[dict] = []
    clavier: list[dict] = []
    if mode == "hybride":
        axe = executer_axe(page)
        clavier = executer_clavier(page, url)
        page.goto(url)
    capture = page.screenshot(full_page=pleine_page)
    return axe, clavier, capture, time.perf_counter() - debut


def analyser_page(
    page: Page,
    url: str,
    *,
    mode: str = "hybride",
    titre: str = "Analyse d'accessibilité",
    fournisseur: Fournisseur | None = None,
    avec_modele: bool = True,
    pleine_page: bool = True,
) -> Resultat:
    """Analyse une page et retourne les faits déterministes plus l'analyse du modèle."""
    if mode not in MODES:
        raise ValueError(f"Mode inconnu : {mode}. Choix : {', '.join(MODES)}")

    axe, clavier, capture, duree = collecter(page, url, mode, pleine_page)
    resultat = Resultat(
        mode=mode, url=url, axe=axe, clavier=clavier,
        duree_collecte_s=round(duree, 2), taille_capture_ko=len(capture) // 1024,
    )
    if not avec_modele:
        return resultat

    fournisseur = fournisseur or creer_fournisseur()
    if mode == "hybride":
        systeme, texte = SYSTEME_HYBRIDE, message_hybride(titre, axe, clavier, url)
    else:
        systeme, texte = SYSTEME_CAPTURES, message_captures(titre)

    try:
        resultat.analyse, resultat.mesures = fournisseur.analyser(systeme, texte, [capture])
    except Exception as erreur:  # le rapport reste utile même si le modèle échoue
        resultat.erreur_modele = f"{type(erreur).__name__}: {erreur}"
    return resultat
