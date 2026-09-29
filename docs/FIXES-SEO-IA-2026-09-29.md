# Fixes SEO/IA + CMS — 2026-09-29

Canvis aplicats localment (sense desplegar). Verificats amb build net de Hugo v0.166.

## SEO / IA

- **.htaccess — 301 a HTTPS:** tots els [R=301] fan servir https://%{HTTP_HOST} absolut. Abans emetien Location: http:// (baixada HTTPS→HTTP i salt extra) perquè Apache rep HTTP intern del proxy.
- **.htaccess — paginació dels hubs:** /tags/page/N/ i /categories/page/N/ ja no fan 301 a /tag/page/N/ (404); ara fan 301 al hub (/tags/ i /categories/).
- **.htaccess — X-Robots-Tag:** aplicat només a feed[.]xml, no a sitemap.xml.
- **seo.html — meta descriptions:** fallback robust; els 426 posts amb description buida (només imatge) ara en tenen. Descripcions úniques per a cada terme d'etiqueta i categoria.
- **seo.html — títols:** NO es toquen. Es respecta el títol original del post (amb la data inclosa, si en té) i el sufix — Blog de Pocallum. Imprescindible per localitzar després les fotos en alta.
- **seo.html — schema:** BlogPosting amb @id, ImageObject, articleSection, keywords, wordCount, inLanguage, isPartOf; Person i Organization amb sameAs i logo; BreadcrumbList a cada post. 0 errors de parseig a 2.357 posts.
- **seo.html — Open Graph/Twitter:** article:published_time/modified_time/section/tag, og:image:alt, meta author.
- **robots.txt:** simplificat a la versió original (User-agent: * amb Disallow buit = tot permès, IA inclosa) + línia Sitemap. La llista explícita de crawlers d'IA s'ha retirat perquè el wildcard ja els permet i podia sobreescriure regles.
- **sitemap.xml:** plantilla pròpia; exclou etiquetes amb ≤1 post i afegeix imatges (image:image). 5.702 → 3.407 URLs + 2.352 imatges.
- **Etiquetes primes:** robots noindex, follow a les 2.295 etiquetes amb ≤1 post.
- **Paginació de termes arreglada:** les pàgines /tag/<slug>/ i /category/<slug>/ renderitzaven TOTS els posts (fins a 318) i generaven /page/N/ duplicats amb self-canonical. Ara fan paginació real (12 per pàgina) i pager. Exemple: /tag/leica-m6/ = 12 posts + /page/2/ = 5; /category/leica-m6/ = 12 + /page/2/ = 12...
- **Paginació de portada:** H1 "Pàgina N" i títol únic a les 196 pàgines que abans no tenien H1.
- **Taxonomies unificades:** 3 posts recents (fets des del CMS) tenien etiquetes amb majúscules/espais en lloc del slug. Unificades a la forma canònica existent: Test→test, blanc i negre→blanc-i-negre, Barcelona→barcelona, Nou Barris→nou-barris, Prosperitat→prosperitat, Casal de barri de Prosperitat→casal-de-barri-de-prosperitat, música en viu→musica-en-viu, Música en directe→musica-en-directe, Fotografia de concerts→fotografia-de-concerts, Punk→punk, Verdum→verdum, Vía Júlia→via-julia. Grups amb variants: 0.
- **hugo.toml:** ítem de menú Càmeres → /categories/.
- **Miniatures de llistat:** alt amb el títol del post (index, llistats de taxonomia i arxiu).

## CMS /admin — miniatures invisibles

- **Causa:** la CSP del /admin/ (static/admin/.htaccess) tenia img-src 'self' https: data: sense blob:. Sveltia resol el media intern (uploads a static/media/) amb URLs blob: (URL.createObjectURL), així que les miniatures noves quedaven bloquejades. Les d'URL absoluta (https:) sí que es veien.
- **Fix:** img-src 'self' https: data: blob:; i nova directiva media-src 'self' blob:;.

## Pendent (requereix servidor o contingut)

- **Rendiment d'imatges:** la portada carrega ~6,3 MB; cal pujar les variants -800.webp / -2500.webp al servidor i activar imatgesWebp = true i srcset. No s'ha activat per no servir imatges inexistents.
- **Alt del contingut llegat:** 4.412 imatges dels posts; és edició de contingut.
- **Títols duplicats:** 37 grups; decisió editorial (no tocar).
- **GSC:** cal el token google-site-verification.

## Desplegament

Cap canvi és a producció. El desplegament és push a develop → Dinahosting + GitHub Pages, i requereix el vistiplau exprés de l'usuari.
