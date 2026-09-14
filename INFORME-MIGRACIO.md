# Migració blog.pocallum.cat — de WordPress a Hugo
**Data:** 2026-09-14 | **Estat:** Fase 3 en curs. Conversió XML→Markdown feta, post-processament pendent.

> La font de veritat operativa del projecte és **[CLAUDE.md](CLAUDE.md)**.

---

## Contexte

El blog viu actualment en WordPress a `blog.pocallum.cat`, en català, amb una arquitectura consolidada des del 2010:

| Dada | Valor |
|------|-------|
| Posts | 2.353 |
| Paraules | 137.029 |
| Categories | 96 (majoritàriament càmeres i òptiques) |
| Etiquetes | 3.177 |
| Comentaris | 71 |
| Arxiu mensual | desembre 2010 → avui (~16 anys) |
| Permalinks | `/YYYY/MM/DD/slug/` |
| Pàgines fixes | Inici, About, Avís Legal, Contacte, Cerca, legal (privacitat/cookies) |

El web pare (`pocallum.cat`) ja és un Hugo migrat, amb tema propi `themes/pocallum`, GitHub Pages, Pagefind, i una pàgina d'entrada al blog a `/blog/` amb estadístiques i narrativa.

---

## Opcions

| | **Un sol projecte** (blog integrat a pocallum.cat) | **Dos projectes** (blog com a site Hugo independent) |
|---|---|---|
| URLs | Canvien → milers de redireccions 301, reindexació lenta | **Idèntiques** (`permalinks` replica `/YYYY/MM/DD/slug/`) |
| SEO | Risc de pèrdua de posicionament acumulat des del 2010 | **Neutre**: Google veu el mateix subdomini amb el mateix contingut |
| Build | +2.353 posts i milers de pàgines de taxonomia al build del pare | Builds ràpids i acotats per separat |
| Git | Històric barrejat, repo molt més gran (15 anys de fotos) | Repos nets amb cicles de vida independents |
| Idiomes | Col·lisiona amb el multilingüe ca/en del pare (posts sense versió EN) | Blog monolingüe català, sense friccions |
| Manteniment | Un sol lloc per a tot | Dues configuracions, però cadascuna més simple |

## Recomanació: **dos projectes**

L'argument decisiu és la **preservació d'URLs**. Hugo pot reproduir els permalinks de WordPress exactament (`/:year/:month/:day/:slug/`), així ni Google ni els enllaços entrants noten el canvi. Una fusió al domini pare imposaria redireccions massives i un impacte SEO innecessari.

Arguments de suport:

1. **Escala de taxonomies.** 96 categories sobre càmeres/òptiques i 3.177 etiquetes generen milers de pàgines d'arxiu. En projecte propi es governen sols (es poden fins i tot redefinir: separar taxonomia "càmera" d'"etiqueta").
2. **Cicles de vida diferents.** El blog publica sovint (crònica); el pare canvia poc. Deploys i històrics independents = menys soroll i builds ràpids.
3. **Idiomes.** El blog és només en català; el pare és ca/en. Fusionar forçaria a gestionar 2.353 posts sense traducció dins d'una configuració multilingüe.
4. **L'arquitectura actual ja funciona així.** El pare té una pàgina gateway `/blog/` dissenyada per enllaçar al subdomini; el blog WordPress ja enllaça de tornada a pocallum.cat. Canviar el motor sense canviar l'arquitectura d'informació.

---

## Tàctica (2026-09-14)

> **Desenvolupar-ho TOT i aprovar-ho a GitHub Pages (les imatges es veuen allà on són ara, al servidor).** Un cop aprovat: **backup complet del WordPress → deploy del Hugo a la URL de producció (Dinahosting) → verificar → esborrar el WordPress.** El WordPress no es toca fins al tall final.

---

## Decisions preses (2026-09-14)

1. **Tema.** Nou, derivat del sistema de disseny de `themes/pocallum` (paleta, fonts, capçalera/peu), però **mantenint els elements del blog actual**: cronologia, arxiu mensual i, sobre tot, **cerca per càmera i òptica** — és un blog de fotògraf i aquesta taxonomia és ciutadana de primera classe.
2. **Hosting i tàctica (clarificat 2026-09-14).** **Es desenvolupa tot al staging (GitHub Pages, branca `develop`)** amb **les imatges allà on són ara** (URLs absolutes a `https://blog.pocallum.cat/wp-content/uploads/...`). El WordPress **roman online i intacte** durant tot el desenvolupament. Només quan el staging està complet i aprovat: backup complet → deploy del Hugo al docroot de producció a Dinahosting (`~/www/blog/`, mantenint `wp-content/uploads`) → verificar 1:1 → **aleshores** esborrar el WordPress. Motiu de la producció a Dinahosting: 2,3 GB d'originals → fora de límits de GitHub Pages; el servidor ja té SSL + espai + les imatges + els formularis.
3. **Comentaris.** Els 71 llegats es congelen com a contingut estàtic. Per a nous: servei extern **giscus** (GitHub Discussions, sense cookies ni tracking) — pendent de validació en fase de tema; si no s'adopta, el blog queda sense comentaris nous.
4. **Imatges.** Les originals **romanen al servidor** (`/wp-content/uploads/...`, rutes relatives als posts). **Staging:** URLs absolutes al servidor. **Local:** rsync a `static/uploads/` (gitignored).
5. **Optimització d'imatges (alta qualitat).** Les originals **mai es toquen**. El llegat no es processa. Els nous posts s'optimitzen a WebP (~q85, 2400px màx) abans de pujar, guardant l'original com a arxiu — equivalent al `convert-images.sh` del pare.

