"""Diagnostic de la détection des fenêtres modales.

À lancer si le test test_modale échoue : montre, candidat par candidat, ce que
le module observe après le clic.

    python eval\\diagnostic_modale.py
"""
import pathlib
import sys

from playwright.sync_api import sync_playwright

RACINE = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE))
from agent.clavier import (  # noqa: E402
    JS_INTERACTIFS, JS_SELECTEUR, JS_SIGNATURE, JS_SUPERPOSITIONS, SELECTEUR_INTERACTIF,
)

URL = (RACINE / "demo" / "page_cassee.html").resolve().as_uri()

with sync_playwright() as p:
    navigateur = p.chromium.launch()
    page = navigateur.new_page(viewport={"width": 1280, "height": 900})
    page.goto(URL)
    candidats = page.evaluate(JS_INTERACTIFS, [SELECTEUR_INTERACTIF, JS_SELECTEUR, JS_SIGNATURE])
    print(f"{len(candidats)} éléments interactifs ; les 25 premiers sont testés.\n")

    for i, candidat in enumerate(candidats[:25], 1):
        page.goto("about:blank")
        page.goto(URL)
        avant = page.evaluate(JS_SUPERPOSITIONS)
        try:
            page.click(candidat["selecteur"], timeout=3000)
            etat = "cliqué"
        except Exception as erreur:
            print(f"{i:2}. {candidat['selecteur']:42} clic impossible : {type(erreur).__name__}")
            continue
        if page.url.split("#")[0] != URL.split("#")[0]:
            etat = "a quitté la page"
        apres = page.evaluate(JS_SUPERPOSITIONS)
        nouvelles = [x for x in apres if x not in avant]
        print(f"{i:2}. {candidat['selecteur']:42} {etat:18} "
              f"surcouches avant={avant} après={apres} nouvelles={nouvelles}")
    navigateur.close()
