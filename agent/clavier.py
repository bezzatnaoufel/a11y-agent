"""Tests déterministes du comportement au clavier.

axe-core analyse le DOM ; ce module analyse le COMPORTEMENT. Il appuie
réellement sur Tab dans le navigateur et observe où va le focus.

Quatre familles de violations, invisibles à la fois pour axe-core et pour
une capture d'écran :
  - 2.1.1 éléments interactifs qu'on ne peut pas atteindre au clavier
  - 2.1.2 pièges : une fois dedans, impossible d'en sortir
  - 2.4.7 focus invisible : rien ne change à l'écran quand l'élément est focalisé
  - 2.4.3 ordre de tabulation incohérent avec l'ordre de lecture
  - modales : focus non déplacé, Échap inopérant, rôle manquant

Un piège bloque le parcours vers l'avant. Le module parcourt donc aussi la
page à rebours (Maj+Tab depuis la fin) pour atteindre ce qui suit le piège.
"""
from __future__ import annotations

from playwright.sync_api import Page

# Ce qui doit pouvoir être utilisé au clavier.
SELECTEUR_INTERACTIF = (
    "a[href], button, input:not([type=hidden]), select, textarea, "
    "[tabindex]:not([tabindex='-1']), [onclick], [role=button], [role=link], [role=checkbox]"
)

MAX_TAB = 80

# --- Fonctions JavaScript exécutées dans la page -------------------------

JS_SELECTEUR = """
(el) => {
  if (!el || el === document.body || el === document.documentElement) return null;
  const partie = (n) => {
    if (n.id) return '#' + CSS.escape(n.id);
    let s = n.tagName.toLowerCase();
    const p = n.parentElement;
    if (!p) return s;
    const memes = [...p.children].filter(c => c.tagName === n.tagName);
    if (memes.length > 1) s += ':nth-of-type(' + (memes.indexOf(n) + 1) + ')';
    return s;
  };
  const morceaux = [];
  let n = el;
  while (n && n !== document.body) {
    const m = partie(n);
    morceaux.unshift(m);
    if (m.startsWith('#')) break;
    n = n.parentElement;
  }
  return morceaux.join(' > ');
}"""

# Signature visuelle : ce qui distingue l'élément à l'écran.
JS_SIGNATURE = """
(el) => {
  const s = getComputedStyle(el);
  // Un contour de largeur nulle ou de style « none » ne se voit pas, quel que
  // soit son décalage ou sa couleur : on le normalise pour éviter de prendre
  // une différence purement calculée pour un changement visible.
  const contour = (s.outlineStyle === 'none' || parseFloat(s.outlineWidth) === 0)
    ? 'sans-contour'
    : [s.outlineStyle, s.outlineWidth, s.outlineColor].join(' ');
  return [contour, s.boxShadow, s.borderColor, s.borderWidth, s.backgroundColor,
          s.color, s.textDecorationLine, s.filter, s.transform].join('|');
}"""

JS_ETAT_ACTIF = """
([jsSel, jsSig]) => {
  const el = document.activeElement;
  if (!el || el === document.body || el === document.documentElement) return null;
  const r = el.getBoundingClientRect();
  return {
    selecteur: new Function('return (' + jsSel + ')')()(el),
    html: el.outerHTML.slice(0, 200),
    signature_focus: new Function('return (' + jsSig + ')')()(el),
    ordre_dom: [...document.querySelectorAll('*')].indexOf(el),
    y: r.top + window.scrollY,
  };
}"""

JS_INTERACTIFS = """
([selecteur, jsSel, jsSig]) => [...document.querySelectorAll(selecteur)]
  .filter(el => {
    const r = el.getBoundingClientRect();
    const s = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none';
  })
  .map(el => ({
    selecteur: new Function('return (' + jsSel + ')')()(el),
    html: el.outerHTML.slice(0, 200),
    signature_repos: new Function('return (' + jsSig + ')')()(el),
    ordre_dom: [...document.querySelectorAll('*')].indexOf(el),
  }))"""


def _violation(regle: str, criteres: list[str], impact: str, aide: str, noeuds: list[dict]) -> dict:
    """Même forme que les violations d'agent.collect, pour pouvoir les fusionner."""
    return {
        "regle": regle,
        "impact": impact,
        "criteres_wcag": criteres,
        "bonne_pratique": False,
        "aide": aide,
        "url_aide": "https://www.w3.org/WAI/WCAG22/quickref/",
        "noeuds": noeuds,
    }


