# Auditoria completa — blog.pocallum.cat

**Data:** 2026-09-29 · **Abast:** seguretat, SEO+IA, responsive i accessibilitat · **Producció:** https://blog.pocallum.cat (Dinahosting)

**Mètode:** build net (Hugo v0.166, ~8.885 pàgines / 6.736 HTML reals + 3.343 àlies), anàlisi estàtica de plantilles/CSS/HTML, comprovacions HTTP de només lectura a producció, càlcul de contrast WCAG i revisió del repo i dels workflows. Cap escriptura a producció.

> Nota: l'auditoria s'ha fet després de desplegar les correccions SEO/IA, els textos legals i la generació WebP del llegat. Les troballes reflecteixen l'estat actual.

---

## Resum executiu

| Prioritat | Àrea | Trobada |
|---|---|---|
| P0 | Web/Infra | Els `.webp` es serveixen **sense `Content-Type`** (els `.jpg` sí en tenen) → risc de no renderitzar amb `nosniff` |
| P0 | Rendiment | **Cap imatge té `width`/`height` ni `aspect-ratio`** → CLS a tot el lloc (93.082 `img`) |
| P0 | A11y | El **lightbox no s'obre amb teclat** (2.1.1) |
| P0 | A11y | **Contrastos insuficients** (1.4.3): dates de tira 1,11:1, anys d'arxiu buits 1,11:1, tile sense imatge 2,60:1, separador pager 1,18:1 |
| P1 | A11y | **2.369 imatges amb `alt=""`**; 2.085 dins d'enllaços sense nom accessible (1.1.1/2.4.4/4.1.2) |
| P1 | Rendiment | Sense `srcset`/`sizes` resolutiu (85.102 `source` amb 1 sol candidat); fons hero/contact no adaptatius |
| P1 | Seguretat | CSP amb `script-src 'unsafe-inline'` + Goldmark `unsafe=true` (XSS) |
| P1 | Seguretat | CI: accions `@v4` (no SHA), `npx pagefind` sense versió, Hugo sense checksum, workflows sense `permissions`, SSH `accept-new`/`no` |
| P2 | Responsive | Objectius tàctils <44 px (hamburguesa ~28×21, lupa, socials, pager) |
| P2 | Responsive | Tipografia a mòbil de 0,45–0,58 rem (7–9 px) |
| P2 | A11y | 2 pàgines amb 2 `h1`, 4 `h2` buits, 8 salts de nivell; llistes sense `role="list"` a Safari |
| P2 | A11y | Skip link sense `tabindex="-1"` al destí; `aria-current` absent a la nav |
| P3 | Seguretat | `/stats/analytics.json` públic; HSTS sense `preload`; 404 amb GoatCounter sense SRI; 94 imatges + 168 enllaços `http://`; falten COOP/CORP; redirecció de barra final via `http://` |
| P3 | A11y | Menú mòbil depèn de JS i l'`aria-label` no canvia; animacions JS ignoren `prefers-reduced-motion`; `/admin/` i `/stats/` sense `h1`/`main` |
| P3 | Responsive | Desbordament de text/codi; `.post-card` no s'apila a 320 px; logo `nowrap` amb nav `padding` fix |

---

## 1. SEGURETAT

### Què ja està bé
- **TLS 1.3** (AEAD-AES256-GCM-SHA384) i HTTP/2; certificat Let's Encrypt vàlid 23/09→22/12/2026 amb SAN `blog.pocallum.cat`. TLS 1.0/1.1 **rebutjats**.
- **HTTP→HTTPS** operatiu amb `Cache-Control: no-store` (evita el bucle de Varnish).
- **Rutes sensibles bloquejades:** `/.git/config`, `/.env`, `/.htaccess`, `wp-config.php`, `*.sql`, `*.bak` → 403; `/wp-admin/`, `/wp-login.php`, `/xmlrpc.php`, `/migration/`, `/public/` → 404. Sense llistat de directoris. Sense PHP a `static/`.
- **Cap secret comitejat**; `public/`, `public-review/` i `migration/` gitignored.
- **SRI verificat** a GoatCounter i giscus (hashes `sha384` coincideixen amb els scripts reals) i `crossorigin="anonymous"`.
- **CSP amb** `object-src 'none'`, `base-uri 'self'`, `form-action 'self'`, `frame-ancestors 'none'`, `worker-src 'self'`, `upgrade-insecure-requests`.
- **/admin/ amb CSP propi** que no afluixa el global; `noindex, nofollow` a admin i stats.
- **Dependències:** Chart.js 4.4.0 i Sveltia CMS 0.217.0, sense advisories vigents.

