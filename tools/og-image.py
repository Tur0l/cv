#!/usr/bin/env python3
"""Genera site/assets/img/og.png (1200x630), la imagen que sale al compartir el enlace."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

base = Path(__file__).resolve().parent.parent / "site"
fonts = base / "assets/fonts"
W, H = 1200, 630
BG, INK, DIM, ACC = (11, 26, 32), (228, 238, 241), (142, 163, 169), (94, 196, 213)

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)
sans = lambda w, s: ImageFont.truetype(str(fonts / f"ibm-plex-sans-latin-{w}-normal.woff2"), s)
mono = lambda w, s: ImageFont.truetype(str(fonts / f"ibm-plex-mono-latin-{w}-normal.woff2"), s)

# El logo ">_" del favicon a la derecha (sin foto, por privacidad). Se dibuja a 4x y se reduce
# para que los bordes salgan suaves.
size, k = 300, 4
px, py = W - size - 100, (H - size) // 2
logo = Image.new("RGBA", (size * k, size * k), (0, 0, 0, 0))
ld = ImageDraw.Draw(logo)
u = size * k / 32                       # unidades del viewBox 32x32 del favicon
ld.rounded_rectangle((0, 0, size * k - 1, size * k - 1), radius=7 * u, fill=(14, 107, 125))
def stroke(points):
    pts = [(a * u, b * u) for a, b in points]
    ld.line(pts, fill="white", width=round(3 * u), joint="curve")
    for x0, y0 in pts:                  # extremos redondeados, como stroke-linecap="round"
        r = 1.5 * u
        ld.ellipse((x0 - r, y0 - r, x0 + r, y0 + r), fill="white")
stroke([(8, 10.5), (14, 16), (8, 21.5)])
stroke([(16.5, 22), (24, 22)])
logo = logo.resize((size, size), Image.LANCZOS)
d.rounded_rectangle((px - 10, py - 10, px + size + 10, py + size + 10), radius=7 * size / 32 + 10, outline=ACC, width=3)
img.paste(logo, (px, py), logo)

x = 84
d.text((x, 118), "CURRICULUM VITAE · 2026", font=mono(600, 22), fill=ACC)
d.text((x, 166), "Alberto Arturo", font=sans(700, 68), fill=INK)
d.text((x, 244), "Morales García", font=sans(700, 68), fill=INK)
d.text((x, 350), "ASIR · Ciberseguridad (CETI)", font=mono(600, 28), fill=ACC)
d.text((x, 398), "Sistemas · Redes · Bastionado", font=sans(400, 28), fill=DIM)
d.text((x, 436), "Respuesta a incidentes", font=sans(400, 28), fill=DIM)
d.text((x, 530), "$ cv.turolol.win", font=mono(400, 24), fill=INK)

out = base / "assets/img/og.png"
img.save(out, optimize=True)
print(out, out.stat().st_size // 1024, "KB")