def _noeud(cible: dict, resume: str) -> dict:
    return {"selecteur": cible["selecteur"], "html": cible.get("html", ""), "resume": resume}


# --- Parcours ------------------------------------------------------------

def _parcourir(page: Page, arriere: bool = False) -> tuple[list[dict], dict | None]:
    """Appuie sur Tab (ou Maj+Tab) et retourne les éléments atteints, plus le piège éventuel."""
    touche = "Shift+Tab" if arriere else "Tab"
    page.evaluate("() => document.body.focus()")
    page.evaluate("() => { document.activeElement && document.activeElement.blur(); }")

    atteints: list[dict] = []
    precedent = None
    bloque = 0

    for _ in range(MAX_TAB):
        page.keyboard.press(touche)
        etat = page.evaluate(JS_ETAT_ACTIF, [JS_SELECTEUR, JS_SIGNATURE])
        if etat is None:
            precedent = None
            continue

        if precedent and etat["selecteur"] == precedent:
            bloque += 1
            if bloque >= 3:
                return atteints, etat  # le focus ne bouge plus : piège
        else:
            bloque = 0

        precedent = etat["selecteur"]
        if not any(a["selecteur"] == etat["selecteur"] for a in atteints):
            atteints.append(etat)
        elif len(atteints) > 1 and etat["selecteur"] == atteints[0]["selecteur"]:
            break  # cycle complet

    return atteints, None


def _verifier_piege(page: Page, etat: dict) -> bool:
    """Confirme qu'on ne peut sortir ni vers l'avant ni vers l'arrière."""
    page.focus(etat["selecteur"])
    for touche in ("Tab", "Shift+Tab"):
        page.keyboard.press(touche)
        courant = page.evaluate(JS_ETAT_ACTIF, [JS_SELECTEUR, JS_SIGNATURE])
        if courant is None or courant["selecteur"] != etat["selecteur"]:
            return False
    return True


# --- Modales -------------------------------------------------------------

JS_SUPERPOSITIONS = """
() => [...document.querySelectorAll('dialog, div, section, aside')]
  .filter(el => {
    const s = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    return (el.tagName === 'DIALOG' || s.position === 'fixed' || s.position === 'absolute')
      && s.display !== 'none' && s.visibility !== 'hidden'
      && r.width * r.height > 0.15 * window.innerWidth * window.innerHeight;
  })
  .map(el => el.id || el.className || el.tagName)"""


def _tester_modales(page: Page, url: str) -> list[dict]:
    """Repère les éléments qui ouvrent une surcouche et vérifie qu'elle est utilisable au clavier."""
    problemes: list[dict] = []
    candidats = page.evaluate(JS_INTERACTIFS, [SELECTEUR_INTERACTIF, JS_SELECTEUR, JS_SIGNATURE])
    # Le navigateur normalise l'URL (« file://C:\... » devient « file:///C:/... » sous
    # Windows). On compare donc à ce qu'il rapporte, jamais à la chaîne fournie.
    reference = page.url.split("#")[0]

    for candidat in candidats[:25]:
        # Remise à zéro explicite : un simple goto vers la même URL n'est pas
        # garanti de recharger la page si un clic précédent y a ajouté un « # ».
        page.goto("about:blank")
        page.goto(url)
        avant = page.evaluate(JS_SUPERPOSITIONS)
        try:
            page.click(candidat["selecteur"], timeout=3000)
        except Exception:
            continue
        # Un ancrage (« # ») ajouté par le clic ne compte pas comme une navigation.
        if page.url.split("#")[0] != reference:
            continue
        apres = page.evaluate(JS_SUPERPOSITIONS)
        nouvelles = [x for x in apres if x not in avant]
        if not nouvelles:
            continue

        # Une surcouche est apparue : trois vérifications.
        details = page.evaluate(
            """(nom) => {
                const el = [...document.querySelectorAll('dialog, div, section, aside')]
                  .find(e => (e.id || e.className || e.tagName) === nom);
                if (!el) return null;
                const actif = document.activeElement;
                return {
                  focus_dedans: el.contains(actif),
                  role_dialogue: el.tagName === 'DIALOG'
                    || ['dialog', 'alertdialog'].includes(el.getAttribute('role')),
                  html: el.outerHTML.slice(0, 200),
                  selecteur: el.id ? '#' + el.id : el.tagName.toLowerCase(),
                };
            }""",
            nouvelles[0],
        )
        if not details:
            continue

        page.keyboard.press("Escape")
        toujours_ouverte = page.evaluate(JS_SUPERPOSITIONS) == apres

        manques = []
        if not details["focus_dedans"]:
            manques.append("le focus reste derrière la fenêtre")
        if toujours_ouverte:
            manques.append("la touche Échap ne la ferme pas")
        if not details["role_dialogue"]:
            manques.append("aucun rôle de dialogue n'est déclaré")
        if manques:
            problemes.append({
                "selecteur": details["selecteur"],
                "html": details["html"],
                "resume": f"Fenêtre ouverte par {candidat['selecteur']} : " + " ; ".join(manques) + ".",
            })

    page.goto("about:blank")
    page.goto(url)
    return problemes


