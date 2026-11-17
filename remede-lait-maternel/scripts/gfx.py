"""Primitives de dessin vectoriel (Pillow, suréchantillonné) + icônes au trait or."""
import math, random, os
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FD = os.path.join(ROOT, "fonts")


def hx(h, a=255):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


BG, BG2, BG3 = hx("#151516"), hx("#0B0B0C"), hx("#201E1F")
OR, ORC, ORS = hx("#B6A57A"), hx("#E4D9B0"), hx("#706650")
CREME = hx("#EFE8D8")
GRIS = hx("#8C8A84")

FONTS = {
    "titre": "playfair-display-latin-600-normal.ttf",
    "titre_i": "playfair-display-latin-600-italic.ttf",
    "lora": "lora-latin-500-normal.ttf",
    "lora_i": "lora-latin-500-italic.ttf",
    "lora_b": "lora-latin-700-normal.ttf",
    "inter": "/usr/share/fonts/opentype/inter/Inter-Regular.otf",
    "inter_i": "/usr/share/fonts/opentype/inter/Inter-Italic.otf",
    "inter_m": "/usr/share/fonts/opentype/inter/Inter-Medium.otf",
    "inter_sb": "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf",
    "inter_b": "/usr/share/fonts/opentype/inter/Inter-Bold.otf",
    "inter_xb": "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf",
}
ITAL = {"titre": "titre_i", "lora": "lora_i", "inter": "inter_i", "inter_m": "inter_i",
        "inter_sb": "inter_i", "lora_i": "lora", "lora_b": "lora_i"}


@lru_cache(None)
def font(key, size):
    p = FONTS[key]
    if not p.startswith("/"):
        p = os.path.join(FD, p)
    return ImageFont.truetype(p, size)


# ---------------------------------------------------------------- texte riche
def _spans(text, accents, italics):
    """Découpe text en (mot, accent?, italique?) en repérant les sous-chaînes."""
    n = len(text)
    acc = [False] * n
    ita = [False] * n
    for lst, arr in ((accents, acc), (italics, ita)):
        for s in lst or []:
            i = text.find(s)
            while i >= 0:
                for k in range(i, i + len(s)):
                    arr[k] = True
                i = text.find(s, i + len(s))
    toks, i = [], 0
    while i < n:
        if text[i] == "\n":
            toks.append("\n")
            i += 1
            continue
        if text[i] == " ":
            i += 1
            continue
        j = i
        while j < n and text[j] not in " \n":
            j += 1
        # sous-découpe si le style change au milieu du mot
        k = i
        parts = []
        while k < j:
            m = k
            while m < j and (acc[m], ita[m]) == (acc[k], ita[k]):
                m += 1
            parts.append((text[k:m], acc[k], ita[k]))
            k = m
        toks.append(parts)
        i = j
    return toks


def text_img(text, fkey="inter", size=32, color=CREME, maxw=900, align="c", accents=None,
             italics=None, accent_color=OR, lh=1.28, max_lines=None):
    """Rend un bloc de texte (retour à la ligne automatique) -> image RGBA rognée."""
    f = font(fkey, size)
    fi = font(ITAL.get(fkey, fkey), size)
    sp = f.getlength(" ")
    toks = _spans(text, accents, italics)
    lines, cur, curw = [], [], 0
    for parts in toks:
        if parts == "\n":
            lines.append((cur, curw))
            cur, curw = [], 0
            continue
        w = sum((fi if it else f).getlength(t) for t, _, it in parts)
        if cur and curw + sp + w > maxw:
            lines.append((cur, curw))
            cur, curw = [], 0
        curw = curw + (sp if cur else 0) + w
        cur.append((parts, w))
    if cur:
        lines.append((cur, curw))
    H = int(size * lh)
    W = int(max(w for _, w in lines)) + 4
    img = Image.new("RGBA", (W, H * len(lines) + int(size * 0.25)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for li, (cur, lw) in enumerate(lines):
        x = {"c": (W - lw) / 2, "l": 0, "r": W - lw}[align]
        for parts, w in cur:
            for t, ac, it in parts:
                ff = fi if it else f
                d.text((x, li * H), t, font=ff, fill=accent_color if ac else color)
                x += ff.getlength(t)
            x += sp
    img.n_lines = len(lines)
    return img


def fit_text(text, fkey, sizes, maxw, max_lines, **kw):
    for s in sizes:
        im = text_img(text, fkey, s, maxw=maxw, **kw)
        if im.n_lines <= max_lines:
            return im
    return im


# ---------------------------------------------------------------- canevas vectoriel
def smooth(pts, n=14, closed=False):
    """Catmull-Rom passant par les points."""
    if len(pts) < 3:
        return list(pts)
    P = list(pts)
    if closed:
        P = [P[-1]] + P + [P[0], P[1]]
    else:
        P = [P[0]] + P + [P[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[a]) + (-p0[a] + p2[a]) * t + (2 * p0[a] - 5 * p1[a] + 4 * p2[a] - p3[a]) * t2
                                    + (-p0[a] + 3 * p1[a] - 3 * p2[a] + p3[a]) * t3) for a in (0, 1)))
    out.append(P[-2] if not closed else out[0])
    return out


