"""Tests de la génération du rapport (hors ligne, sans navigateur ni modèle)."""
from agent.analyse import Resultat
from agent.rapport import MARQUEUR, fusionner, rediger
from agent.schema import Analyse

AXE = [{
    "regle": "color-contrast", "impact": "serious", "criteres_wcag": ["1.4.3"],
    "bonne_pratique": False, "aide": "Elements must meet contrast ratio thresholds",
    "url_aide": "https://example.org",
    "noeuds": [{"selecteur": "#texte-aide", "html": "<p>", "resume": "Fix any of the following: ..."}],
}]
CLAVIER = [{
    "regle": "clavier-piege", "impact": "critical", "criteres_wcag": ["2.1.2"],
    "bonne_pratique": False, "aide": "Le focus reste prisonnier de cet élément",
    "url_aide": "https://example.org",
    "noeuds": [{"selecteur": "#carte", "html": "<div>", "resume": "Ni Tab ni Maj+Tab ne permettent d'en sortir."}],
}]

ANALYSE_MODELE = Analyse.model_validate({
    "resume": "Deux problèmes visuels.",
    "constats": [
        {"titre": "Texte dans une image", "criteres_wcag": ["1.4.5"], "selecteur": "#banniere",
         "gravite": "majeure", "source": "capture", "explication": "Ne s'agrandit pas.",
         "piste_correction": "Utiliser du texte réel."},
        {"titre": "Contraste faible", "criteres_wcag": ["1.4.3"], "selecteur": "#texte-aide",
         "gravite": "majeure", "source": "axe", "explication": "Reformule un fait déjà listé.",
         "piste_correction": "—"},
    ],
})


def resultat(**kw) -> Resultat:
    base = {"mode": "hybride", "url": "http://exemple", "axe": AXE, "clavier": CLAVIER,
            "duree_collecte_s": 2.5}
    return Resultat(**{**base, **kw})


def test_messages_axe_traduits_en_francais():
    texte = rediger(resultat())
    assert "Contraste insuffisant entre le texte et son fond" in texte
    assert "Elements must meet contrast" not in texte


def test_regle_inconnue_signalee_comme_non_traduite():
    inconnue = [{**AXE[0], "regle": "regle-inventee"}]
    assert "non traduite" in rediger(resultat(axe=inconnue))


def test_gravite_deduite_de_l_impact():
    texte = rediger(resultat())
    assert "🔴 1 bloquant(s), 🟠 1 majeur(s)" in texte


def test_les_constats_du_modele_ne_doublonnent_pas_les_faits():
    constats = fusionner(resultat(analyse=ANALYSE_MODELE))
    titres = [c["titre"] for c in constats]
    # L'apport visuel est conservé, la reformulation d'un fait axe est écartée.
    assert "Texte dans une image" in titres
    assert "Contraste faible" not in titres


def test_portee_annonce_l_absence_d_analyse_visuelle():
    assert "Analyse visuelle non effectuée" in rediger(resultat())


def test_mode_captures_annonce_une_analyse_partielle():
    assert "Analyse partielle" in rediger(resultat(mode="captures", axe=[], clavier=[]))


def test_marqueur_present_pour_la_mise_a_jour_du_commentaire():
    assert rediger(resultat()).startswith(MARQUEUR)


def test_rapport_sans_violation():
    assert "Aucun problème détecté" in rediger(resultat(axe=[], clavier=[]))
