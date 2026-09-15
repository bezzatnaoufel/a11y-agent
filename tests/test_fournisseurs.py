"""Tests des fournisseurs avec des clients simulés : aucun modèle ni clé d'API requis."""
import json
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from agent.fournisseurs import ErreurLicence, creer_fournisseur
from agent.schema import schema_json_aplati

ANALYSE = {
    "resume": "Deux problèmes.",
    "constats": [{
        "titre": "Contraste insuffisant", "criteres_wcag": ["1.4.3"], "selecteur": "#texte-aide",
        "gravite": "majeure", "source": "axe",
        "explication": "Texte difficile à lire.", "piste_correction": "Foncer le texte.",
    }],
}
IMAGE = b"\x89PNG faux"


def test_modele_proprietaire_refuse_par_defaut():
    for nom in ("anthropic", "gemini"):
        with pytest.raises(ErreurLicence):
            creer_fournisseur(nom)


def test_modele_libre_accepte_par_defaut():
    assert creer_fournisseur("ollama").libre


def test_schema_sans_references():
    assert "$ref" not in json.dumps(schema_json_aplati())


def test_ollama():
    reponse = SimpleNamespace(message=SimpleNamespace(content=json.dumps(ANALYSE)),
                              prompt_eval_count=1200, eval_count=300)
    with patch("ollama.Client") as Client:
        Client.return_value.chat.return_value = reponse
        analyse, mesures = creer_fournisseur("ollama").analyser("sys", "texte", [IMAGE])
        appel = Client.return_value.chat.call_args.kwargs
    assert appel["messages"][1]["images"] == [IMAGE]
    assert appel["options"]["temperature"] == 0
    assert analyse.constats[0].criteres_wcag == ["1.4.3"]
    assert mesures.jetons_entree == 1200 and not mesures.donnees_envoyees_a_un_tiers


def test_anthropic():
    bloc = SimpleNamespace(type="tool_use", input=ANALYSE)
    reponse = SimpleNamespace(content=[bloc], usage=SimpleNamespace(input_tokens=1500, output_tokens=400))
    with patch("anthropic.Anthropic") as Client:
        Client.return_value.messages.create.return_value = reponse
        f = creer_fournisseur("anthropic", autoriser_proprietaire=True)
        analyse, mesures = f.analyser("sys", "texte", [IMAGE])
        appel = Client.return_value.messages.create.call_args.kwargs
    assert appel["tool_choice"]["name"] == "rapport_accessibilite"
    assert appel["messages"][0]["content"][0]["type"] == "image"
    assert analyse.resume == "Deux problèmes."
    assert mesures.donnees_envoyees_a_un_tiers


def test_gemini():
    reponse = SimpleNamespace(text=json.dumps(ANALYSE),
                              usage_metadata=SimpleNamespace(prompt_token_count=1400, candidates_token_count=350))
    with patch("google.genai.Client") as Client:
        Client.return_value.models.generate_content.return_value = reponse
        f = creer_fournisseur("gemini", modele="modele-test", autoriser_proprietaire=True)
        analyse, mesures = f.analyser("sys", "texte", [IMAGE])
    assert analyse.constats[0].gravite == "majeure"
    assert mesures.jetons_sortie == 350


def test_gemini_sans_modele_configure():
    f = creer_fournisseur("gemini", autoriser_proprietaire=True)
    f.modele = ""
    with pytest.raises(ValueError):
        f.analyser("sys", "texte", [])
