# CLAUDE.md — blog.pocallum.cat

> Guia operativa per a Claude Code en aquest projecte.

## Projecte

Blog personal de **Pocallum** (Joan Linux Martínez), fotògraf cultural a Barcelona. Crònica fotogràfica des del 2010: concerts, festivals, càmeres, òptiques, viatges i vida de barri. En migració de WordPress a Hugo.

**Arquitectura acordada (2026-09-14): projecte independent del web pare** (`../pocallum.cat`). Dos sites Hugo separats; el pare manté la pàgina gateway `/blog/` que enllaça aquí. No tocar el projecte pare des d'aquest repo.

**Tres entorns:**
- **A) Local** — `hugo server -D` → `http://localhost:1313` (casa i feina). Imatges baixades amb rsync a `static/uploads/` (gitignored) o apuntant a la producció.
- **B) Staging** — GitHub Pages (branca `develop`). **Les imatges es veuen allà on són ara: URLs absolutes cap al servidor de producció** (`https://blog.pocallum.cat/wp-content/uploads/...`). El WordPress continua online durant tot el desenvolupament — és la xarxa de seguretat.
- **C) Producció** — `https://blog.pocallum.cat` → **Dinahosting** (HTML Hugo + imatges al mateix docroot).

- **Producció:** `https://blog.pocallum.cat` → **Dinahosting** (servidor actual, `vl28359.dinaserver.com`). S'aprofita l'SSL i l'espai que ja paguem. El servidor també hostatja formularis de contacte i semblants.
- **Local:** `hugo server -D` → `http://localhost:1313`

---

## Estat actual del WordPress (radiografia)

| Dada | Valor |
|------|-------|
| Posts | 2.353 |
| Paraules | 137.029 |
| Categories | 96 (majoritàriament càmeres i òptiques) |
| Etiquetes | 3.177 |
| Comentaris | 71 |
| Arxiu mensual | desembre 2010 → avui |
| Permalinks | `/YYYY/MM/DD/slug/` (slugs amb prefix de data) |
| Idioma | Només català |
| Pàgines fixes | Inici, About, Avís Legal, Contacte, Cerca, privacitat/cookies |

---

## Decisions preses (2026-09-14)

### 1. Tema: nou, derivat de `themes/pocallum`
- Hereta el sistema de disseny del pare: paleta (negre `#080808`, accent `#FF5500`), fonts autoallotjades (Syne, Inter, IBM Plex Sans Condensed), capçalera/peu coherents.
- **Manté els elements característics del blog actual:** cronologia, arxiu mensual, i sobretot la **cerca per càmera i òptica** — és un blog de fotògraf; la taxonomia de càmeres és ciutadana de primera classe.
- Els layouts divergeixen prou del pare per justificar tema propi, no submòdul compartit.

### 2. Hosting i flux de desenvolupament (clarificat 2026-09-14)
- **Estratègia general: desenvolupar-ho TOT al staging (GitHub Pages) i no tocar res de producció fins que tot estigui aprovat.** El WordPress queda online i intacte durant tot el desenvolupament.
- **Staging (GitHub Pages, branca `develop`):** preview del blog Hugo amb **les imatges servides des d'on són ara**, amb URLs absolutes cap al servidor (`https://blog.pocallum.cat/wp-content/uploads/...`). Aquí s'aprova el resultat.
- **Producció (Dinahosting):** docroot `~/www/blog/` — el mateix servidor on ja viuen les imatges a `wp-content/uploads`. Cap migració d'imatges, cap canvi d'URL.
- **Local:** `hugo server` (imatges via rsync `imatges_locals` o directes cap a la producció).
- Motius del canvi vs. GitHub Pages com a producció: 2,3 GB d'originals no hi caben (límit 1 GB); Dinahosting ja té SSL + espai + les imatges + els formularis; i les URLs d'imatge incrustades des del 2010 queden al mateix lloc.

### 2b. SEQÜÈNCIA DE TALL (crucial — ordre obligatori, lliçó apresa del pare)

El tall a producció es fa **només quan el staging està complet i aprovat**, i exactament en aquest ordre:

