# Tasques pendents — blog.pocallum.cat

> Llista de coses detectades i **no fetes** (o fetes a mitges), per reprendre quan convingui.
> Última revisió: 2026-10-20. Prioritat: **P0** = convé aviat · **P1** = important · **P2** = quan hi hagi temps.

## P0

### 1. Pàgines legals buides
`aviso-legal`, `politica-de-privacidad` i `politica-de-cookies` existeixen amb frontmatter però **sense contingut** (al WordPress ja estaven buides).
- **Què cal:** redactar el text legal (titular: Joan Linux Martínez i Serres), o decidir si s'eliminen del menú fins que hi siguin.
- **Per què:** són pàgines enllaçades al peu; ara mateix donen una pàgina buida.

### 2. Comprovar els vídeos de Vimeo en un navegador real
Al post *Ciutat Flamenco* els 3 iframes carreguen, però el Chrome **headless** de prova rebia «We couldn't verify the security of your connection. Access to this content has been restricted».
- **Què cal:** obrir el post en un mòbil i/o navegador normal. Si surt el mateix missatge, revisar a Vimeo *Settings → Privacy → Where can this be embedded* (cal permetre `blog.pocallum.cat`).
- **Per què:** és el blocatge típic de Vimeo a navegadors automatitzats, però si fos restricció de domini, els vídeos no es veurien a ningú.

## P1

### 3. Imatges externes trencades (19)
De l'auditoria del 2026-10-02: 10 de `pocallum.cat/sites/default/files/*` (rutes velles Drupal del web mare, post *Pinhole Day 2017*), 4 d'`awpcp.org`, 2 de Google Photos caducades i 3 d'altres.
- **Què cal:** rehostar a `/media/` o substituir per una imatge equivalent.

### 4. 2.368 imatges de post sense `alt`
- **Què cal:** omplir `alt` (a mà als posts nous; al llegat es pot derivar del títol o del peu de foto, però cal revisar-ho per no posar text soroll).

### 5. Token de verificació de Google Search Console
- **Què cal:** que l'usuari generi el token i es posi al `<head>` (`google-site-verification`) o com a registre DNS TXT.

## P2

### 6. Aprimar el repositori (`.git` = 960 MB)
El codi no pesa això: són **blobs històrics** (imatges antigues i commits de migració). Retallar les imatges d'avui no els elimina.
- **Com:** `git filter-repo --strip-blobs-bigger-than 2M` (o per rutes) → `git push --force` a `develop` i `main` → **cal re-clonar** tots els clons, i el CMS (Sveltia) treballa sobre `develop`, així que s'ha de fer en un moment tranquil.
- **Abans:** còpia de seguretat sencera (`git clone --mirror`), i tenir en compte que GitHub no allibera els objectes antics immediatament (cal demanar-ho a suport o esperar la GC).
- **Per què:** clonar el repo va lent; no afecta el web.

### 7. Dimensions de les imatges del CMS a `data/imatges_dim.json`
Els posts nous no hi són. Ja no cal perquè el hero anuncia la variant de 2500 px si el `.webp` existeix, però amb les dimensions s'emetrien `width`/`height` (menys salt de layout) i `srcset` amb amplades reals.
- **Com:** afegir al workflow `optimitza-media.yml` un pas que escrigui les dimensions de `static/media/*` al JSON (el fitxer és d'una sola línia i fa 970 KB: cal escriure'l amb el mateix format perquè el diff sigui petit).

### 8. KPI «Avui» del dashboard en hora local
A `static/stats/index.html`, el dia es calcula en **UTC** i GoatCounter usa **Europe/Madrid** → a la matinada el KPI pot anar 2 h desfasat.

### 9. Avís de fallada del deploy
Durant l'incident de GitHub del 2026-10-19 el job `notifica` (obre l'Issue `deploy-failure`) **també va fallar**, així que no hi va haver avís.
- **Què cal:** revisar permisos/`gh` del pas i provar-ho amb una fallada controlada.

### 10. `Sitemap:` al `robots.txt` del web mare
És un altre repo (`../pocallum.cat`); no s'ha de tocar des d'aquí.

### 11. Caché dels previews a WhatsApp/Facebook
El `og:image` ja és correcte (1200 px, ~95 KB), però les xarxes guarden el preview antic. Per forçar-lo: compartir amb `?v=2` o passar la URL pel depurador de Facebook.

## Notes
- El workflow `optimitza-media.yml` **no toca** les imatges del llegat (`/wp-content/uploads/`, al servidor): només `static/media/`.
- Les imatges del llegat (3,4 GB) es van deixar intactes per decisió de projecte.
