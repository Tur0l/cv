# cv.turolol.win

Mi CV como web: **https://cv.turolol.win** (en inglés en [/en/](https://cv.turolol.win/en/)).

*My CV as a website, in Spanish and English. Static, no third-party resources, strict CSP.*

Pantallas que encajan al hacer scroll o deslizar en el móvil, y dos demos interactivas:

- **Sigue una petición**: eliges quién llama (usuario legítimo, escáner extranjero, bot de fuerza bruta, VPS comprometido…) y ves qué capa de mi homelab lo para.
- **Failover del TFC**: tumba un nodo del clúster Proxmox VE y mira cómo la VM vuelve en otro, con el tiempo real medido (140 s).

## Cómo está hecha

- **HTML, CSS y JavaScript a mano**, sin frameworks ni dependencias. Las fuentes (IBM Plex) van alojadas aquí.
- **Nada en línea**: ni `<script>` ni `<style>` ni `style=`. Por eso la CSP puede ser `default-src 'none'` con todo en `'self'`, más **Trusted Types** obligatorios (el JS no usa `innerHTML` ni similares).
- **Cabeceras** en [`site/_headers`](site/_headers): CSP, HSTS, `nosniff`, `frame-ancestors 'none'`, Permissions-Policy cerrada, COOP/CORP.
- **Sin cookies, sin rastreadores, sin peticiones a terceros.** La foto va sin metadatos y el email se monta con JavaScript para que no lo recojan los bots.
- **Accesible**: funciona sin JavaScript, respeta `prefers-reduced-motion`, se maneja con teclado y tiene modo oscuro automático.
- [`/.well-known/security.txt`](site/.well-known/security.txt) según RFC 9116.

## Estructura

```
site/            la web tal cual se publica (salida de Cloudflare Pages, sin build)
  index.html     español
  en/index.html  inglés (mismos id de sección: el selector de idioma te deja donde estabas)
  _headers       cabeceras de seguridad
tools/check.py   comprobaciones que corre el CI: nada en línea, enlaces, secciones, security.txt
tools/qr.py      genera y verifica el QR de las tarjetas (qr/)
tools/og-image.py  imagen para la vista previa al compartir el enlace
```

## Desarrollo

```sh
python3 -m http.server -d site 8000   # http://localhost:8000
python3 tools/check.py                # antes de cada push
```

Cada push a `main` lo publica Cloudflare Pages. El `Expires` de `security.txt` caduca el 15-oct-2027: renovarlo antes (el CI falla si caduca o pasa de un año).

## Licencia

El código es MIT ([LICENSE](LICENSE)). El contenido del CV y la foto son míos y no se pueden reutilizar. Las fuentes IBM Plex van bajo [SIL OFL 1.1](site/assets/fonts/OFL.txt).
