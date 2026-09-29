# Auditoria SEO i IA — blog.pocallum.cat

- **Data:** 2026-09-29
- **Abast:** tot el lloc (2.357 posts, 3.035 etiquetes, 92 categories, 207 pàgines d'arxiu, ~6.700 pàgines reals + 3.338 àlies)
- **Mètode:** build net local `hugo --minify -d public-audit` (Hugo v0.166.0, CI fixa v0.164.0) + anàlisi programàtica del HTML generat + comprovacions HTTP de només lectura sobre producció
- **Producció:** `https://blog.pocallum.cat` (Dinahosting)
- **Nota:** el `public/` del repo és obsolet (barreja rutes antigues `/tags/`, `/categories/` amb les noves); totes les xifres són del build net.

---

## Resum executiu

| # | Severitat | Trobada | Impacte |
|---|-----------|---------|---------|
| 1 | 🔴 Crític | Els 301 generats per `.htaccess` apunten a `http://` (baixada HTTPS→HTTP + salt extra) | Rastreig, senyals de confiança, sitemap/redirects |
| 2 | 🔴 Crític | `/tags/page/N/` i `/categories/page/N/` → 301 → **404** (259 pàgines trencades) | Rastreig, errors 404 |
| 3 | 🔴 Crític | **426 posts (18%)** amb `<meta name="description" content>` **buit** | CTR i snippets |
| 4 | 🔴 Crític | `sitemap.xml` serveix `X-Robots-Tag: noindex` | Contradicció amb l'index del lloc |
| 5 | 🟠 Alt | Home carrega **~6,3 MB en 12 imatges**; miniatures de fins a 1,2 MB, sense `srcset`/WebP | Core Web Vitals, mòbil |
| 6 | 🟠 Alt | `/categories/` i `/tags/` (hubs de taxonomia) tenen **0 enllaços interns** | Descobribilitat del cercador de càmeres/òptiques |
| 7 | 🟠 Alt | `/admin/` (CMS) és indexable (sense `noindex`) | Pàgina interna a l'índex |
| 8 | 🟠 Alt | 1.894 posts amb `<title>` > 60 car. (sufix de marca massa llarg) | Títols truncats a SERP |
| 9 | 🟡 Mitjà | 3.035 pàgines d'etiqueta amb **descripció idèntica** i 2.305 amb 1 sol post (contingut prim) | Index bloat / qualitat |
| 10 | 🟡 Mitjà | 814 posts amb **data al títol**; 37 grups de títols duplicats | Rellevància i duplicació |
| 11 | 🟡 Mitjà | Schema incomplet: sense `BreadcrumbList`, `Person`/`Organization` amb `sameAs`, `ImageObject`, `articleSection`, `keywords` | Rich results i GEO/IA |
| 12 | 🟡 Mitjà | 4.412 imatges sense `alt`; sense **sitemap d'imatges** | Google Images (canal clau per a un blog de fotografia) |
| 13 | 🟡 Mitjà | 196 pàgines de paginació de portada sense `<h1>` i amb títol idèntic | Qualitat on-page |
| 14 | 🟢 Baix | `robots.txt` no declara explícitament els crawlers d'IA; sense `llms-full.txt` | GEO/AEO (oportunitat) |
| 15 | 🟢 Baix | Sense `google-site-verification` (pendent de l'usuari) | Search Console |

**El que ja està bé:** paritat d'URLs 1:1 (2.360/2.360), 0 enllaços interns trencats, canonical correcte a totes les pàgines (inclosa la paginació amb self-canonical), JSON-LD `BlogPosting`/`WebSite` analitzable a totes les pàgines, `og:*` i Twitter Cards presents, RSS amb `X-Robots-Tag: noindex`, headers de seguretat complets, `llms.txt` operatiu, HSTS i HTTP→HTTPS funcionant.

---

## 1. Rastreig i indexabilitat

### 1.1 `robots.txt` ✅
```
User-agent: *
# Cercadors i crawlers d'IA (GPTBot, ClaudeBot, PerplexityBot, Google-Extended…): benvinguts.
Disallow:

Sitemap: https://blog.pocallum.cat/sitemap.xml
```
Correcte: tot permès i sitemap declarat. El comentari és només per a humans (no és una directiva). Es pot reforçar amb regles `User-agent` explícites per a IA (vegeu §8).

### 1.2 `sitemap.xml` ⚠️
- **5.702 URLs**, 705 KB (límit 50.000/50 MB): sense risc de tall.
- Composició: 2.357 posts, 3.035 etiquetes, 93 categories, 207 arxiu, 2 hubs, 8 altres.
- `<lastmod>` a 5.701 URLs (bona senyal de frescor).
- La paginació **no** s'inclou (correcte).
- ❌ **Bug:** el `.htaccess` aplica `X-Robots-Tag: noindex` a **tot** fitxer `.xml$`, cosa que inclou el propi `sitemap.xml`:
```apache
<FilesMatch "\.xml$">
  Header set X-Robots-Tag "noindex"
</FilesMatch>
```
Verificat en producció: `x-robots-tag: noindex` a `/sitemap.xml`. Confús i incorrecte (la intenció era noindexar els feeds). **Fix:** limitar-ho a `feed.xml`:
```apache
<Files "feed.xml">
  Header set X-Robots-Tag "noindex"
</Files>
```
- Oportunitat: afegir un **sitemap d'imatges** (`<image:image>`) — el blog és fotogràfic. Hugo no ho fa sol perquè el frontmatter usa `image:`/`thumbnail:` i no `images:[]`; cal un `layouts/sitemap.xml` propi.

### 1.3 `llms.txt` ✅
Present a `/llms.txt` (200, `text/plain`). Conté títol, resum, mapa del lloc i les 15 darreres cròniques amb resum. Correcte com a punt de partida.

### 1.4 Canonicals ✅
`<link rel="canonical">` a **totes** les pàgines reals. La paginació usa self-canonical (`/page/N/`), no canonicalitza a l'arrel — correcte. Els àlies (3.338, `/page/1/`, `/tag/…/page/1/`) tenen canonical al pare. Bé.

### 1.5 `noindex` / `robots` ✅⚠️
- `index, follow` a totes les pàgines públiques; `404.html` amb `noindex`.
- ❌ `static/admin/index.html` **no** té `noindex` (427 pàgines indexables si s'hi enllaça). `static/stats/index.html` sí que en té.

### 1.6 Àlies i paginació
- 3.338 àlies de redirecció (`http-equiv=refresh`), correctes.
- ⚠️ Hugo genera `/tags/page/2..253/` i `/categories/page/2..8/` que renderitzen **el mateix contingut que el hub** (3.035 enllaços a termes a cada pàgina) amb self-canonical. Són duplicats exactes, orfes (no s'enllacen des del hub) i fora del sitemap. Impacte baix però convé resoldre'ls (vegeu §2.2).

---

## 2. Paritat d'URLs i redireccions

### 2.1 🔴 Baixada HTTPS→HTTP als 301
Tots els `RewriteRule` amb `[R=301]` emeten un `Location: http://…` perquè Apache, darrere el proxy de Dinahosting, rep HTTP intern. Verificat en producció:

| URL sol·licitada | 301 Location |
|---|---|
| `https://…/tags/plouen/` | `http://…/tag/plouen/` |
| `https://…/category/camara/leica-m6/` | `http://…/category/leica-m6/` |
| `https://…/tags/page/2/` | `http://…/tag/page/2/` |

Conseqüència: cada redirecció fa **2 salts** (HTTPS → HTTP → HTTPS) i una baixada de protocol. **Fix:** fer absolutes les substitucions a HTTPS:
```apache
RewriteRule ^tags/([^/]+)/?$ https://%{HTTP_HOST}/tag/$1/ [R=301,L]
RewriteRule ^categories/([^/]+)/?$ https://%{HTTP_HOST}/category/$1/ [R=301,L]
# …i així amb tots els [R=301]
```

### 2.2 🔴 `/tags/page/N/` i `/categories/page/N/` → 404
La regla genèrica `^tags/(.+)$` també captura la paginació del hub:
```
/tags/page/2/       → 301 → /tag/page/2/       → 404
/categories/page/2/ → 301 → /category/page/2/  → 404
```
Són **252 + 7 = 259 pàgines** que acaben en 404. **Fix:** limitar la regla a un sol segment i excloure `page`:
```apache
RewriteRule ^tags/([^/]+)/?$ https://%{HTTP_HOST}/tag/$1/ [R=301,L]
RewriteRule ^categories/([^/]+)/?$ https://%{HTTP_HOST}/category/$1/ [R=301,L]
```

### 2.3 ⚠️ Canvis locals sense desplegar
`static/.htaccess` té **11 línies afegides no confirmades** (redireccions de `/YYYY/MM/DD/slug/feed/`, `/author/*`, `/category/camara|optioca/`). No són a producció fins que es faci commit + push. A més, hereten el problema §2.1 (Location a http). Cal revisar-les i desplegar-les juntes.

### 2.4 Paritat
2.360/2.360 URLs amb 200 (QA `scripts/qa-urls.py`). /feed/ i /comments/feed/ redirigeixen/serveixen correctament. /author/* → home. Bé.

---

## 3. On-page

### 3.1 Títols
- Mediana del títol **complet: 76 car.** (1.894 > 60, 1.480 > 70). El sufix `" — Blog de Pocallum — camera & action!"` fa **41 caràcters**. El títol "core" té mediana 39 i només 399 > 60.
- **Recomanació:** escurçar el sufix a `" · Pocallum"` (o treure'l als posts). Guany immediat de llegibilitat a SERP.
- **814 posts** comencen el títol amb data (ex. `2026-09-19 - Festa Major…`). La URL ja porta la data → soroll a SERP. Es pot netejar a `seo.html` (només per al `<title>`/`og:title`) o via `title-seo`.
- **37 grups de títols duplicats** (76 posts), ex. `Barcelona`, `Assaig al barri`. Sovint comparteixen categoria/URLs semblants.
- Només **134 posts (5%)** tenen `title-seo` i **276 (11%)** tenen `description` al frontmatter.

### 3.2 Meta descripcions
- ❌ **426 posts amb description buida.** Causa arrel a `themes/blog/layouts/partials/seo.html`: per a posts només amb imatge, `.Summary` no és buit (conté el markup de la imatge) però `plainify` el deixa a `""`, i `$desc` s'assigna a buit en lloc de conservar el fallback del lloc. Exemple real: `/2013/03/27/jamborees-backstage/`.
  **Fix suggerit:**
  ```go
  {{- if eq (strings.TrimSpace $desc) "" -}}
    {{- $desc = .Site.Params.description | plainify | strings.TrimSpace | truncate 155 -}}
  {{- end -}}
  ```
  (millor encara: generar una descripció derivada del títol + categories si no hi ha text).
- **3.035 pàgines d'etiqueta i 92 de categoria** comparteixen la mateixa descripció genèrica del lloc `"Crònica fotogràfica tal com raja. Des del 2010."` → descripcions duplicades massives. **Fix:** generar descripció per terme (nom + nombre de posts), p. ex. `"318 cròniques fotografiades amb Leica-M6."`.
- 20 grups de descripcions duplicades entre posts (59 posts) per resums idèntics; 1 sola descripció > 160 car. La truncació a 155 funciona.

### 3.3 Encapçalaments
- 2 posts amb **dos `<h1>`** (`2026-06-22a25-barcelona-big-blues-band…`, `2011/02/19/per-fi-la-tv-publica…`).
- **196 pàgines de paginació de portada sense `<h1>`** (el hero només es renderitza a la pàgina 1). També 196 amb el mateix `<title>` i la mateixa descripció.
- La resta (posts, termes, arxiu) tenen exactament 1 `<h1>`. Bé.

### 3.4 Enllaçat intern
- **1.234.622 enllaços interns**, mediana de **93 enllaços entrants per post**, **0 posts orfes** (els 19 casos aparents eren artefactes de percent-encoding en URLs amb caràcters com `·`, `ç`, `ï`).
- **0 enllaços interns trencats** (l'únic "trencat" local és `/pagefind/pagefind-ui.css`, que existeix a producció).
- ❌ **0 enllaços cap a `/categories/` i `/tags/`** des de cap plantilla. Els hubs de taxonomia només són accessibles pel sitemap/llms. **Fix:** afegir "Càmeres i òptiques" al menú o al peu.

### 3.5 Imatges
- Posts: 77.905 `<img>`, **4.412 sense `alt`** (5,7%) i 192 amb `alt=""`.
- Miniatures de llistat: `alt=""` (decoratiu, acceptable), però per a un blog de fotografia convé `alt` amb el títol del post per a Google Images.
- Noms de fitxer del llegat poc SEO (`IMG_5673.jpg`, `DSCF6763.jpg`), difícils de canviar sense tocar el servidor.

---

## 4. Dades estructurades (Schema.org)

### Què hi ha
- **Home:** `WebSite` amb `SearchAction` apuntant a `/cerca/?q={search_term_string}` (coincideix amb el `?q=` de Pagefind).
- **Posts:** `BlogPosting` amb `headline`, `description`, `datePublished`, `dateModified`, `mainEntityOfPage`, `author`, `publisher`, `url`, `image`.
- 0 errors de parseig. Tots els posts en tenen.

### Què falta (alt valor per SEO + IA)
- `@id` estables i `sameAs` (xarxes socials) per a `Person` i `Organization` → ajuda els motors d'IA a desambiguar l'autor/editor.
- `author.url` (p. ex. `/about/` o `about.pocallum.cat`), `author.sameAs` (Instagram, Facebook).
- `publisher.logo` (ImageObject) — necessari per a rich results d'organització.
- `image` hauria de ser un `ImageObject` amb `url`/`width`/`height`/`caption`.
- `BreadcrumbList` als posts (Inici › Categoria › Post).
- `articleSection`, `keywords` (tags), `inLanguage`, `wordCount`, `isAccessibleForFree`.
- `CollectionPage`/`ItemList` a les pàgines de taxonomia (ara no tenen cap JSON-LD).
- `dateModified` = `date` sempre (`enableGitInfo=false`, sense `lastmod`): no hi ha senyal de frescor real. Considerar `enableGitInfo=true` o un `lastmod` explícit.

---

## 5. Open Graph / X Cards

Presents i correctes a totes les pàgines: `og:site_name`, `og:locale=ca_ES`, `og:title`, `og:description`, `og:type` (article/website), `og:url`, `og:image`, `twitter:card/title/description/image`.

Mancances:
- `article:published_time`, `article:modified_time`, `article:author`, `article:section`, `article:tag`.
- `og:image:width`, `og:image:height`, `og:image:alt` (`ogImageAlt` no està definit a `hugo.toml`).
- `twitter:site` i `twitter:creator`.
- Cap pàgina sense `og:image$` (totes en tenen gràcies al fallback).

---

## 6. Contingut prim i taxonomies

- **Contingut molt prim:** mediana de **37 paraules** per post; 1.501 posts < 50 paraules, 1.891 < 100, 2.092 < 200. És un blog fotogràfic (llegat amb poc text), però per SEO/IA convé afegir 1-2 frases de context o captions.
- **Etiquetes:** 3.045 úniques, **2.305 usades un sol cop** → 3.035 pàgines d'etiqueta majoritàriament prims i gairebé duplicats. **Recomanació:** `noindex` a etiquetes amb ≤1 post, o consolidar-les.
- **Categories:** 92, bona granularitat (càmeres/òptiques), alineades amb la proposta de valor.
- 28 posts sense categoria i 1.510 sense etiquetes.

---

## 7. Rendiment i Core Web Vitals

- La portada carrega **12 imatges = ~6,3 MB** (úniques). Algunes miniatures són originals de fins a **1,2 MB** mostrades en una graella de ~300 px.
- `imatgesWebp = false` a `hugo.toml`: `partials/img.html` ja sap generar `<picture>` amb `-800.webp` / `-2500.webp`, però no s'usa. `scripts/optimitza-llegat.sh` genera aquests derivats (cal pujar-los al servidor).
- No hi ha `srcset`/`sizes` ni `width`/`height` als `<img>` (CLS depèn de `aspect-ratio` CSS a les graelles; el `prose` no en té).
- CSS 33 KB + JS 5 KB (minificats i amb fingerprint); fonts autoallotjades amb 2 preloads. Bo.
- HTML de portada 3,7 KB gzip; `Content-Encoding: gzip` actiu; HTTP/2. Sense `Cache-Control` explícit als estàtics.

---

## 8. IA / GEO / AEO

**Fortaleses:**
- `llms.txt` operatiu amb mapa i darreres cròniques.
- `robots.txt` permet tots els crawlers (GPTBot, ClaudeBot, PerplexityBot, Google-Extended…).
- Contingut en català, autor identificat, RSS, dates i categories → bona citabilitat.

**Oportunitats:**
- Declarar **explícitament** els agents d'IA a `robots.txt` (`User-agent: GPTBot`, `ClaudeBot`, `PerplexityBot`, `Google-Extended`, `Applebot-Extended`, `CCBot`, `Bytespider` … `Allow: /`) perquè la intenció quedi fora de dubte.
- Afegir `llms-full.txt` (o ampliar `llms.txt`) amb l'índex complet de posts/categories; molts agents en fan ús.
- **Entitat autor:** afegir `Person` amb `sameAs` i `url` a les dades estructurades, i enllaçar `/about/` des dels posts (E-E-A-T).
- **Citabilitat:** els 426 posts sense text i la mediana de 37 paraules dificulten que un motor d'IA extregui respostes. Una frase de resum per post (o reaprofitar l'àlbum/caption) hi ajudaria molt.
- Dades estructurades `BreadcrumbList` i `ImageObject` (vegeu §4).

---

## 9. Accessibilitat relacionada amb SEO
- 4.412 imatges sense `alt` (§3.5).
- 196 pàgines de paginació sense `<h1>`.
- La resta de bones pràctiques (skip-link, focus, contrast) ja es van auditar el 2026-09-15.

---

## 10. Pla d'acció prioritzat

### P0 — immediat (baix esforç, impacte alt)
1. `.htaccess`:
   - Fer absolutes a `https://%{HTTP_HOST}` **totes** les substitucions `[R=301]` (elimina la baixada a HTTP).
   - Canviar `^tags/(.+)$` i `^categories/(.+)$` per `^tags/([^/]+)/?$` i `^categories/([^/]+)/?$` (no trencar `page/N`).
2. `seo.html`: fallback quan la descripció resultant queda buida (arregla 426 posts).
3. `.htaccess`: `X-Robots-Tag: noindex` només a `feed.xml`, no a `sitemap.xml`.
4. `static/admin/index.html`: afegir `<meta name="robots" content="noindex, nofollow">` i/o `X-Robots-Tag` a `static/admin/.htaccess`.

### P1 — curt termini
5. Enllaçar `/categories/` (i `/tags/`) al menú/peu.
6. Escurçar el sufix del `<title>` i netejar la data inicial als títols (`<title>`/`og:title`).
7. Descripcions úniques per a les pàgines de categoria/etiqueta des dels `_index.md`.
8. Activar les variants WebP (`imatgesWebp = true` + pujar `-800.webp`/`-2500.webp`) i afegir `srcset`/`sizes` a llista i hero.

### P2 — mitjà termini
9. Ampliar JSON-LD (Person/Organization+sameAs, BreadcrumbList, ImageObject, articleSection/keywords) i OG d'article.
10. Afegir `alt` a les miniatures de llistat i a les imatges del llegat sense alt.
11. `noindex` o consolidació d'etiquetes amb 1 post; revisar `/tags/page/N/` duplicats.
12. Sitemap d'imatges.
13. `lastmod`/`enableGitInfo` per a senyal de frescor.

### P3 — baix
14. `llms-full.txt`; regles explícites per a IA a `robots.txt`.
15. `noindex` a la paginació del hub d'etiquetes/categories si es manté.
16. Verificació de Search Console (`google-site-verification`).
17. Alinear la versió de Hugo del CI (0.164) amb la local (0.166) i corregir l'avís `languageCode` → `locale`.

---

## 11. Mètriques de referència (build net 2026-09-29)

| Mètrica | Valor |
|---|---|
| Pàgines reals / àlies | 6.673 / 3.338 |
| Posts | 2.357 |
| Etiquetes / Categories | 3.035 / 92 |
| Sitemap URLs | 5.702 |
| Posts amb │description│ no buida | 1.931 (82%) |
| Posts amb │description│ buida | 426 (18%) |
| Posts amb │description│ al frontmatter | 276 (11%) |
| Posts amb │title-seo│ | 134 (5%) |
| Títol complet > 60 car. | 1.894 |
| Grups de títols duplicats | 37 (76 posts) |
| Grups de descripcions duplicades (posts) | 20 (59 posts) |
| Imatges de post sense alt | 4.412 / 77.905 |
| Enllaços interns | 1.234.622 |
| Posts orfes | 0 |
| Enllaços interns trencats | 0 |
| Pes imatges portada | ~6,3 MB (12 imatges) |

---

## Annex — comandes de verificació

```bash
# Build net i auditoria
rm -rf public-audit && hugo --minify -d public-audit

# Redirects (producció, només lectura)
curl -sSI https://blog.pocallum.cat/tags/plouen/ | grep -i '^location'
curl -sSL -o /dev/null -w '%{url_effective} %{http_code}\n' https://blog.pocallum.cat/tags/page/2/

# X-Robots del sitemap
curl -sSI https://blog.pocallum.cat/sitemap.xml | grep -i x-robots

# Descripcions buides
grep -rl '<meta name=description content>' public-audit | wc -l
```
