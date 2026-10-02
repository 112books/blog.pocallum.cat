# Auditoria SEO i IA — blog.pocallum.cat (2026-10-02)

- **Abast:** blog complet (2.397 posts, ~3.000 etiquetes, 92 categories, ~6.700 pàgines reals) + revisió read-only de la web mare `pocallum.cat`.
- **Mètode:** build net local `hugo --minify` (v0.166.0; CI fixa v0.164.0) + anàlisi programàtica del HTML + comprovacions HTTP de només lectura a producció.
- **Objectiu declarat per l'usuari:** SEO i IA per **captar clients per a la web mare**.
- **Nota:** aquesta auditoria actualitza `AUDITORIA-SEO-IA-2026-09-29.md`; molts dels seus P0 ja estan aplicats i verificats.
- **Actualització (mateixa sessió):** s'han implementat les accions **P0 i P1** —sufix curt del `<title>` (` · Pocallum`), bloc **CTA de captació** al final dels posts, `robots.txt` amb agents d'IA explícits, **`llms-full.txt`** (584 KB, 3.231 entrades), `CollectionPage`/`ItemList` a taxonomies i termes, enllaç **`/tags/`** al peu i `rel="me"`/`sameAs` blog↔pare. Verificat: títols de post > 60 car. del **84% → 31%** (mediana 77 → 50).

---

## Resum executiu

| # | Estat | Trobada | Impacte |
|---|-------|---------|---------|
| 1 | 🔴 Obert | **2.023 de 2.397 posts (84%)** amb `<title>` > 60 car. (mediana **77**, p90 **107**) pel sufix `" — Blog de Pocallum — camera & action!"` | Títols truncats a SERP → menys CTR |
| 2 | 🟠 Obert | **Sense CTA contextual dins dels posts** cap a serveis/portfoli de `pocallum.cat` | Es perd la conversió amb la intenció més alta |
| 3 | 🟠 Obert | Pàgines de **taxonomia (tags/categories) sense JSON-LD** `CollectionPage`/`ItemList` | Rich results i GEO |
| 4 | 🟠 Obert | `robots.txt` **no declara explícitament** els agents d'IA (només un comentari) | GEO/AEO |
| 5 | 🟠 Obert | Sense `llms-full.txt` (índex complet) | GEO/AEO |
| 6 | 🟡 Obert | **2.368 imatges de post sense `alt`** (3,0%) | Google Images / a11y |
| 7 | 🟡 Obert | Algunes imatges externes mortes (19) de tercers | Imatge trencada |
| 8 | 🟡 Obert | Sense `google-site-verification` | Search Console |
| 9 | 🟢 Oportunitat | `dateModified = date` (sense senyal de frescor real) | Rastreig |
| 10 | 🟢 Oportunitat | 14 posts amb títol duplicat / 814 amb data al títol | Duplicació / soroll |

**Verificat com a correcte (millores des del 29/09):** `sitemap.xml` **sense** `X-Robots-Tag: noindex`; redirects `/tags/`, `/categories/`, jeràrquics i `/tags/page/N/` acaben a **HTTPS 200**; **0 descripcions buides** als posts (mediana 77 car.); `/admin/` amb `noindex`; JSON-LD `BlogPosting` + `BreadcrumbList` + `Person`/`Organization` amb `sameAs`; `og:image` amb amplada/alçada i `article:*`; `llms.txt` operatiu; variants WebP `-800`/`-2500` **100% presents**; 0 enllaços interns trencats; hub `/categories/` enllaçat des del menú (capçalera i peu) a totes les pàgines (el `/tags/` encara no).

---

## 1. On-page

### 1.1 Títols — el principal pendent 🔴
- Sufix actual `.Site.Title` = `"Blog de Pocallum — camera & action!"` → suma **41 caràcters** a cada títol.
- Mesura sobre el build net (només posts, sense àlies):
  - **2.023 / 2.397** títols > 60 car.
  - Mediana **77** car., p90 **107** car.
  - El "core" del títol sol ser ~39 car., així que el problema és gairebé tot sufix.
