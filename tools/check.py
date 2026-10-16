#!/usr/bin/env python3
"""Comprobaciones de la web antes de publicar (las corre también el CI):
- Nada de código en línea que la CSP estricta bloquearía (scripts, <style>, style=, on*=).
- Nada de sumideros de Trusted Types en el JS (innerHTML, eval...).
- Todas las rutas locales existen.
- Las dos versiones (es/en) tienen las mismas secciones, para cambiar de idioma sin perderse.
- security.txt sigue vigente y caduca en menos de un año (RFC 9116).
"""
import re, sys
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent / "site"
errors = []

class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.path, self.ids, self.sections, self.refs = path, set(), [], []
        self._script_inline = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        where = f"{self.path.relative_to(SITE)}:{self.getpos()[0]}"
        if "id" in a:
            if a["id"] in self.ids:
                errors.append(f"{where}: id repetido '{a['id']}'")
            self.ids.add(a["id"])
        if tag == "section" and "id" in a:
            self.sections.append(a["id"])
        if "style" in a:
            errors.append(f"{where}: atributo style= (lo bloquea la CSP)")
        for k in a:
            if k.startswith("on"):
                errors.append(f"{where}: manejador en línea {k}=")
        if tag == "style":
            errors.append(f"{where}: bloque <style> en línea")
        if tag == "script":
            if "src" in a:
                self.refs.append((where, a["src"]))
            elif a.get("type") != "application/ld+json":
                errors.append(f"{where}: <script> en línea")
        for attr in ("src", "href"):
            if tag != "script" and attr in a:
                self.refs.append((where, a[attr]))
        if "srcset" in a:
            for part in a["srcset"].split(","):
                self.refs.append((where, part.split()[0]))

def local_target(page: Path, ref: str):
    if re.match(r"^(https?:|mailto:|#|data:)", ref) or ref == "":
        return None
    ref = ref.split("#")[0]
    target = (SITE / ref.lstrip("/")) if ref.startswith("/") else (page.parent / ref)
    if ref.endswith("/") or target.is_dir():
        target = target / "index.html"
    return target

pages = {}
for page in sorted(SITE.rglob("*.html")):
    p = Page(page)
    p.feed(page.read_text(encoding="utf-8"))
    pages[page] = p
    for where, ref in p.refs:
        t = local_target(page, ref)
        if t is not None and not t.exists():
            errors.append(f"{where}: no existe {ref}")
        if ref.startswith("#") and len(ref) > 1 and ref[1:] not in p.ids:
            errors.append(f"{where}: ancla rota {ref}")

es, en = pages.get(SITE / "index.html"), pages.get(SITE / "en/index.html")
if es and en and es.sections != en.sections:
    errors.append(f"secciones distintas: es={es.sections} en={en.sections}")

for js in SITE.rglob("*.js"):
    code = re.sub(r"/\*.*?\*/", "", js.read_text(encoding="utf-8"), flags=re.S)
    for sink in ("innerHTML", "outerHTML", "insertAdjacentHTML", "document.write", "eval(", "new Function"):
        if sink in code:
            errors.append(f"{js.relative_to(SITE)}: usa {sink} (sumidero de Trusted Types)")

sec = SITE / ".well-known/security.txt"
m = re.search(r"^Expires:\s*(\S+)", sec.read_text(encoding="utf-8"), re.M)
if not m:
    errors.append("security.txt sin Expires")
else:
    days = (datetime.fromisoformat(m.group(1).replace("Z", "+00:00")) - datetime.now(timezone.utc)).days
    if not 0 < days <= 366:
        errors.append(f"security.txt: Expires a {days} días (debe ser futuro y < 1 año)")

for e in errors:
    print("ERROR", e)
print(f"{len(pages)} páginas revisadas, {len(errors)} errores")
sys.exit(1 if errors else 0)
