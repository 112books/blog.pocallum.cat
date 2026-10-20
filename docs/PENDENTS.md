# Tasques pendents — blog.pocallum.cat

> Llista de coses detectades i **no fetes**, per reprendre quan convingui.
> Última revisió: 2026-10-20.

## P1

### 1. Text `alt` a 2.362 imatges de post
Anàlisi (2026-10-20): de 2.772 imatges en Markdown, **2.370 tenen l'alt buit** (`![](...)`); no hi ha cap `<img>` en cru. Al WordPress original tampoc hi era: a l'export, de 2.737 imatges, 1.736 tenien `alt=""` i 629 ni atribut; les 372 amb text eren **noms de fitxer** (`dsf2973`, `l1210440`) — no serveixen com a descripció.
- **Opció A (mecànica):** omplir amb context: «*Títol del post* — fotografia 3 de 12», afegint càmera/pel·lícula si surt al nom del fitxer. És honest però repetitiu; treu l'avís d'«alt absent» però no descriu la foto.
- **Opció B (bona de veritat):** generar una descripció per imatge amb un model de visió (script + clau d'API com a secret; passada única sobre les 2.370 i incremental per als posts nous). És l'única via per tenir `alt` útil; té cost d'API i cal revisar-ne una mostra.
- **Cost estimat (opció B):** ~1,2–1,5 M tokens d'entrada (2.370 imatges a ~512 px) + ~50 k de sortida. Amb un model econòmic de visió surt per **~0,3–1,5 €**; amb un de gamma alta, **~5–8 €**. La feina grossa no és el cost sinó el temps (~15–25 min) i revisar una mostra.
- **Script ja fet:** `scripts/genera-alts.py` (compatible amb qualsevol endpoint OpenAI: `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `ALT_MODEL`). Només toca les imatges amb alt buit → es pot repetir sense por; resol `/media/` al disc i baixa les remotes; redueix a 512 px abans d'enviar. Provat de punta a punta amb un servidor de prova (3 imatges, idempotent).
- **Què falta:** la clau d'API. Passos:
  1. `python3 scripts/genera-alts.py --dry-run` → 2.362 imatges pendents.
  2. Pilot: `OPENAI_API_KEY=… python3 scripts/genera-alts.py --limit 20 --backup` i revisar els 20 alts.
  3. Si el to agrada: `… python3 scripts/genera-alts.py --backup` (passada completa) i commit.
- **Al CMS:** els posts nous ja tenen els camps **«Text alt de la miniatura»** i **«Text alt de la imatge principal»** (si es deixen buits, s'usa el títol); les imatges del cos es fan amb `![descripció](URL)`.

### 2. Imatges externes trencades (19)
De l'auditoria del 2026-10-02: 10 de `pocallum.cat/sites/default/files/*` (rutes velles Drupal del web mare, post *Pinhole Day 2017*), 4 d'`awpcp.org`, 2 de Google Photos caducades i 3 d'altres.
- **Què cal:** rehostar a `/media/` o substituir per una equivalent.

### 3. Google Search Console — FET
Comprovat el 2026-10-20: `blog.pocallum.cat` té el TXT `google-site-verification=DEMhy57yvKrKuqiZ4Ym1_suj13AmNy5DyAzr3OklaKM` (i l'àpex `pocallum.cat` el seu, `HA1EtBzA-…`) i l'usuari confirma que la propietat **està verificada des de fa anys**. No cal cap token ni meta tag al codi.
- **Opcional:** assegurar que el `sitemap.xml` estigui enviat a la propietat de `blog.pocallum.cat`.

## P2

### 4. Aprimar el repositori (`.git` = 960 MB)
El codi no pesa això: són **blobs històrics** (imatges antigues i commits de migració). Retallar les imatges d'avui no els elimina.
- **Com:** `git filter-repo --strip-blobs-bigger-than 2M` (o per rutes) → `git push --force` a `develop` i `main` → **cal re-clonar** tots els clons, i el CMS (Sveltia) treballa sobre `develop`, així que s'ha de fer en un moment tranquil.
- **Abans:** còpia de seguretat (`git clone --mirror`); GitHub no allibera els objectes antics immediatament (cal demanar-ho a suport o esperar la GC).

### 5. Dimensions de les imatges del CMS a `data/imatges_dim.json`
Els posts nous no hi són. Ja no cal per al hero (s'anuncia la variant de 2500 px si el `.webp` existeix), però amb les dimensions s'emetrien `width`/`height` (menys salt de layout) i `srcset` amb amplades reals.
- **Com:** afegir al workflow `optimitza-media.yml` un pas que escrigui les dimensions de `static/media/*` al JSON (el fitxer és d'una sola línia i fa 970 KB: cal escriure'l amb el mateix format perquè el diff sigui petit).

### 6. KPI «Avui» del dashboard en hora local
A `static/stats/index.html`, el dia es calcula en **UTC** i GoatCounter usa **Europe/Madrid** → a la matinada el KPI pot anar 2 h desfasat.

### 7. Avís de fallada del deploy
Durant l'incident de GitHub del 2026-10-19 el job `notifica` (obre l'Issue `deploy-failure`) **també va fallar**, així que no hi va haver avís.
- **Què cal:** revisar permisos/`gh` del pas i provar-ho amb una fallada controlada.

### 8. `Sitemap:` al `robots.txt` del web mare
És un altre repo (`../pocallum.cat`); no s'ha de tocar des d'aquí.

### 9. Caché dels previews a WhatsApp/Facebook
El `og:image` ja és correcte (1200 px, ~95 KB), però les xarxes guarden el preview antic. Per forçar-lo: compartir amb `?v=2` o passar la URL pel depurador de Facebook.

## Fet (per memòria)
- **Pàgines legals:** *Avís Legal*, *Política de Privacitat* i *Política de Cookies* **tenen contingut** (2,1 / 3,4 / 1,4 KB) i serveixen 200. La nota antiga deia que estaven buides *al WordPress*; al passar a Hugo es van omplir.
- **Vídeos de Vimeo:** verificat al navegador real (2026-10-20) que es veuen bé al post de Ciutat Flamenco. El missatge de restricció només sortia al Chrome headless.
- **Límit de 2500 px** a `static/media` (workflow `optimitza-media.yml`), **og:image** a 1200 px, **títols i rànquings per període** al dashboard.
