#!/usr/bin/env python3
"""Gera o resource pack do HUD (barra estilo ===0=== com texturas 9x9 tileadas)."""
from PIL import Image, ImageDraw
import json, os, shutil, zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RES = os.path.join(ROOT, "src", "main", "resources")
TEXDIR = os.path.join(RES, "assets", "hud", "textures", "gui")
FONTDIR = os.path.join(RES, "assets", "hud", "font")
MODELDIR = os.path.join(RES, "assets", "minecraft", "models", "item")
for d in (TEXDIR, FONTDIR, MODELDIR):
    os.makedirs(d, exist_ok=True)

# ------------------------------------------------------------- paleta ------
OUT_TOP   = (26, 18, 32)     # contorno superior (claro)
OUT_BOT   = (10, 7, 14)      # contorno inferior (escuro)
TRACK     = (58, 48, 68)     # trilho vazio
HILITE    = (92, 78, 104)    # linha de brilho do trilho
SULCO     = (40, 32, 48)     # sulco central
GREEN     = (112, 226, 96)   # corpo da barra cheia (verde xp)
GREEN_HI  = (176, 255, 140)  # brilho
GREEN_LO  = (58, 150, 52)    # sombra

def new9():
    return Image.new("RGBA", (9, 9), (0, 0, 0, 0))

def px(img, x, y, rgb):
    img.putpixel((x, y), rgb + (255,))

# ---------------------------------------------- cantos e centro 9x9 -------
def corner(kind):
    """kind: tl/tr/bl/br — borda arredondada em diagonal."""
    c = new9()
    if kind == "tl":
        px(c, 3, 0, OUT_TOP); px(c, 2, 0, OUT_TOP); px(c, 1, 1, OUT_TOP)
        px(c, 0, 3, OUT_TOP); px(c, 0, 2, OUT_TOP)
        for x, y in ((4, 1), (3, 2), (2, 3)): px(c, x, y, TRACK)
        for x, y in ((1, 4), (2, 4)): px(c, x, y, TRACK)
        px(c, 4, 2, HILITE)
    elif kind == "tr":
        px(c, 5, 0, OUT_TOP); px(c, 6, 0, OUT_TOP); px(c, 7, 1, OUT_TOP)
        px(c, 8, 3, OUT_TOP); px(c, 8, 2, OUT_TOP)
        for x, y in ((4, 1), (5, 2), (6, 3)): px(c, x, y, TRACK)
        for x, y in ((7, 4), (6, 4)): px(c, x, y, TRACK)
        px(c, 4, 2, HILITE)
    elif kind == "bl":
        px(c, 3, 8, OUT_BOT); px(c, 2, 8, OUT_BOT); px(c, 1, 7, OUT_BOT)
        px(c, 0, 5, OUT_BOT); px(c, 0, 6, OUT_BOT)
        for x, y in ((4, 7), (3, 6), (2, 5)): px(c, x, y, TRACK)
        for x, y in ((1, 4), (2, 4)): px(c, x, y, TRACK)
        px(c, 4, 6, SULCO)
    else:  # br
        px(c, 5, 8, OUT_BOT); px(c, 6, 8, OUT_BOT); px(c, 7, 7, OUT_BOT)
        px(c, 8, 5, OUT_BOT); px(c, 8, 6, OUT_BOT)
        for x, y in ((4, 7), (5, 6), (6, 5)): px(c, x, y, TRACK)
        for x, y in ((7, 4), (6, 4)): px(c, x, y, TRACK)
        px(c, 4, 6, SULCO)
    return c

def center_track():
    c = new9()
    d = ImageDraw.Draw(c)
    d.rectangle([0, 0, 8, 8], fill=TRACK)
    d.line([0, 0, 8, 0], fill=OUT_TOP)       # borda superior continua
    d.line([0, 8, 8, 8], fill=OUT_BOT)       # borda inferior continua
    d.line([0, 2, 8, 2], fill=HILITE)        # brilho
    d.line([0, 4, 8, 4], fill=SULCO)         # sulco central
    return c

def edge_fill(side):
    """Camada cheia (verde) que cobre sozinha a borda arredondada."""
    c = new9()
    if side == "left":
        px(c, 3, 0, GREEN_LO); px(c, 2, 0, GREEN_LO); px(c, 1, 1, GREEN_LO)
        px(c, 0, 3, GREEN); px(c, 0, 2, GREEN)
        for x, y in ((4, 1), (3, 2), (2, 3), (1, 4), (2, 4)): px(c, x, y, GREEN)
        px(c, 4, 2, GREEN_HI)
    else:
        px(c, 5, 0, GREEN_LO); px(c, 6, 0, GREEN_LO); px(c, 7, 1, GREEN_LO)
        px(c, 8, 3, GREEN); px(c, 8, 2, GREEN)
        for x, y in ((4, 1), (5, 2), (6, 3), (7, 4), (6, 4)): px(c, x, y, GREEN)
        px(c, 4, 2, GREEN_HI)
    return c