---

## Pla de migració (fases)

1. ✅ **Exportació** — XML complet de WordPress + còpia de `wp-content/uploads`. Mesurar mida total d'imatges.
2. ✅ **Scaffolding** — `hugo new site` a aquest directori, `hugo.toml` amb `permalinks` idèntics, taxonomies `categories` + `tags`, RSS activat.
3. 🔄 **Conversió** — WordPress XML → Markdown (`wordpress-export-to-markdown` v3.0.5). **2.354 posts generats**. Falta post-processament (thumbnail, image, tags, Vimeo) + migrar pàgines fixes.
4. **Tema** — layout de llistat cronològic, single, arxiu mensual, càmeres/taxonomies, cerca (Pagefind), RSS idèntic a `/feed/`.
5. **Comentaris i pàgines fixes** — renderitzar comentaris estàtics; migrar About/Avís/Contacte/legal.
6. **QA** — comparativa d'URLs: crawlar el WordPress actual vs el Hugo local i verificar resposta 200 a 1:1.
7. **Deploy i tall** — un cop el staging està complet i aprovat, en aquest ordre: **(1)** backup complet (BD + fitxers, incloent `uploads`, fora del servidor) → **(2)** pujar el `public/` del Hugo al docroot `~/www/blog/` mantenint `wp-content/` → **(3)** verificar la producció 1:1 contra l'Hugo local → **(4) només aleshores** esborrar el WordPress conservant sempre `wp-content/uploads`. Els subscritors de RSS (`/feed/`) i les URLs no noten cap canvi.

---

## Pròxim pas

Completar el **post-processament de la conversió** (fase 3): executar `migration/post-processa.py` per afegir `thumbnail:`, `image:` i `tags:` al frontmatter dels 2.354 posts, resoldre els Vimeo shortcodes, i copiar els fitxers a `content/posts/`. Després: migrar les 7 pàgines fixes i iniciar la fase 4 (tema).

## Estat de la fase 1 (exportació, 2026-09-14)

- ✅ XML complet baixat a `migration/` (4 fitxers, 59 MB, via WP-CLI + PHP 8.2)
- ✅ Recomptes verificats: 2.353 posts publicats (+10 no publicats), 96 categories, 3.177 etiquetes, 96 comentaris (71 aprovats + resta pendent/esborrall)
- ✅ `uploads` analitzat: 3,4 GB totals; 1,2 GB miniatures + 69 MB `-scaled` (regenerables, no es migren); **2,3 GB d'originals (9.706 fitxers)** → romanen al servidor

---

## Estat de la fase 3 (conversió, 2026-09-14)

### Eina utilitzada
`wordpress-export-to-markdown` v3.0.5 — execució:
```bash
npx wordpress-export-to-markdown --export=export-complet.xml --outdir=/tmp/wpfull --postfields=title,date,slug,categories,tags,excerpt,author,draft
```

### Resultats
- **2.354 posts** generats a `/tmp/wpfull/posts/` (2.363 al WP + 10 drafts)
- 7 pàgines generades a `/tmp/wpfull/pages/`
- Frontmatter: title, date, slug, categories, author
- Contingut: Markdown amb imatges `![alt](url)`

### Problemes detectats
1. **Tags buits**: el camp `tags` surt buit a tots els fitxers. L'XML del WP té 843 posts amb tags (3.020 tags únics). L'eina no parseja correctament les etiquetes del XML.
2. **`coverImage` buit**: l'eina no mapeja `_thumbnail_id` → imatge. Cal script per extreure thumbnail de `_thumbnail_id` → adjunt → `guid`.
3. **Vimeo shortcodes escapats**: `\[vimeo ID w=W h=H\]` en lloc de renderitzar l'iframe (3 posts).

### Post-processament
Script `migration/post-processa.py` creat per:
- Afegir `tags:` al frontmatter des de l'XML (843 posts amb tags)
- Afegir `thumbnail:` de `_thumbnail_id` → adjunt → `guid` (2.349 posts amb thumbnail)
- Afegir `image:` del primer `<img>` del contingut
- Convertir shortcodes `[vimeo]` → shortcode Hugo `{{< vimeo ID >}}`
- Copiar fitxers a `content/posts/`

*Informe generat el 2026-09-14 · projecte blog.pocallum.cat → Hugo*