- **Recomanació:** sufix curt per a posts: `" · Pocallum"` (11 car.) o treure'l. Es pot fer només a `<title>`/`og:title` sense tocar el títol visible. Guany immediat de CTR.
- 814 posts comencen amb data al títol (`2026-09-19 - …`); la URL ja porta la data → es pot netejar només al `<title>`.

### 1.2 Meta descripcions ✅
- **0 buides** (abans 426). Mediana 77 car., dins del rang òptim.
- Pendent menor: 14 grups de descripcions duplicades entre posts.

### 1.3 Imatges
- **2.368 / 78.910** sense `alt` (3,0%; abans 4.412).
- Variants WebP de `srcset`: **100% existeixen** (4.783 provades).
- Originals locals: **100% 200** (3.404 provades).
- **19 imatges externes trencades** (1,1% de 1.690): vegeu §5.

### 1.4 Enllaçat intern ✅
- Hub `/categories/` present al menú de capçalera i peu a **6.739 pàgines**. ⚠️ El hub `/tags/` té **0 enllaços interns** (només és al sitemap i a `llms.txt`) → convé afegir-lo (p. ex. al peu o a la pàgina de cerca).
- 0 posts orfes, 0 enllaços interns trencats (auditoria 29/09, es manté).

---

## 2. Dades estructurades

- **Posts:** `BlogPosting` + `BreadcrumbList` complets (headline, description, dates, author, publisher, image, articleSection, keywords, wordCount).
- **Home:** `WebSite` + `SearchAction`.
- **Manca:** `CollectionPage`/`ItemList` a les pàgines de terme i als hubs de taxonomia (3.087 pàgines sense cap JSON-LD). Baix risc, alt valor GEO ("càmeres amb què he fotografiat").
- **Entitat autor:** `Person` amb `@id`, `url` (/about/) i `sameAs` (Instagram, Facebook). Es pot afegir **`sameAs` cap a pocallum.cat** i `rel="me"` per reforçar E-E-A-T.

---

## 3. IA / GEO / AEO

### 3.1 Blog
- `llms.txt` ✅ operatiu (mapa del lloc + 15 darreres cròniques).
- `robots.txt` ✅ tot permès, però els agents d'IA només apareixen **en un comentari**.
- **Recomanacions:**
  1. Blocs `User-agent` **explícits** amb `Allow: /`: GPTBot, OAI-SearchBot, ChatGPT-User, ClaudeBot, Claude-User, PerplexityBot, Google-Extended, Applebot-Extended, CCBot, Bytespider, Amazonbot, meta-externalagent.
  2. `llms-full.txt`: índex complet (tots els posts + categories + etiquetes + autors) perquè els agents el puguin citar.
  3. Enllaç `llms.txt` des del `<head>` (`<link rel="llms" href="/llms.txt">`) — convenció creixent.
- **Punt feble de citabilitat:** mediana de **37 paraules/post** (llegat). Una frase de context per post (o captions) ajudaria molt que un assistent pugui extreure respostes. És la palanca GEO més gran a llarg termini.

### 3.2 Web mare (`pocallum.cat`, repo separat)
- `llms.txt` **molt bo**: serveis, credencials, publicacions i llicència **RSL 1.0** ("AI retrieval, not training").
- JSON-LD `LocalBusiness`+`Photographer` complet (adreça, geo, horaris, `areaServed`, `knowsAbout`, telèfon) + `WebSite`.
- Sitemap multilingüe (`/ca/`, `/en/`).
- `robots.txt` **només** `User-agent: *` → falta la línia `Sitemap:` i, si es vol, els blocs d'IA.
- Nota menor: `WebSite.description` amb cometes escapades dobles al text.

---

## 4. Captació de clients (blog → web mare) 🎯

**El que ja hi és bé:**
- Enllaç **"Pocallum.cat"** al menú de capçalera **i** al peu de **totes** les pàgines (`target="_blank"`).
- `Organization.url` de l'estructura apunta a `pocallum.cat`.
- Pàgina `/contact/` amb correu i enllaç a `pocallum.cat/contacte/`.

