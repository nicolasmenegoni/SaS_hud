from PIL import Image
import os
TEX = "/workspace/src/main/resources/assets/textures/gui/hud"

def tile(name, width_tiles):
    img = Image.open(os.path.join(TEX, name)).convert("RGBA")
    out = Image.new("RGBA", (9*width_tiles, 9), (40, 40, 46, 255))
    for i in range(width_tiles):
        out.alpha_composite(img, (i*9, 0))
    return out

# barra: empty de fundo + full por cima (parcial) -> simula xp 35%
def composite(empty_name, full_name, tiles_total, tiles_full):
    base = tile(empty_name, tiles_total)
    fill = tile(full_name, tiles_full)
    base.alpha_composite(fill, (0, 0))
    return base

sheet = Image.new("RGBA", (9*22+20, 9*8+40), (24, 24, 28, 255))
y = 10
for label, e, f, tf in [
    ("xp 0%", "xp_bar_empty.png", "xp_bar_full.png", 0),
    ("xp 35%", "xp_bar_empty.png", "xp_bar_full.png", 7),
    ("xp 100%", "xp_bar_empty.png", "xp_bar_full.png", 20),
    ("water 50%", "water_bar_empty.png", "water_bar_full.png", 10),
    ("money 75%", "money_bar_empty.png", "money_bar_full.png", 15),
]:
    sheet.alpha_composite(composite(e, f, 20, tf), (10, y)); y += 14

# digitos brancos em linha
x = 10
for dch in "0123456789":
    g = Image.open(os.path.join(TEX, f"digit_{dch}.png")).convert("RGBA")
    px = g.load()
    for yy in range(g.height):
        for xx in range(g.width):
            r, gg, b, a = px[xx, yy]
            if a: px[xx, yy] = (255, 220, 90, 255)  # cor de teste (dourado)
    sheet.alpha_composite(g, (x, y)); x += 8
sheet.save("/tmp/preview_bars.png")
print("ok /tmp/preview_bars.png")

# ASCII art da textura para inspecao textual
im = Image.open(os.path.join(TEX, "xp_bar_full.png")).convert("RGBA")
chars = {}
for py in range(9):
    row = ""
    for px_ in range(9):
        c = im.getpixel((px_, py))
        key = c[:3] if c[3] else None
        if key is None: ch = "."
        else:
            lum = sum(key)/3
            ch = "#" if lum > 110 else ("+" if lum > 70 else ("o" if lum > 40 else "-"))
        row += ch
    print(row)
