"""Génération du rapport d'accessibilité en Markdown, destiné au commentaire de PR.

Le rapport fonctionne avec ou sans le modèle : sans lui, il présente les faits
déterministes et annonce explicitement ce qui n'a pas été évalué. Un rapport
qui déclare ses angles morts vaut mieux qu'un rapport qui laisse croire à une
analyse complète.
"""
from __future__ import annotations

from agent.analyse import Resultat
from agent.lexique import traduire

MARQUEUR = "<!-- a11y-agent -->"  # permet au CI de retrouver et mettre à jour son commentaire

EMOJI = {"bloquante": "🔴", "majeure": "🟠", "mineure": "🟡"}
RANG = {"bloquante": 0, "majeure": 1, "mineure": 2}

# Gravité par défaut quand seul l'outil déterministe s'est prononcé.
GRAVITE_IMPACT = {
    "critical": "bloquante", "serious": "majeure",
    "moderate": "mineure", "minor": "mineure", None: "mineure",
}

ORIGINE = {"axe": "axe-core", "clavier": "parcours clavier", "capture": "analyse visuelle"}


def _constats_deterministes(resultat: Resultat) -> list[dict]:
    """Aplatit les violations axe et clavier en une liste de constats."""
    constats = []
    for source, violations in (("axe", resultat.axe), ("clavier", resultat.clavier)):
        for v in violations:
            if source == "axe":
                # Les messages d'axe-core sont en anglais : on passe par le lexique.
                fr = traduire(v["regle"], v["aide"])
                titre, explication, piste = fr["titre"], fr["impact"], fr["piste"]
            else:
                # Le module clavier produit déjà des messages en français.
                titre = v["aide"]
                explication = v["noeuds"][0]["resume"] if v["noeuds"] else ""
                piste = ""
            constats.append({
                "titre": titre,
                "criteres_wcag": v["criteres_wcag"],
                "gravite": GRAVITE_IMPACT.get(v["impact"], "mineure"),
                "source": source,
                "elements": [n["selecteur"] for n in v["noeuds"]],
                "explication": explication,
                "piste_correction": piste,
            })
    return constats


def _constats_du_modele(resultat: Resultat) -> list[dict]:
    if not resultat.analyse:
        return []
    return [{
        "titre": c.titre,
        "criteres_wcag": c.criteres_wcag,
        "gravite": c.gravite,
        "source": c.source,
        "elements": [c.selecteur] if c.selecteur else [],
        "explication": c.explication,
        "piste_correction": c.piste_correction,
    } for c in resultat.analyse.constats]


def fusionner(resultat: Resultat) -> list[dict]:
    """Faits déterministes d'abord ; du modèle, on ne garde que l'apport visuel.

    Les constats du modèle marqués « axe » ou « clavier » reformulent des faits
    déjà listés : on les écarte pour ne pas compter deux fois la même violation.
    """
    constats = _constats_deterministes(resultat)
    for c in _constats_du_modele(resultat):
        if c["source"] == "capture":
            constats.append(c)
    return sorted(constats, key=lambda c: (RANG.get(c["gravite"], 2), c["source"]))


def rediger_entete(resultat: Resultat, constats: list[dict]) -> list[str]:
    comptes = {g: sum(1 for c in constats if c["gravite"] == g) for g in RANG}
    lignes = [
        MARQUEUR,
        "## Rapport d'accessibilité (WCAG 2.2 AA)",
        "",
        f"**{len(constats)} problème(s)** : "
        f"{EMOJI['bloquante']} {comptes['bloquante']} bloquant(s), "
        f"{EMOJI['majeure']} {comptes['majeure']} majeur(s), "
        f"{EMOJI['mineure']} {comptes['mineure']} mineur(s).",
        "",
    ]
    if resultat.analyse and resultat.analyse.resume:
        lignes += [f"> {resultat.analyse.resume}", ""]
    return lignes


def rediger(resultat: Resultat) -> str:
    """Rapport complet en Markdown."""
    constats = fusionner(resultat)
    lignes = rediger_entete(resultat, constats)

    if not constats:
        lignes.append("Aucun problème détecté par les vérifications effectuées.")
    for c in constats:
        criteres = ", ".join(c["criteres_wcag"]) or "—"
        lignes.append(f"### {EMOJI.get(c['gravite'], '🟡')} {c['titre']}")
        lignes.append(f"*Critère WCAG {criteres} · détecté par {ORIGINE.get(c['source'], c['source'])}*")
        lignes.append("")
        if c["elements"]:
            cibles = ", ".join(f"`{e}`" for e in c["elements"][:5])
            reste = len(c["elements"]) - 5
            lignes.append(f"**Élément(s)** : {cibles}" + (f" et {reste} autre(s)" if reste > 0 else ""))
        if c["explication"]:
            lignes.append(f"**Impact** : {c['explication']}")
        if c["piste_correction"]:
            lignes.append(f"**Piste** : {c['piste_correction']}")
        lignes.append("")

    lignes += ["---", "", "<details><summary>Portée de cette analyse</summary>", ""]
    lignes += _portee(resultat)
    lignes += ["</details>"]
    return "\n".join(lignes)


def _portee(resultat: Resultat) -> list[str]:
    """Déclare honnêtement ce qui a été vérifié et ce qui ne l'a pas été."""
    lignes = []
    if resultat.mode == "hybride":
        lignes.append("- Règles WCAG du DOM vérifiées avec axe-core dans un navigateur réel.")
        lignes.append("- Comportement au clavier réellement testé : atteignabilité, pièges, "
                      "visibilité du focus, ordre de tabulation, fenêtres modales.")
    else:
        lignes.append("- **Analyse partielle** : seules des captures d'écran ont été examinées. "
                      "Les noms accessibles, la structure du DOM et le comportement au clavier "
                      "n'ont pas pu être vérifiés.")

    if resultat.analyse:
        m = resultat.mesures
        lignes.append(f"- Analyse visuelle par {m.modele} ({m.duree_s:.0f} s), "
                      f"exécuté localement." if m and not m.donnees_envoyees_a_un_tiers
                      else f"- Analyse visuelle par {m.modele}.")
    else:
        lignes.append("- **Analyse visuelle non effectuée** : les problèmes qui ne se voient "
                      "qu'à l'œil (texte intégré dans une image, information portée par la "
                      "seule couleur, hiérarchie visuelle) n'ont pas été évalués."
                      + (f" Cause : {resultat.erreur_modele}." if resultat.erreur_modele else ""))

    lignes += [
        "- Les tests automatisés ne couvrent qu'une partie des critères WCAG ; "
        "ils ne remplacent pas un test avec de vrais utilisateurs.",
        f"- Collecte effectuée en {resultat.duree_collecte_s} s.",
        "",
    ]
    return lignes
