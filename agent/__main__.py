"""Ligne de commande de l'agent.

Exemples :
    python -m agent demo/page_cassee.html
    python -m agent https://exemple.org --mode captures
    python -m agent demo/page_cassee.html --sans-modele     # couche déterministe seule
    python -m agent demo/page_cassee.html --modele qwen3-vl:2b-instruct --capture fenetre
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

from playwright.sync_api import sync_playwright

from agent.analyse import MODES, analyser_page
from agent.fournisseurs import FOURNISSEURS, creer_fournisseur
from agent.rapport import rediger


def vers_url(cible: str) -> str:
    """Accepte une adresse http(s) ou un chemin de fichier local."""
    if cible.startswith(("http://", "https://", "file://")):
        return cible
    chemin = pathlib.Path(cible).resolve()
    if not chemin.exists():
        raise SystemExit(f"Fichier introuvable : {cible}")
    return chemin.as_uri()


def construire_arguments() -> argparse.ArgumentParser:
    a = argparse.ArgumentParser(description="Agent de test d'accessibilité (WCAG 2.2 AA).")
    a.add_argument("cible", help="URL ou chemin d'un fichier HTML")
    a.add_argument("--mode", choices=MODES, default="hybride",
                   help="hybride (défaut) ou captures, le mode de référence de l'énoncé")
    a.add_argument("--fournisseur", choices=list(FOURNISSEURS), default="ollama")
    a.add_argument("--modele", default=None, help="Nom du modèle (défaut : celui du fournisseur)")
    a.add_argument("--titre", default="Analyse d'accessibilité", help="Titre de la Pull Request")
    a.add_argument("--sans-modele", action="store_true", help="Couche déterministe seule")
    a.add_argument("--capture", choices=("pleine", "fenetre"), default="pleine",
                   help="pleine page (défaut) ou fenêtre visible : une image plus petite "
                        "accélère nettement l'inférence sur processeur")
    a.add_argument("--largeur", type=int, default=1280, help="Largeur de la fenêtre en pixels")
    a.add_argument("--hauteur", type=int, default=900, help="Hauteur de la fenêtre en pixels")
    a.add_argument("--json", dest="fichier_json", help="Écrire le résultat complet dans ce fichier")
    a.add_argument("--rapport", dest="fichier_rapport",
                   help="Écrire le rapport Markdown dans ce fichier (celui publié sur la PR)")
    a.add_argument("--autoriser-proprietaire", action="store_true",
                   help="Autorise un modèle propriétaire : évaluation comparative uniquement")
    return a


def main(argv: list[str] | None = None) -> int:
    args = construire_arguments().parse_args(argv)
    url = vers_url(args.cible)

    fournisseur = None
    if not args.sans_modele:
        fournisseur = creer_fournisseur(
            args.fournisseur, args.modele, autoriser_proprietaire=args.autoriser_proprietaire
        )

    with sync_playwright() as p:
        navigateur = p.chromium.launch()
        page = navigateur.new_page(viewport={"width": args.largeur, "height": args.hauteur})
        resultat = analyser_page(
            page, url, mode=args.mode, titre=args.titre, fournisseur=fournisseur,
            avec_modele=not args.sans_modele, pleine_page=args.capture == "pleine",
        )
        navigateur.close()

    print(f"\nMode : {resultat.mode}   Page : {resultat.url}")
    print(f"Collecte déterministe : {resultat.duree_collecte_s} s, "
          f"{resultat.nombre_faits} élément(s) en défaut, "
          f"capture de {resultat.taille_capture_ko} ko")

    for origine, violations in (("axe-core", resultat.axe), ("clavier", resultat.clavier)):
        for v in violations:
            cibles = ", ".join(n["selecteur"] for n in v["noeuds"][:4])
            print(f"  [{origine}] {v['regle']:26} {', '.join(v['criteres_wcag']) or '—':10} {cibles}")

    if resultat.erreur_modele:
        print(f"\nLe modèle n'a pas répondu : {resultat.erreur_modele}")
    elif resultat.analyse:
        m = resultat.mesures
        print(f"\nModèle : {m.fournisseur}/{m.modele} — {m.duree_s:.1f} s, "
              f"{m.jetons_entree} jetons en entrée, {m.jetons_sortie} en sortie, "
              f"données envoyées à un tiers : {'oui' if m.donnees_envoyees_a_un_tiers else 'non'}")
        print(f"\nRésumé : {resultat.analyse.resume}\n")
        for c in resultat.analyse.constats:
            print(f"  ({c.source}/{c.gravite}) {c.titre}  [{', '.join(c.criteres_wcag)}]")
            print(f"      {c.explication}")
            print(f"      → {c.piste_correction}")

    if args.fichier_rapport:
        pathlib.Path(args.fichier_rapport).write_text(rediger(resultat), encoding="utf-8")
        print(f"\nRapport Markdown écrit dans {args.fichier_rapport}")

    if args.fichier_json:
        contenu = {
            "mode": resultat.mode,
            "url": resultat.url,
            "axe": resultat.axe,
            "clavier": resultat.clavier,
            "duree_collecte_s": resultat.duree_collecte_s,
            "analyse": resultat.analyse.model_dump() if resultat.analyse else None,
            "mesures": resultat.mesures.__dict__ if resultat.mesures else None,
            "erreur_modele": resultat.erreur_modele,
        }
        pathlib.Path(args.fichier_json).write_text(
            json.dumps(contenu, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"\nRésultat complet écrit dans {args.fichier_json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
