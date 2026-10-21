# Informe de feina — Text alternatiu (alt) a les imatges del blog

**Projecte:** blog.pocallum.cat
**Data:** 2026-10-20
**Tasca:** Omplir l'`alt` de les ~2.362 imatges de posts que no en tenien.

## Resum

- **Imatges pendents inicials:** 2.362 (de 2.772 imatges en Markdown).
- **Alts generats:** 2.354 (amb DeepSeek `deepseek-flash`).
- **Imatges restants sense alt:** 8 (URLs trencades, formats no suportats: .tif, .png d'awpcp.org, Google Photos caducades, zeroimage.com).
- **Fitxers modificats:** 2.120 posts.
- **Build Hugo:** OK (exit 0).
- **Commit:** `14f7c80d64` — "content(alt): omple el text alternatiu de 2.354 imatges del llegat amb DeepSeek".

## Procés

1. **Dry-run:** 2.362 imatges sense alt confirmades.
2. **Pilot de 20:** validat el to (descriptiu, en català, específic). 1 de 20 tallat lleugerament.
3. **Passada completa:** executada en lots de 50 (idempotent). ~47 lots, ~5-6 hores en total.
4. **Neteja:** fitxers `.bak` esborrats. Build Hugo verificat.
5. **Documentació:** `docs/PENDENTS.md` actualitzat (tasca marcada com a completada).

## Dificultats trobades

- **`deepseek-flash` és un model de raonament:** retorna la resposta a `reasoning_content`, no a `content`. Cal augmentar `max_tokens` a 2000 perquè completi el raonament i produeixi `content`.
- **Imatges de Google Photos:** algunes URLs han donat timeout (Read timed out). Aquestes imatges queden sense alt.
- **Formats no suportats:** .tif, alguns .png (awpcp.org) no es poden llegir amb Pillow. Quan Pillow falla, l'script registra l'error i continua.
- **Temps:** ~5-6s per imatge (model de raonament). Total ~5-6 hores per a 2.362 imatges.

## Modificacions al script

- `scripts/genera-alts.py`: max_tokens 90 → 2000, fallback a `reasoning_content` + títol del post, `reasoning_effort: low`.

## Imatges restants (8)

| Post | URL | Motiu |
|------|-----|-------|
| 27-04-2025-dia-mundial-de-la-fotografia-estenopeica-2025.md | awpcp.org (4 imatges) | no s'ha pogut llegir |
| alfonso-de-castro-again.md | Google Photos (trencada) | cannot identify image file |
| assaig-al-casal.md | Google Photos (trencada) | cannot identify image file |
| estrenant-la-camera-estenopeica-zero-2000.md | zeroimage.com | no s'ha pogut llegir |
| exposicio-gent-de-nou-barris-gent-darreu.md | 112gallery.eu (scaled) | no s'ha pogut llegir |

Aquestes es poden reparar manualment o rehostar.

## Estat del repositori

- Branch: `develop`
- Commit: `14f7c80d64`
- Fitxers modificats: 2.121 (2.120 posts + docs/PENDENTS.md + scripts/genera-alts.py + CLAUDE.md)
- Build Hugo: OK
- Push: **pendent de verificació** (desplega a producció)
- Control horari: **pendent** (cal indicar les hores de la sessió)