#!/usr/bin/env python3
"""QR de las tarjetas: puntos redondos, ojos redondeados y el logo ">_" en el centro.
Saca SVG (imprenta) y PNG de 2048 px por variante de color, y comprueba que se leen
bien con zxing a tamaño real, en pequeño y desenfocado antes de darlos por buenos."""
import sys
from pathlib import Path
import segno
import zxingcpp
from PIL import Image, ImageDraw, ImageFilter

URL = "https://cv.turolol.win"
OUT = Path(__file__).resolve().parent.parent / "qr"
VARIANTS = {"qr-cv-turquesa": "#0e6b7d", "qr-cv-negro": "#000000"}
BORDER = 4      # zona de silencio obligatoria, en módulos
DOT = 0.46      # radio de cada punto (0.5 = toca al vecino)
LOGO = 7        # hueco central, en módulos (impar)

qr = segno.make(URL, error="h", micro=False, boost_error=False)
m = [list(row) for row in qr.matrix]
n = len(m)
ALIGN = {2: 18, 3: 22, 4: 26, 5: 30, 6: 34}  # centro del patrón de alineación (v2-v6)

def in_box(r, c, top, left, size):
    return top <= r < top + size and left <= c < left + size

finders = [(0, 0), (0, n - 7), (n - 7, 0)]
align = ALIGN.get(qr.version)
lo = (n - LOGO) // 2

def special(r, c):
    if any(in_box(r, c, t, l, 7) for t, l in finders):
        return True
    if align and in_box(r, c, align - 2, align - 2, 5):
        return True
    return in_box(r, c, lo, lo, LOGO)

def shapes():
    """Formas en unidades de módulo, con la zona de silencio ya sumada."""
    o = BORDER
    for r in range(n):
        for c in range(n):
            if m[r][c] and not special(r, c):
                yield ("dot", c + o + .5, r + o + .5, DOT)
    for t, l in finders:
        x, y = l + o, t + o
        yield ("rrect", x, y, 7, 7, 2.0, "fg")
        yield ("rrect", x + 1, y + 1, 5, 5, 1.4, "bg")
        yield ("rrect", x + 2, y + 2, 3, 3, 0.9, "fg")
    if align:
        x = y = align - 2 + o
        yield ("rrect", x, y, 5, 5, 1.5, "fg")
        yield ("rrect", x + 1, y + 1, 3, 3, 0.9, "bg")
        yield ("dot", x + 2.5, y + 2.5, 0.5)
    # Logo: cuadrado redondeado con ">_" en blanco, con medio módulo de aire alrededor
    x = y = lo + o + .5
    s = LOGO - 1
    yield ("rrect", x, y, s, s, 1.4, "fg")
    yield ("glyph", x, y, s)

def glyph_lines(x, y, s):
    # Mismo trazo que el favicon: chevron + subrayado (coordenadas sobre 32x32)
    k = s / 32
    p = lambda a, b: (x + a * k, y + b * k)
    return [p(9, 10), p(15, 16), p(9, 22)], [p(17.5, 22.5), p(24.5, 22.5)], 3.2 * k

def svg(color):
    W = n + 2 * BORDER
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {W}" width="{W * 10}" height="{W * 10}">',
           f'<title>QR a {URL}</title><rect width="{W}" height="{W}" fill="#ffffff"/>', f'<g fill="{color}">']
    for sh in shapes():
        if sh[0] == "dot":
            out.append(f'<circle cx="{sh[1]:g}" cy="{sh[2]:g}" r="{sh[3]:g}"/>')
        elif sh[0] == "rrect":
            _, x, y, w, h, rad, fill = sh
            f = "" if fill == "fg" else ' fill="#ffffff"'
            out.append(f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="{rad:g}"{f}/>')
        elif sh[0] == "glyph":
            chev, under, sw = glyph_lines(*sh[1:])
            d = "M" + " L".join(f"{a:.3f} {b:.3f}" for a, b in chev) + " M" + " L".join(f"{a:.3f} {b:.3f}" for a, b in under)
            out.append(f'<path d="{d}" fill="none" stroke="#ffffff" stroke-width="{sw:.3f}" stroke-linecap="round" stroke-linejoin="round"/>')
    out.append("</g></svg>")
    return "\n".join(out)

def png(color, size=2048, ss=3):
    W = n + 2 * BORDER
    S = size * ss
    u = S / W
    mask = Image.new("L", (S, S), 0)
    d = ImageDraw.Draw(mask)
    for sh in shapes():
        if sh[0] == "dot":
            _, cx, cy, r = sh
            d.ellipse(((cx - r) * u, (cy - r) * u, (cx + r) * u, (cy + r) * u), fill=255)
        elif sh[0] == "rrect":
            _, x, y, w, h, rad, fill = sh
            d.rounded_rectangle((x * u, y * u, (x + w) * u, (y + h) * u), radius=rad * u, fill=255 if fill == "fg" else 0)
        elif sh[0] == "glyph":
            chev, under, sw = glyph_lines(*sh[1:])
            for line in (chev, under):
                pts = [(a * u, b * u) for a, b in line]
                d.line(pts, fill=0, width=round(sw * u), joint="curve")
                for px, py in (pts[0], pts[-1]):
                    rr = sw * u / 2
                    d.ellipse((px - rr, py - rr, px + rr, py + rr), fill=0)
    mask = mask.resize((size, size), Image.LANCZOS)
    img = Image.new("RGB", (size, size), "#ffffff")
    img.paste(Image.new("RGB", (size, size), color), (0, 0), mask)
    return img

def verify(img, label):
    tests = {
        "2048 px": img,
        "160 px (tarjeta pequeña)": img.resize((160, 160), Image.LANCZOS),
        "desenfocada": img.resize((400, 400), Image.LANCZOS).filter(ImageFilter.GaussianBlur(2)),
    }
    ok = True
    for name, im in tests.items():
        got = [b.text for b in zxingcpp.read_barcodes(im)]
        good = got == [URL]
        ok &= good
        print(f"  {label} · {name}: {'OK' if good else 'FALLA ' + repr(got)}")
    return ok

OUT.mkdir(exist_ok=True)
print(f"{URL} → versión {qr.version} ({n}×{n} módulos), corrección {qr.error}")
all_ok = True
for name, color in VARIANTS.items():
    (OUT / f"{name}.svg").write_text(svg(color), encoding="utf-8")
    img = png(color)
    img.save(OUT / f"{name}.png", optimize=True)
    all_ok &= verify(img, name)
sys.exit(0 if all_ok else 1)
