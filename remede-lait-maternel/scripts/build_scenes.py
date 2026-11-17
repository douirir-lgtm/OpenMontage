"""Construit projet/scenes.json : une scène par diapo de la source, calée sur l'audio.
Textes recopiés tels quels depuis les diapos ; temps issus de faster-whisper (word_timestamps).

  python3 scripts/build_scenes.py              # 1re version  -> projet/scenes.json
  python3 scripts/build_scenes.py --corrigee   # version corrigée (sortie/verification_scientifique.md)
                                               #   -> projet/scenes_corrigee.json (audio : work/audio_corrigee.m4a)
"""
import argparse, json, os, re, unicodedata

_ap = argparse.ArgumentParser()
_ap.add_argument("--corrigee", action="store_true", help="applique les corrections scientifiques (voir sortie/corrections_appliquees.md)")
_ap.add_argument("--sortie", default=None, help="fichier JSON produit (défaut : projet/scenes.json ou projet/scenes_corrigee.json)")
ARGS = _ap.parse_args()
C = ARGS.corrigee


def V(avant, apres):
    """Texte de la 1re version, ou texte corrigé avec --corrigee."""
    return apres if C else avant

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = json.load(open(os.path.join(ROOT, "projet/transcription.json")))
DUREE = 236.774

# ---------------------------------------------------------------- mots
raw = [dict(w) for s in T for w in s["words"]]
words = []
for w in raw:
    t = w["w"]
    st = t.strip()
    if words and (not t.startswith(" ") or st in ("?", "!", ":", ";", "»")):
        sep = " " if st in ("?", "!", ":", ";", "»") else ""
        words[-1]["m"] += sep + st
        words[-1]["f"] = max(words[-1]["f"], w["e"])
    else:
        words.append({"m": st, "d": w["s"], "f": w["e"]})

# Corrections d'orthographe de la transcription (le son n'est pas modifié).
CORR = []  # (description)
def fix(old, new, near, note):
    """Remplace la suite de mots `old` (près du temps `near`) par `new` (même nombre de mots, ou suppression si None)."""
    o = old.split(" ")
    for i in range(len(words) - len(o) + 1):
        if abs(words[i]["d"] - near) < 4 and [w["m"] for w in words[i:i + len(o)]] == o:
            if new is None:
                del words[i:i + len(o)]
            else:
                n = new.split(" ")
                assert len(n) == len(o), (old, new)
                for k, m in enumerate(n):
                    words[i + k]["m"] = m.replace("_", " ")
            CORR.append({"t": round(near, 1), "entendu_par_whisper": old, "affiche": new, "raison": note})
            return
    raise SystemExit(f"correction introuvable: {old!r} @ {near}")

# Temps des mots « Chaque jour, » dans work/audio_corrigee.m4a (faster-whisper, voir montage_audio.py --corrigee)
JOUR = (("Chaque", 81.10, 81.28), ("jour,", 81.28, 81.56))

# Nouvelle phrase de la voix clonée (scripts/montage_audio.py) : « C'est la thèse de Remède. »
# Temps mesurés par faster-whisper sur work/audio_remede.m4a.
_i = [k for k, w in enumerate(words) if 7.0 <= w["d"] < 9.6]
words[_i[0]:_i[-1] + 1] = [{"m": m, "d": d, "f": f} for m, d, f in
                           (("C'est", 7.52, 7.64), ("la", 7.64, 7.72), ("thèse", 7.72, 8.16), ("de", 8.16, 8.28), ("Remède.", 8.28, 8.80))]
CORR.append({"t": 7.5, "entendu_par_whisper": "C'est la thèse de Symbiose Sciences et Suna.", "affiche": "C'est la thèse de Remède.",
             "raison": "phrase remplacée dans l'audio par la voix clonée (nom du profil TikTok)"})
