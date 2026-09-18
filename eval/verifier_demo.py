"""Vérifie que la vérité terrain correspond à ce que axe-core détecte réellement.

Usage : python eval/verifier_demo.py

Contrôles :
  1. Page cassée : chaque violation marquée « detectable_axe » est bien trouvée
     par la règle attendue, sur le bon élément.
  2. Page cassée : axe ne signale rien qui soit absent de la vérité terrain.
  3. Page corrigée : axe ne signale plus aucune violation WCAG.
"""
from __future__ import annotations

import functools
import http.server
import json
import sys
import threading
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE))
from agent.clavier import executer_clavier  # noqa: E402
from agent.collect import executer_axe  # noqa: E402

DEMO = RACINE / "demo"
VT = json.loads((DEMO / "verite_terrain.json").read_text(encoding="utf-8"))

JS_CORRESPOND = """([selAxe, selsVT]) => {
  const el = document.querySelector(selAxe);
  if (!el) return false;
  const racines = [document.documentElement, document.head, document.body];
  return selsVT.some(s => [...document.querySelectorAll(s)]
    .some(v => v === el || (!racines.includes(v) && v.contains(el))));
}"""


def demarrer_serveur() -> tuple[http.server.ThreadingHTTPServer, str]:
    gestionnaire = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(DEMO))
    gestionnaire.log_message = lambda *a, **k: None
    serveur = http.server.ThreadingHTTPServer(("127.0.0.1", 0), gestionnaire)
    threading.Thread(target=serveur.serve_forever, daemon=True).start()
    return serveur, f"http://127.0.0.1:{serveur.server_address[1]}"


def selecteurs(v: dict) -> list[str]:
    return [v["selecteur"], *v.get("selecteurs_additionnels", [])]


def correspond(page: Page, sel_axe: str, v: dict) -> bool:
    return page.evaluate(JS_CORRESPOND, [sel_axe, selecteurs(v)])


def verifier_page_cassee(page: Page) -> bool:
    trouvees = executer_axe(page, inclure_bonnes_pratiques=True)
    ok = True

    print("\n=== Page cassée : violations attendues par axe ===")
    for v in VT["violations"]:
        regle = v["detectable_axe"]
        if not regle:
            continue
        noeuds = [n for f in trouvees if f["regle"] == regle for n in f["noeuds"]]
        succes = any(correspond(page, n["selecteur"], v) for n in noeuds)
        ok &= succes
        print(f"  {'✔' if succes else '✘'} {v['id']} {regle:24} {v['titre']}")

    print("\n=== Page cassée : détections axe hors vérité terrain ===")
    imprevues = 0
    for f in trouvees:
        for n in f["noeuds"]:
            if not any(correspond(page, n["selecteur"], v) for v in VT["violations"]):
                imprevues += 1
                print(f"  ? {f['regle']} sur {n['selecteur']} ({f['aide']})")
    if not imprevues:
        print("  (aucune)")
    ok &= imprevues == 0

    print("\n=== Page cassée : violations attendues au clavier ===")
    clavier = executer_clavier(page, page.url)
    for v in VT["violations"]:
        if not v.get("detectable_clavier"):
            continue
        noeuds = [(f["regle"], n) for f in clavier for n in f["noeuds"]]
        trouve = next((regle for regle, n in noeuds if correspond(page, n["selecteur"], v)), None)
        ok &= bool(trouve)
        print(f"  {'✔' if trouve else '✘'} {v['id']} {trouve or 'non détectée':26} {v['titre']}")

    imprevues_clavier = [
        (f["regle"], n["selecteur"]) for f in clavier for n in f["noeuds"]
        if not any(correspond(page, n["selecteur"], v) for v in VT["violations"])
    ]
    for regle, sel in imprevues_clavier:
        print(f"  ? {regle} sur {sel} (hors vérité terrain)")
    ok &= not imprevues_clavier

    print("\n=== Page cassée : ce que axe détecte en plus des règles attendues ===")
    for v in VT["violations"]:
        regles = sorted({f["regle"] for f in trouvees for n in f["noeuds"]
                         if f["regle"] != v["detectable_axe"] and correspond(page, n["selecteur"], v)})
        if regles:
            print(f"  · {v['id']} aussi signalée par : {', '.join(regles)}")
    return ok


def verifier_page_corrigee(page: Page) -> bool:
    trouvees = executer_axe(page, inclure_bonnes_pratiques=False) + executer_clavier(page, page.url)
    print("\n=== Page corrigée : violations restantes (axe et clavier) ===")
    for f in trouvees:
        for n in f["noeuds"]:
            print(f"  ✘ {f['regle']} sur {n['selecteur']} ({f['aide']})")
    if not trouvees:
        print("  ✔ aucune")
    return not trouvees


def main() -> int:
    serveur, base = demarrer_serveur()
    try:
        with sync_playwright() as p:
            navigateur = p.chromium.launch()
            page = navigateur.new_page(viewport={"width": 1280, "height": 900})

            page.goto(f"{base}/{VT['page']}")
            ok_cassee = verifier_page_cassee(page)

            page.goto(f"{base}/{VT['page_corrigee']}")
            ok_corrigee = verifier_page_corrigee(page)
            navigateur.close()
    finally:
        serveur.shutdown()

    total = len(VT["violations"])
    par_axe = sum(1 for v in VT["violations"] if v["detectable_axe"])
    par_clavier = sum(1 for v in VT["violations"] if v.get("detectable_clavier"))
    deterministe = sum(1 for v in VT["violations"] if v["detectable_axe"] or v.get("detectable_clavier"))
    invisibles = sum(1 for v in VT["violations"] if v["visible_capture"] == "non")
    print(f"\nRésumé : {total} violations, {par_axe} détectables par axe, "
          f"{par_clavier} au clavier, {deterministe} au total sans IA, "
          f"{invisibles} invisibles sur capture.")
    print("VÉRITÉ TERRAIN VALIDE" if ok_cassee and ok_corrigee else "INCOHÉRENCES À CORRIGER")
    return 0 if ok_cassee and ok_corrigee else 1


if __name__ == "__main__":
    raise SystemExit(main())