1. **BACKUP COMPLET previ** (obligatori abans de tocar res): boleà complet de la BD del WordPress + còpia íntegra dels fitxers de `~/www/blog/` (incloent `wp-content/uploads`, 3,4 GB) a un destí fora del servidor. El WordPress actual és la xarxa de seguretat de tot el procés.
2. **Deploy del Hugo a producció:** pujar el `public/` del Hugo al docroot `~/www/blog/` amb rsync, **mantenint `wp-content/`** (les imatges no es mouen).
3. **Verificar el build a producció** — crawlar `https://blog.pocallum.cat` contra l'Hugo local i recolzar-se en el checklist de la fase 6 (QA 1:1 URLs + imatges). **Sense aquesta verificació no es toca res més.**
4. **Només aleshores:** apagar i esborrar el WordPress — retirar el nucli (admin, includes, lesinits, `wp-login.php`, plugins) **conservant sempre `wp-content/uploads`** (les imatges continuen servint des d'allà). El DNS i el domini no es toquen (ja apunten al servidor).

> **Regla d'or:** 1) backup → 2) deploy HTML → 3) verificar producció 1:1 → 4) esborrar el WP. **Mai** en ordre diferent. El WordPress **no s'esborra** fins que el Hugo estigui publicat i verificat a la mateixa URL.

### 2c. PRODUCCIÓ — REGLA ABSOLUTA (2026-09-15, arran d'una violació)

> **MAI es toca producció (`blog.pocallum.cat` / Dinahosting / qualsevol acció sobre el servidor) sense la DOBLE VERIFICACIÓ explícita de l'usuari.**

Això inclou, sense excepció:
- **Pushear a `develop`** quan el workflow `deploy-produccio.yml` hi estigui actiu — cada push desplega a producció. **Avisar SEMPRE abans de cap push**, i el push només amb el vistiplau de l'usuari.
- **Qualsevol acció sobre el servidor** (SSH, rsync, descàrregues, esborrats, canvis de fitxers): **preguntar primer**, esperar resposta, i descriure exactament què es farà abans de fer-ho.
- Descarregar, copiar o moure dades del servidor a un altre lloc: només amb permís previ explícit.

Els canvis que **no** requereixen verificació: treball local, staging (GitHub Pages), commits al repo, i qualsevol cosa que no toqui ni desplegui.

Història per no repetir-la: el 2026-09-15 es va desplegar a producció amb un sol push a `develop` sense avisar l'usuari, i es van descarregar 3,5 GB del servidor sense permís. Dues violacions de confiança que no es poden repetir. El control l'ha de tenir sempre l'usuari.

### 3. Comentaris
- Els **71 comentaris llegats es congelen** com a contingut estàtic dins dels posts.
- Per a comentaris nous: **servei extern — giscus** (recomanat): open source, sobre GitHub Discussions, sense cookies ni tracking, integrable a GitHub Pages. Requereix compte GitHub per comentar (fricció acceptable: 71 comentaris en 15 anys). **Pendent de validació en fase de tema; si no s'adopta, el blog queda sense comentaris nous.**
- Descartat: Disqus (tracking, contra la filosofia del projecte).

### 4. Imatges: romanen al servidor de producció
- Les imatges **no es copien al repo**: es queden a `~/www/blog/wp-content/uploads/` i el Hugo les referencia amb rutes relatives (`/wp-content/uploads/...`) — cap canvi d'URL.
- **Staging:** els posts hi mostren les imatges amb **URLs absolutes al servidor** (`https://blog.pocallum.cat/wp-content/uploads/...`).
- **Local:** mode sense connexió mitjançant rsync a `static/uploads/` (gitignored).
- Posts nous: imatges a `static/uploads/` o page bundles (publicades com a `/uploads/...`), a decidir en fase de tema.
- **Model d'imatges del post (des de fase 3):**
  - **Imatge miniatura** (`thumbnail:` al frontmatter): prové de `_thumbnail_id` al WP → adjunt → `guid` (URL). Sempre al servidor local: `/wp-content/uploads/...`. S'usa als llistats (home, arxiu, categories, cerques). **Si no hi ha miniatura, s'usa la principal.**
  - **Imatge principal** (`image:` al frontmatter): primer `<img>` del contingut. Sovint `lh*.googleusercontent.com` (enllaços a àlbums de Picasa/Google Fotos que enllacen a la foto completa). S'usa a la capçalera del post.
  - Les dues **no sempre coincideixen**; sovint la miniatura és una versió local i la principal és un hotlink a Google Fotos.

### 5. Vimeo: posts i vídeos nous
- **3 posts amb shortcode `[vimeo ID w=W h=H]`** al llegat. L'eina de conversió escapa l'shortcode; l'iframe renderitzat ja queda al contingut (l'WordPress l'havia emès abans de l'export).
- **Estratègia per a vídeos nous:** usar un shortcode Hugo `{{< vimeo ID >}}` o un **render hook de links** (`_markup/render-link.html`) que detecti automàticament URLs `vimeo.com/XXXX` i les embedi — ambdues opcions per decidir en fase de tema. L'objectiu és poder posar la URL de Vimeo directament al contingut i que Hugo l'empotri sense edicions addicionals.

### 6. Imatges: optimització mantingent qualitat
- **Som fotògrafs: alta qualitat sempre.** Les originals mai es destrueixen ni es toquen.
- **Llegat:** les imatges existents NO es processen (rutes i bytes tal qual).
- **Nous posts:** optimitzar a WebP abans de pujar al servidor (qualitat ~85, llarg màxim ~2400px per a display; les originals es guarden com a arxiu). Equival al `scripts/convert-images.sh` del pare.
- Si mai es vol optimitzar el llegat, només com a còpia de display a sobre, mai substituint l'original.

---

## Stack tècnic (previst)

| Capa | Tecnologia |
|------|-----------|
| SSG | Hugo v0.164+ extended |
| Tema | Custom `themes/blog/` (derivat del sistema pocallum) |
| CSS | Vanilla CSS amb custom properties (cap framework) |
| JS | Vanilla JS mínim |
| Idioma | Només català |
| Hosting | Producció: Dinahosting (`~/www/blog/`) · Staging: GitHub Pages · Local: hugo server |
| Cerca | Pagefind (indexació estàtica) |
| Analytics | GoatCounter (sense cookies, GDPR) + dashboard `/admin/` |
| Comentaris | giscus (pendent de validació) |
| DNS/Domini | Dinahosting (DNS + docroot de producció) |

---

## Comandes útils

```bash
# Menú interactiu (status, sync, server, build, deploy, nou post)
./sync-blog.sh

# Nou post (equivalent a l'opció p del menú; data i slug amb prefix)
hugo new posts/2026-09-14-titol.md

# Build de producció (minificat)
hugo --minify

# Servidor local amb drafts
hugo server -D

# Post-processament conversió (afegeix thumbnail, image, tags)
python3 migration/post-processa.py
```

