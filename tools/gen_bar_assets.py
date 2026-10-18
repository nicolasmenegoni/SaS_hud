#!/usr/bin/env python3
"""Gera os assets do HUD (barras 9x9 + fontes de digito/espaco) para o plugin SaS_hud."""
from PIL import Image, ImageDraw
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TEX = os.path.join(ROOT, "src", "main", "resources", "assets", "textures", "gui", "hud")
FONT = os.path.join(ROOT, "src", "main", "resources", "assets", "sas_hud", "font")
MODEL = os.path.join(ROOT, "src", "main", "resources", "assets", "minecraft", "models", "item")
os.makedirs(TEX, exist_ok=True)
os.makedirs(FONT, exist_ok=True)
os.makedirs(MODEL, exist_ok=True)

def save(img, path):
    img.save(path)
    print("gerado:", os.path.relpath(path, ROOT))

# ---------------------------------------------------------------- cores ----
OUT_D  = (12, 8, 14, 255)     # contorno escuro embaixo
OUT_U  = (30, 22, 36, 255)    # contorno escuro em cima
TRACK  = (74, 62, 84, 255)    # trilho vazio
FILL   = (122, 102, 138, 255) # trilho cheio (tom roxo-acinzentado neutro)
GREEN  = (90, 210, 80, 255)   # xp
CYAN   = (70, 200, 210)    # agua
GOLD   = (250, 215, 80)    # dinheiro
RED    = (225, 70, 60)     # vida
PURPLE = (175, 95, 220)   # elite

def track_base(fill=False):
    """Trilho: cantos arredondados, miolo 1px vertical uniforme -> tileia 9x9."""
    img = Image.new("RGBA", (9, 9), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    body = FILL if fill else TRACK
    d.rectangle([0, 1, 8, 7], fill=body)              # corpo (sem cantos)
    d.line([1, 0, 7, 0], fill=OUT_U)                  # borda superior
    d.line([1, 8, 7, 8], fill=OUT_D)                  # borda inferior
    d.line([(0, 1), (0, 7)], fill=body)               # laterais
    d.line([(8, 1), (8, 7)], fill=body)
    # cantos chanfrados (pixel art arredondada)
    for x, y in ((0, 0), (8, 0), (0, 8), (8, 8)):
        pass
    return img

def overlay_groove(img):
    """Sombra interna na linha do meio: faz a barra parecer embutida."""
    d = ImageDraw.Draw(img)
    sh = tuple(max(0, int(c * 0.62)) for c in img.getpixel((4, 4))[:3]) + (255,)
    hi = tuple(min(255, int(c * 1.18) + 14) for c in img.getpixel((4, 2))[:3]) + (255,)
    d.line([1, 4, 7, 4], fill=sh)                     # sulco central
    d.line([1, 3, 7, 3], fill=hi)                     # brilho acima do sulco
    return img

def bar_pair(name, color=None):
    """Gera <name>_empty.png e <name>_full.png (9x9)."""
    empty = track_base(fill=False)
    full = track_base(fill=True)
    if color is not None:
        # recolorir o corpo do cheio
        px = full.load()
        for y in range(9):
            for x in range(9):
                r, g, b, a = px[x, y]
                if a == 255 and (r, g, b) == FILL[:3]:
                    px[x, y] = color + (255,)
    overlay_groove(empty)
    overlay_groove(full)
    save(empty, os.path.join(TEX, name + "_empty.png"))
    save(full, os.path.join(TEX, name + "_full.png"))

bar_pair("xp_bar")          # xp usa a cor vanilla (textura própria do jogo)
bar_pair("water_bar", CYAN)
bar_pair("money_bar", GOLD)
bar_pair("health_bar", RED)
bar_pair("elite_bar", PURPLE)

# ------------------------------------------------------- fonte de dígitos --
# Cada glifo ocupa 8px de largura; o desenho tem ~5px + 3px de entre-dígitos.
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

def glyph_image(rows):
    img = Image.new("RGBA", (8, 7), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch == "1":
                d.point((x, y), fill=(255, 255, 255, 255))
    return img

for digit, rows in DIGITS.items():
    save(glyph_image(rows), os.path.join(TEX, f"digit_{digit}.png"))

# espaço: imagem 1x1 totalmente transparente
blank = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
save(blank, os.path.join(TEX, "blank.png"))

print("concluido")