if C:
    # Voix corrigée (scripts/montage_audio.py --corrigee) : « Une seule tétée, » -> « Chaque jour, » (≈ 80,4–81,6 s).
    # Temps mesurés par faster-whisper sur work/audio_corrigee.m4a (voir sortie/corrections_appliquees.md).
    _i = [k for k, w in enumerate(words) if 80.3 <= w["d"] < 81.5]
    assert [words[k]["m"] for k in _i] == ["Une", "seule", "tété,"], [words[k]["m"] for k in _i]
    words[_i[0]:_i[-1] + 1] = [{"m": m, "d": d, "f": f} for m, d, f in JOUR]
    CORR.append({"t": 80.4, "entendu_par_whisper": "Une seule tété,", "affiche": "Chaque jour,",
                 "raison": "mots remplacés dans l'audio par la voix clonée (10⁵–10⁷ bactéries : par jour, pas par tétée)"})
fix("1400", "1_400", 2.5, "espace des milliers")
fix("qu'endroit islamique.", "En_droit islamique,", 56.6, "« qu'endroit » n'a pas de sens ; « En droit islamique » très probable")
fix("Si une", "si une", 57.5, "suite de la phrase précédente")
fix("tétés", "tétées", 68.0, "orthographe (diapo : « 5 tétées »)")
if not C:
    fix("tété,", "tétée,", 81.0, "orthographe")
fix("Des cellules souches. Les", "Des cellules souches ? Les", 87.0, "écho interrogatif d'une 2e voix (probable)")
fix("Des textes. Un classique,", "Des textes classiques, _", 116.5, "« Un » a une probabilité de 0,05 : « Des textes classiques » très probable")
fix("conseillait", "conseillaient", 119.0, "accord avec « Des textes classiques »")
fix("brûlerait", "brouillerait", 163.8, "« brouiller les pistes »")
fix("micro-RN,", "micro-ARN,", 179.0, "diapo : « microARN »")
fix("On sait synthétiser. On sait synthétiser", "On sait synthétiser _ _ _", 206.6, "répétition hallucinée par Whisper (durée nulle, probabilité 0,01)")
words = [w for w in words if w["m"].strip(" _ ") != ""]
for w in words:
    w["d"], w["f"] = round(w["d"], 2), round(max(w["f"], w["d"] + 0.08), 2)
for a, b in zip(words, words[1:]):       # pas de recouvrement
    if b["d"] < a["d"] + 0.06:
        b["d"] = round(a["d"] + 0.06, 2)
    a["f"] = min(a["f"], b["d"])


def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return re.sub(r"[^a-z0-9]", "", "".join(c for c in s if unicodedata.category(c) != "Mn"))


def at(phrase, after=0.0):
    """Instant où la voix commence à dire `phrase` (premier passage après `after`)."""
    p = [norm(x) for x in phrase.split()]
    for i in range(len(words) - len(p) + 1):
        if words[i]["d"] >= after - 0.01 and all(norm(words[i + k]["m"]).startswith(p[k]) for k in range(len(p))):
            return words[i]["d"]
    raise SystemExit(f"repère introuvable: {phrase!r} après {after}")


# ---------------------------------------------------------------- scènes
CUTS = [0.0, 10.0, 24.7, 51.6, 56.8, 109.5, 117.0, 129.2, 132.5, 152.2, 159.5, 191.4, 195.7, 211.4, 228.4, DUREE]
def E(id, texte, a, **kw):
    return dict(id=id, texte=texte, a=round(a, 2), **kw)