class Cv:
    """Canevas en unités logiques (uw x uh) rendu dans une image w x h, suréchantillonné."""

    def __init__(self, w, h, uw=100, uh=None, ss=3):
        uh = uh if uh is not None else uw * h / w
        self.w, self.h, self.ss = w, h, ss
        self.kx, self.ky = w * ss / uw, h * ss / uh
        self.k = min(self.kx, self.ky)
        self.im = Image.new("RGBA", (w * ss, h * ss), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)

    def _m(self, pts):
        return [(x * self.kx, y * self.ky) for x, y in pts]

    def path(self, pts, w=1.6, color=OR, closed=False, sm=True):
        p = smooth(pts, closed=closed) if sm else (list(pts) + ([pts[0]] if closed else []))
        p = self._m(p)
        W = max(1, int(round(w * self.k)))
        self.d.line(p, fill=color, width=W, joint="curve")
        r = W / 2
        for (x, y) in (p[0], p[-1]):
            self.d.ellipse((x - r, y - r, x + r, y + r), fill=color)

    def circle(self, cx, cy, r, w=1.6, color=OR, fill=None):
        x, y, rx, ry = cx * self.kx, cy * self.ky, r * self.kx, r * self.ky
        self.d.ellipse((x - rx, y - ry, x + rx, y + ry), outline=color if w else None, fill=fill,
                       width=max(1, int(round(w * self.k))) if w else 0)

    def poly(self, pts, fill=OR):
        self.d.polygon(self._m(pts), fill=fill)

    def out(self):
        return self.im.resize((self.w, self.h), Image.LANCZOS)


def glow(img, radius=10, color=ORC, strength=0.55, pad=None):
    """Ajoute un halo doux derrière l'image. Renvoie (image, marge)."""
    pad = pad if pad is not None else int(radius * 2.2)
    W, H = img.size
    big = Image.new("RGBA", (W + 2 * pad, H + 2 * pad), (0, 0, 0, 0))
    a = Image.new("L", big.size, 0)
    a.paste(img.getchannel("A"), (pad, pad))
    a = a.filter(ImageFilter.GaussianBlur(radius)).point(lambda v: int(min(255, v * strength * 1.6)))
    g = Image.new("RGBA", big.size, color[:3] + (0,))
    g.putalpha(a)
    big.alpha_composite(g)
    big.alpha_composite(img, (pad, pad))
    return big, pad


