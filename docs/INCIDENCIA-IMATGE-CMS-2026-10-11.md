# Incidència: pujada d'imatge del CMS fallida i post amb la imatge trencada — 2026-10-11

## Símptoma
En crear el post **«2026-10-08 - Asta and Salma en gran fromat»** des del CMS (Sveltia), la pujada de la fotografia va fallar amb el missatge genèric **«failed to fetch»**. Tot i això, el post es va publicar amb `thumbnail:` i `image:` apuntant a `/media/2026-10-08 - Horsman8x10 - Foma100 - Asta and Salma0001.jpg`, un fitxer que no era al repositori → imatge principal i `og:image` amb **404** (també la miniatura als llistats).

## Causa arrel
Dues capes:

1. **Sveltia 0.217.0** (bundle self-hosted a `static/admin/vendor/sveltia-cms.js`, del 18/09) tenia el bug [sveltia/sveltia-cms#1012](https://github.com/sveltia/sveltia-cms/issues/1012): `commitChanges()` enviava totes les addicions en una sola mutació `createCommitOnBranch`; si la petició a l'API de GitHub falla (502/timeout — que el navegador només pot reportar com a *failed to fetch* perquè la resposta 502 no porta capçaleres CORS), **l'entrada es desava igualment sense els recursos nous**. Corregit a la **v0.221.1** («keep new files in the draft until the save succeeds» + «split large GitHub saves»).
2. La foto en si era petita (**JPG de 1,2 MB, 1994×2500**); no va ser un problema de mida sinó una fallada puntual de l'API de GitHub en el moment de la pujada.

## Solució
1. **Imatge restaurada per git** (commit `b5cdcfc491`): el JPG original de l'extrem `1TBSSExtern` copiat a `static/media/` amb el nom exacte que ja referència el frontmatter, i les dimensions afegides a `data/imatges_dim.json` perquè el hero ofereixi el WebP de 2500 i no només el de 800.
2. **CMS actualitzat** (commit `1e77600e65`): `sveltia-cms.js` 0.217.0 → **0.234.0** (inclou el fix de la #1012) i CSP de `/admin/` ampliat (`blob:` a `connect-src` i `frame-src`, `manifest-src blob:`), segons les recomanacions actuals.

## Verificació
- **Producció:** JPG → 200 `image/jpeg` (1.248.729 bytes); `-800.webp` → 200; `-2500.webp` → 200. La pàgina emet `<picture>` amb tots dos candidats i l'`og:image` correcte. Post → 200.
- **CMS a producció:** `sveltia-cms.js` 0.234.0 (sha256 `51a07123b4c0a133958151e450251470d510c02df3f0c4baec6e7a22d501a06b`); capçalera CSP amb `blob:` a `connect-src`/`frame-src` i `manifest-src blob:`.
- **Prova local del bundle nou:** carrega, parseja `config.yml` i no dona cap error JS (només un `console.warn` inofensiu perquè el fitxer `.mjs` es diu `sveltia-cms.js`; també apareixia a la 0.217.0).
- **Deploys** de staging i producció: OK (runs `38170207058/38170207094` i `38170850336/38170850392`).

## Residual
- No s'ha pogut provar el **login** del CMS des de l'entorn de treball (cal el compte de GitHub de l'usuari). Cal confirmar-ho obrint `https://blog.pocallum.cat/admin/` i tornant a provar una pujada d'imatge.
- El post només referencia un retrat com a imatge principal; els altres dos de la sessió (`0002`, `0003`) són a l'àlbum.
- Si tornés a aparèixer `failed to fetch`, cal recollir l'error exacte de la consola del navegador (F12 → Console/Xarxa) per identificar la petició.
