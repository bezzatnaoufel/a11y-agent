<!-- a11y-agent -->
## Rapport d'accessibilité (WCAG 2.2 AA)

**18 problème(s)** : 🔴 8 bloquant(s), 🟠 8 majeur(s), 🟡 2 mineur(s).

### 🔴 Valeur d'attribut ARIA invalide
*Critère WCAG 4.1.2 · détecté par axe-core*

**Élément(s)** : `#menu-toggle`
**Impact** : La valeur n'est pas reconnue : l'état correspondant n'est pas transmis aux technologies d'assistance.
**Piste** : Vérifier les valeurs admises (par exemple true / false pour aria-expanded).

### 🔴 Bouton sans nom accessible
*Critère WCAG 4.1.2 · détecté par axe-core*

**Élément(s)** : `#voir-mdp`
**Impact** : Un lecteur d'écran annonce seulement « bouton », sans indiquer son action.
**Piste** : Ajouter un texte visible, ou un aria-label, et masquer l'icône décorative.

### 🔴 Image sans texte alternatif
*Critère WCAG 1.1.1 · détecté par axe-core*

**Élément(s)** : `#carte-img`
**Impact** : L'information portée par l'image est perdue ; le lecteur d'écran lit parfois le nom du fichier.
**Piste** : Ajouter un alt décrivant l'information utile, ou alt="" si l'image est décorative.

### 🔴 Champ de formulaire sans étiquette associée
*Critère WCAG 4.1.2 · détecté par axe-core*

**Élément(s)** : `#nom`
**Impact** : Le champ est annoncé sans son intitulé : l'utilisateur ne sait pas quoi y saisir. L'étiquette peut sembler correcte visuellement tout en n'étant pas reliée au champ.
**Piste** : Relier l'étiquette au champ avec for et id.

### 🔴 Liste déroulante sans nom accessible
*Critère WCAG 4.1.2 · détecté par axe-core*

**Élément(s)** : `#arrondissement`
**Impact** : L'utilisateur entend les options sans savoir à quoi elles se rapportent. Un simple texte placé au-dessus ne suffit pas s'il n'est pas relié au champ.
**Piste** : Utiliser <label for> associé à la liste.

### 🔴 Le focus reste prisonnier de cet élément
*Critère WCAG 2.1.2 · détecté par parcours clavier*

**Élément(s)** : `#carte-interactive`
**Impact** : Ni Tab ni Maj+Tab ne permettent de quitter cet élément : un utilisateur au clavier y reste bloqué et ne peut plus atteindre le reste de la page.

### 🔴 Élément interactif impossible à atteindre au clavier
*Critère WCAG 2.1.1 · détecté par parcours clavier*

**Élément(s)** : `#forfait-jour`, `#forfait-mois`, `#forfait-annee`
**Impact** : Cet élément réagit au clic mais n'est jamais atteint par la touche Tab. Un utilisateur au clavier ou de lecteur d'écran ne peut pas l'activer.

### 🔴 Fenêtre modale inutilisable au clavier
*Critère WCAG 2.1.1, 4.1.2 · détecté par parcours clavier*

**Élément(s)** : `#modale`
**Impact** : Fenêtre ouverte par #lien-conditions : le focus reste derrière la fenêtre ; la touche Échap ne la ferme pas ; aucun rôle de dialogue n'est déclaré.

### 🟠 Élément focalisable masqué aux technologies d'assistance
*Critère WCAG 4.1.2 · détecté par axe-core*

**Élément(s)** : `.chat`
**Impact** : L'élément reçoit le focus au clavier, mais le lecteur d'écran n'annonce rien : l'utilisateur ne sait pas où il se trouve.
**Piste** : Retirer aria-hidden, ou rendre l'élément non focalisable.

### 🟠 Contraste insuffisant entre le texte et son fond
*Critère WCAG 1.4.3 · détecté par axe-core*

