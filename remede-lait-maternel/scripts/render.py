"""Rendu 1080x1920 @30 i/s de projet/scenes.json (Pillow -> ffmpeg).
  python3 scripts/render.py apercus        # une image par écran + contrôles
  python3 scripts/render.py image 12.3 x.png
  python3 scripts/render.py video           # sortie/symbiose-9x16.mp4

Version corrigée : ajouter --corrigee (n'importe où) ->
  projet/scenes_corrigee.json, work/audio_corrigee.m4a, sortie/apercus_corrigee/, sortie/remede-9x16-corrigee.mp4
Chaque chemin peut aussi être imposé par variable d'environnement :
  REMEDE_SCENES, REMEDE_AUDIO, REMEDE_APERCUS, REMEDE_VIDEO (relatifs au dossier du projet ou absolus).
"""
import json, math, os, random, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gfx import *

W, H, FPS = 1080, 1920, 30
SAFE_T, SAFE_B = 150, H - 250
SUB_Y = 1500                       # centre vertical des sous-titres
CONTENT_B = 1385                   # bas de la zone de contenu (au-dessus des sous-titres)
CORRIGEE = "--corrigee" in sys.argv
if CORRIGEE:
    sys.argv.remove("--corrigee")
_DEF = (dict(SCENES="projet/scenes_corrigee.json", AUDIO="work/audio_corrigee.m4a", APERCUS="sortie/apercus_corrigee",
             VIDEO="sortie/remede-9x16-corrigee.mp4") if CORRIGEE else
        dict(SCENES="projet/scenes.json", AUDIO="work/audio_remede.m4a", APERCUS="sortie/apercus", VIDEO="sortie/symbiose-9x16.mp4"))
PATHS = {k: os.path.join(ROOT, os.environ.get("REMEDE_" + k, v)) for k, v in _DEF.items()}
DATA = json.load(open(PATHS["SCENES"]))
SCENES = DATA["scenes"]
DUR = DATA["meta"]["duree"]
NFRAMES = math.ceil(DUR * FPS)


# ================================================================ sprites
class Sp:
    __slots__ = "img x y at dur anim chk name pulse box".split()

    def __init__(s, img, x, y, at, anim="up", dur=0.55, chk=True, name="", pulse=False, pad=0):
        s.img, s.x, s.y, s.at, s.dur, s.anim, s.chk, s.name, s.pulse = img, int(x), int(y), at, dur, anim, chk, name, pulse
        s.box = (s.x + pad, s.y + pad, s.x + img.width - pad, s.y + img.height - pad)


class Screen:
    def __init__(s):
        s.sp = []

    def add(s, img, y, at, cx=None, x=None, anim="up", dur=0.55, chk=True, name="", pulse=False, gl=0, gs=0.5):
        pad = 0
        if gl:
            img, pad = glow(img, gl, strength=gs)
        if x is None:
            x = (W if cx is None else 2 * cx) / 2 - img.width / 2 + pad
        sp = Sp(img, x - pad, y - pad, at, anim, dur, chk, name, pulse, pad)
        s.sp.append(sp)
        return sp.box[3]          # bas du contenu

    def text(s, text, y, at, fkey="inter", size=32, color=CREME, maxw=900, cx=None, x=None, align="c", name="", **kw):
        anim = kw.pop("anim", "up")
        gl = kw.pop("gl", 0)
        dur = kw.pop("dur", 0.55)
        im = text_img(text, fkey, size, color, maxw, align, **kw)
        return s.add(im, y, at, cx=cx, x=x, anim=anim, dur=dur, name=name or text[:24], gl=gl)


def icon(fn, size, uw=100, uh=None, **kw):
    c = Cv(size, int(size * (uh or uw) / uw), uw, uh)
    fn(c, **kw)
    return c.out()


def ring(r, w=3, color=OR):
    c = Cv(2 * r + 8, 2 * r + 8, 2 * r + 8)
    c.circle(r + 4, r + 4, r, w, color)
    return c.out()


def hline(w, color=ORS, th=2, diamond=True):
    im = Image.new("RGBA", (w, 14), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 6, w, 6 + th - 1), fill=color)
    if diamond:
        d.polygon([(w / 2 - 7, 7), (w / 2, 0), (w / 2 + 7, 7), (w / 2, 14)], fill=ORC)
    return im


def vline(h, color=ORS, th=2):
    return Image.new("RGBA", (th, h), color)


def pill(text):
    t = text_img(text, "inter_sb", 28, ORC, maxw=800)
    w, h = t.width + 86, 58
    im = rrect(w, h, 29, fill=BG2[:3] + (225,), outline=ORS, ow=2)
    d = ImageDraw.Draw(im)
    d.polygon([(30, 29), (37, 21), (44, 29), (37, 37)], fill=OR)
    im.alpha_composite(t, (58, 12))
    return im


def card(w, h, strong=False):
    return rrect(w, h, 22, fill=BG2[:3] + (170,), outline=OR if strong else ORS, ow=2)


# ================================================================ en-tête de scène
def header(sc):
    scr = Screen()
    t0 = sc["debut"]
    y = 190
    if sc.get("pastille"):
        scr.add(pill(sc["pastille"]), 178, t0 + 0.15, anim="up", name="pastille")
        y = 266
    if sc.get("titre"):
        im = fit_text(sc["titre"], "titre", [64, 58, 52, 48], 930, 2, color=OR, accents=sc.get("mots_cles"), accent_color=ORC, lh=1.22)
        y = scr.add(im, y, t0 + 0.3, name="titre")
        scr.add(hline(220), y + 14, t0 + 0.55, anim="wl", dur=0.7, chk=False)
        y += 30
    return scr, y + 36


