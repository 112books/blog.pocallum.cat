# Incidència: miniatura i imatge principal no es veien — 2026-10-07

## Símptoma

En publicar un article des del CMS (Sveltia) — *BAUM Fest 2026: tinta i art*,
`content/posts/2026-10-07-2026-10-02-baum-fest-2026-tinta-i-art.md` — la
**miniatura no apareixia a la portada** ni la **imatge principal** a la pàgina
del post. Tota la resta del web funcionava.

## Causa arrel

El fitxer pujat pel CMS tenia un **espai al nom**:

```
static/media/2026-10-02-LM6-RPX400@800-HC110-B-11-BAUMfest-B- 0031.jpg
                                                         ^ espai
```

`img.html` genera un `<picture>` amb un `<source srcset="…-800.webp 800w">`.
En un context `srcset`, el motor de plantilles de Go (`html/template`) marca com
a no segura qualsevol URL que contingui un espai i l'escriu literalment com
**`#ZgotmplZ`**:

```html
<picture>
  <source srcset="#ZgotmplZ 800w" type="image/webp">   <!-- trencat -->
  <img src="/media/…BAUMfest-B-%200031.jpg">           <!-- aquest sí que va bé -->
</picture>
```

El navegador (suporta WebP) tria el `<source>`, intenta carregar `#ZgotmplZ`
(un fragment de la pròpia pàgina, no una imatge) i, com que un `<source>` de
`<picture>` seleccionat que falla **no cau a l'`<img>`**, la imatge queda trencada.

Detall: en context `<img src>` Go **sí** normalitza l'espai a `%20`; el problema és
específic de l'atribut `srcset`.

## Per què només passava a staging/producció

A local, `static/media/` no té la variant `-800.webp`, així que `img.html` emet
només l'`<img>` (sense `<source>`) i la imatge es veu. És el workflow de desplegament
qui **genera els WebP abans del build**; un cop existeixen, s'emet el `<source>`
trencat. Per això el bug no reproduïble en local sí que apareixia en desplegar.

## Solució

`themes/blog/layouts/partials/img.html`: percent-encodar els espais (`%20`) en
construir les rutes `-800.webp`/`-2500.webp` del `srcset`, mantenint la ruta crua
per a la comprovació `os.FileExists`. Cobreix qualsevol imatge de `/media/`.

- Commit: `8a477bee4f` a `develop` (`fix(img): percent-encode spaces in srcset to avoid #ZgotmplZ`).
- Deploys: producció run `37617290097` i staging run `37617290043`, tots dos success.

## Verificació

- **Reproducció en local** de la condició de CI (creant un WebP de prova amb
  espai al nom): abans `#ZgotmplZ`; després `%20` i **0** ocurrències de `#ZgotmplZ`
  a tot el build.
- **Producció** (`https://blog.pocallum.cat/`): `#ZgotmplZ` = 0 i
  `<source srcset="/media/…BAUMfest-B-%200031-800.webp 800w">`.
- **Post**: hero i tira amb la mateixa `srcset` corregida.
- **Imatge real**: JPG i WebP retornen `200` (`image/jpeg`, `image/webp`).
- **Staging**: verificat el mateix (propagació de GitHub Pages d'1–2 min).

## Relació amb la incidència del 2026-09-30

Totes dues afectaven imatges noves del CMS a través del `<source>` de WebP:
- **2026-09-30** (`INCIDENCIA-IMATGE-CMS-2026-09-30.md`): faltava el fitxer WebP →
  `<source>` a 404. Es va resoldre, entre altres, amb el guard `os.FileExists` que
  només emet `<picture>` si el WebP existeix.
- **2026-10-07** (aquest): el WebP existia però la ruta contenia un espai →
  `#ZgotmplZ`.

## Residual / prevenció

- Aquest és l'únic fitxer de `static/media/` i l'únic post amb un espai al nom;
  la resta del flux ja queda cobert pel fix.
- Millores:
  1. **Guàrdia implementada (2026-10-07):** pas «Guarda — cap #ZgotmplZ al build» a
     `deploy-produccio.yml` i `deploy-staging.yml`, just després del build i abans de
     publicar → el desplegament falla (i el job `notifica` obre l'Issue `deploy-failure`)
     si el `public/` conté `#ZgotmplZ`. Verificada amb una simulació del bug: detecta el
     `srcset="#ZgotmplZ"` i descarta la prosa que només esmenta el literal.
  2. Normalitzar/«slugificar» els noms de fitxer a la pujada del CMS: **descartat** per
     indicació de l'usuari — no es toquen els fitxers que ja funcionen.
