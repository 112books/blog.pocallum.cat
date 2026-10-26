# Manual del CMS — publicar al blog

> Guia per a qui publica (usuari del CMS). Els detalls tècnics del projecte són a `CLAUDE.md`.
> Última actualització: 2026-10-26.

## Accés

- **Producció:** <https://blog.pocallum.cat/admin/>
- **Staging:** <https://112books.github.io/blog.pocallum.cat/admin/>
- Login amb el compte de GitHub (botó «Inicia sessió amb GitHub»). No hi ha contrasenya pròpia.

Cada desament desa un commit a la branca `develop` i llança sols dos desplegaments (staging i producció). No cal fer res més: al cap de 2–3 minuts el post és en línia.

## Crear un post

**Posts → New Post**. Camps, en ordre:

| Camp | Què hi va |
|------|-----------|
| **Títol** | El títol visible. No cal posar-hi la data: ja surt de «Data i hora». |
| **Data i hora** | Dia **i hora** de publicació. Ve omplert amb el moment de creació. |
| **Slug** | Opcional. Si el deixes buit, es genera del títol. |
| **Categories** | Càmeres i òptiques (llista tancada; se'n poden crear de noves a l'apartat *Categories*). |
| **Tags** | Separa'ls per comes: `jazz, blues, concert`. |
| **Miniatura** | Foto dels llistats (portada, arxiu, categories). Si és buida, s'usa la imatge principal. |
| **Text alt de la miniatura** | Descripció curta per a lectors de pantalla i Google. Si és buit, s'usa el títol. |
| **Imatge principal** | Foto de capçalera del post. |
| **Text alt de la imatge principal** | Descripció curta. Si és buit, s'usa el títol. |
| **URL àlbum** | Opcional: enllaç a Google Fotos o similar («Veure l'àlbum complet →»). |
| **Draft** | Marcat = esborrany: **no es publica** a staging ni a producció. |
| **Contingut** | El text en Markdown. Imatges: `![descripció de la foto](URL)`. Vimeo: `{{< vimeo 123456789 >}}`. |
| **— SEO —** | `noindex` (no indexar), «Títol SEO» i «Descripció SEO» (màx. 155 car.). Opcionals. |

## Data i hora: per a què serveix

L'hora no canvia l'URL (que continua sent `/2026/10/26/slug/`), però **sí l'ordre**:

- La portada, els llistats, l'arxiu, el feed i la tira de navegació del post ordenen per data **i hora**.
- Si publiques **dos o tres posts el mateix dia**, posa'ls hores diferents i sortiran en l'ordre que vulguis (el més recent primer).
- Exemple: `2026-10-26 10:30`, `2026-10-26 18:05`, `2026-10-26 22:40`.
- Si deixes l'hora a `00:00` (o en un post antic només hi ha el dia), el desempat entre posts del mateix dia el decideix el títol — pot no ser l'ordre que vols.

Els **2.353 posts migrats del WordPress** tenen només dia. Si un dia et molesta l'ordre d'un post antic, obre'l al CMS i posa-li una hora com a la resta de camps.

## Imatges

- Les imatges pujades al CMS van a `static/media/` i es publiquen a `/media/…`. No cal tocar res més.
- El desplegament genera automàticament les versions **WebP** (800 i 2500 px) i una derivada **og.jpg** de 1200 px per als previews de WhatsApp/X/Facebook.
- Límit: les imatges de `static/media` es redueixen a **2500 px** de costat més llarg (qualitat 85). Les originals bones les guardes tu fora del repo (catàleg de Lightroom).
- **Text alt sempre**: a les imatges del cos, escriu-lo dins els claudàtors (`![descripció](URL)`). Als camps de miniatura i imatge principal hi ha els camps `thumbnail_alt` i `image_alt`.

## Publicar, despublicar, esborrar

- **Publicar:** desmarca **Draft** i desa. Els drafts no surten a cap dels dos llocs.
- **Canviar un post publicat:** edita'l i desa; es redesplega sol.
- **Esborrar:** des del CMS (acció *Delete*). L'URL passa a 404; si el post estava indexat, Google el podarà.

## Errors típics

| Símptoma | Causa / què fer |
|---|---|
| En desar surt «failed to fetch» o falta la imatge | La pujada ha fallat a mitges. Torna a obrir el post i torna a pujar la imatge abans de desar. Si el post queda amb `thumbnail`/`image` apuntant a un fitxer que no existeix, la imatge dona 404. |
| La imatge no es veu al web | Comprova que el fitxer s'ha pujat (es veu al widget) i que el desplegament ha acabat. Al cap de 2–3 minuts recarrega amb `Ctrl+Shift+R`. |
| 404 en un post acabat de crear | Segurament és **Draft**. Desmarca'l i desa. |
| El títol i l'URL porten la data dues vegades | No escriguis la data al títol: el camp «Data i hora» ja la posa a l'URL i als llistats. |
| La pujada d'imatge falla amb un fitxer molt gran | Redueix-lo abans (2500 px, ~1,5 MB). El workflow ho fa sol, però el CMS puja el fitxer original. |
| No puc fer login | Cal tenir sessió de GitHub al navegador i permís sobre el repo `112books/blog.pocallum.cat`. |

## On mirar més

- `docs/PENDENTS.md` — què queda per fer al projecte.
- `CLAUDE.md` — arquitectura, desplegament i decisions tècniques (per a agents).
- `docs/INCIDENCIA-*.md` — historial d'incidències d'imatges i desplegaments.