- Els posts nous porten **prefix de data al nom de fitxer i al títol** (`2026-09-14-titol.md` → URL `/2026/09/14/2026-09-14-titol/`), com al WordPress.
- El repo GitHub és `112books/blog.pocallum.cat` (privat→public 2026-09-14, perquè el pla Free no suporta Pages en repos privats). Branques `main` (codi) i `develop` (desplega staging). Staging: `https://112books.github.io/blog.pocallum.cat/`.

---

## Resultats conversió (2026-09-14)

### Eina: `wordpress-export-to-markdown` v3.0.5
- Execució (segona, definitiva): `npx wordpress-export-to-markdown@3.0.5 --input migration/export.xml --output migration/wpfull --frontmatter-fields "title,date,slug,categories,tags,excerpt,author,draft" --save-images none --wizard false --post-folders false`
- **2.353 posts** publicats (i **10 drafts** a `_drafts/`) a `migration/wpfull/posts/`
- **6 pàgines fixes** migrades directament des de `migration/pages/*.xml` al post-processament
- **Alerta:** el CLI per defecte del servidor (PHP 7.0) no executa l'export actual; fer servir `/opt/php-8.2/bin/php /usr/local/bin/wp ...`

### Troballes importants
1. **Tags**: la segona execució sí que els extreu (843 posts); el post-processament els reescriu des de l'XML igualment (font canònica).
2. **`coverImage` buit**: l'eina no mapeja `_thumbnail_id` → imatge. El post-processament extreu la miniatura de `_thumbnail_id` → adjunt → `guid`.
3. **Vimeo shortcodes escapats**: `\[vimeo ID w=W h=H\]` → convertits a `{{< vimeo ID >}}` (3 posts; es consumeix la barra inversa).
4. **Frontmatter generat**: title, date, slug, categories, author, tags, thumbnail, image. Darrere: contingut Markdown amb imatges en format `![alt](url)`.
5. **Slugs URL-encoded del WP (~18 posts)**: reescrits al valor original (`forc%cc%a7at`) per a paritat d'URLs; `excerpt` eliminat (corromput a la font).

### Post-processament fet
Script `migration/post-processa.py` (executat 2026-09-14, segona execució completa):
- ✅ `tags:` afegit des de l'XML (font canònica) — **843 posts**
- ✅ `thumbnail:` de `_thumbnail_id` → adjunt → `guid` — **2.349 posts** (2 recuperats per WP-CLI perquè l'adjunt no era a l'XML)
- ✅ `image:` del primer `<img>` del contingut — **2.323 posts**
- ✅ Shortcodes `\[vimeo ID w=W h=H\]` → `{{< vimeo ID >}}` (3 posts)
- ✅ `excerpt` **eliminat** (196 posts corromputs a la font: accents → `??` al propi XML del WP)
- ✅ **Slugs URL-encoded del WP (~18 posts):** el WP guarda `forc%cc%a7at` (= `forçat`); es reescriu el `slug:` del frontmatter al valor original per a paritat d'URLs. Verificat vs WP viu (200/404).
- ✅ Pàgines fixes (6 publicades) migrades a `content/*.md`; **3 buides al WP** (aviso-legal, privacitat, cookies) esperen contingut legal.

**Materials:** `migration/` (gitignored): XML posts (56 MB) + XML pàgines (24 KB) + `wpfull/posts/` (2.353 posts + 10 drafts a `_drafts/`). Els drafts no es copien a `content/posts/`.

**Reexecució:** `python3 migration/post-processa.py` regenera `content/posts/` des de `migration/wpfull/posts/` (idempotent). Les 2 miniatures recuperades per WP-CLI s'apliquen amb un script manual (detalall a `INFORME-MIGRACIO.md`).

---

## Requisits d'URLs (crític per SEO)

**Els permalinks han de ser idèntics als del WordPress.** Configuració Hugo:

```toml
[permalinks]
  posts = "/:year/:month/:day/:slug/"
```

- El slug conserva el prefix de data (`2026-08-24a28-escapada-a-taull`) — ve del WordPress tal qual.
- RSS a `/feed/` (subscritors existents).
- Pàgines fixes a les mateixes rutes: `/about/`, `/aviso-legal/`, `/contact/`, `/cerca/`, `/politica-de-privacidad/`, `/politica-de-cookies/`.
- QA abans del tall: crawlar el WordPress actual vs el Hugo local i verificar resposta 200 a 1:1 per cada URL.

---

## Taxonomies (previst)

```toml
[taxonomies]
  category = "categories"   # inclou càmeres i òptiques (estructura actual)
  tag      = "tags"
```

