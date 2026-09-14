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

### 3. Comentaris
- Els **71 comentaris llegats es congelen** com a contingut estàtic dins dels posts.
- Per a comentaris nous: **servei extern — giscus** (recomanat): open source, sobre GitHub Discussions, sense cookies ni tracking, integrable a GitHub Pages. Requereix compte GitHub per comentar (fricció acceptable: 71 comentaris en 15 anys). **Pendent de validació en fase de tema; si no s'adopta, el blog queda sense comentaris nous.**
- Descartat: Disqus (tracking, contra la filosofia del projecte).

### 4. Imatges: romanen al servidor de producció
- Les imatges **no es copien al repo**: es queden a `~/www/blog/wp-content/uploads/` i el Hugo les referencia amb rutes relatives (`/wp-content/uploads/...`) — cap canvi d'URL.
- **Staging:** els posts hi mostren les imatges amb **URLs absolutes al servidor** (`https://blog.pocallum.cat/wp-content/uploads/...`).
- **Local:** mode sense connexió mitjançant rsync a `static/uploads/` (gitignored).
- Posts nous: imatges a `static/uploads/` o page bundles (publicades com a `/uploads/...`), a decidir en fase de tema.

### 5. Imatges: optimització mantingent qualitat
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
```

- Els posts nous porten **prefix de data al nom de fitxer i al títol** (`2026-09-14-titol.md` → URL `/2026/09/14/2026-09-14-titol/`), com al WordPress.
- El repo GitHub és `112books/blog.pocallum.cat` (pendent de crear; afegir `origin` quan existeixi).

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

1. **Exportació** — XML complet de WordPress + còpia de `wp-content/uploads`. **Mesurar mida total d'imatges** (ja fet: 3,4 GB totals; 2,3 GB originals → decisió Dinahosting).
2. **Scaffolding** — `hugo new site`, `hugo.toml` amb permalinks idèntics, taxonomies, RSS.
3. **Conversió** — XML → Markdown (`wordpress-export-to-markdown`, `wp2hugo` o `exitwp`). Validar: 2.353 posts, dates, categories, tags, slugs.
4. **Tema** — llistat cronològic, single, arxiu mensual, càmeres/taxonomies, cerca Pagefind, RSS, comentaris estàtics + giscus.
5. **Pàgines fixes** — About, Avís Legal, Contacte, Cerca, legal.
6. **QA** — comparativa d'URLs 1:1 WordPress vs Hugo.
7. **Deploy** — pujar el `public/` del Hugo al docroot de Dinahosting (`~/www/blog/`), substituint el WordPress però **mantenint `wp-content/uploads`** (les imatges no es mouen). Staging via GitHub Pages (branca `develop`). **Ordre obligatori (lliçó apresa del pare):** pujar HTML + verificar el build *abans* de fer cap canvi de DNS o apagar el WordPress. Apagat en dues passes (freeze + backup).

---

## Dashboard d'estadístiques (`/admin/`)

Replicar el dashboard del pare: `static/admin/index.html` autocontingut (estètica pocallum, protegit per contrasenya SHA-256) + `static/admin/analytics.json` generat cada hora per GitHub Actions des de l'API de GoatCounter.

- **Referència:** repo `../goatcounter-dashboard` i implementació del pare (`../pocallum.cat/static/admin/`, `scripts/`, `.github/workflows/fetch-analytics.yml`)
- **Secret requerit:** `GOATCOUNTER_TOKEN` al repo (cal site GoatCounter nou per al blog, p. ex. `blog-pocallum`)
- **Implementació:** fases 4–5, un cop el tema estigui en marxa

---

## Segona fase (post-migració)

- **CMS de publicació remota** — objectiu: poder publicar posts mentre es viatja, sense necessitat de l'ordinador amb el repo. Candidats: Decap CMS o Sveltia CMS (backend git sobre GitHub, compatible amb GitHub Pages). A decidir i implementar quan la migració estigui en producció.

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