**El que falta (impacte directe en conversió):**
1. **Cap CTA contextual dins dels posts.** Un lector que acaba una crònica d'un concert és el moment de màxima intenció. Cal un bloc al final del post (abans dels comentaris): una frase + enllaç a serveis/portfoli/contacte del web mare.
2. El text de l'enllaç del menú és només "Pocallum.cat"; no comunica **què ofereix** (fotografia de cultura/directe). Un `aria-label`/`title` o un text "Serveis de fotografia" ajudaria.
3. Afegir `sameAs`/`rel="me"` cap a `pocallum.cat` (i viceversa) per lligar les dues entitats als ulls de Google i dels LLM.

**Idea concreta (baix esforç, alt retorn):** al `single.html`, després del contingut, un bloc estil targeta:
> *"Soc en Joan Linux Martínez, fotògraf de cultura en directe a Barcelona. Fotografio concerts, festivals i arts escèniques des del 2002. Si necessites fotografia per a un esdeveniment → [pocallum.cat](https://pocallum.cat)"*

amb enllaç a `pocallum.cat` (serveis/contacte). Es pot fer servir el títol del post i la categoria per personalitzar-lo.

---

## 5. Imatges trencades (19, totes externes)

| Host | N | Posts |
|------|---|-------|
| `pocallum.cat/sites/default/files/*` | 10 | `worldwide-pinhole-photography-day-2017…` (rutes velles Drupal del web mare) |
| `awpcp.org/wp-content/uploads/2025/04/*` | 4 | `27-04-2025-dia-mundial-de-la-fotografia-estenopeica-2025` |
| `lh3.googleusercontent.com…authuser=0` | 2 | posts 3129, 3206 (enllaços privats/caducats → `accounts.google.com`) |
| `i0.wp.com/112gallery.eu/…` | 1 | `exposicio-gent-de-nou-barris-gent-darreu` |
| `upload.wikimedia.org/…/Sparschwein_Haspa03.jpg` | 1 | `money-money-i-mes-money` |
| `www.zeroimage.com/Pinhole/zero2000_film.jpg` | 1 | `estrenant-la-camera-estenopeica-zero-2000` |

**Accions possibles:** rehostar les que es puguin recuperar (Wayback/local), o bé reemplaçar/retirar. Les 10 de `pocallum.cat/sites/default/files` són del web mare: val la pena mirar si existeixen en una altra ruta al servidor nou abans de donar-les per perdudes.

---

## 6. Pla d'acció prioritzat

### P0 — impacte alt, esforç baix
1. **Escurçar el sufix del `<title>`** a `" · Pocallum"` (o treure'l als posts). ~2.000 títols a SERP.
2. **Bloc CTA de captació** al final de cada post → `pocallum.cat`.
3. **`google-site-verification`** (acció de l'usuari: meta tag o DNS TXT).

### P1 — curt termini
4. `robots.txt`: blocs explícits d'agents d'IA + `Sitemap:`.
5. `llms-full.txt` + `<link rel="llms">`.
6. JSON-LD `CollectionPage`/`ItemList` a taxonomies.
7. `sameAs`/`rel="me"` blog ↔ web mare.

### P2 — mitjà termini
8. `alt` a les 2.368 imatges que en manquen (derivable del títol/categoria).
9. Rehostar/reparar les 19 imatges externes trencades.
10. `lastmod`/`enableGitInfo` per a senyal de frescor real.
11. 1 frase de context als posts més prims (palanca GEO).

### Web mare (repo separat, no es toca des d'aquí)
12. Afegir `Sitemap:` a `pocallum.cat/robots.txt`.
13. Aprofitar el CTA del blog i el `sameAs` creuat.

---

## 7. Mètriques de referència (build net 2026-10-02)

| Mètrica | Valor |
|---|---|
| Posts | 2.397 |
| Posts amb `<title>` > 60 car. | 2.023 (84%) |
| Mediana / p90 del títol | 77 / 107 car. |
| Posts amb descripció buida | 0 |
| Mediana descripció | 77 car. |
| Imatges de post / sense `alt` | 78.910 / 2.368 (3,0%) |
| Variants WebP provades / existents | 4.783 / 4.783 |
| Originals locals provats / 200 | 3.404 / 3.404 |
| Imatges externes / trencades | 1.690 / 19 |
| Enllaços interns a hubs de taxonomia | presents via menú a totes les pàgines |
