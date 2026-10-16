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

# Foto en círculo a la derecha
size = 330
photo = Image.open(base / "assets/img/alberto-480.webp").convert("RGB").resize((size, size), Image.LANCZOS)
mask = Image.new("L", (size * 4, size * 4), 0)
ImageDraw.Draw(mask).ellipse((0, 0, size * 4 - 1, size * 4 - 1), fill=255)
mask = mask.resize((size, size), Image.LANCZOS)
px, py = W - size - 90, (H - size) // 2
d.ellipse((px - 8, py - 8, px + size + 8, py + size + 8), outline=ACC, width=3)
img.paste(photo, (px, py), mask)

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
