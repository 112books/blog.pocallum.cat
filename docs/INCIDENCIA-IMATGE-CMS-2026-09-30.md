# Incidència: imatge nova del CMS no es veia — 2026-09-30

## Símptoma
En publicar un article des del CMS (Sveltia), la imatge es veia al CMS però **no al web**.

## Causa arrel
En activar el WebP, `img.html` emet `<picture>` per a totes les imatges de `/media/`, amb un `<source srcset="…-800.webp">`. La imatge nova (`IMG_3571.jpg`, pujada pel CMS) no tenia les variants `-800.webp`/`-2500.webp` (només s'havien generat per a les imatges existents en el moment d'activar-ho). El `<source>` apuntava a un 404 i, com que el navegador tria la font `image/webp`, **no cau a l'`<img>`** → imatge trencada.

## Solució (3 capes)
1. **Generats els WebP** d'`IMG_3571` (73 KB i 765 KB; l'original feia 2,5 MB) i afegides les dimensions al mapa `data/imatges_dim.json`.
2. **Partial robust** (`img.html`): per a imatges de `/media/`, només emet `<picture>` **si el WebP existeix** a `static/` (`os.FileExists`); si no, emet `<img>` amb l'original.
3. **Automatització als deploys**: els workflows de staging i producció generen els WebP que faltin a `static/media` **abans del build**, amb `continue-on-error: true`, així les properes pujades s'optimitzen soles i cap error no bloqueja el deploy.

## Verificació
- **Fallback provat**: traient temporalment el WebP, la pàgina emet `<img src=/media/IMG_3571.jpg …>` i **0** `<picture>`.
- **Producció**: `/media/IMG_3571-800.webp` i `-2500.webp` → 200 (`content-type: image/webp`); el post serveix `<picture>` amb els dos candidats.
- Commits: `7705d57035`, `fa23173c7d`.

## Residual
- El llegat (`/wp-content/`) no es pot comprovar per existència (és remot); la cobertura actual és del 100%.
- Els posts nous del CMS fan servir `/media/`, així que el guard cobreix el flux normal.