S = []
# 1 — titre
S.append(dict(titre="REMEDE", mots_cles=["REMEDE"], pastille=None, ecrans=[dict(visuel="titre", elements=[
    E("embleme", None, 0.15),
    E("titre", "REMEDE", 1.3),
    E("accent_titre", None, at("Remède")),
    E("sous_titre", "Le Lait Maternel – Entre Révélation Textuelle et Preuve Biologique", at("contenaient déjà")),
    E("edition", "ÉDITION 2026 – ANALYSE DE CONCORDANCE", at("Remède") + 0.6),
])]))
# 2 — deux ordres
t2 = at("Gardons bien")
S.append(dict(titre=None, pastille=None, ecrans=[
    dict(visuel="venn", fin=t2 - 0.15, elements=[
        E("cercle_a", "L’ORDRE RÉVÉLÉ", at("La loi révélée")),
        E("a1", "Coran & Sunnah", at("celle des textes")),
        E("a2", "Jurisprudence Classique", at("celle des textes") + 0.35),
        E("a3", "Sagesse Législative", at("celle des textes") + 0.7),
        E("cercle_b", "L’ORDRE NATUREL", at("et la loi naturelle")),
        E("b1", "Données Biomoléculaires", at("celle que découvre")),
        E("b2", "Métagénomique (2024-2025)", at("celle que découvre") + 0.35),
        E("b3", "Cell Host & Microbe / Nature", at("celle que découvre") + 0.7),
        E("icone", None, at("deux langages")),
        E("lentille", None, at("une seule et même")),
    ]),
    dict(visuel="citation_seule", debut=t2 - 0.15, elements=[
        E("citation", "« Il n’y a pas de contradiction entre la parole d’Allah et Sa création. »", t2 + 0.1, mots_cles=["parole d’Allah", "Sa création"]),
        E("filet", None, at("c'est la grille")),
    ]),
]))
# 3 — chronologie
t3 = at("Jusqu'à 24 mois")
S.append(dict(titre="La Chronologie : 24 Mois pour Construire l'Homme", mots_cles=["24 Mois"], pastille="Sourate Al-Baqarah 2:233", ecrans=[
    dict(visuel="verset", fin=t3 - 0.2, elements=[
        E("citation", "« Les mères allaiteront leurs enfants deux années complètes... »", at("Il recommande"), mots_cles=["deux années complètes"]),
        E("reference", "(Sourate Al-Baqarah 2:233)", at("deux années complètes", 26)),
        E("note", "Interprétation : Période critique de mue vers l’autonomie immunitaire.", at("Il correspond"), mots_cles=["Interprétation :"]),
    ]),
    dict(visuel="frise", debut=t3 - 0.2, elements=[
        E("axe_or", None, t3, duree=2.6),
        E("p0", "0", t3),
        E("seg1", "0-6", t3 + 0.5, titre="Phase d'établissement", detail="(Introduction souches maternelles)"),
        E("seg2", "6-24", at("pic de myélinisation"), titre="Diversification & Myélinisation", detail="(Pic de développement cortical)"),
        E("marque24", "24", at("cerveau", 36), titre="Clôture de la fenêtre épigénétique"),
        E("axe_gris", None, at("vers 24-36"), duree=1.6),
        E("seg3", "24-36", at("vers 24-36") + 0.3, titre="Structure adulte acquise"),
        E("p36", "36 Mois", at("se stabilise")),
        E("encadre", "La durée coranique correspond exactement à la ‘window of opportunity’ immunitaire et neurologique.", at("Donc, l'allaitement"), mots_cles=["‘window of opportunity’"]),
    ]),
]))
# 4 — emblème
S.append(dict(titre=None, pastille=None, ecrans=[dict(visuel="embleme", elements=[E("embleme", None, 51.7)])]))
# 5 — parenté par substance
t5 = at("Qu'est-ce qui peut bien")
S.append(dict(titre="La Parenté par Substance : Une Chimère Biologique", mots_cles=["Chimère Biologique"], pastille="Bukhârî & Muslim", ecrans=[
    dict(visuel="hadith", fin=t5 - 0.2, elements=[
        E("citation", "« Ce qui est interdit par la filiation l’est aussi par l’allaitement. »", at("si une femme allaite"), mots_cles=["l’allaitement."]),
        E("reference", "(Bukhârî & Muslim)", at("il devient son enfant")),
        E("tetees", None, at("qu'après un minimum"), n=5, pas=0.55),
        E("condition", "Condition juridique : 5 tétées complètes = transfert substantiel.", at("cinq tétées", 66), mots_cles=["Condition juridique :"]),
    ]),
    dict(visuel="silhouette", debut=t5 - 0.2, elements=[
        E("silhouette", None, t5, duree=2.2),
        E("stat_tetee", V("Chaque tétée : 10⁵ à 10⁷ bactéries viables + 386 microARN.", "Chaque jour : 10⁵ à 10⁷ bactéries + des centaines de microARN."),
          at(V("Une seule tétée", "Chaque jour"), 79), mots_cles=["10⁵ à 10⁷", V("386 microARN.", "des centaines de microARN.")]),
        E("stat_souches", "44,3% des souches de Bifidobacterium longum proviennent de la mère (Cell Host & Microbe, 2024).", at("bactéries vivantes"), mots_cles=["44,3%"], italiques=["Bifidobacterium longum"]),
        E("flux", None, at("Les cellules souches de la mère"), duree=5.0),
        E("label_souches", "Cellules souches & ADN maternels", at("Les cellules souches de la mère")),
        *([E("souris", "(observé chez la souris)", at("Les cellules souches de la mère") + 0.3)] if C else []),
        E("label_chimere", "Microchimérisme", at("il crée une véritable")),
        E("halo", None, at("chimère biologique", 100)),
    ]),
]))
# 6 — emblème
S.append(dict(titre=None, pastille=None, ecrans=[dict(visuel="embleme", elements=[E("embleme", None, 109.6)])]))
# 7 — citations classiques
S.append(dict(titre=None, pastille=None, ecrans=[dict(visuel="citations", elements=[
    E("dessin", None, 117.1),
    E("citation1", "« Il faut éviter la femme stupide car l’intelligence se transmet par le lait. »", at("conseillaient de choisir"), mots_cles=["se transmet par le lait."]),
    E("auteur1", "– Cheikh Al-Fawzân", at("conseillaient de choisir") + 1.4),
    E("citation2", "« Le lait est une influence (athar) qui transmet les maladies et les défauts moraux. »", at("mais aussi avec"), mots_cles=["influence"], italiques=["athar"]),
    E("auteur2", "– Ibn Al-Qayyim", at("mais aussi avec") + 1.4),
    E("question", "Question : Comment un trait de caractère peut-il être transmis par un liquide ?", at("Comme si ces traits"), mots_cles=["Question :"]),
])]))
# 8 — emblème
S.append(dict(titre=None, pastille=None, ecrans=[dict(visuel="embleme", elements=[E("embleme", None, 129.3)])]))
# 9 — influence
S.append(dict(titre="L’Influence : Transmission du Tempérament", mots_cles=["Tempérament"], pastille=V("Nature Scientific Reports, 2025", "Scientific Reports, 2025"), ecrans=[dict(visuel="chaine", elements=[
    E("goutte", "Cortisol Lacté", at("produit du lait riche"), detail="(Hormone de Stress)"),
    E("fleche1", "Passage Barrière Intestinale", at("Ce cortisol passe")),
    E("cerveau", V("Reprogrammation Épigénétique", "Effet sur l’humeur (hypothèse)"), at("il pourrait influencer")),
    E("fleche2", None, at("et donc potentiellement")),
    E("emotions", "Régulation des Émotions", at("et donc potentiellement") + 0.3),
    E("axe", V("L’Axe Cortisol-Tempérament (Nature Scientific Reports, 2025)", "L’Axe Cortisol-Tempérament (Scientific Reports, 2025)"), at("l'expression de ces gènes"), mots_cles=["L’Axe Cortisol-Tempérament"]),
    E("correlation", "Corrélation : Cortisol élevé = Nourrisson craintif et émotions négatives.", at("un tempérament plus anxieux"), mots_cles=["Corrélation :"]),
    E("conclusion", "La ‘moralité’ de la nourrice est un profil hormonal et microbien transmissible.", at("On aurait donc"), mots_cles=["profil hormonal et microbien"]),
])]))
# 10 — emblème
S.append(dict(titre=None, pastille=None, ecrans=[dict(visuel="embleme", elements=[E("embleme", None, 152.3)])]))
# 11 — spécificité
t11 = at("Chaque lait maternel")
S.append(dict(titre="Spécificité Individuelle : L’Empreinte Digitale du Lait", mots_cles=["L’Empreinte Digitale"], pastille="Fatwa n°15990", ecrans=[
    dict(visuel="fatwa", fin=t11 - 0.2, elements=[
        E("helice", None, 159.7, duree=1.6),
        E("regle", "Interdiction des banques de lait anonymes (Fatwa n°15990) pour préserver la traçabilité.", at("l'interdiction des banques"), mots_cles=["(Fatwa n°15990)", "traçabilité."]),
    ]),
    dict(visuel="helices", debut=t11 - 0.2, elements=[
        E("helice_a", "Lait Maternel Unique", t11, detail="(Signature Cohérente)", duree=1.6),
        E("entete", "THE SCIENCE", at("Il a sa propre")),
        E("microbien", "Fingerprint Microbien : Chaque mère possède un microbiome unique.", at("Il a sa propre"), mots_cles=["Fingerprint Microbien :"]),
        E("moleculaire", V("Fingerprint Moléculaire : Signature unique de 386 microARN.",
                             "Fingerprint Moléculaire : profil de microARN propre à chaque lait (non démontré)."), at("son profil unique"), mots_cles=["Fingerprint Moléculaire :"]),
        E("helice_b", "Mélange de Laits", at("Mélanger des laits"), detail=V("(Confusion Biologique)", "(Hypothèse : Confusion Biologique)"), duree=1.6),
        E("risque", V("Risque : Compétition conflictuelle entre souches bactériennes étrangères.",
                      "Hypothèse : Compétition conflictuelle entre souches bactériennes étrangères."),
          at("et à créer une sorte"), mots_cles=[V("Risque :", "Hypothèse :")]),
    ]),
]))
# 12 — pureté
S.append(dict(titre="La Pureté (Anzha) : Un Bouclier Immunitaire", mots_cles=["Bouclier Immunitaire"], pastille=None, ecrans=[dict(visuel="bouclier", elements=[
    E("description", "Description prophétique du lait comme substance pure.", 191.7),
    E("bouclier", None, 191.6, duree=1.2),
    E("chimique", "Défense Chimique", 192.3, detail="(Lactoferrine & Lysozyme)"),
    E("cellulaire", "Défense Cellulaire", 192.7, detail="(Leucocytes vivants)"),
    E("competition", "Compétition", 193.1, detail="(Bifidobacterium)"),
    E("synthese", "La pureté religieuse correspond à la pureté immunologique : un environnement stérile pour les pathogènes, mais vivant pour les bienfaits.", at("C'est une thérapie vivante"), mots_cles=["vivant pour les bienfaits."]),
])]))
# 13 — irremplaçabilité
t13 = at("la technologie actuelle")
S.append(dict(titre="L’Irremplaçabilité : Le Vivant vs L’Inerte", mots_cles=["Le Vivant"], pastille=None, ecrans=[dict(visuel="comparatif", elements=[
    E("col_a", "LAIT MATERNEL (Vivant)", 195.75),
    E("a1", "Microbiome Vertical", at("Un microbiome entier")),
    E("a2", "Cellules Souches Mères", at("des cellules souches qui réparent")),
    E("a3", "MicroARN Régulateurs", at("des micro-ARN qui régulent")),
    E("a4", "Leucocytes Vivants", at("des cellules immunitaires")),
    E("col_b", "INDUSTRIE / FORMULE (Inerte)", at("comme le montre")),
    E("b1", "Impossible (Aucun microbiome vivant)", t13),
    E("b2", "Impossible (Unique à l’ADN maternel)", t13 + 0.45),
    E("b3", "Impossible (Non synthétisable)", t13 + 0.9),
    E("b4", "Impossible", t13 + 1.35),
    E("pasteurisation", "La pasteurisation détruit 90-100% des bactéries bénéfiques et toutes les cellules souches.", at("On sait synthétiser"), mots_cles=["90-100%"]),
    E("therapie", "Le lait maternel est une thérapie cellulaire individualisée.", at("mais pas un écosystème"), mots_cles=["thérapie cellulaire individualisée."]),
])]))
# 14 — synthèse
S.append(dict(titre="Synthèse de Concordance", mots_cles=["Concordance"], pastille=None, ecrans=[dict(visuel="tableau", elements=[
    E("col1", "Énoncé Juridique", at("D'un côté")),
    E("col2", "Preuve Biologique (2024-2025)", at("De l'autre")),
    E("col3", "Concordance", at("De l'autre") + 0.6),
    E("l1", "Durée 2 ans", at("Pour la durée"), preuve="Fenêtre épigénétique 0-24 mois", concordance=V("100% Exacte", "Concordante"), fort=True),
    E("l2", "Parenté (5 tétées)", at("Pour la parenté"), preuve="Chimérisme cellulaire & génétique", concordance=V("Substantielle", "Observée chez l’animal")),
    E("l3", "Influence Caractère", at("Pour le choix"), preuve="Axe Cortisol-Humeur", concordance=V("Confirmée", "Corrélation observée")),
    E("l4", "Interdiction Mélange", at("la transmission d'hormones"), preuve="Signature biologique unique", concordance=V("Confirmée", "Hypothèse (non\u00a0démontrée)")),
    E("l5", "Pureté", at("la transmission d'hormones") + 0.5, preuve="Système de défense triple", concordance="Confirmée"),
    E("pied", "La concordance entre la tradition prophétique et les découvertes scientifiques modernes confirme une sagesse intemporelle et une précision biologique.", at("c'est le résumé")),
])]))
# 15 — conclusion
S.append(dict(titre="Conclusion : Une Greffe Thérapeutique", mots_cles=["Greffe Thérapeutique"], pastille=None, ecrans=[dict(visuel="conclusion", elements=[
    E("cadre", None, 228.5, duree=1.4),
    E("intro", "L’analyse contemporaine révèle que l’allaitement est une greffe complexe :", at("il s'agirait d'une greffe"), mots_cles=["greffe complexe"]),
    E("g1", "Greffe Microbiologique (Bactéries)", at("Une greffe de microbes")),
    E("g2", "Greffe Cellulaire (Cellules Souches)", at("une greffe de cellules")),
    E("g3", "Programmation Épigénétique (MicroARN)", at("et une transplantation")),
    E("final", V("La jurisprudence islamique a légiféré sur des réalités biologiques que la science n’a quantifiées qu’en 2025.",
                 "La jurisprudence islamique a légiféré sur des réalités biologiques que la science quantifie depuis 2007."),
      at("et une transplantation") + 0.7, mots_cles=[V("qu’en 2025.", "depuis 2007.")]),
    *([E("sources", "Sources : voir description", DUREE - 2.0)] if C else []),
])]))

