"""Test de bout en bout de l'analyse, avec un modèle simulé (aucun modèle requis)."""
import pathlib

import pytest
from playwright.sync_api import sync_playwright

from agent.analyse import analyser_page
from agent.fournisseurs import Fournisseur, Mesures
from agent.schema import Analyse

DEMO = pathlib.Path(__file__).resolve().parent.parent / "demo"

pytestmark = pytest.mark.lent

REPONSE = {
    "resume": "Analyse simulée.",
    "constats": [{
        "titre": "Texte intégré dans une image",
        "criteres_wcag": ["1.4.5"], "selecteur": "#bandeau-promo",
        "gravite": "majeure", "source": "capture",
        "explication": "L'offre n'est pas du texte réel.",
        "piste_correction": "Utiliser du texte HTML stylé en CSS.",
    }],
}


class FournisseurSimule(Fournisseur):
    """Enregistre ce qu'on lui envoie et renvoie une analyse fixe."""
    nom = "simule"
    libre = True
    modele_par_defaut = "simule"

    def __init__(self):
        super().__init__()
        self.systeme = self.texte = None
        self.images = []

    def analyser(self, systeme, texte, images):
        self.systeme, self.texte, self.images = systeme, texte, images
        return Analyse.model_validate(REPONSE), Mesures(self.nom, self.modele, 0.1, 100, 20, False)


def executer(nom: str, mode: str) -> tuple:
    faux = FournisseurSimule()
    url = (DEMO / nom).resolve().as_uri()
    with sync_playwright() as p:
        navigateur = p.chromium.launch()
        page = navigateur.new_page(viewport={"width": 1280, "height": 900})
        resultat = analyser_page(page, url, mode=mode, fournisseur=faux)
        navigateur.close()
    return resultat, faux


def test_mode_hybride_transmet_les_faits():
    resultat, faux = executer("page_cassee.html", "hybride")
    # Les faits déterministes sont collectés puis transmis au modèle.
    assert resultat.nombre_faits >= 19
    assert "color-contrast" in faux.texte and "clavier-piege" in faux.texte
    assert "faits établis" in faux.systeme.lower()
    assert faux.images and faux.images[0][:4] == b"\x89PNG"
    assert resultat.analyse.constats[0].source == "capture"


def test_mode_captures_ne_transmet_aucun_fait():
    resultat, faux = executer("page_cassee.html", "captures")
    assert resultat.axe == [] and resultat.clavier == []
    assert "axe-core" not in faux.texte
    assert faux.images  # seule la capture est fournie


def test_sans_modele():
    url = (DEMO / "page_cassee.html").resolve().as_uri()
    with sync_playwright() as p:
        navigateur = p.chromium.launch()
        page = navigateur.new_page(viewport={"width": 1280, "height": 900})
        resultat = analyser_page(page, url, avec_modele=False)
        navigateur.close()
    assert resultat.analyse is None and resultat.nombre_faits >= 19


def test_echec_du_modele_nempeche_pas_la_collecte():
    class Casse(FournisseurSimule):
        def analyser(self, systeme, texte, images):
            raise RuntimeError("modèle indisponible")

    url = (DEMO / "page_cassee.html").resolve().as_uri()
    with sync_playwright() as p:
        navigateur = p.chromium.launch()
        page = navigateur.new_page(viewport={"width": 1280, "height": 900})
        resultat = analyser_page(page, url, fournisseur=Casse())
        navigateur.close()
    assert resultat.analyse is None
    assert "modèle indisponible" in resultat.erreur_modele
    assert resultat.nombre_faits >= 19