**Élément(s)** : `#texte-aide`, `#btn-creer`
**Impact** : Le texte devient difficile à lire, en particulier pour les personnes malvoyantes ou sur un écran en plein soleil.
**Piste** : Viser au moins 4,5:1 pour le texte normal et 3:1 pour le grand texte.

### 🟠 Page sans titre
*Critère WCAG 2.4.2 · détecté par axe-core*

**Élément(s)** : `html`
**Impact** : L'onglet et l'annonce du lecteur d'écran n'indiquent pas de quelle page il s'agit, ce qui gêne la navigation entre plusieurs onglets.
**Piste** : Ajouter un élément <title> descriptif et unique.

### 🟠 Langue de la page non déclarée
*Critère WCAG 3.1.1 · détecté par axe-core*

**Élément(s)** : `html`
**Impact** : Un lecteur d'écran applique la mauvaise prononciation : du français lu avec une voix anglaise devient incompréhensible.
**Piste** : Ajouter lang="fr-CA" sur l'élément <html>.

### 🟠 Lien identifiable uniquement par la couleur
*Critère WCAG 1.4.1 · détecté par axe-core*

**Élément(s)** : `#lien-confidentialite`
**Impact** : Une personne daltonienne ne distingue pas le lien du texte environnant.
**Piste** : Souligner le lien, ou ajouter un autre indice visuel que la couleur.

### 🟠 Lien sans nom accessible
*Critère WCAG 2.4.4, 4.1.2 · détecté par axe-core*

**Élément(s)** : `#lien-facebook`
**Impact** : Le lecteur d'écran annonce « lien » sans indiquer la destination ; dans la liste des liens de la page, il est inutilisable.
**Piste** : Ajouter un texte visible, ou un aria-label décrivant la destination.

### 🟠 Cible tactile trop petite
*Critère WCAG 2.5.8 · détecté par axe-core*

**Élément(s)** : `#moins`, `#plus`
**Impact** : Difficile à atteindre pour une personne ayant des difficultés motrices ou utilisant un écran tactile.
**Piste** : Viser au moins 24 × 24 pixels, ou un espacement équivalent entre les cibles.

### 🟠 Aucun indicateur visuel quand l'élément reçoit le focus
*Critère WCAG 2.4.7 · détecté par parcours clavier*

**Élément(s)** : `#nav-principale > a:nth-of-type(1)`, `#nav-principale > a:nth-of-type(2)`, `#nav-principale > a:nth-of-type(3)`
**Impact** : Rien ne change à l'écran quand cet élément est focalisé : impossible de savoir où l'on se trouve dans la page.

### 🟡 Zoom bloqué sur mobile
*Critère WCAG 1.4.4 · détecté par axe-core*

**Élément(s)** : `meta[name="viewport"]`
**Impact** : Une personne malvoyante ne peut pas agrandir le texte pour le lire.
**Piste** : Retirer user-scalable=no et maximum-scale de la balise viewport.

### 🟡 L'ordre de tabulation ne suit pas l'ordre de lecture
*Critère WCAG 2.4.3 · détecté par parcours clavier*

**Élément(s)** : `#lien-aide`, `#nav-principale > a:nth-of-type(1)`
**Impact** : Cet élément reçoit le focus avant des éléments qui le précèdent visuellement, ce qui rend la navigation déroutante (souvent causé par un tabindex positif).

---

<details><summary>Portée de cette analyse</summary>

- Règles WCAG du DOM vérifiées avec axe-core dans un navigateur réel.
- Comportement au clavier réellement testé : atteignabilité, pièges, visibilité du focus, ordre de tabulation, fenêtres modales.
- **Analyse visuelle non effectuée** : les problèmes qui ne se voient qu'à l'œil (texte intégré dans une image, information portée par la seule couleur, hiérarchie visuelle) n'ont pas été évalués.
- Les tests automatisés ne couvrent qu'une partie des critères WCAG ; ils ne remplacent pas un test avec de vrais utilisateurs.
- Collecte effectuée en 3.05 s.

</details>