def center_fill():
    c = new9()
    d = ImageDraw.Draw(c)
    d.rectangle([0, 0, 8, 8], fill=GREEN)
    d.line([0, 0, 8, 0], fill=GREEN_LO)      # sombra superior
    d.line([0, 8, 8, 8], fill=GREEN_LO)      # sombra inferior
    d.line([0, 2, 8, 2], fill=GREEN_HI)      # brilho especular
    d.line([0, 4, 8, 4], fill=(84, 190, 74)) # nervura central
    return c

def mid_strip(name):
    """Tira horizontal 9x9 que repete (tile) — une um pedaço no outro."""
    s = new9()
    d = ImageDraw.Draw(s)
    if name == "track":
        d.rectangle([0, 1, 8, 7], fill=TRACK)
        d.line([0, 0, 8, 0], fill=OUT_TOP)
        d.line([0, 8, 8, 8], fill=OUT_BOT)
        d.line([0, 2, 8, 2], fill=HILITE)
        d.line([0, 4, 8, 4], fill=SULCO)
    else:
        d.rectangle([0, 1, 8, 7], fill=GREEN)
        d.line([0, 0, 8, 0], fill=GREEN_LO)
        d.line([0, 8, 8, 8], fill=GREEN_LO)
        d.line([0, 2, 8, 2], fill=GREEN_HI)
        d.line([0, 4, 8, 4], fill=(84, 190, 74))
    return s

def save(img, path):
    img.save(path)

def layer(name, left, right, middle):
    """Camada full:<name>: <esq><meio*25><dir>, altura 9px."""
    w = 9 * (2 + 25)
    img = Image.new("RGBA", (w, 9), (0, 0, 0, 0))
    img.alpha_composite(left, (0, 0))
    for i in range(25):
        img.alpha_composite(middle, (9 * (1 + i), 0))
    img.alpha_composite(right, (9 * 26, 0))
    save(img, os.path.join(TEXDIR, name + ".png"))
    return w

W_LAYER = layer("xp_track", corner("tl"), corner("tr"), mid_strip("track"))
layer("xp_fill", edge_fill("left"), edge_fill("right"), mid_strip("fill"))
layer("xp_cap_l", corner("tl"), edge_fill("left"), None) if False else None
# tampas das extremidades da camada cheia (desenhadas por cima do trilho)
capL = new9(); capR = new9()
ImageDraw.Draw(capL).rectangle([0, 0, 8, 8], fill=(0, 0, 0, 0))
save(edge_fill("left"), os.path.join(TEXDIR, "xp_cap_left.png"))
save(edge_fill("right"), os.path.join(TEXDIR, "xp_cap_right.png"))

# ------------------------------------------------------------ dígitos -----
DIGITS = {
    "0": ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    "1": ["01100", "00100", "00100", "00100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00001", "00010", "00100", "01000", "11111"],
    "3": ["11110", "00001", "00001", "01110", "00001", "00001", "11110"],
    "4": ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    "5": ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    "6": ["00110", "01000", "10000", "11110", "10001", "10001", "01110"],
    "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    "9": ["01110", "10001", "10001", "01111", "00001", "00010", "01100"],
}
for digit, rows in DIGITS.items():
    g = Image.new("RGBA", (8, 7), (0, 0, 0, 0))
    d = ImageDraw.Draw(g)
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch == "1":
                d.point((x, y), fill=(255, 255, 255, 255))
    save(g, os.path.join(TEXDIR, f"digit_{digit}.png"))

blank = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
save(blank, os.path.join(TEXDIR, "blank.png"))

# ------------------------------------------------------------ fontes ------
def provider(file, chars):
    return {"type": "bitmap", "file": f"hud:textures/gui/{file}", "ascent": 8, "chars": chars}

def write_font(name, providers):
    path = os.path.join(FONTDIR, name + ".json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"providers": providers}, f, ensure_ascii=False)
        f.write("\n")

write_font("xp_bar", [
    provider("xp_track.png", "\ue000"),
    provider("xp_fill.png", "\ue001"),
])
# fonte pública para textos customizados (chat/actionbar)
write_font("digits", [
    provider("blank.png", " "),
    *[provider(f"digit_{d}.png", str(d)) for d in "0123456789"],
])

# --------------------------------------------- modelos de item (itens) ----
def item_model(id_, texture, gui_light=False):
    m = {
        "parent": "minecraft:item/generated",
        "textures": {"layer0": f"hud:textures/gui/{texture}"},
    }
    if gui_light:
        m["gui_light"] = "front"
    p = os.path.join(MODELDIR, id_ + ".json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(m, f, indent=2)
        f.write("\n")

item_model("xp_track", "xp_track.png", True)
item_model("xp_fill", "xp_fill.png", True)
item_model("xp_cap_left", "xp_cap_left.png", True)
item_model("xp_cap_right", "xp_cap_right.png", True)
for d in "0123456789":
    item_model(f"digit_{d}", f"digit_{d}.png", True)

print("recursos gerados em", os.path.relpath(TEXDIR, ROOT))