### Trobades
1. **CSP `script-src 'unsafe-inline'`** (Mitjana). Evidència: `static/.htaccess` (CSP) + `hugo.toml` `unsafe = true`. Únic script inline executable: init de PagefindUI a `cerca.html` (els JSON-LD no són executables). Recomanació: hashes sha256 dels scripts inline (o moure'ls a fitxers), CSP propi a `/stats/`, mantenir `unsafe=false` i endurir `img-src`.
2. **Supply chain CI** (Mitjana): accions `@v4`, `npx pagefind` sense versió, Hugo sense checksum. Fixar per SHA, `pagefind@X.Y.Z` i verificar SHA256.
3. **Workflows sense `permissions`** (Mitjana): `deploy-produccio.yml` i `optimitza-webp.yml`. Afegir `permissions: contents: read`.
4. **SSH TOFU** (Mitjana): `ssh-keyscan` + `StrictHostKeyChecking=no`/`accept-new`. Guardar la clau del host com a secret i usar `StrictHostKeyChecking=yes`.
5. **`/stats/analytics.json` públic** (Baixa): 200, 18 KB amb visites i posts més vistos. Protegir amb `.htaccess` (basic auth/allowlist) si no és intencionat.
6. **HSTS** sense `includeSubDomains`/`preload` (Baixa).
7. **404 amb GoatCounter sense SRI** i URL protocol-relative (Baixa).
8. **Contingut mixt:** 94 imatges i 168 enllaços `http://` al llegat (Baixa; les imatges les arregla `upgrade-insecure-requests`, els enllaços no).
9. **Falten COOP/CORP** (Baixa).
10. **Redirecció de barra final via `http://`** (Baixa): `/wp-content/uploads` → 301 http → 301 https.
11. **Informativa:** `/admin/config.yml` accessible (només `app_id`, públic per disseny); sense `/.well-known/security.txt`.

---

## 2. SEO i IA

### Què ja està bé
- **Paritat d'URLs i redireccions** correctes (301 a HTTPS absolut; fix de `/tags/page/N` i `/categories/page/N`; `X-Robots-Tag` només a `feed.xml`).
- **0 descripcions buides**; **BlogPosting + BreadcrumbList** a 2.396/2.396 posts, 0 errors.
- **Sitemap** 3.447 URLs + 2.382 imatges; **robots.txt** amb Sitemap; **llms.txt** operatiu.
- **Canonical** a totes les pàgines, paginació amb self-canonical.
- **WebP:** portada de 2,80 MB → 0,20 MB (**‑93%**); llegat amb `picture`.

### Trobades
1. **`Content-Type` dels `.webp` absent** (Alt; vegeu P0). És el principal risc nou: `img.html` tria la font `webp`; amb `nosniff` alguns navegadors poden no renderitzar-la i no hi ha fallback. Fix: `AddType image/webp .webp` al servidor.
2. **CLS per imatges sense dimensions** (Alt; vegeu Responsive).
3. **`twitter:site`/`creator` i `og:image:width`/`height` absents** (Baix): afegir-los millora targetes i rich results.
4. **2 posts amb 2 `h1`** i **27 grups de descripcions duplicades** (68 pàg.) (Baix).
5. **4.447 imatges sense `alt`** al contingut (Baix/Alt segons a11y).
6. **Etiquetes amb 1 post** ja són `noindex, follow` i fora del sitemap (correcte).

---

## 3. RESPONSIVE

### Què ja està bé
- `meta viewport` correcte a totes les pàgines reals, sense bloqueig de zoom.
- Breakpoints fluids (540/600/768/900) i tipografia `clamp()`; `.container max-width:72rem`.
- Reorganització correcta a mòbil (mosaic, túnel, post-nav, footer, stats).
- Menú hamburguesa amb `aria-expanded`/`hidden` i tancament amb Escape.
- Lightbox i tira Netflix amb `overflow-x` + `scroll-snap` i swipe tàctil.

### Trobades
1. **Sense dimensions ni `aspect-ratio`** (Alt): 93.082 `img`, 0 amb dimensions. Afegir `width`/`height` al partial i un `render-image.html`; mentre no hi siguin, `aspect-ratio` per a les miniatures de relació coneguda.
2. **Sense `srcset`/`sizes`** (Alt): generar diverses amplades o, com a mínim, declarar `sizes`; fons amb `image-set()` o media queries.
3. **`.webp` sense `Content-Type`** (Mitjà) — igual que P0.
4. **Objectius tàctils <44 px** (Mitjà): hamburguesa, lupa, socials, pager, tags. Afegir `min-width/min-height:44px`.
5. **Tipografia massa petita** (Mitjà): `.home-stat__label` 0,45 rem, dates/títols de tira 0,55–0,58 rem. No baixar de ~0,7 rem.
6. **Desbordament de text/codi** (Baix): `overflow-wrap:anywhere` i `.prose pre{overflow-x:auto}`; `body{overflow-x:clip}` l'amaga.
7. **`.post-card` no s'apila** (Baix): a ≤480 px, columna única; reduir `padding-inline` del contenidor.
8. **Logo `nowrap` + nav `padding:2rem`** (Baix): risc a 320 px. Ajustar a ≤380 px.

---

## 4. ACCESSIBILITAT (WCAG 2.2 AA)

### Què ja està bé
- `lang="ca"` a totes les pàgines; landmarks correctes; skip link; focus visible global (6,25:1).
- **Lightbox** amb `role="dialog"`, `aria-modal`, focus trap i retorn de focus; `prefers-reduced-motion` a la transició.
- **SVG** tots `aria-hidden`; botons amb `aria-label`; iframes Vimeo amb `title`.
- 0 imatges sense atribut `alt` (les de plantilla); `aria-current` a pager i tira; `datetime` a l'arxiu.

### Trobades
1. **2.369 imatges amb `alt=""` i 2.085 enllaços sense nom** (Greu). Origen: migració Picasa/Google Fotos. Fix: render hook que apliqui un `alt` de reserva (o `aria-label` a l'enllaç) quan vingui buit; post-processar el llegat.
2. **Lightbox no operable per teclat** (Greu): `main.js` només afegeix `click` a `.prose img`. Fix: `tabindex="0"`, `role="button"`, `aria-label` i `keydown` Enter/Espai.
3. **Contrastos insuficients** (Greu): dates de tira 1,11:1; anys d'arxiu buits 1,11:1; tile sense imatge 2,60:1; separador pager 1,18:1; data 404 3,66:1; placeholder cerca 4,36:1. Fix: no usar `--line` com a text; pujar a `--mid` (#909090) o més.
4. **Encapçalaments** (Moderada): 2 pàgines amb 2 `h1`, 4 `h2` buits, 8 salts de nivell. Fix al contingut/migració.
5. **Llistes a Safari** (Moderada): `list-style:none` global; afegir `role="list"` als `ul` d'arxiu/túnel.
6. **Skip link** (Moderada): afegir `tabindex="-1"` a `#main-content`.
7. **`aria-current="page"` a la nav** (Baixa).
8. **Menú mòbil** (Baixa): canviar l'`aria-label` a "Tanca el menú" quan és obert.
9. **`prefers-reduced-motion` al JS** (Baixa): comptador i scroll suau l'ignoren.
10. **`/admin/` i `/stats/`** (Baixa): sense `h1`/`main`; input del token sense etiqueta.

---

## Pla d'acció prioritzat

### P0 — immediat
1. `AddType image/webp .webp` a `static/.htaccess` (o panell Dinahosting) i verificar `Content-Type`.
2. Diminir CLS: dimensions al partial i render hook d'imatge (o `aspect-ratio` a les miniatures).
3. Lightbox per teclat (`tabindex`/`role`/`keydown`).
4. Contrastos: pujar els colors que fallen a AA.

### P1 — curt termini
5. `alt` de reserva per a les 2.369 imatges de contingut (render hook + llegat).
6. `srcset`/`sizes` i fons adaptatius.
7. CSP: hashes en lloc d'`'unsafe-inline'`; CSP a `/stats/`; allowlist a `img-src`.
8. CI: accions per SHA, `pagefind` fixat, checksum Hugo, `permissions`, host key SSH fix.
9. Objectius tàctils ≥44 px i tipografia mòbil ≥0,7 rem.
10. Protegir `/stats/analytics.json`.

### P2 — mitjà
11. Encapçalaments (reescriure `h1`/`h2` del llegat), `role="list"`, skip link `tabindex`, `aria-current`, label del menú, reduced-motion al JS.
12. `og:image:width/height` i `twitter:site`.
13. HSTS `preload`, COOP/CORP, SRI a la 404, normalitzar `http://` del llegat, redirecció de barra final.
14. Stack-trace de caps d'impressió: `.post-card` a 320 px, logo `nowrap`, desbordament de text/codi.

### P3 — baix
15. `/.well-known/security.txt`; a11y de `/admin/` i `/stats/`.
16. 2 posts amb 2 `h1` i 27 grups de descripcions duplicades.

---

## Verificació de producció (només lectura)
- `Content-Type` dels `.webp` absent (confirmat juga amb `.jpg` correcte).
- `/stats/analytics.json` → 200; rutes sensibles → 403/404.
- TLS 1.3, HTTP/2, HSTS, CSP, X-Frame-Options, Referrer-Policy, Permissions-Policy presents.
- WebP del llegat → 200 (p. ex. `jamborees-backstage-2500.webp`).

---

*Document generat a partir de build net i comprovacions en producció. Els subagents d'auditoria (seguretat/responsive/a11y) no van modificar res.*
