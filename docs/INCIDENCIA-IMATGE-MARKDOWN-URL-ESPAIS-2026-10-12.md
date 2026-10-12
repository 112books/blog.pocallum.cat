# Incidència: imatge del post no carregava — URL amb espais sense encodar al Markdown — 2026-10-12

## Símptoma

En publicar el post *2026-10-08 — Holga Week amb una Holga CFN*
(`content/posts/2026-10-11-2026-10-08-holgaweek-amb-holga-cfn.md`),
una de les dues imatges del contingut **no apareixia**. La resta del
post (hero, thumbnail, segona imatge) es veia bé.

## Causa arrel

El CMS (Sveltia) va escriure la URL de la imatge al Markdown **amb
espais sense percent-encodar**:

```markdown
[![Asta i la Selma A](/media/2026-10-08 - Holga-CFN - RolleiRPX400 - Asta and Salma - B - 0001.jpg "Asta i la Selma")](https://...)
```

**goldmark** (el parser CommonMark que usa Hugo) **no accepta espais
sense encodar en destinations de links/imatges** (spec CommonMark: la
destinació sense `<>` no pot contenir espais). En lloc d'emetre un
`<img>`, va deixar la sintaxi `![alt](url)` com a **text pla visible**
al HTML renderitzat:

```html
<a href=https://...>![Asta i la Selma A](/media/2026-10-08 - Holga-CFN...)
</a>
```

La guàrdia existent (`#ZgotmplZ`) no ho va detectar perquè en aquest
cas no hi ha URL insegura en cap atribut HTML — simplement no hi ha
`<img>` en absolut.

## Per què l'altra imatge funcionava

El CMS havia percent-encodat la URL de la segona imatge (`0008.jpg`):
```markdown
/media/2026-10-08%20-%20Holga-CFN%20-%20RolleiRPX400%20-%20Asta%20and%20Salma%20-%200008.jpg
```
Aquesta es renderitzava correctament via `render-image.html`.

## Fix aplicat (commit `1cd8a8e853`)

### 1. Post (fix immediat)
URL de `B - 0001.jpg` reescrita amb `%20`:
```markdown
[![Asta i la Selma A](/media/2026-10-08%20-%20Holga-CFN%20-%20RolleiRPX400%20-%20Asta%20and%20Salma%20-%20B%20-%200001.jpg "Asta i la Selma")](https://...)
```

### 2. `themes/blog/layouts/_markup/render-image.html` (fix defensiu)
Afegit `replace .Destination " " "%20"` per si goldmark en alguna
versió futura passés URLs amb espais al hook:
```html
{{- $dest := replace .Destination " " "%20" -}}
<img src="{{ $dest | safeURL }}" ...>
```

### 3. Workflows de deploy (nova guàrdia)
Afegida a `deploy-produccio.yml` i `deploy-staging.yml` una guàrdia
que detecta markdown `![` sense renderitzar al build i atura el deploy:
```bash
fails=$(grep -rlP --include='*.html' '!\[.+?\]\(/' public/ || true)
```

## Prevenció futura

- La nova guàrdia del workflow aturarà qualsevol deploy on quedi
  markdown `![alt](url)` sense renderitzar al HTML.
- Quan el CMS escrigui URLs d'imatge, cal que siguin percent-encoded.
  Sveltia a vegades ho fa i a vegades no — és un comportament
  inconsistent del CMS. La guàrdia és la xarxa de seguretat.

## Relació amb incidències anteriors d'imatge

| Data | Fitxer | Causa | Símptoma |
|------|--------|-------|---------|
| 2026-09-30 | `INCIDENCIA-IMATGE-CMS-2026-09-30.md` | Pujada fallida al CMS | Fitxer absent del repo |
| 2026-10-07 | `INCIDENCIA-MINIATURES-ZGOTMPLZ-2026-10-07.md` | Espai al nom → `#ZgotmplZ` al `srcset` | Imatge trencada (cap source vàlid) |
| 2026-10-11 | `INCIDENCIA-IMATGE-CMS-2026-10-11.md` | Bug Sveltia #1012 (timeout 502) | Fitxer absent malgrat post desat |
| **2026-10-12** | **aquest fitxer** | **URL amb espais al Markdown** | **`<img>` no generat — text pla** |
