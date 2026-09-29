# Fixes aplicats de l'auditoria — 2026-09-29

Resum dels canvis aplicats i desplegats a producció arran de l'auditoria completa (vegeu `AUDITORIA-COMPLETA-2026-09-29.md`).

## P0
- **MIME dels .webp**: `AddType image/webp .webp` a `static/.htaccess`. Verificat: `content-type: image/webp`.
- **CLS**: mapa de dimensions `data/imatges_dim.json` (2.822 imatges) + `width`/`height` a `img.html` i `render-image.html`; `loading`/`decoding`. 78.509/93.079 imatges amb dimensions.
- **Lightbox per teclat**: `.prose img` focusable (`tabindex`/`role`/`aria-label`) i obertura amb Enter/Espai.
- **Contrastos AA**: colors de text de la tira, arxiu buit, pager, 404 i placeholder de cerca pujats a `--mid`/més opacitat.

## P1 — rendiment i a11y
- **srcset/sizes real**: `<source srcset="…-800.webp 800w, …-2500.webp 2500w" sizes=…>` amb descriptors `w`.
- **alt de reserva** des del `title` i **`aria-label="Veure l'àlbum complet"`** als enllaços que només contenien una imatge.
- **Objectius tàctils** 44×44 (hamburguesa, lupa, socials, pager) i **tipografia mòbil** de 0,45–0,58 rem a 0,7–0,82 rem.

## P1 — seguretat i CI
- **CSP global sense `'unsafe-inline'`**: la init de Pagefind passa a `assets/js/cerca.js` i `/stats/` té CSP propi.
- **CI**: `actions/checkout` i `peaceiris/actions-gh-pages` fixades per SHA, checksum SHA256 del tarball de Hugo, `pagefind@1.5.2`, `permissions: contents: read` on calia, i `known_hosts` fix (secret `DINAHOSTING_KNOWN_HOSTS`) amb `StrictHostKeyChecking=yes`.

## P2 — accessibilitat/responsive
- Skip link amb `main tabindex="-1"`; `aria-current="page"` a la nav; label del menú mòbil que canvia; SRI a la 404; `role="list"` a l'arxiu; `prefers-reduced-motion` al JS.
- HSTS `includeSubDomains; preload`; capçaleres `Cross-Origin-Opener-Policy: same-origin` i `Cross-Origin-Resource-Policy: same-site`.
- Mòbil: `.post-card` apilat i padding reduït a ≤480 px, logo a ≤380 px, `overflow-wrap` i `pre` amb scroll.
- Contingut: 2 `h1` del cos passats a `h2` i 4 encapçalaments buits eliminats; `aria-current` i h1 únic.

## Pendent (decisions de l'usuari)
- **`/stats/analytics.json` públic** (200): protegir amb auth si no es vol exposar.
- Extendre el mapa de dimensions als continguts amb imatge no mapejada (avui 84%).
- Normalitzar enllaços `http://` del llegat (168) a `https://`.
- 27 grups de descripcions duplicades i 2 posts amb títol duplicat (editorial).
- `og:image:width/height` i `twitter:site`/`creator`.
- `/.well-known/security.txt`; a11y interna de `/admin/` i `/stats/`.

## Verificació
Cada bloc s'ha verificat en un build net i, després del desplegament, amb comprovacions de només lectura a producció (capçaleres HTTP, HTML servit, mida de recursos).