- **Cerca per càmera/òptica:** requisit destacat per l'usuari. Durant la conversió es valorarà si convé separar la taxonomia `camera` de `category` (les categories actuals són majoritàriament marques i models), però **mai abans de tenir l'exportació analitzada**. Canvi de taxonomia = canvi d'URLs d'arxiu; documentar-ho si es fa.
- Arxiu mensual: índex per any/mes (l'actual sidebar de WordPress va de desembre 2010 a avui).

### Canvi d'URLs d'arxiu executat (2026-09-15, auditoria SEO) — DOCUMENTAT

**Context:** el WP servia els tags a `/tag/<slug>/` (flat) i les categories a `/category/<pare>/<fill>/` (jeràrquic: 85 fills sota 3 pares — `camara`, `optioca`, `publicacions`; cap top-level). El Hugo inicial els va generar als plural (`/tags/`, `/categories/`) i aplanats → **3.114 URLs amb 15 anys d'indexació trencaven** (Wayback: 2.908 tags + 259 categories històriques).

**Solució (paritat màxima + 301):**
- `hugo.toml [permalinks.term]`: `tags = "/tag/:slug"`, `categories = "/category/:slug"` (paritat exacta per als 3.020 tags) + `[permalinks.taxonomy]` manté els índexs a `/tags/` i `/categories/` (el browser de càmeres no es mou).
- `.htaccess` (mod_rewrite): 301 de les jeràrquiques WP → aplanades (`/category/<pare>/<fill>/` → `/category/<fill>/`, + `/page/N/` i `/feed/`), cas especial `horsman-8x10″` (nicename WP amb U+2033 → Hugo `horsman-8x10`), `/category/publicacions/` → `/categories/`, i 301 dels plurals provisionals (`/tags/<x>/` → `/tag/<x>/`, `/categories/<x>/` → `/category/<x>/`).
- `/feed/` del WP es serveix via rewrite intern a `/feed.xml` (subscriptors existents) + 301 `/comments/feed/`.
- **Tag no coberts:** ~12 tags Wayback que el WP final ja no tenia en cap post publicat → 404 honest (Google els poda).
- **`llms.txt`** (conveni per a cercadors d'IA): output format `llms` a la home → `layouts/home.llms.txt` amb mapa del lloc + 15 darreres cròniques.
- **robots.txt:** template propi (`themes/blog/layouts/robots.txt`) amb `Disallow:` buit (allow all, cercadors i crawlers d'IA explícitament benvinguts) + línia `Sitemap:`.
- **seo.html:** og:image ara prioritza `thumbnail:` (local, fiable) sobre `image:` (sovint hotlink Google); descriptions amb `plainify | trim` (text net, sense `\n` inicial); og:type `website` a totes les pàgines no-post; **self-canonical a `/page/N/`** (abans canonicalitzava a l'arrel → Google desindexava la paginació).
- **Pendent de l'usuari:** token de verificació de Google Search Console (cap meta `google-site-verification` al HTML actual; si el GSC del WP era via meta tag de Yoast, s'ha perdut amb el WP — cal re-verificar el domini, via meta tag o DNS TXT).

---

## Pla de migració (fases)

1. ✅ **Exportació** — XML complet de WordPress + còpia de `wp-content/uploads`. **Mesurar mida total d'imatges** (ja fet: 3,4 GB totals; 2,3 GB originals → decisió Dinahosting).
2. ✅ **Scaffolding** — `hugo new site`, `hugo.toml` amb permalinks idèntics, taxonomies, RSS.
3. ✅ **Conversió** — XML → Markdown (`wordpress-export-to-markdown` v3.0.5). **2.353 posts (i 10 drafts)** a `content/posts/` amb `tags`, `thumbnail`, `image` i Vimeo resos; pàgines fixes migrades. Materials i script a `migration/` (gitignored).
4. ✅ **Tema** — llistat cronològic (portada hero + galeria 8 posts), single amb tira Netflix, arxiu mensual, taxonomies/categories, cerca Pagefind, pàgines fixes (about/contacte/cerca) amb fons hero. Stats animats portada. Lightbox, mosaic. RSS, comentaris estàtics.
5. ✅ **Pàgines fixes** — About, Contacte, Cerca implementades. Avís Legal, Privacitat i Cookies: frontmatter creat, contingut legal pendent.
6. ✅ **QA** — `scripts/qa-urls.py` (2026-09-15): primera passada 2.360 URLs, 9 Hugo 404 per interpunt `·` (slugs percent-encoded `%c2%b7` al frontmatter — desxifrats al caràcter real, commit `bce1b88bd`; l'script ara percent-encoda els paths). **Passada final: 2.360/2.360 = 100%** local vs producció.
7. ✅ **SEO** — partial `seo.html` centralitzat (robots, description truncada 155, OG, Twitter, JSON-LD dict+safeJS). Meta descriptions Yoast injectades (271 posts). Title-seo injectat (130 posts). Verificat amb json.loads a tots els posts. Commit `9ec8e8258`.
8. ✅ **CMS** (2026-09-18) — Sveltia CMS operatiu a staging i producció (login GitHub via GitHub App, `app_id` configurat). Vegeu § Pla CMS.
9. ✅ **Deploy** (2026-09-15) — pujar el `public/` del Hugo al docroot de Dinahosting (`~/www/blog/`), substituint el WordPress però **mantenint `wp-content/uploads`** (les imatges no es mouen). **FET: producció 100% verificat (25/25 URLs reals del sitemap → 200; 2.353 posts, 94 categories, 3.021 tags).** El WordPress queda congelat online fins a l'apagat acordat.

**Sessió 2026-09-15 — afegits:**
- **Pàgina 404** del blog adaptada de la del pare (`themes/blog/layouts/404.html` standalone): fons foto `static/images/404.jpg` + overlay, logo `blog.pocallum.cat`, títol "Aquesta foto no s'ha fet.", suggeriments = 3 últimes cròniques amb miniatura (thumbnail). CSS `e404-*` a `assets/css/main.css`. Imatge idèntica a la del pare.
- **Fix rsync exit 23** a `.github/workflows/deploy-produccio.yml`: afegit `--exclude='.well-known/'` (no pot esborrar `.htaccess` per permisos) i `--omit-dir-times` + `--no-perms` (solució definitiva). Abans cada deploy acabava amb `exit code 23` encara que els fitxers es pugessin bé; ara surt net.
- **`.htaccess` amb ErrorDocument 404** (`static/.htaccess`): cal perquè Dinahosting/Apache serveixi la 404.html de Hugo en lloc de la pàgina per defecte.
- **CMS: els 2.027 posts (no 2.353)** que mostra Sveltia és límit de paginació de l'API de GitHub llistant una carpeta enorme — **no és pèrdua de dades**. Els 2.353 fitxers són tots al repo i es renderitzen bé. Impacte: només si volguessis editar un dels 326 "fantasma" caldria fer-ho per git.
- **Favicon (2026-09-15):** `static/favicon.ico` = **el del pare, marca LinuxBCN** (l'entitat que desenvolupa el web, amb crèdit al footer del pare) — copiat byte a byte de `../pocallum.cat/static/favicon.ico` (16+32, PNG-in-ICO). Enllaçat amb `?v=2` (bust de caché) al `head.html` i al `404.html` juntament amb el SVG propi (`/images/logo.svg`) pels navegadors moderns. Abans Safari no mostrava res (no suporta favicons SVG).
- **Analytics (2026-09-15):** tres bugs arreglats al pipeline GoatCounter → dashboard `/stats/`: (1) el workflow antic commiteja amb `[skip ci]` i push via GITHUB_TOKEN que **no dispara workflows** (protecció anti-bucle GitHub) — ara commiteja a `develop` i cala `deploy-staging.yml` + `deploy-produccio.yml` explícitament; (2) `/stats/hits?limit=100` només tornava el top-100 paths de l'any — ara `scripts/fetch-hits.py` pagina amb `exclude_paths` (path_id) fins `more=false`: **525 paths / 1.206 visites** vs 100/719 d'abans; (3) cron fora punta (`17 * * * *`, GitHub descarta runs a `:00`). Nota: el pare té el mateix bug del top-100 pendent. Recordatori: **mai posar `[skip ci]` (ni al cos!) en commits que han de disparar workflows**.
- **L'error "Broken pipe" del primer deploy** no era pèrdua: era connexió tallada en transferència; un rsync incremental en completà la resta.
- **Auditoria 2026-09-15 (accessibilitat + responsive + seguretat)**: fixes aplicats (skip-link contrast AA, focus trap lightbox, nav hidden, fletxes mòbil, tancament lightbox amb reduced-motion) + headers de seguretat (HSTS, X-Content-Type-Options, X-Frame-Options, Referrer-Policy). **Redirect HTTP→HTTPS (fix 2026-09-17):** el primer intent amb `%{HTTPS} off` buclava perquè Apache rep HTTP intern del proxy. **Però el proxy SÍ envia `X-Forwarded-Proto`** (verificat empíricament amb un `check-headers.php`): `http` vs `https`. Solució a `static/.htaccess`: `RewriteCond %{HTTP:X-Forwarded-Proto} ^http$` → `301` a HTTPS amb `E=NO_CACHE:1` + `Header Cache-Control no-store` (evita que Varnish cachegi el 301 i el serveixi a clients HTTPS → bucle). No cal el panell de Dinahosting.

**Sessió 2026-09-15 (tarda) — QA final + auditoria SEO/GEO/AEO:**
- **QA 1:1 completada: 2.360/2.360 = 100%** (detall a la fase 6).
- **`[skip ci]` al cos del commit = salt de workflows**: el commit `14c4b9a34` portava el text literal al cos i GitHub va saltar TOTS els workflows del push. Regla: mai posar `[skip ci]` enlloc del missatge si has de disparar workflows.
- **fetch-analytics.yml reescrit**: checkout `ref: develop`, commit d'`analytics.json` a develop + triggers explícits `gh workflow run` dels dos deploys (push via GITHUB_TOKEN no engega workflows), cron `17 * * * *` fora punta; merge develop→main perquè els scheduled corrin des de la branca per defecte.
- **`scripts/fetch-hits.py` nou**: `/stats/hits?limit=100` només torna el top-100 paths de l'any → pagina amb `exclude_paths` (path_id CSV) fins `more=false`: **525 paths / 1.206 visites**. El pare té el mateix bug pendent.
- **Footer: "Powered by LinuxBCN.com"** amb enllaç, com al pare (atribució al desenvolupador).
- **Auditoria SEO/GEO/AEO + paquet de fixes (commit `942f30f8f`)** — detall complet a la secció "Canvi d'URLs d'arxiu executat". Troballes crítiques: 3.114 URLs d'arxiu trencades (tags/categories), `/feed/` 404, robots.txt sense Sitemap, descriptions amb `\n` inicial, `/page/N/` canonicalitzant a l'arrel. Fixes: paritat exacta `/tag/:slug` + `/category/:slug`, 301s al `.htaccess` (jeràrquiques WP, plurals provisionals, `/feed/` via rewrite intern), robots.txt propi, **llms.txt** (conveni IA), og:image = `thumbnail` → `image` → **fons de portada** (imatgeFons, LC-A 2025) → default, self-canonical a paginació, og:type `website` a llistes, enllaços de termes via `.GetTerms`.
- **Bug Hugo detectat**: `X | trim C` executa `strings.Trim(C, X)` (ordre invertit amb el pipe) en aquesta versió → usar `strings.TrimSpace` (pipe-safe).
- **Pendent de l'usuari (SEO):** token de verificació GSC (cap meta `google-site-verification`; cal re-verificar domini via meta tag o DNS TXT).

### ✅ RESOLT — HTTP→HTTPS redirect (fix aplicat i verificat 2026-09-17)

**Actualització 2026-09-16 (canvi d'arquitectura, confirmat per l'usuari):** `pocallum.cat` (el pare) **ja no és a GitHub Pages — migració permanent a Dinahosting**, mateix servidor que `blog.pocallum.cat`. `@`/`www` de `pocallum.cat` apunten ara a Dinahosting de forma definitiva (no és el ball temporal de DNS que preveia el pla original). Let's Encrypt acabat d'activar per a `pocallum.cat` al panell; per a `blog.pocallum.cat` ja es renovava automàticament (confirmat abans). **Cap pas de revert de DNS pendent** — els punts 1-3 i 5-7 del pla original ja no apliquen.

**Fix (2026-09-17):** el redirect ja està resolt via `.htaccess` usant `X-Forwarded-Proto` (verificat que el proxy de Dinahosting SÍ l'envia, amb un `check-headers.php` → HTTP: `http` / HTTPS: `https`). Regla: `RewriteCond %{HTTP:X-Forwarded-Proto} ^http$` → 301 a HTTPS, amb `E=NO_CACHE:1` + `Header Cache-Control no-store` perquè Varnish no cachegi el 301 i el serveixi a clients HTTPS (bucle). **Comprovat en producció:** `http://...` → 301 → `https://...` 200, sense bucle, i totes les cadenes de paritat (tags/categories/feed) acaben a HTTPS. **No cal activar res al panell de Dinahosting** per a aquest redirect.

**Nota important:** aquest canvi és al domini/DNS del **projecte pare** (`pocallum.cat`), no d'aquest repo — es documenta aquí només perquè afecta l'estat compartit del servidor Dinahosting. Si cal actualitzar l'arquitectura descrita a `../pocallum.cat/CLAUDE.md` (que fins ara assumia GitHub Pages com a producció del pare), és feina d'una sessió al repo pare, no d'aquí.

**Estat verificat (17/09/2026):**
- `https://blog.pocallum.cat` → HTTP/2 200, cert Let's Encrypt renovant-se automàticament
- `https://pocallum.cat` → servit des de Dinahosting, Let's Encrypt acabat d'activar
- `http://blog.pocallum.cat` → **301 → HTTPS (RESOLT)**
- `http://pocallum.cat` → a verificar (probablement mateix cas pendent al pare, que comparteix proxy)

---

## Dashboard d'estadístiques (`/admin/`)

Replicar el dashboard del pare: `static/admin/index.html` autocontingut (estètica pocallum, protegit per contrasenya SHA-256) + `static/admin/analytics.json` generat cada hora per GitHub Actions des de l'API de GoatCounter.

- **Referència:** repo `../goatcounter-dashboard` i implementació del pare (`../pocallum.cat/static/admin/`, `scripts/`, `.github/workflows/fetch-analytics.yml`)
- **GoatCounter existent:** el blog ja té GoatCounter configurat al WordPress (`wp-admin → goatcounter-wp` → site code `pocallum-blog`; verificat directament al HTML que emet el WP: `data-goatcounter="https://pocallum-blog.goatcounter.com/count"`). **Reaprofitarem el site ja creat** (mateix codi) en lloc de crear-ne un de nou. El `hugo.toml` ja té `goatcounterSite = "pocallum-blog"` — **no canviar-lo**. Falta afegir el `GOATCOUNTER_TOKEN` al repo (secret de GitHub Actions), pendent.
- **Implementació:** fases 4–5, un cop el tema estigui en marxa
- **⏳ Pendent (demanat per l'usuari, 2026-09-15):** afegir al dashboard el **gràfic de visites per dia de la setmana** (i per hora del dia) — important per decidir **quin dia/hora publicar**. Cal agregar la dimensió temporal dels hits (camp `Time` del `/stats/hits` de GoatCounter) al `process-analytics.py` i pintar el gràfic a la primera pàgina del dashboard.
- **Chart.js autonallotjat (fix 2026-09-17):** el dashboard carregava Chart.js des de `cdn.jsdelivr.net`, que el CSP (`script-src 'self' ...`, sense jsdelivr) bloquejava → els gràfics no es pintaven. Fix: `static/stats/vendor/chart.umd.min.js` (v4.4.0, SRI verificat `sha384-e6nUZLBkQ86NJ6TVVKAeSaK8jWa3NhkYWZFomE39AvDbQWeie9PlQqM3pmYW5d1g`) referenciat com a `vendor/chart.umd.min.js`. Deploy via push a `develop` (commit `1890f7dbac`). Si mai es puja el dashboard, **no tornar a apuntar a cap CDN**. El pare té el mateix problema pendent (`../pocallum.cat`).

---

## Pla SEO (pròxima sessió)

Substitueix Yoast Free. Tot implementat a Hugo, sense plugins ni serveis externs.

### Què cal fer

**Pas 1 — Partial SEO** (`themes/blog/layouts/partials/seo.html`):
- `<meta name="description">` des del camp `description:` del frontmatter (o auto-truncat del contingut si buit)
- `<meta name="robots">` (respecta `draft: true` i `noindex: true`)
- Open Graph: `og:title`, `og:description`, `og:image` (usa `thumbnail:`), `og:type` (article/website)
- Twitter Cards: `twitter:card`, `twitter:image`, `twitter:description`
- Canonical URL (Hugo ja la genera, però centralitzar al partial)
- Incluir a `baseof.html` en lloc dels `_internal/` de Hugo

**Pas 2 — JSON-LD BlogPosting** (al `single.html`):
- `@type: BlogPosting`, `headline`, `datePublished`, `dateModified`, `image`, `author`, `url`
- Molt valorat per Google per a contingut fotogràfic/cultural

**Pas 3 — Meta descriptions del llegat** (script `migration/extreu-yoast.py`):
- Extreure `_yoast_wpseo_metadesc` i `_yoast_wpseo_title` del `migration/export.xml`
- Injectar com a `description:` al frontmatter de cada post que en tingui
- Estimació: X posts amb meta description de Yoast (a verificar al XML)

**Pas 4 — Arquetip** (`archetypes/posts.md`):
- Plantilla amb tots els camps: `title`, `date`, `description` (buit, amb comentari 155 car.), `categories`, `tags`, `thumbnail`

### Camp `description:` als posts nous

Format frontmatter:
```yaml
description: "Breu descripció per a Google, màx. 155 caràcters, en català."
```
Si buit, Hugo usarà el `.Summary` (primers 70 paraules). Funciona però no és òptim.

---

## Pla CMS — Sveltia CMS (single user)

Objectiu: publicar posts des de qualsevol dispositiu (mòbil inclòs) sense accedir al repositori local.

### Arquitectura

- **Backend:** GitHub (repo `112books/blog.pocallum.cat`, branca `develop`)
- **Frontend admin:** `static/admin/index.html` + `static/admin/config.yml` (**ja creats**)
- **URL admin (staging):** `https://112books.github.io/blog.pocallum.cat/admin/`
- **URL admin (producció):** `https://blog.pocallum.cat/admin/` (un cop desplegat a Dinahosting)
- **Autenticació:** GitHub OAuth (usuari únic — un sol compte GitHub)
- **Deploy:** automàtic a staging (GitHub Pages) + automàtic a Dinahosting (rsync) en cada push a `develop`
- **Media uploads:** `static/media/` (commitat al repo; NO confondre amb `static/uploads/` que és gitignored per al development local)

### Flux d'usuari (single user)

1. Publica des del CMS (mòbil o desktop) → push a `develop`
2. GitHub Actions build + deploy automàtic a **staging** (GitHub Pages) i **producció** (Dinahosting)
3. El post és visible tant a staging com a producció de seguida

### Secrets de GitHub Actions (pendent de configurar)

**Producció (Dinahosting) — 4 secrets:**
- `SSH_PRIVATE_KEY_DINAHOSTING` — clau SSH privada (ed25519 recomanat)
- `DINAHOSTING_HOST` — hostname o IP del servidor (`vl28359.dinaserver.com`)
- `DINAHOSTING_USER` — usuari SSH de Dinahosting
- `DINAHOSTING_PATH` — ruta del docroot (`~/www/blog` o absoluta)

**GoatCounter — 1 secret (pendent):**
- `GOATCOUNTER_TOKEN` — token d'API de GoatCounter (per al dashboard d'estadístiques)

### GitHub App per l'OAuth (creada — 2026-09-18)

És una **GitHub App** (no OAuth App clàssica) — Client ID `Ov23litV55M1TEQIQJk1`, admet **múltiples Redirect URLs** alhora (avantatge sobre OAuth App clàssica, que només n'admet una). Redirect URLs configurades: staging (`https://112books.github.io/blog.pocallum.cat/admin/`) i producció (`https://blog.pocallum.cat/admin/`), totes dues actives simultàniament.

Secrets `OAUTH_CLIENT_ID`/`OAUTH_CLIENT_SECRET` existeixen al repo (creats 15/09) però **no s'usen** — Sveltia amb backend `github` + auth PKCE no necessita servidor d'intercanvi de token (GitHub suporta PKCE per apps client-side). El Client ID va directament al `config.yml` (públic, no secret).

**Fix aplicat (2026-09-18) — `/admin/` no funcionava, 2 causes:**
1. **CSP de producció** (`static/.htaccess`, afegit a l'auditoria de seguretat del 16/09) bloquejava `script-src` cap a `unpkg.com` → pàgina en blanc a Dinahosting. Staging (GitHub Pages) no té `.htaccess`, no li afectava.
2. **`config.yml` sense `app_id`** → Sveltia no mostrava el botó de login GitHub, només l'opció de token manual.

Solució: `sveltia-cms.js` autoallotjat a `static/admin/vendor/` (2 MB, mateix criteri que Chart.js — mai apuntar a CDN, veure nota SSL/stats més amunt) + CSP propi per `/admin/` a `static/admin/.htaccess` (permet `api.github.com`, `github.com` per OAuth, fonts `cdn.jsdelivr.net` del CMS, sense afluixar el CSP del lloc principal) + `app_id: Ov23litV55M1TEQIQJk1` a `config.yml`. Commit `b0d2c7be85`, desplegat i verificat a staging i producció (curl: script 200, `app_id` present, CSP escopejat correcte a `/admin/`).

**Fix aplicat (2026-09-18, sessió tarda) — primer post real des del CMS, 3 problemes:**
1. **Camp URL d'àlbum absent.** Afegit `album_url` (opcional) al collection `posts` de `config.yml` + render a `themes/blog/layouts/_default/single.html` (link "Veure l'àlbum complet →" sota la data, només si s'omple).
2. **Error "Couldn't load the catalan translation. Please try again later."** Causa: la interfície de Sveltia carrega els strings d'idioma dinàmicament via `fetch` a `https://unpkg.com/@sveltia/cms@versió/locales/<idioma>.json`; `unpkg.com` no era a `connect-src` del CSP de `static/admin/.htaccess` → bloquejat. Afegit `https://unpkg.com` al `connect-src`. El català (`ca`) ja és una de les llengües suportades pel bundle — no calia cap altre canvi, ni camp d'idioma als posts (el blog és mono-idioma i aquest error és de la UI del CMS, no del contingut).
3. **404 al preview de producció.** El post tenia `draft: true` — ni `deploy-staging.yml` ni `deploy-produccio.yml` fan `hugo -D`, així que els drafts no es publiquen enlloc (comportament correcte). Cal desmarcar "Draft" al CMS per publicar de veritat.

Efecte secundari detectat (no arreglat automàticament, informat a l'usuari): si s'escriu la data manualment dins el `title` (hàbit del WordPress) mentre el camp `date` queda a la data de creació, el `slug` acaba amb data duplicada al nom de fitxer. No cal escriure la data al títol — Hugo ja la genera a la URL des del camp `date` (`[permalinks] posts = "/:year/:month/:day/:slug/"`).

Commit `1206143a59`, rebase sobre commits del bot CMS (`d845aa18cc`, `ae0932a465`), push `ae0932a465..6c526bda03` a `develop` (desplegament automàtic staging + producció, confirmat per l'usuari abans del push).

### Configuració del CMS (config.yml)

```yaml
backend: { name: github, repo: 112books/blog.pocallum.cat, branch: develop }
media_folder: "static/media"
public_folder: "/media"
collections:
  - Categories: folder content/categories, value_field: valor (slug), display_fields: title
  - Pàgines fixes: files collection (about, contact, cerca, aviso-legal, polítiques)
  - Posts: folder content/posts, categories → relation a Categories,
           thumbnail/image → widget image (drag&drop a static/media)
```

**Slug:** auto-generat des del títol amb neteja de caràcters especials. L'usuari pot sobreescriure'l.
**Imatges:** widget `image` → drag&drop → van a `static/media/` → commitades automàticament al repo.
**Categories:** 92 termes gestionats com a col·lecció separada (content/categories/*/\_index.md).
**Fons pàgines:** camp `imatgeFons` al frontmatter (widgets image a les pàgines fixes + \_index.md per al home).

### Workflow: deploy-produccio.yml (ja creat)

- Trigger: push a `develop` o `workflow_dispatch`
- Build Hugo + Pagefind + rsync a Dinahosting
- **Exclou `wp-content/`** (imatges WordPress intactes)
- Prem `cancel-in-progress: false` (no cancel·la un deploy en curs)

---

## Segona fase (post-migració)

---

## To i veu

- **Idioma:** català
- **To:** crònica personal, directe, proper — el blog és "la banda sonora del que es fotografia"
- **No és un bloc corporatiu:** sense estratègia de continguts ni calendari editorial
- **Evitar:** màrqueting buit, superlatifs, castellanismes

---

## Relació amb el web pare

- `pocallum.cat/blog/` és la pàgina gateway (estadístiques + narrativa) que enllaça aquí — **actualitzar les estadístiques del frontmatter** quan la migració acabi (números reals del Hugo: posts, paraules, categories, etiquetes).
- Enllaç de tornada al pare des de la navegació del blog (el WordPress actual ja ho fa: "Pocallum.cat" al menú).
- `AGENTS.md` del pare diu "el blog és extern, no tocar" — norma que s'ha de revisar quan la migració acabi.

---

## Fora d'abast

- Multilingüe (el blog és i serà només en català)
- Newsletter / mailing list
- Comentaris amb sistema propi o backend
- Migració d'usuaris de WordPress
- Botiga o e-commerce

---

## Control horari

Skill actiu: `gestor-hores` — registra automàticament el temps de treball per sessió.

- Logs a `.taques/blog.pocallum.cat/YYYY-MM-DD.md` (creat automàticament)
- Comandes: `/time-log [tasca] [hores]`, `/time-report [periode]`, `/time-config [hores] [tarifa]`
- No modificar manualment els fitxers `.taques/` — són append-only

### ⚠️ Regla d'or del registre horari (obligatòria)

El control horari és la base de la **facturació/comptabilitat del client**. Per tant:

- **Només es registren hores reals i verificables.** Mai inventar ni estimar per defecte.
- **Base de tot registre:** evidències objectives (timestamps de fitxers, commits de git, hores declarades per l'usuari). Si no hi ha evidència, es pregunta a l'usuari **abans** d'anotar res.
- **No inventar tasques ni hores.** Si no saps una hora, un inici de sessió o una durada → **pregunta abans d'escriure**.
- Cal anotar sempre **hora d'inici real** (confirmada per l'usuari si no hi ha evidència).
- Els logs es revisen amb l'usuari abans de considerar-los vàlids per a facturació.
- **Rigor sobre rapidesa:** val més deixar una tasca sense hora que anotar-ne una d'inventada.
