"""Tests du module clavier sur les pages de démo (navigateur réel, plus lents).

Pour ne lancer que les tests rapides : python -m pytest -q -m "not lent"
"""
import pathlib

import pytest
from playwright.sync_api import sync_playwright

from agent.clavier import executer_clavier

DEMO = pathlib.Path(__file__).resolve().parent.parent / "demo"

pytestmark = pytest.mark.lent


def analyser(nom: str) -> dict[str, list[str]]:
    """Retourne {règle: [sélecteurs]} pour la page demandée."""
    url = (DEMO / nom).resolve().as_uri()
    with sync_playwright() as p:
        navigateur = p.chromium.launch()
        page = navigateur.new_page(viewport={"width": 1280, "height": 900})
        page.goto(url)
        violations = executer_clavier(page, url)
        navigateur.close()
    return {v["regle"]: [n["selecteur"] for n in v["noeuds"]] for v in violations}


@pytest.fixture(scope="module")
def cassee():
    return analyser("page_cassee.html")


@pytest.fixture(scope="module")
def corrigee():
    return analyser("page_corrigee.html")


def test_piege_clavier(cassee):
    assert cassee["clavier-piege"] == ["#carte-interactive"]


def test_elements_non_atteignables(cassee):
    assert set(cassee["clavier-non-atteignable"]) == {"#forfait-jour", "#forfait-mois", "#forfait-annee"}


def test_focus_invisible(cassee):
    # Les trois liens de navigation portent outline: none sans style de remplacement.
    assert len(cassee["clavier-focus-invisible"]) == 3
    assert all("nav-principale" in s for s in cassee["clavier-focus-invisible"])


def test_ordre_de_tabulation(cassee):
    # Le lien du pied de page porte tabindex="1" : il reçoit le focus en premier.
    assert "#lien-aide" in cassee["clavier-ordre-tabulation"]


def test_modale(cassee):
    assert cassee["clavier-modale"] == ["#modale"]


def test_aucune_fausse_alerte_sur_la_page_corrigee(corrigee):
    assert corrigee == {}