# ================================================================ écrans (un visuel = une fonction)
def v_titre(scr, E, top, sc, e):
    scr.add(beam(820, 1000), 60, E["embleme"]["a"], anim="fade", dur=1.5, chk=False, pulse=True)
    scr.add(halo(980, 980, strength=0.22), 60, E["embleme"]["a"], anim="fade", dur=1.5, chk=False, pulse=True)
    scr.add(emblem(600), 240, E["embleme"]["a"], anim="rad", dur=2.6, gl=9, name="embleme")
    txt = E["titre"]["texte"]
    y0 = 900

    def spaced(color, size=132, track=0.16):
        f = font("titre", size)
        adv = [f.getlength(ch) for ch in txt]
        tr = size * track
        w = int(sum(adv) + tr * (len(txt) - 1)) + 8
        im = Image.new("RGBA", (w, int(size * 1.3)), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        x = 4
        for ch, a in zip(txt, adv):
            d.text((x, 0), ch, font=f, fill=color)
            x += a + tr
        return im.crop(im.getbbox())

    base = spaced(OR)
    scr.add(base, y0, E["titre"]["a"], dur=0.9, name="titre")
    scr.add(spaced(ORC), y0, E["accent_titre"]["a"], anim="fade", dur=0.8, chk=False, gl=14, gs=0.5)
    y = y0 + base.height + 30
    scr.add(hline(260, OR), y, E["accent_titre"]["a"], anim="wl", dur=0.8, chk=False)
    y += 46
    y = scr.text(E["sous_titre"]["texte"], y, E["sous_titre"]["a"], "inter_m", 34, CREME, 860)
    scr.text(E["edition"]["texte"], y + 34, E["edition"]["a"], "inter_sb", 23, OR, 900)


def v_embleme(scr, E, top, sc, e):
    a = E["embleme"]["a"]
    scr.add(beam(900, 1150), 150, a, anim="fade", dur=1.0, chk=False, pulse=True)
    scr.add(halo(1060, 1060, strength=0.26), 270, a, anim="fade", dur=1.0, chk=False, pulse=True)
    scr.add(emblem(760), 420, a, anim="rad", dur=1.8, gl=10, name="embleme")


def v_venn(scr, E, top, sc, e):
    r, ya, yb = 300, 560, 950
    def lens():
        m1 = Image.new("L", (2 * r, yb - ya + 2 * r), 0)
        m2 = m1.copy()
        ImageDraw.Draw(m1).ellipse((0, 0, 2 * r, 2 * r), fill=255)
        ImageDraw.Draw(m2).ellipse((0, yb - ya, 2 * r, yb - ya + 2 * r), fill=255)
        m = ImageChops.multiply(m1, m2).filter(ImageFilter.GaussianBlur(10)).point(lambda v: int(v * 0.26))
        im = Image.new("RGBA", m.size, ORC[:3] + (0,))
        im.putalpha(m)
        return im
    scr.add(lens(), ya - r, E["lentille"]["a"], cx=540, anim="fade", dur=0.9, chk=False, pulse=True)
    for k, yc in (("cercle_a", ya), ("cercle_b", yb)):
        scr.add(ring(r), yc - r - 4, E[k]["a"], anim="rad", dur=1.3, chk=False, gl=7, gs=0.4)
    scr.text(E["cercle_a"]["texte"], ya - r + 62, E["cercle_a"]["a"] + 0.3, "titre", 46, CREME, 500)
    for i, k in enumerate(("a1", "a2", "a3")):
        scr.text("• " + E[k]["texte"], ya - r + 150 + i * 56, E[k]["a"], "inter_m", 32, CREME, 520, accents=["•"])
    c = Cv(250, 170, 150, 102)
    ic_book(c, ox=0, oy=6, s=0.86)
    ic_microscope(c, ox=74, oy=0, s=0.94)
    scr.add(c.out(), (ya + yb) // 2 - 88, E["icone"]["a"], gl=8, gs=0.6, name="icone", anim="fade", dur=0.8)
    scr.text(E["cercle_b"]["texte"], yb - 70 + 12, E["cercle_b"]["a"] + 0.3, "titre", 46, CREME, 500)
    for i, k in enumerate(("b1", "b2", "b3")):
        scr.text("• " + E[k]["texte"], yb + 30 + i * 56, E[k]["a"], "inter_m", 32, CREME, 520, accents=["•"])


def v_citation_seule(scr, E, top, sc, e):
    a = E["citation"]["a"]
    scr.add(beam(900, 1100), 150, a - 0.2, anim="fade", dur=0.8, chk=False, pulse=True)
    scr.add(sprig(300, 120), 470, a - 0.1, cx=540, anim="wl", dur=0.8, chk=False)
    y = scr.text(E["citation"]["texte"], 630, a, "lora_i", 68, CREME, 880, accents=E["citation"]["mots_cles"], dur=0.8, gl=0)
    scr.add(hline(360, OR), y + 60, E["filet"]["a"], anim="wl", dur=0.9, chk=False)


def v_verset(scr, E, top, sc, e):
    a = E["citation"]["a"]
    scr.add(halo(1060, 760, strength=0.20), top - 40, a, anim="fade", dur=1.0, chk=False, pulse=True)
    y = scr.text(E["citation"]["texte"], top + 70, a, "lora_i", 68, CREME, 880, accents=E["citation"]["mots_cles"], dur=0.8)
    y = scr.text(E["reference"]["texte"], y + 34, E["reference"]["a"], "inter_m", 34, OR, 800)
    scr.add(hline(300), y + 44, E["note"]["a"] - 0.2, anim="wl", dur=0.7, chk=False)
    scr.text(E["note"]["texte"], y + 96, E["note"]["a"], "inter_m", 38, CREME, 820, accents=E["note"]["mots_cles"])


def v_frise(scr, E, top, sc, e):
    x0, x6, x24, x36 = 100, 360, 690, 990
    ya = top + 366
    c1, c2, c3 = 230, 525, 822
    # axe
    scr.add(Image.new("RGBA", (x24 - x0, 5), OR), ya - 2, E["axe_or"]["a"], x=x0, anim="wl", dur=E["axe_or"]["duree"], chk=False, gl=6, gs=0.6)
    scr.add(Image.new("RGBA", (x36 - x24, 5), GRIS[:3] + (170,)), ya - 2, E["axe_gris"]["a"], x=x24, anim="wl", dur=E["axe_gris"]["duree"], chk=False)
    def dot(col, r=11):
        c = Cv(2 * r, 2 * r, 2 * r); c.circle(r, r, r - 1, 0, col, fill=col); return c.out()
    scr.add(dot(OR, 8), ya - 8, E["p0"]["a"], cx=x0, anim="fade", chk=False)
    scr.add(Image.new("RGBA", (3, 34), OR), ya - 17, E["seg2"]["a"] - 0.3, cx=x6, anim="fade", chk=False)
    lab = dict(fkey="inter_sb", size=32)
    scr.text(E["p0"]["texte"], ya + 26, E["p0"]["a"], cx=x0, color=OR, **lab)
    for k, cx, fn, col, tc in (("seg1", c1, None, OR, CREME), ("seg2", c2, ic_brain, OR, CREME), ("seg3", c3, ic_tree, GRIS, GRIS)):
        el = E[k]
        if fn is None:
            c = Cv(190, 190, 100); mother_child(c, color=OR, w=2.0, ox=-4, oy=-10, s=0.98); im = c.out()
        else:
            im = icon(fn, 190, color=col)
        scr.add(im, top + 130, el["a"], cx=cx, gl=7 if col == OR else 0, gs=0.5, name="ico_" + k, anim="fade", dur=0.8)
        scr.add(dot(col), ya - 11, el["a"], cx=cx, anim="fade", chk=False)
        scr.text(el["texte"], ya + 26, el["a"], cx=cx, color=col, **lab)
        y = scr.text(el["titre"], ya + 88, el["a"] + 0.15, "inter_sb", 30, tc, 285, cx=cx)
        if el.get("detail"):
            scr.text(el["detail"], y + 6, el["a"] + 0.3, "inter", 25, OR, 285, cx=cx)
    m = E["marque24"]
    scr.add(Image.new("RGBA", (4, ya + 30 - (top + 104)), ORC), top + 104, m["a"], cx=x24, anim="wt", dur=0.8, chk=False, gl=8, gs=0.7)
    scr.text(m["titre"], top, m["a"] + 0.3, "inter_sb", 30, ORC, 360, cx=x24, name="cloture")
    scr.text(m["texte"], ya + 38, m["a"], cx=x24, color=ORC, **lab)
    scr.text(E["p36"]["texte"], ya + 26, E["p36"]["a"], x=x36 - 86, color=GRIS, **lab)
    en = E["encadre"]
    t = text_img(en["texte"], "inter_m", 36, CREME, 830, accents=en["mots_cles"])
    yc = ya + 318
    scr.add(halo(1000, t.height + 260, strength=0.2), yc - 100, en["a"], anim="fade", chk=False, pulse=True)
    scr.add(card(920, t.height + 64, True), yc, en["a"], chk=False)
    scr.add(t, yc + 30, en["a"], name="encadre")


def v_hadith(scr, E, top, sc, e):
    a = E["citation"]["a"]
    scr.add(halo(1060, 700, strength=0.2), top - 40, a, anim="fade", dur=1.0, chk=False, pulse=True)
    y = scr.text(E["citation"]["texte"], top + 50, a, "lora", 68, CREME, 880, accents=E["citation"]["mots_cles"], dur=0.8)
    y = scr.text(E["reference"]["texte"], y + 30, E["reference"]["a"], "inter_m", 34, OR, 800)
    te = E["tetees"]
    y += 70
    d = icon(ic_drop, 92)
    for i in range(te["n"]):
        scr.add(d, y, te["a"] + i * te["pas"], cx=540 + (i - 2) * 130, gl=7, gs=0.6, name=f"goutte{i+1}", anim="up", dur=0.4)
    scr.text(E["condition"]["texte"], y + 140, E["condition"]["a"], "inter_m", 38, CREME, 860, accents=E["condition"]["mots_cles"])


def v_silhouette(scr, E, top, sc, e):
    sw, sh = 336, 605
    y0 = top + 4
    scr.add(halo(760, 760, strength=0.30), y0 - 110, E["halo"]["a"], anim="fade", dur=1.2, chk=False, pulse=True)
    scr.add(beam(560, sh + 120), y0 - 110, E["silhouette"]["a"], anim="fade", dur=1.2, chk=False)
    scr.add(ic_toddler(sw, sh), y0, E["silhouette"]["a"], anim="wt", dur=E["silhouette"]["duree"], name="silhouette", gl=5, gs=0.35)
    scr.add(ic_toddler_flow(sw, sh), y0, E["flux"]["a"], anim="wb", dur=E["flux"]["duree"], chk=False, gl=9, gs=0.9)
    scr.text(E["label_chimere"]["texte"], y0 + 170, E["label_chimere"]["a"], "inter_sb", 33, ORC, 290, cx=198, gl=8)
    yl = scr.text(E["label_souches"]["texte"], y0 + 330, E["label_souches"]["a"], "inter_sb", 32, ORC, 290, cx=884)
    if "souris" in E:   # version corrigée : précision « observé chez la souris »
        scr.text(E["souris"]["texte"], yl + 10, E["souris"]["a"], "inter_i", 25, CREME, 300, cx=884)
    yc = y0 + sh + 26
    cw = 455
    ims = []
    for k in ("stat_tetee", "stat_souches"):
        el = E[k]
        ims.append(text_img(el["texte"], "inter_m", 31, CREME, cw - 52, align="l", accents=el.get("mots_cles"), italics=el.get("italiques")))
    hh = max(i.height for i in ims) + 52
    for i, k in enumerate(("stat_tetee", "stat_souches")):
        x = 70 + i * (cw + 30)
        scr.add(card(cw, hh), yc, E[k]["a"], x=x, chk=False)
        scr.add(ims[i], yc + 26, E[k]["a"], x=x + 28, name=k)


def v_citations(scr, E, top, sc, e):
    a = E["dessin"]["a"]
    scr.add(halo(760, 560, strength=0.22), 110, a, anim="fade", chk=False, pulse=True)
    scr.add(emblem(300, False), 180, a, anim="wt", dur=1.6, gl=8, name="dessin")
    y = 524
    for q, au in (("citation1", "auteur1"), ("citation2", "auteur2")):
        y = scr.text(E[q]["texte"], y, E[q]["a"], "lora_i", 50, CREME, 900, accents=E[q].get("mots_cles"), italics=E[q].get("italiques"))
        y = scr.text(E[au]["texte"], y + 12, E[au]["a"], "inter_m", 32, OR, 900) + 56
    scr.add(hline(300), y - 28, E["question"]["a"] - 0.2, anim="wl", dur=0.7, chk=False)
    scr.text(E["question"]["texte"], y + 10, E["question"]["a"], "inter_m", 40, CREME, 860, accents=E["question"]["mots_cles"])


def v_chaine(scr, E, top, sc, e):
    xs = (180, 540, 900)
    yi = top + 110
    g = E["goutte"]
    scr.add(icon(ic_drop, 170), yi - 10, g["a"], cx=xs[0], gl=8, gs=0.6, name="goutte", anim="fade", dur=0.8)
    y = scr.text(g["texte"], yi + 176, g["a"] + 0.2, "inter_sb", 31, ORC, 290, cx=xs[0])
    scr.text(g["detail"], y + 4, g["a"] + 0.35, "inter", 25, CREME, 290, cx=xs[0])
    f1 = E["fleche1"]
    scr.add(ic_arrow(170, 50), yi + 50, f1["a"], cx=360, anim="wl", dur=0.8, chk=False)
    scr.text(f1["texte"], top + 6, f1["a"] + 0.2, "inter_sb", 26, OR, 250, cx=360, name="passage")
    b = E["cerveau"]
    scr.add(halo(420, 420, strength=0.3), yi - 135, b["a"], cx=xs[1], anim="fade", chk=False, pulse=True)
    scr.add(icon(ic_brain, 176), yi - 14, b["a"], cx=xs[1], gl=8, gs=0.6, name="cerveau", anim="fade", dur=0.8)
    scr.text(b["texte"], yi + 176, b["a"] + 0.2, "inter_sb", 31, ORC, 300, cx=xs[1])
    scr.add(ic_arrow(170, 50), yi + 50, E["fleche2"]["a"], cx=720, anim="wl", dur=0.8, chk=False)
    em = E["emotions"]
    scr.add(rrect(220, 150, 26, fill=BG2[:3] + (150,), outline=OR, ow=2), yi, em["a"], cx=xs[2], chk=False, gl=6, gs=0.4)
    scr.text(em["texte"], yi + 32, em["a"], "inter_sb", 29, ORC, 200, cx=xs[2], name="emotions")
    y = scr.text(E["axe"]["texte"], yi + 296, E["axe"]["a"], "inter_m", 36, CREME, 860, accents=E["axe"]["mots_cles"])
    co = E["correlation"]
    t = text_img(co["texte"], "inter_m", 38, CREME, 830, accents=co["mots_cles"])
    scr.add(card(920, t.height + 60, True), y + 40, co["a"], chk=False)
    y = scr.add(t, y + 68, co["a"], name="correlation")
    scr.text(E["conclusion"]["texte"], y + 66, E["conclusion"]["a"], "lora_i", 43, CREME, 880, accents=E["conclusion"]["mots_cles"])


def v_fatwa(scr, E, top, sc, e):
    h = E["helice"]
    scr.add(beam(520, 560), top - 60, h["a"], anim="fade", chk=False, pulse=True)
    scr.add(ic_helix(170, 453), top + 10, h["a"], anim="wt", dur=h["duree"], gl=8, gs=0.5, name="helice")
    r = E["regle"]
    scr.text(r["texte"], top + 530, r["a"], "inter_m", 50, CREME, 860, accents=r["mots_cles"], dur=0.8)


def v_helices(scr, E, top, sc, e):
    for k, cx, br, col in (("helice_a", 290, False, ORC), ("helice_b", 790, True, GRIS)):
        el = E[k]
        if not br:
            scr.add(halo(440, 520, strength=0.26), top - 60, el["a"], cx=cx, anim="fade", chk=False, pulse=True)
        scr.add(ic_helix(140, 373, br), top + 6, el["a"], cx=cx, anim="wt", dur=el["duree"], gl=7 if not br else 0, gs=0.5, name=k)
        y = scr.text(el["texte"], top + 398, el["a"] + 0.3, "lora_b", 36, col, 440, cx=cx)
        dsz = 27 if font("inter", 27).getlength(el["detail"]) <= 440 else 25   # détail plus long (version corrigée) : une ligne
        scr.text(el["detail"], y + 2, el["a"] + 0.45, "inter", dsz, CREME, 440, cx=cx)
    y = top + 498
    scr.add(hline(940, ORS, 2, False), y, E["entete"]["a"], anim="wl", dur=0.8, chk=False)
    y = scr.text(E["entete"]["texte"], y + 24, E["entete"]["a"], "inter_b", 24, OR, 600, x=80, align="l") + 14
    for k in ("microbien", "moleculaire", "risque"):
        el = E[k]
        y = scr.text(el["texte"], y, el["a"], "inter_m", 32, CREME, 900, x=80, align="l", accents=el["mots_cles"], accent_color=OR) + 20


def v_bouclier(scr, E, top, sc, e):
    y = scr.text(E["description"]["texte"], top, E["description"]["a"], "inter_m", 36, CREME, 900)
    b = E["bouclier"]
    ys = y + 30
    scr.add(halo(640, 640, strength=0.24), ys - 100, b["a"], anim="fade", chk=False, pulse=True)
    scr.add(icon(ic_shield, 470, 100, 112), ys, b["a"], anim="wt", dur=b["duree"], chk=False, gl=8, gs=0.5)
    def node(k, cx, yy, fn, size):
        el = E[k]
        scr.add(icon(fn, size), yy, el["a"], cx=cx, gl=6, gs=0.5, name="ico_" + k, anim="fade")
        y2 = scr.text(el["texte"], yy + size + 12, el["a"] + 0.1, "inter_sb", 29, ORC, 250, cx=cx)
        scr.text(el["detail"], y2 + 2, el["a"] + 0.2, "inter", 24, CREME, 250, cx=cx)
    node("chimique", 540, ys + 78, ic_molecule, 140)
    node("cellulaire", 174, ys + 170, ic_cell, 120)
    node("competition", 906, ys + 170, ic_bacteria, 120)
    s = E["synthese"]
    scr.text(s["texte"], ys + 590, s["a"], "inter_m", 39, CREME, 900, accents=s["mots_cles"])


def v_comparatif(scr, E, top, sc, e):
    xa, xb = 70, 575
    scr.text(E["col_a"]["texte"], top + 2, E["col_a"]["a"], "lora_b", 31, ORC, 450, x=xa, align="l")
    scr.text(E["col_b"]["texte"], top + 6, E["col_b"]["a"], "lora_b", 25, GRIS, 450, x=xb, align="l")
    scr.add(hline(940, ORS, 2, False), top + 62, E["col_a"]["a"], anim="wl", dur=0.8, chk=False)
    scr.add(vline(530, ORS), top - 4, E["col_b"]["a"], cx=548, anim="wt", dur=0.8, chk=False)
    c = Cv(26, 26, 26); c.circle(13, 13, 9, 3, ORC); c.circle(13, 13, 4, 0, ORC, fill=ORC); dot = c.out()
    c = Cv(26, 26, 26); c.path([(6, 6), (20, 20)], 2.6, GRIS, sm=False); c.path([(20, 6), (6, 20)], 2.6, GRIS, sm=False); cross = c.out()
    for i in range(4):
        y = top + 96 + i * 110
        a, b = E[f"a{i+1}"], E[f"b{i+1}"]
        scr.add(dot, y + 8, a["a"], x=xa, chk=False, gl=5, gs=0.7)
        scr.text(a["texte"], y, a["a"], "inter_m", 35, CREME, 420, x=xa + 44, align="l")
        scr.add(cross, y + 6, b["a"], x=xb, chk=False)
        scr.text(b["texte"], y, b["a"], "inter", 29, GRIS, 395, x=xb + 42, align="l", accents=["Impossible"], accent_color=CREME)
    p = E["pasteurisation"]
    t = text_img(p["texte"], "inter_b", 40, OR, 840, accents=p["mots_cles"], accent_color=ORC)
    yc = top + 556
    scr.add(card(920, t.height + 56, True), yc, p["a"], chk=False)
    y = scr.add(t, yc + 28, p["a"], name="pasteurisation")
    th = E["therapie"]
    scr.add(halo(1040, 360, strength=0.22), y + 10, th["a"], anim="fade", chk=False, pulse=True)
    scr.text(th["texte"], y + 70, th["a"], "lora", 46, CREME, 880, accents=th["mots_cles"])


def v_tableau(scr, E, top, sc, e):
    cols = ((62, 372), (384, 742), (754, 1018))
    for k, (a, b) in zip(("col1", "col2", "col3"), cols):
        scr.text(E[k]["texte"], top + 4, E[k]["a"], "lora_b", 26, OR, b - a, cx=(a + b) // 2)
    scr.add(hline(940, ORS, 2, False), top + 78, E["col1"]["a"], anim="wl", dur=0.9, chk=False)
    rh = 138
    for i in range(5):
        el = E[f"l{i+1}"]
        y = top + 104 + i * (rh + 14)
        scr.add(card(940, rh, el.get("fort", False)), y, el["a"], chk=False)
        specs = ((el["texte"], "inter_sb", 31, ORC, 0), (el["preuve"], "inter", 30, CREME, 0.12),
                 (el["concordance"], "inter_b" if el.get("fort") else "inter_sb", 30 if len(el["concordance"]) <= 18 else 28, ORC if el.get("fort") else CREME, 0.3))
        for (txt, fk, sz, col, dl), (a, b) in zip(specs, cols):
            im = text_img(txt, fk, sz, col, b - a - 24)
            scr.add(im, y + (rh - im.height) // 2 + 3, el["a"] + dl, cx=(a + b) // 2, name=txt[:20],
                    gl=10 if (el.get("fort") and dl == 0.3) else 0, gs=0.8)
        for (a, b) in cols[:2]:
            scr.add(vline(rh - 36, ORS[:3] + (150,)), y + 18, el["a"], x=b + 7, anim="fade", chk=False)
    p = E["pied"]
    scr.text(p["texte"], top + 104 + 5 * (rh + 14) + 22, p["a"], "inter", 31, CREME, 900)


def v_conclusion(scr, E, top, sc, e):
    c = E["cadre"]
    def frame(y):
        scr.add(sprig(230, 92, True), y - 40, c["a"], x=70, anim="wl", dur=c["duree"], chk=False)
        scr.add(sprig(230, 92), y - 40, c["a"], x=780, anim="wl", dur=c["duree"], chk=False)
        scr.add(hline(470, ORS, 2, True), y, c["a"], anim="wl", dur=c["duree"], chk=False)
    frame(top + 30)
    y = scr.text(E["intro"]["texte"], top + 112, E["intro"]["a"], "lora", 46, CREME, 860, accents=E["intro"]["mots_cles"])
    y += 34
    for k in ("g1", "g2", "g3"):
        y = scr.text("– " + E[k]["texte"], y, E[k]["a"], "inter_m", 38, CREME, 920, accents=["–"]) + 16
    frame(y + 44)
    f = E["final"]
    scr.add(halo(1060, 520, strength=0.3), y + 20, f["a"], anim="fade", chk=False, pulse=True)
    y = scr.text(f["texte"].replace("qu’en 2025", "qu’en\u00a02025").replace("depuis 2007", "depuis\u00a02007"), y + 124, f["a"],
                 "lora_b", 52, OR, 900, accents=f["mots_cles"], accent_color=ORC, dur=0.8)
    if "sources" in E:  # version corrigée : mention discrète en fin de vidéo
        scr.text(E["sources"]["texte"], y + 14, E["sources"]["a"], "inter_m", 28, GRIS, 900, anim="fade", dur=0.6)


VIS = {k[2:]: v for k, v in globals().items() if k.startswith("v_")}
_cache = {}


def scene_sprites(i):
    """-> (sprites d'en-tête, [sprites par écran])"""
    if i not in _cache:
        sc = SCENES[i]
        if sc["ecrans"][0]["visuel"] == "titre":
            hd, top = Screen(), 190
        else:
            hd, top = header(sc)
        scrs = []
        for e in sc["ecrans"]:
            s = Screen()
            VIS[e["visuel"]](s, {x["id"]: x for x in e["elements"]}, top, sc, e)
            scrs.append(s.sp)
        _cache[i] = (hd.sp, scrs)
    return _cache[i]


# ================================================================ fond + particules
def make_bg():
    import numpy as np
    yy, xx = np.mgrid[0:H, 0:W].astype("float32")
    r = np.hypot((xx - W / 2) / (W * 0.75), (yy - H * 0.42) / (H * 0.62))
    a = np.clip(r * 1.15, 0, 1)[..., None]
    b = np.clip((r - 0.55) * 1.6, 0, 1)[..., None]
    c3, c1, c2 = (np.array(c[:3], dtype="float32") for c in (BG3, BG, BG2))
    img = (c3 * (1 - a) + c1 * a) * (1 - b) + c2 * b
    rng = np.random.default_rng(3)
    img += rng.uniform(-0.6, 0.6, img.shape)          # léger tramage contre les bandes
    im = Image.fromarray(np.clip(img, 0, 255).astype("uint8"), "RGB").convert("RGBA")
    # cadre en filet or sombre + ornements d'angle (décor seulement)
    fr = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(fr).rectangle((34, 34, W - 35, H - 35), outline=ORS[:3] + (110,), width=2)
    co = corner(120)
    co.putalpha(co.getchannel("A").point(lambda v: int(v * 0.8)))
    for k, (x, y) in enumerate(((48, 48), (W - 168, 48), (W - 168, H - 168), (48, H - 168))):
        fr.alpha_composite(co.rotate(-90 * k), (x, y))
    im.alpha_composite(fr)
    return im


_rnd = random.Random(5)
PART = [dict(x=_rnd.uniform(40, W - 40), y=_rnd.uniform(0, H), v=_rnd.uniform(5, 16), amp=_rnd.uniform(6, 22),
             ph=_rnd.uniform(0, 6.28), fr=_rnd.uniform(0.15, 0.4), s=_rnd.choice((0, 0, 1, 1, 2)), al=_rnd.uniform(0.25, 0.8)) for _ in range(46)]
_G = {}


def G():
    if not _G:
        _G["bg"] = make_bg()
        dots = []
        for r in (3, 4, 6):
            c = Cv(4 * r, 4 * r, 4 * r)
            c.circle(2 * r, 2 * r, r * 0.55, 0, ORC, fill=ORC[:3] + (150,))
            dots.append(c.out().filter(ImageFilter.GaussianBlur(r * 0.35)))
        _G["dots"] = dots
        _G["subs"] = build_subs()
        _G["subimg"] = {}
    return _G


def comp(im, sp, x, y, alpha=1.0):
    """alpha_composite avec rognage aux bords et opacité."""
    x, y = int(round(x)), int(round(y))
    x0, y0 = max(0, -x), max(0, -y)
    x1, y1 = min(sp.width, W - x), min(sp.height, H - y)
    if x1 <= x0 or y1 <= y0:
        return
    if (x0, y0, x1, y1) != (0, 0, sp.width, sp.height):
        sp = sp.crop((x0, y0, x1, y1))
    if alpha < 0.995:
        if alpha <= 0.004:
            return
        sp = sp.copy()
        k = alpha
        sp.putalpha(sp.getchannel("A").point(lambda v: int(v * k)))
    im.alpha_composite(sp, (x + x0, y + y0))


def draw_sp(im, s, t, fade):
    if t < s.at:
        return
    p = min(1.0, (t - s.at) / s.dur)
    e = 1 - (1 - p) ** 3
    img, x, y = s.img, s.x, s.y
    a = fade
    if s.anim == "up":
        a *= e
        y += (1 - e) * 28
    elif s.anim == "fade":
        a *= e
    elif p < 1:
        a *= min(1.0, (t - s.at) / 0.12)
        w, h = img.size
        if s.anim == "wl":
            img = img.crop((0, 0, max(1, int(w * e)), h))
        elif s.anim == "wt":
            img = img.crop((0, 0, w, max(1, int(h * p))))
        elif s.anim == "wb":
            k = max(1, int(h * p))
            img = img.crop((0, h - k, w, h))
            y += h - k
        elif s.anim == "rad":
            m = Image.new("L", (w, h), 0)
            ImageDraw.Draw(m).pieslice((-w, -h, 2 * w, 2 * h), -90, -90 + 360 * (p * p * (3 - 2 * p)), fill=255)
            img = img.copy()
            img.putalpha(ImageChops.multiply(img.getchannel("A"), m))
    if s.pulse:
        a *= 0.82 + 0.18 * math.sin(2 * math.pi * (t - s.at) / 3.4)
    comp(im, img, x, y, a)


# ================================================================ sous-titres mot par mot
def build_subs():
    ws = [w for sc in SCENES for w in sc["mots"]]
    groups, cur = [], []
    def endp(m):
        return m.rstrip("  »\"").endswith((".", ",", "?", "!", ":", ";", "…"))
    for i, w in enumerate(ws):
        if cur:
            prev = cur[-1]
            chars = sum(len(x["m"]) for x in cur) + len(w["m"])
            if len(cur) >= 4 or (len(cur) >= 2 and endp(prev["m"])) or w["d"] - prev["f"] > 0.55 or chars > 30 \
                    or (endp(prev["m"]) and prev["m"].rstrip("  ").endswith((".", "?", "!"))):
                groups.append(cur)
                cur = []
        cur.append(w)
    groups.append(cur)
    # éviter les groupes d'un seul mot quand on peut les rattacher
    out = []
    for g in groups:
        if out and len(g) == 1 and len(out[-1]) <= 3 and g[0]["d"] - out[-1][-1]["f"] < 0.4 and not out[-1][-1]["m"].rstrip("  ").endswith((".", "?", "!")):
            out[-1] = out[-1] + g
        else:
            out.append(g)
    res = []
    for k, g in enumerate(out):
        fin = g[-1]["f"] + 0.9
        if k + 1 < len(out):
            fin = min(fin, out[k + 1][0]["d"])
        res.append(dict(mots=g, d=g[0]["d"], f=fin))
    return res


SUBF, SUBS = "inter_xb", 56


def sub_layout(gi):
    g = G()
    if gi in g["subimg"]:
        return g["subimg"][gi]
    f = font(SUBF, SUBS)
    items = []
    for w in g["subs"][gi]["mots"]:
        tw = int(f.getlength(w["m"]))
        items.append((w, tw + 36))
    lines, cur, cw = [], [], 0
    for it in items:
        if cur and cw + 12 + it[1] > 960:
            lines.append((cur, cw)); cur, cw = [], 0
        cw += (12 if cur else 0) + it[1]
        cur.append(it)
    lines.append((cur, cw))
    ph, lh = 84, 98
    y0 = SUB_Y - (len(lines) * lh - (lh - ph)) // 2
    res = []
    for li, (cur, cw) in enumerate(lines):
        x = (W - cw) // 2
        for w, pw in cur:
            ims = []
            for act in (False, True):
                im = rrect(pw, ph, 16, fill=(ORC if act else BG2[:3] + (232,)))
                d = ImageDraw.Draw(im)
                if not act:
                    d.rounded_rectangle((10, ph - 7, pw - 10, ph - 4), 2, fill=OR)
                d.text((18, 9), w["m"], font=f, fill=BG2 if act else CREME)
                ims.append(im)
            act_g, _ = glow(ims[1], 10, strength=0.5)
            res.append((w, x, y0 + li * lh, ims[0], act_g))
            x += pw + 12
    g["subimg"][gi] = res
    if len(g["subimg"]) > 6:
        g["subimg"].pop(next(iter(g["subimg"])))
    return res


def sub_state(t):
    """-> (index du groupe, [(mot, actif?)]) affiché à l'instant t, ou None."""
    subs = G()["subs"]
    for gi, s in enumerate(subs):
        if s["d"] <= t < s["f"]:
            vis = [w for w in s["mots"] if w["d"] <= t]
            cur = vis[-1] if vis and t < vis[-1]["f"] + 0.25 else None
            return gi, [(w["m"], w is cur) for w in vis]
    return None


def draw_subs(im, t):
    st = sub_state(t)
    if not st:
        return
    gi = st[0]
    s = G()["subs"][gi]
    out = min(1.0, (s["f"] - t) / 0.12) if s["f"] - s["mots"][-1]["f"] > 0.5 else 1.0
    for w, x, y, n_im, a_im in sub_layout(gi):
        if t < w["d"]:
            continue
        p = min(1.0, (t - w["d"]) / 0.1)
        last = [x_ for x_ in s["mots"] if x_["d"] <= t][-1]
        act = (w is last) and t < w["f"] + 0.25
        if act:
            comp(im, a_im, x - 22, y - 22 + (1 - p) * 10, p * out)
        else:
            comp(im, n_im, x, y, out)


# ================================================================ image
def scene_at(t):
    for i, sc in enumerate(SCENES):
        if sc["debut"] <= t < sc["fin"]:
            return i
    return len(SCENES) - 1


def render(t, subs=True):
    g = G()
    im = g["bg"].copy()
    for p in PART:
        y = (p["y"] - p["v"] * t) % (H + 40) - 20
        x = p["x"] + p["amp"] * math.sin(p["ph"] + p["fr"] * t)
        a = p["al"] * (0.6 + 0.4 * math.sin(p["ph"] * 3 + t * 0.9))
        d = g["dots"][p["s"]]
        comp(im, d, x - d.width / 2, y - d.height / 2, a)
    i = scene_at(t)
    sc = SCENES[i]
    hd, scrs = scene_sprites(i)
    last = (i == len(SCENES) - 1)
    f_sc = 1.0 if last else max(0.0, min(1.0, (sc["fin"] - t) / 0.22))
    for s in hd:
        draw_sp(im, s, t, f_sc)
    for k, e in enumerate(sc["ecrans"]):
        if e["debut"] <= t < e["fin"]:
            f = 1.0 if (last and k == len(sc["ecrans"]) - 1) else max(0.0, min(1.0, (e["fin"] - t) / 0.22))
            for s in scrs[k]:
                draw_sp(im, s, t, f)
    if subs:
        draw_subs(im, t)
    return im.convert("RGB")


def frame_bytes(n):
    return render(n / FPS).tobytes()


# ================================================================ contrôles
def checks():
    """Débordements, zone sûre et chevauchements, sur les boîtes de contenu des sprites."""
    pb = []
    for i, sc in enumerate(SCENES):
        hd, scrs = scene_sprites(i)
        for k, sps in enumerate(scrs):
            L = [s for s in hd + sps if s.chk]
            tag = f"scène {sc['id']} écran {k+1} ({sc['ecrans'][k]['visuel']})"
            for s in L:
                x0, y0, x1, y1 = s.box
                if x0 < 44 or x1 > W - 44:
                    pb.append(f"{tag}: « {s.name} » déborde en largeur ({x0}..{x1})")
                if y0 < SAFE_T or y1 > CONTENT_B:
                    pb.append(f"{tag}: « {s.name} » hors zone de contenu ({y0}..{y1}, autorisé {SAFE_T}..{CONTENT_B})")
            for a in range(len(L)):
                for b in range(a + 1, len(L)):
                    A, B = L[a].box, L[b].box
                    if min(A[2], B[2]) - max(A[0], B[0]) > 2 and min(A[3], B[3]) - max(A[1], B[1]) > 2:
                        pb.append(f"{tag}: « {L[a].name} » chevauche « {L[b].name} » {A} / {B}")
    # sous-titres
    g = G()
    for gi in range(len(g["subs"])):
        for w, x, y, n_im, a_im in sub_layout(gi):
            if x < 44 or x + n_im.width > W - 44 or y < CONTENT_B + 10 or y + n_im.height > SAFE_B:
                pb.append(f"sous-titre groupe {gi} « {w['m']} » hors zone ({x},{y},{x+n_im.width},{y+n_im.height})")
    return pb


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "apercus"
    if mode == "image":
        render(float(sys.argv[2])).save(sys.argv[3])
    elif mode == "apercus":
        out = PATHS["APERCUS"]
        os.makedirs(out, exist_ok=True)
        for f in os.listdir(out):
            os.remove(os.path.join(out, f))
        for sc in SCENES:
            for k, e in enumerate(sc["ecrans"]):
                t = e["fin"] - 0.3
                render(t).save(os.path.join(out, f"scene{sc['id']:02d}_ecran{k+1}_{e['visuel']}_{t:.1f}s.png"))
        pb = checks()
        print(f"{len(pb)} problème(s)")
        for p in pb:
            print(" -", p)
        g = G()
        n = [len(s["mots"]) for s in g["subs"]]
        print("groupes de sous-titres:", len(n), "tailles:", {k: n.count(k) for k in sorted(set(n))})
    elif mode == "video":
        from multiprocessing import Pool
        a, b = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (0, NFRAMES)
        outp = sys.argv[4] if len(sys.argv) > 4 else PATHS["VIDEO"]
        cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"]
        if (a, b) == (0, NFRAMES):
            cmd += ["-i", PATHS["AUDIO"], "-map", "0:v", "-map", "1:a", "-c:a", "copy"]
        cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", "-movflags", "+faststart", outp]
        ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        with Pool(4) as pool:
            for k, buf in enumerate(pool.imap(frame_bytes, range(a, b), chunksize=6)):
                ff.stdin.write(buf)
                if k % 300 == 0:
                    print(f"{a+k}/{b}", flush=True)
        ff.stdin.close()
        print("ffmpeg:", ff.wait())


if __name__ == "__main__":
    main()