def halo(w, h, color=ORC, strength=0.34):
    """Halo radial doux (ellipse)."""
    s = 8
    sw, sh = max(2, w // s), max(2, h // s)
    a = Image.new("L", (sw, sh), 0)
    px = a.load()
    for y in range(sh):
        for x in range(sw):
            r = math.hypot((x + .5 - sw / 2) / (sw / 2), (y + .5 - sh / 2) / (sh / 2))
            v = max(0.0, 1 - r)
            px[x, y] = int(255 * strength * v * v)
    a = a.resize((w, h), Image.BICUBIC)
    im = Image.new("RGBA", (w, h), color[:3] + (0,))
    im.putalpha(a)
    return im


def beam(w, h, top=0.22, color=ORC, strength=0.20):
    """Faisceau de lumière tombant (trapèze dégradé), comme un projecteur."""
    s = 4
    sw, sh = w // s, h // s
    a = Image.new("L", (sw, sh), 0)
    px = a.load()
    for y in range(sh):
        ty = y / sh
        half = (top + (1 - top) * ty) * sw / 2
        for x in range(sw):
            dx = abs(x + .5 - sw / 2) / max(half, 1)
            if dx < 1:
                edge = (1 - dx) ** 1.5
                px[x, y] = int(255 * strength * edge * (1 - 0.75 * ty) * min(1, ty * 6 + .15))
    a = a.resize((w, h), Image.BICUBIC).filter(ImageFilter.GaussianBlur(6))
    im = Image.new("RGBA", (w, h), color[:3] + (0,))
    im.putalpha(a)
    return im


def rrect(w, h, r, fill=None, outline=None, ow=2):
    ss = 3
    im = Image.new("RGBA", (w * ss, h * ss), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((ow * ss / 2, ow * ss / 2, w * ss - 1 - ow * ss / 2, h * ss - 1 - ow * ss / 2),
                                         r * ss, fill=fill, outline=outline, width=ow * ss if outline else 0)
    return im.resize((w, h), Image.LANCZOS)


# ---------------------------------------------------------------- icônes (unités 0..100)
def _leaf(c, x, y, ang, L=7.0, wd=2.4, color=OR, w=0.7):
    ca, sa = math.cos(ang), math.sin(ang)
    def tr(u, v):
        return (x + u * ca - v * sa, y + u * sa + v * ca)
    a = [tr(0, 0), tr(L * .5, wd), tr(L, 0)]
    b = [tr(0, 0), tr(L * .5, -wd), tr(L, 0)]
    c.path(a, w, color)
    c.path(b, w, color)
    c.path([tr(0, 0), tr(L, 0)], w * .7, color, sm=False)


def _flower(c, x, y, r=3.2, color=OR, w=0.7):
    for i in range(5):
        a = i * 2 * math.pi / 5 - math.pi / 2
        c.circle(x + r * .62 * math.cos(a), y + r * .62 * math.sin(a), r * .5, w, color)
    c.circle(x, y, r * .22, 0, color, fill=color)


def wreath(c, cx=50, cy=50, R=44, color=OR):
    for side in (1, -1):
        angs = [90 + side * a for a in range(14, 166, 1)]
        c.path([(cx + R * math.cos(math.radians(a)), cy + R * math.sin(math.radians(a))) for a in angs[::6]], 0.8, color)
        k = 0
        for a in range(20, 164, 9):
            th = math.radians(90 + side * a)
            x, y = cx + R * math.cos(th), cy + R * math.sin(th)
            tang = th + side * math.pi / 2
            if a in (56, 110):
                _flower(c, x, y, 4.2, color)
            else:
                io = 1 if k % 2 == 0 else -1
                _leaf(c, x, y, tang + io * 0.75 * side, 7.5, 2.3, color)
                _leaf(c, x, y, tang - io * 0.25 * side, 6.0, 1.9, color)
            k += 1
    # petit écu en bas
    c.poly([(44, 91), (56, 91), (56, 97), (50, 101), (44, 97)], fill=color)


def mother_child(c, color=OR, w=1.5, ox=0, oy=0, s=1.0):
    def T(pts):
        return [(ox + x * s, oy + y * s) for x, y in pts]
    ws = w * s
    c.path(T([(22, 96), (17, 74), (22, 48), (36, 28), (54, 20), (68, 26), (74, 38)]), ws, color)      # voile extérieur
    c.path(T([(74, 38), (76, 45), (80, 51), (76, 54), (76, 58), (72, 63), (64, 65)]), ws, color)      # profil
    c.path(T([(60, 24), (53, 36), (54, 52), (62, 64), (57, 76), (44, 84)]), ws, color)              # bord du voile
    c.path(T([(46, 26), (38, 42), (39, 60), (46, 76)]), ws * .7, color)                           # pli
    c.path(T([(36, 34), (29, 50), (30, 68), (36, 84)]), ws * .7, color)                           # pli
    c.path(T([(68, 45), (71, 47), (74, 45)]), ws * .7, color)                                     # œil clos
    c.path(T([(22, 96), (32, 84), (44, 84)]), ws, color)                                          # épaule
    c.path(T([(36, 84), (40, 98), (56, 106), (76, 104), (90, 94), (92, 84)]), ws, color)            # bras
    c.circle(ox + 78 * s, oy + 80 * s, 10.5 * s, ws, color)                                       # tête de l'enfant
    c.path(T([(69, 86), (60, 90), (56, 98)]), ws * .8, color)                                     # corps de l'enfant
    c.path(T([(74, 78), (77, 80), (80, 78)]), ws * .6, color)                                     # œil de l'enfant


def emblem(size, wreath_on=True):
    c = Cv(size, size, 100)
    if wreath_on:
        wreath(c)
        mother_child(c, ox=21, oy=14, s=0.58, w=2.0)
    else:
        mother_child(c, ox=-6, oy=-12, s=1.0, w=1.6)
    return c.out()


def ic_book(c, ox=0, oy=0, s=1, color=OR):
    def T(p): return [(ox + x * s, oy + y * s) for x, y in p]
    w = 1.6 * s
    c.path(T([(50, 30), (30, 24), (8, 28), (8, 78), (30, 74), (50, 80)]), w, color, sm=False)
    c.path(T([(50, 30), (70, 24), (92, 28), (92, 78), (70, 74), (50, 80)]), w, color, sm=False)
    c.path(T([(50, 30), (50, 80)]), w, color, sm=False)
    for y in (40, 50, 60):
        c.path(T([(16, y), (42, y - 2)]), w * .6, color, sm=False)
        c.path(T([(58, y - 2), (84, y)]), w * .6, color, sm=False)
    c.path(T([(4, 82), (30, 79), (50, 86), (70, 79), (96, 82)]), w, color, sm=False)


def ic_microscope(c, ox=0, oy=0, s=1, color=OR):
    def T(p): return [(ox + x * s, oy + y * s) for x, y in p]
    w = 1.6 * s
    c.path(T([(38, 14), (50, 8), (66, 44), (54, 50)]), w, color, closed=True, sm=False)   # tube
    c.path(T([(57, 49), (62, 60), (56, 63), (51, 52)]), w, color, sm=False)               # objectif
    c.path(T([(36, 68), (74, 68)]), w, color, sm=False)                                # platine
    c.path(T([(62, 20), (82, 36), (86, 58), (76, 78), (62, 88)]), w, color)               # potence
    c.path(T([(26, 90), (84, 90)]), w * 1.3, color, sm=False)                            # pied
    c.path(T([(46, 68), (46, 90)]), w, color, sm=False)


def ic_brain(c, color=OR, w=1.8):
    c.path([(20, 55), (18, 40), (28, 24), (45, 16), (64, 18), (80, 30), (86, 46), (80, 60), (66, 66), (60, 74), (50, 72), (46, 64), (32, 66)], w, color, closed=True)
    for p in ([(30, 40), (40, 36), (46, 44), (56, 38)], [(50, 24), (56, 32), (66, 30), (72, 38)],
              [(34, 54), (44, 52), (52, 58)], [(64, 48), (72, 52), (78, 46)]):
        c.path(p, w * .7, color)
    c.path([(55, 73), (57, 86)], w, color, sm=False)
    for x, y in ((38, 30), (60, 42), (70, 26), (44, 48)):
        c.circle(x, y, 1.6, 0, ORC, fill=ORC)


def ic_tree(c, color=OR, w=1.8):
    c.path([(45, 92), (47, 74), (46, 60)], w, color)
    c.path([(55, 92), (53, 74), (54, 60)], w, color)
    c.path([(50, 60), (40, 46)], w * .7, color, sm=False)
    c.path([(50, 60), (62, 44)], w * .7, color, sm=False)
    c.path([(50, 60), (50, 36)], w * .7, color, sm=False)
    c.path([(22, 46), (18, 32), (30, 18), (46, 10), (62, 12), (78, 22), (84, 38), (76, 54), (60, 60), (40, 60), (28, 56)], w, color, closed=True)
    c.path([(30, 92), (70, 92)], w, color, sm=False)


def ic_drop(c, color=OR, w=2.0):
    c.path([(50, 8), (64, 36), (74, 58), (68, 80), (50, 90), (32, 80), (26, 58), (36, 36)], w, color, closed=True)
    c.path([(37, 60), (40, 73), (49, 80)], w * .7, color)


def ic_heart(c, color=ORC):
    pts = []
    for i in range(60):
        t = i / 60 * 2 * math.pi
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        pts.append((50 + x * 2.6, 48 + y * 2.6))
    c.poly(pts, fill=color)


def ic_arrow(w, h, color=OR):
    c = Cv(w, h, 100, 100 * h / w)
    y = 50 * h / w
    c.path([(2, y), (92, y)], 1.6, color, sm=False)
    c.path([(84, y - 6), (96, y), (84, y + 6)], 1.6, color, sm=False)
    c.poly([(46, y), (50, y - 5), (54, y), (50, y + 5)], fill=ORC)
    return c.out()


def ic_shield(c, color=OR, w=1.6):
    P = [(50, 5), (70, 12), (91, 16), (91, 50), (80, 80), (50, 106), (20, 80), (9, 50), (9, 16), (30, 12)]
    c.path(P, w, color, closed=True)
    c.path([(50 + (x - 50) * .88, 55 + (y - 55) * .88) for x, y in P], w * .7, color, closed=True)


def ic_cell(c, color=OR, w=1.8):
    c.path([(50 + (40 + 2.2 * math.sin(12 * a)) * math.cos(a), 50 + (40 + 2.2 * math.sin(12 * a)) * math.sin(a))
            for a in [i * 2 * math.pi / 72 for i in range(72)]], w, color, closed=True, sm=False)
    c.path([(32, 36), (46, 28), (56, 36), (48, 46), (36, 50)], w * .8, color, closed=True)
    c.path([(56, 56), (70, 52), (72, 66), (60, 74), (50, 68)], w * .8, color, closed=True)
    for x, y in ((66, 34), (34, 64), (44, 76)):
        c.circle(x, y, 2.6, w * .6, color)


def ic_bacteria(c, color=OR):
    rnd = random.Random(7)
    spots = [(28, 26), (58, 20), (76, 44), (40, 52), (22, 70), (60, 74), (80, 78), (50, 36)]
    for x, y in spots:
        a = rnd.uniform(0, math.pi)
        L = rnd.uniform(7, 11)
        p = [(x - L * math.cos(a), y - L * math.sin(a)), (x + L * math.cos(a), y + L * math.sin(a))]
        c.path(p, 8.5, color, sm=False)
        c.path(p, 5.4, (0, 0, 0, 0), sm=False)


def ic_molecule(c, color=OR, w=1.6):
    hexa = [(50 + 14 * math.cos(i * math.pi / 3), 50 + 14 * math.sin(i * math.pi / 3)) for i in range(6)]
    c.path(hexa, w, color, closed=True, sm=False)
    for i, (x, y) in enumerate(hexa):
        a = i * math.pi / 3
        x2, y2 = 50 + 32 * math.cos(a), 50 + 32 * math.sin(a)
        c.path([(x, y), (x2, y2)], w, color, sm=False)
        c.circle(x2, y2, 5, w, color, fill=BG)
    c.circle(50, 50, 5, 0, ORC, fill=ORC)


def ic_toddler(w, h, color=CREME):
    """Silhouette d'enfant debout, de face (unités 100 x 180)."""
    c = Cv(w, h, 100, 180)
    c.circle(50, 24, 18, 1.5, color)
    c.path([(42, 42), (30, 48), (22, 62), (14, 80), (10, 92), (16, 96), (22, 86), (30, 74), (31, 100), (30, 125), (30, 150), (28, 168),
            (24, 174), (36, 176), (44, 172), (46, 150), (50, 128), (54, 150), (56, 172), (64, 176), (76, 174), (72, 168), (70, 150),
            (70, 125), (69, 100), (70, 74), (78, 86), (84, 96), (90, 92), (86, 80), (78, 62), (70, 48), (58, 42)], 1.5, color, closed=True)
    g = OR
    c.path([(40, 22), (45, 15), (55, 15), (60, 22)], 1.1, g)
    c.path([(42, 28), (50, 23), (58, 28)], 1.1, g)
    c.path([(40, 96), (60, 96), (61, 104), (40, 104), (39, 112), (60, 112), (58, 119)], 1.2, g)
    return c.out()


def ic_toddler_flow(w, h):
    c = Cv(w, h, 100, 180)
    c.path([(50, 114), (43, 100), (57, 84), (55, 66), (47, 50), (50, 36), (50, 22)], 2.2, ORC)
    hc = Cv(w, h, 100, 180)
    for (x, y, r) in ((55, 66, 4.2), (50, 22, 4.6), (50, 106, 4.0)):
        c.circle(x, y, r, 0, ORC, fill=ORC)
    return c.out()


def ic_helix(w, h, broken=False):
    """Double hélice (unités 60 x 160)."""
    c = Cv(w, h, 60, 160)
    rnd = random.Random(11)
    ys = [8 + i * 1.5 for i in range(97)]
    def sx(y, ph): return 30 + 21 * math.sin(2 * math.pi * (y - 8) / 96 + ph)
    A = [(sx(y, 0), y) for y in ys]
    B = [(sx(y, math.pi), y) for y in ys]
    if not broken:
        for y in range(14, 152, 9):
            c.path([(sx(y, 0), y), (sx(y, math.pi), y)], 1.5, OR, sm=False)
        c.path(A, 2.4, OR, sm=False)
        c.path(B, 2.4, OR, sm=False)
    else:
        for y in range(14, 152, 9):
            col = OR if rnd.random() < .5 else GRIS
            dx, dy = rnd.uniform(-7, 7), rnd.uniform(-5, 5)
            x1, x2 = sx(y, 0), sx(y, math.pi)
            m = (x1 + x2) / 2
            c.path([(x1 + (m - x1) * rnd.uniform(0, .25), y), (m + dx, y + dy)], 1.6, col, sm=False)
            if rnd.random() < .6:
                c.path([(m + dx + 3, y - dy), (x2, y + rnd.uniform(-3, 3))], 1.6, GRIS if col == OR else OR, sm=False)
        for seg, col in ((A[:38], OR), (A[44:], GRIS), (B[:52], GRIS), (B[58:], OR)):
            c.path(seg, 2.4, col, sm=False)
        for (x, y, d) in ((8, 60, -1), (52, 96, 1), (10, 120, -1)):
            c.path([(x, y), (x + 6 * d, y + 8), (x - 2 * d, y + 16), (x + 4 * d, y + 22)], 1.5, GRIS)
    return c.out()


def sprig(w, h, flip=False):
    """Rameau floral horizontal (unités 100 x 40)."""
    c = Cv(w, h, 100, 40)
    stem = [(4, 22), (30, 18), (60, 22), (92, 16)]
    c.path(stem, 0.9, OR)
    sp = smooth(stem, n=10)
    for i in range(3, len(sp) - 2, 4):
        x, y = sp[i]
        x2, y2 = sp[i + 1]
        a = math.atan2(y2 - y, x2 - x)
        _leaf(c, x, y, a + (0.8 if (i // 4) % 2 else -0.8), 9, 2.6, OR, 0.8)
    _flower(c, 92, 16, 6, OR, 0.8)
    im = c.out()
    return im.transpose(Image.FLIP_LEFT_RIGHT) if flip else im


def corner(size):
    """Ornement d'angle discret (haut-gauche)."""
    c = Cv(size, size, 100)
    c.path([(4, 60), (4, 4), (60, 4)], 1.6, ORS, sm=False)
    c.path([(14, 44), (14, 14), (44, 14)], 1.0, ORS, sm=False)
    c.path([(14, 44), (20, 52), (28, 46), (22, 40)], 1.0, ORS)
    c.path([(44, 14), (52, 20), (46, 28), (40, 22)], 1.0, ORS)
    c.poly([(4, 70), (7, 74), (4, 78), (1, 74)], fill=ORS)
    c.poly([(70, 4), (74, 7), (78, 4), (74, 1)], fill=ORS)
    return c.out()