# --- Point d'entrée ------------------------------------------------------

def executer_clavier(page: Page, url: str | None = None) -> list[dict]:
    """Retourne les violations de comportement au clavier, au format d'agent.collect."""
    url = url or page.url
    violations: list[dict] = []

    interactifs = page.evaluate(JS_INTERACTIFS, [SELECTEUR_INTERACTIF, JS_SELECTEUR, JS_SIGNATURE])
    repos = {i["selecteur"]: i for i in interactifs}

    avant, piege = _parcourir(page)
    atteints = {a["selecteur"]: a for a in avant}

    # Un piège bloque la suite : on repart de la fin avec Maj+Tab.
    if piege and _verifier_piege(page, piege):
        violations.append(_violation(
            "clavier-piege", ["2.1.2"], "critical",
            "Le focus reste prisonnier de cet élément",
            [_noeud(piege, "Ni Tab ni Maj+Tab ne permettent de quitter cet élément : "
                           "un utilisateur au clavier y reste bloqué et ne peut plus "
                           "atteindre le reste de la page.")],
        ))
        page.goto(url)
        arriere, _ = _parcourir(page, arriere=True)
        for a in arriere:
            atteints.setdefault(a["selecteur"], a)

    # 2.1.1 — éléments interactifs jamais atteints
    inaccessibles = [i for sel, i in repos.items() if sel not in atteints]
    if inaccessibles:
        violations.append(_violation(
            "clavier-non-atteignable", ["2.1.1"], "critical",
            "Élément interactif impossible à atteindre au clavier",
            [_noeud(i, "Cet élément réagit au clic mais n'est jamais atteint par la touche Tab. "
                       "Un utilisateur au clavier ou de lecteur d'écran ne peut pas l'activer.")
             for i in inaccessibles],
        ))

    # 2.4.7 — aucun changement visuel au focus
    invisibles = [
        a for sel, a in atteints.items()
        if sel in repos and a["signature_focus"] == repos[sel]["signature_repos"]
    ]
    if invisibles:
        violations.append(_violation(
            "clavier-focus-invisible", ["2.4.7"], "serious",
            "Aucun indicateur visuel quand l'élément reçoit le focus",
            [_noeud(a, "Rien ne change à l'écran quand cet élément est focalisé : "
                       "impossible de savoir où l'on se trouve dans la page.")
             for a in invisibles],
        ))

    # 2.4.3 — ordre de tabulation contraire à l'ordre de lecture
    # On signale les deux éléments de l'inversion : celui qui prend le focus trop
    # tôt (souvent porteur d'un tabindex positif) et celui qu'il a dépassé.
    desordre = []
    for i in range(1, len(avant)):
        if avant[i]["ordre_dom"] < avant[i - 1]["ordre_dom"]:
            for element in (avant[i - 1], avant[i]):
                if element not in desordre:
                    desordre.append(element)
    if desordre:
        violations.append(_violation(
            "clavier-ordre-tabulation", ["2.4.3"], "moderate",
            "L'ordre de tabulation ne suit pas l'ordre de lecture",
            [_noeud(a, "Cet élément reçoit le focus avant des éléments qui le précèdent "
                       "visuellement, ce qui rend la navigation déroutante "
                       "(souvent causé par un tabindex positif).")
             for a in desordre],
        ))

    # Modales
    modales = _tester_modales(page, url)
    if modales:
        violations.append(_violation(
            "clavier-modale", ["2.1.1", "4.1.2"], "critical",
            "Fenêtre modale inutilisable au clavier",
            modales,
        ))

    return violations
