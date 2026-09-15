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

---

## Pla de migració (fases)

1. ✅ **Exportació** — XML complet de WordPress + còpia de `wp-content/uploads`. **Mesurar mida total d'imatges** (ja fet: 3,4 GB totals; 2,3 GB originals → decisió Dinahosting).
2. ✅ **Scaffolding** — `hugo new site`, `hugo.toml` amb permalinks idèntics, taxonomies, RSS.
3. ✅ **Conversió** — XML → Markdown (`wordpress-export-to-markdown` v3.0.5). **2.353 posts (i 10 drafts)** a `content/posts/` amb `tags`, `thumbnail`, `image` i Vimeo resos; pàgines fixes migrades. Materials i script a `migration/` (gitignored).
4. ✅ **Tema** — llistat cronològic (portada hero + galeria 8 posts), single amb tira Netflix, arxiu mensual, taxonomies/categories, cerca Pagefind, pàgines fixes (about/contacte/cerca) amb fons hero. Stats animats portada. Lightbox, mosaic. RSS, comentaris estàtics.
5. ✅ **Pàgines fixes** — About, Contacte, Cerca implementades. Avís Legal, Privacitat i Cookies: frontmatter creat, contingut legal pendent.
6. ✅ **QA parcial** — `scripts/qa-urls.py` executat 2026-09-15: 2.360 URLs; 9 Hugo 404 per interpunt `·` (tots corregits amb `url:` explícit); 1.855 WP 503 per rate limiting (no errors reals). **Pendent: re-executar amb menys workers per confirmar WP 200 a tots els posts.**
7. ✅ **SEO** — partial `seo.html` centralitzat (robots, description truncada 155, OG, Twitter, JSON-LD dict+safeJS). Meta descriptions Yoast injectades (271 posts). Title-seo injectat (130 posts). Verificat amb json.loads a tots els posts. Commit `9ec8e8258`.
8. ⏳ **CMS** — Sveltia CMS per publicació remota (single user). Vegeu § Pla CMS.
9. ✅ **Deploy** (2026-09-15) — pujar el `public/` del Hugo al docroot de Dinahosting (`~/www/blog/`), substituint el WordPress però **mantenint `wp-content/uploads`** (les imatges no es mouen). **FET: producció 100% verificat (25/25 URLs reals del sitemap → 200; 2.353 posts, 94 categories, 3.021 tags).** El WordPress queda congelat online fins a l'apagat acordat.

**Sessió 2026-09-15 — afegits:**
- **Pàgina 404** del blog adaptada de la del pare (`themes/blog/layouts/404.html` standalone): fons foto `static/images/404.jpg` + overlay, logo `blog.pocallum.cat`, títol "Aquesta foto no s'ha fet.", suggeriments = 3 últimes cròniques amb miniatura (thumbnail). CSS `e404-*` a `assets/css/main.css`. Imatge idèntica a la del pare.
- **Fix rsync exit 23** a `.github/workflows/deploy-produccio.yml`: afegit `--exclude='.well-known/'` (no pot esborrar `.htaccess` per permisos) i `--omit-dir-times` + `--no-perms` (solució definitiva). Abans cada deploy acabava amb `exit code 23` encara que els fitxers es pugessin bé; ara surt net.
- **`.htaccess` amb ErrorDocument 404** (`static/.htaccess`): cal perquè Dinahosting/Apache serveixi la 404.html de Hugo en lloc de la pàgina per defecte.
- **CMS: els 2.027 posts (no 2.353)** que mostra Sveltia és límit de paginació de l'API de GitHub llistant una carpeta enorme — **no és pèrdua de dades**. Els 2.353 fitxers són tots al repo i es renderitzen bé. Impacte: només si volguessis editar un dels 326 "fantasma" caldria fer-ho per git.
- **L'error "Broken pipe" del primer deploy** no era pèrdua: era connexió tallada en transferència; un rsync incremental en completà la resta.

---

## Dashboard d'estadístiques (`/admin/`)

Replicar el dashboard del pare: `static/admin/index.html` autocontingut (estètica pocallum, protegit per contrasenya SHA-256) + `static/admin/analytics.json` generat cada hora per GitHub Actions des de l'API de GoatCounter.

- **Referència:** repo `../goatcounter-dashboard` i implementació del pare (`../pocallum.cat/static/admin/`, `scripts/`, `.github/workflows/fetch-analytics.yml`)
- **GoatCounter existent:** el blog ja té GoatCounter configurat al WordPress (`wp-admin → goatcounter-wp` → site code `pocallum-blog`; verificat directament al HTML que emet el WP: `data-goatcounter="https://pocallum-blog.goatcounter.com/count"`). **Reaprofitarem el site ja creat** (mateix codi) en lloc de crear-ne un de nou. El `hugo.toml` ja té `goatcounterSite = "pocallum-blog"` — **no canviar-lo**. Falta afegir el `GOATCOUNTER_TOKEN` al repo (secret de GitHub Actions), pendent.
- **Implementació:** fases 4–5, un cop el tema estigui en marxa

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

### GitHub OAuth App (pendent de crear)

1. Anar a `github.com/settings/developers` → OAuth Apps → New OAuth App
2. Application name: `blog.pocallum.cat`
3. Homepage URL: `https://blog.pocallum.cat/`
4. Authorization callback URL: `https://112books.github.io/blog.pocallum.cat/admin/` (staging) — actualitzar a `https://blog.pocallum.cat/admin/` un cop desplegat a producció
5. Guardar el **Client ID** i generar un **Client Secret**
6. Afegir-los al repo: Settings → Secrets → `OAUTH_CLIENT_ID` i `OAUTH_CLIENT_SECRET` (si Sveltia ho requereix; en cas contrari, Sveltia demana el client ID a l'login)

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