scenes = []
for i, sc in enumerate(S):
    d, f = CUTS[i], CUTS[i + 1]
    ecr = sc["ecrans"]
    for k, e in enumerate(ecr):
        e["debut"] = round(e.get("debut", d if k == 0 else ecr[k - 1]["fin"]), 2)
        e["fin"] = round(e.get("fin", f), 2)
        e = ecr[k] = dict(visuel=e["visuel"], debut=e["debut"], fin=e["fin"], elements=e["elements"])
        for el in e["elements"]:
            el["a"] = round(max(el["a"], e["debut"] + 0.05), 2)   # jamais avant le début de l'écran
            assert el["a"] < e["fin"], (i + 1, el["id"], el["a"], e["debut"], e["fin"])
    scenes.append(dict(id=i + 1, diapo=i + 1, debut=d, fin=round(f, 3), titre=sc["titre"], mots_cles=sc.get("mots_cles", []),
                       pastille=sc["pastille"], ecrans=ecr,
                       mots=[w for w in words if d <= w["d"] < f]))

out = dict(meta=dict(source="entree/source_remede.prophetique_laitmaternel.mp4", duree=DUREE, fps=30, largeur=1080, hauteur=1920,
                     transcription="faster-whisper large-v3, fr, word_timestamps", corrections_sous_titres=CORR),
           scenes=scenes)
if C:
    out["meta"]["version"] = "corrigee"
    out["meta"]["audio"] = "work/audio_corrigee.m4a"
SORTIE = ARGS.sortie or os.path.join(ROOT, "projet/scenes_corrigee.json" if C else "projet/scenes.json")
json.dump(out, open(SORTIE, "w"), ensure_ascii=False, indent=1)
print("->", os.path.relpath(SORTIE, ROOT))
print(len(scenes), "scènes,", sum(len(s["ecrans"]) for s in scenes), "écrans,", len(words), "mots")
for s in scenes:
    for e in s["ecrans"]:
        print(s["id"], e["visuel"], e["debut"], e["fin"], [(x["id"], x["a"]) for x in e["elements"]])
