"""Traduction française des règles axe-core.

Les messages d'axe-core sont en anglais et très verbeux. Ce lexique permet de
produire un rapport entièrement en français sans dépendre du modèle : le
rapport reste donc lisible quand l'agent tourne sans IA (intégration continue
sans GPU, par exemple).

Pour ajouter une règle : reprendre son identifiant tel qu'il apparaît dans les
résultats d'axe et remplir titre, impact et piste. La liste des règles est sur
le site de Deque. Une règle absente du lexique retombe sur le message anglais
d'axe, préfixé d'une mention explicite.
"""
from __future__ import annotations

LEXIQUE: dict[str, dict[str, str]] = {
    "aria-allowed-attr": {
        "titre": "Attribut ARIA non autorisé pour ce rôle",
        "impact": "L'attribut n'est pas reconnu pour ce rôle : l'information est ignorée ou mal interprétée par les technologies d'assistance.",
        "piste": "Vérifier la liste des attributs autorisés pour ce rôle dans la spécification WAI-ARIA.",
    },
    "aria-command-name": {
        "titre": "Commande ARIA sans nom accessible",
        "impact": "Un lecteur d'écran annonce la commande sans dire à quoi elle sert.",
        "piste": "Donner un texte visible, ou un aria-label décrivant l'action.",
    },
    "aria-hidden-focus": {
        "titre": "Élément focalisable masqué aux technologies d'assistance",
        "impact": "L'élément reçoit le focus au clavier, mais le lecteur d'écran n'annonce rien : l'utilisateur ne sait pas où il se trouve.",
        "piste": "Retirer aria-hidden, ou rendre l'élément non focalisable.",
    },
    "aria-input-field-name": {
        "titre": "Champ de saisie ARIA sans nom accessible",
        "impact": "Le champ est annoncé sans indiquer ce qu'il faut y saisir.",
        "piste": "Associer une étiquette, ou renseigner aria-label / aria-labelledby.",
    },
    "aria-required-attr": {
        "titre": "Attribut ARIA obligatoire manquant",
        "impact": "L'état du composant n'est pas communiqué : le lecteur d'écran ne peut pas dire s'il est coché, ouvert ou sélectionné.",
        "piste": "Consulter les attributs requis par ce rôle dans le guide WAI-ARIA (APG).",
    },
    "aria-roles": {
        "titre": "Rôle ARIA invalide",
        "impact": "Un rôle inconnu est ignoré : l'élément est annoncé selon sa nature HTML, souvent sans signification utile.",
        "piste": "Utiliser un rôle existant, ou mieux, l'élément HTML natif correspondant.",
    },
    "aria-toggle-field-name": {
        "titre": "Contrôle à bascule sans nom accessible",
        "impact": "L'utilisateur entend qu'une case ou un interrupteur existe, sans savoir ce qu'il contrôle.",
        "piste": "Associer une étiquette au contrôle.",
    },
    "aria-valid-attr-value": {
        "titre": "Valeur d'attribut ARIA invalide",
        "impact": "La valeur n'est pas reconnue : l'état correspondant n'est pas transmis aux technologies d'assistance.",
        "piste": "Vérifier les valeurs admises (par exemple true / false pour aria-expanded).",
    },
    "area-alt": {
        "titre": "Zone cliquable d'image sans texte alternatif",
        "impact": "La destination de la zone est inconnue pour un lecteur d'écran.",
        "piste": "Ajouter un attribut alt décrivant la destination.",
    },
    "autocomplete-valid": {
        "titre": "Valeur d'autocomplétion invalide",
        "impact": "Le remplissage automatique ne fonctionne pas, ce qui pénalise les personnes ayant des difficultés motrices ou cognitives.",
        "piste": "Utiliser une valeur normalisée d'autocomplete (name, email, tel…).",
    },
    "button-name": {
        "titre": "Bouton sans nom accessible",
        "impact": "Un lecteur d'écran annonce seulement « bouton », sans indiquer son action.",
        "piste": "Ajouter un texte visible, ou un aria-label, et masquer l'icône décorative.",
    },
    "bypass": {
        "titre": "Aucun moyen d'éviter les blocs répétés",
        "impact": "Un utilisateur au clavier doit traverser toute la navigation à chaque page pour atteindre le contenu.",
        "piste": "Ajouter un lien d'évitement vers le contenu principal, ou des régions repères.",
    },
    "color-contrast": {
        "titre": "Contraste insuffisant entre le texte et son fond",
        "impact": "Le texte devient difficile à lire, en particulier pour les personnes malvoyantes ou sur un écran en plein soleil.",
        "piste": "Viser au moins 4,5:1 pour le texte normal et 3:1 pour le grand texte.",
    },
    "definition-list": {
        "titre": "Liste de définitions mal structurée",
        "impact": "La relation entre les termes et leurs définitions n'est pas transmise.",
        "piste": "Ne placer que des <dt> et <dd> comme enfants directs de <dl>.",
    },
    "document-title": {
        "titre": "Page sans titre",
        "impact": "L'onglet et l'annonce du lecteur d'écran n'indiquent pas de quelle page il s'agit, ce qui gêne la navigation entre plusieurs onglets.",
        "piste": "Ajouter un élément <title> descriptif et unique.",
    },
    "empty-heading": {
        "titre": "Titre vide",
        "impact": "Un titre sans contenu perturbe la navigation par titres.",
        "piste": "Renseigner le titre ou supprimer l'élément.",
    },
    "form-field-multiple-labels": {
        "titre": "Champ associé à plusieurs étiquettes",
        "impact": "Selon la technologie utilisée, une seule étiquette est annoncée, parfois la mauvaise.",
        "piste": "Ne conserver qu'une seule étiquette par champ.",
    },
    "frame-title": {
        "titre": "Cadre sans titre",
        "impact": "L'utilisateur ne sait pas ce que contient le cadre avant d'y entrer.",
        "piste": "Ajouter un attribut title décrivant le contenu du cadre.",
    },
    "heading-order": {
        "titre": "Niveaux de titres non séquentiels",
        "impact": "La structure du document devient trompeuse pour qui navigue par titres.",
        "piste": "Ne pas sauter de niveau : après un h2 vient un h3, pas un h4.",
    },
    "html-has-lang": {
        "titre": "Langue de la page non déclarée",
        "impact": "Un lecteur d'écran applique la mauvaise prononciation : du français lu avec une voix anglaise devient incompréhensible.",
        "piste": "Ajouter lang=\"fr-CA\" sur l'élément <html>.",
    },
    "html-lang-valid": {
        "titre": "Code de langue invalide",
        "impact": "Le code n'est pas reconnu : la prononciation reste incorrecte.",
        "piste": "Utiliser un code BCP 47 valide, par exemple fr ou fr-CA.",
    },
    "image-alt": {
        "titre": "Image sans texte alternatif",
        "impact": "L'information portée par l'image est perdue ; le lecteur d'écran lit parfois le nom du fichier.",
        "piste": "Ajouter un alt décrivant l'information utile, ou alt=\"\" si l'image est décorative.",
    },
    "input-image-alt": {
        "titre": "Bouton image sans texte alternatif",
        "impact": "L'action du bouton est inconnue pour un lecteur d'écran.",
        "piste": "Ajouter un attribut alt décrivant l'action.",
    },
    "label": {
        "titre": "Champ de formulaire sans étiquette associée",
        "impact": "Le champ est annoncé sans son intitulé : l'utilisateur ne sait pas quoi y saisir. L'étiquette peut sembler correcte visuellement tout en n'étant pas reliée au champ.",
        "piste": "Relier l'étiquette au champ avec for et id.",
    },
    "landmark-one-main": {
        "titre": "Aucune région principale",
        "impact": "Impossible d'aller directement au contenu principal avec un lecteur d'écran.",
        "piste": "Entourer le contenu principal d'un élément <main>.",
    },
    "link-in-text-block": {
        "titre": "Lien identifiable uniquement par la couleur",
        "impact": "Une personne daltonienne ne distingue pas le lien du texte environnant.",
        "piste": "Souligner le lien, ou ajouter un autre indice visuel que la couleur.",
    },
    "link-name": {
        "titre": "Lien sans nom accessible",
        "impact": "Le lecteur d'écran annonce « lien » sans indiquer la destination ; dans la liste des liens de la page, il est inutilisable.",
        "piste": "Ajouter un texte visible, ou un aria-label décrivant la destination.",
    },
    "list": {
        "titre": "Liste mal structurée",
        "impact": "Le nombre d'éléments et la structure de la liste ne sont pas annoncés.",
        "piste": "Ne placer que des <li> comme enfants directs de <ul> ou <ol>.",
    },
    "listitem": {
        "titre": "Élément de liste hors d'une liste",
        "impact": "L'élément n'est pas reconnu comme faisant partie d'une liste.",
        "piste": "Placer les <li> dans un <ul> ou un <ol>.",
    },
    "meta-refresh": {
        "titre": "Rechargement automatique de la page",
        "impact": "La page se recharge sans prévenir, ce qui fait perdre le focus et le fil de la lecture.",
        "piste": "Supprimer le rafraîchissement automatique, ou le laisser à l'initiative de l'utilisateur.",
    },
    "meta-viewport": {
        "titre": "Zoom bloqué sur mobile",
        "impact": "Une personne malvoyante ne peut pas agrandir le texte pour le lire.",
        "piste": "Retirer user-scalable=no et maximum-scale de la balise viewport.",
    },
    "nested-interactive": {
        "titre": "Contrôles interactifs imbriqués",
        "impact": "Le contrôle intérieur est souvent inatteignable, et l'annonce devient confuse.",
        "piste": "Ne pas imbriquer un bouton ou un lien dans un autre contrôle.",
    },
    "object-alt": {
        "titre": "Objet embarqué sans texte alternatif",
        "impact": "Le contenu de l'objet est inaccessible aux technologies d'assistance.",
        "piste": "Fournir un texte alternatif à l'intérieur de l'élément <object>.",
    },
    "page-has-heading-one": {
        "titre": "Aucun titre de niveau 1",
        "impact": "Le sujet de la page n'est pas identifiable dans la structure des titres.",
        "piste": "Ajouter un <h1> décrivant le contenu principal.",
    },
    "region": {
        "titre": "Contenu hors de toute région repère",
        "impact": "La navigation par régions, utilisée par les lecteurs d'écran, ne couvre pas tout le contenu.",
        "piste": "Placer le contenu dans <header>, <nav>, <main> ou <footer>.",
    },
    "role-img-alt": {
        "titre": "Élément role=\"img\" sans texte alternatif",
        "impact": "L'information visuelle est perdue pour un lecteur d'écran.",
        "piste": "Ajouter un aria-label ou un aria-labelledby.",
    },
    "scrollable-region-focusable": {
        "titre": "Zone défilante inatteignable au clavier",
        "impact": "Le contenu qui dépasse ne peut pas être fait défiler sans souris.",
        "piste": "Rendre la zone focalisable avec tabindex=\"0\".",
    },
    "select-name": {
        "titre": "Liste déroulante sans nom accessible",
        "impact": "L'utilisateur entend les options sans savoir à quoi elles se rapportent. Un simple texte placé au-dessus ne suffit pas s'il n'est pas relié au champ.",
        "piste": "Utiliser <label for> associé à la liste.",
    },
    "svg-img-alt": {
        "titre": "Image SVG sans texte alternatif",
        "impact": "L'information portée par le dessin est perdue.",
        "piste": "Ajouter un <title> dans le SVG, ou un aria-label sur l'élément.",
    },
    "tabindex": {
        "titre": "Valeur de tabindex positive",
        "impact": "L'ordre de tabulation ne suit plus l'ordre de lecture, ce qui désoriente la navigation au clavier.",
        "piste": "Utiliser tabindex=\"0\" et s'appuyer sur l'ordre du document.",
    },
    "target-size": {
        "titre": "Cible tactile trop petite",
        "impact": "Difficile à atteindre pour une personne ayant des difficultés motrices ou utilisant un écran tactile.",
        "piste": "Viser au moins 24 × 24 pixels, ou un espacement équivalent entre les cibles.",
    },
    "td-headers-attr": {
        "titre": "Cellule de tableau liée à un en-tête inexistant",
        "impact": "La relation entre la donnée et son en-tête est perdue.",
        "piste": "Vérifier que les identifiants référencés existent dans le tableau.",
    },
    "th-has-data-cells": {
        "titre": "En-tête de tableau sans cellules associées",
        "impact": "La structure du tableau devient incompréhensible à la lecture linéaire.",
        "piste": "Vérifier la structure du tableau et l'usage de scope.",
    },
    "valid-lang": {
        "titre": "Changement de langue avec un code invalide",
        "impact": "Le passage d'une langue à l'autre n'est pas prononcé correctement.",
        "piste": "Utiliser un code BCP 47 valide sur l'attribut lang.",
    },
    "video-caption": {
        "titre": "Vidéo sans sous-titres",
        "impact": "Le contenu sonore est inaccessible aux personnes sourdes ou malentendantes.",
        "piste": "Fournir une piste de sous-titres synchronisés.",
    },
}


def traduire(regle: str, aide_anglaise: str = "") -> dict[str, str]:
    """Retourne titre, impact et piste en français pour une règle axe-core."""
    if regle in LEXIQUE:
        return LEXIQUE[regle]
    return {
        "titre": f"Règle axe-core « {regle} » (non traduite)",
        "impact": aide_anglaise,
        "piste": f"Consulter la documentation de la règle {regle} sur le site de Deque.",
    }
