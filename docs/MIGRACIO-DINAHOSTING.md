# Migració de pocallum.cat a Dinahosting — referència

> **El document operatiu complet és al repo pare:** [`pocallum.cat/MIGRACIO-DINAHOSTING.md`](../pocallum.cat/MIGRACIO-DINAHOSTING.md).
> Aquest fitxer és només un punter per a les sessions que treballin des d'aquest repo.

## Resum

Moure `pocallum.cat` (site pare) de GitHub Pages a Dinahosting, on ja hi ha el blog (`~/www/blog/`). GitHub queda només com a control de versions. Objectiu final:

```
Dinahosting · vl28359.dinaserver.com · 82.98.166.123
~/www/
├── pocallum/   ← pocallum.cat (nou)
├── staging/    ← staging.pocallum.cat (nou, protegit)
└── blog/       ← blog.pocallum.cat (ja existeix)
```

## Per què

- **SSL:** amb el DNS de tot a Dinahosting, Let's Encrypt es valida directament al panell i es renova automàticament (el certificat de `blog.pocallum.cat` caduca el **22/09/2026** — terminis crítics al document principal).
- **Menys fragilitat:** GitHub Pages + `actions/configure-pages` depèn del custom domain configurat abans del build.
- **CMS unificat** al final (Sveltia CMS per `pocallum.cat`).

## Regles crítiques

1. **No tocar mai `wp-content/`** al servidor.
2. **Redirect HTTP→HTTPS mai al `.htaccess`** (loop pel proxy de Dinahosting) — es fa al panell.
3. **Ordre:** build verificat a Dina → DNS → SSL → verificació → neteges GitHub.
4. **Mantenir el custom domain a GitHub Pages fins que tot estigui verificat** (rollback = 1 canvi de DNS).
5. **Cap acció sobre servidor/DNS/panells sense vistiplau explícit de l'usuari.**

## Conexió amb aquest repo

- El workflow `deploy-produccio.yml` del blog és el **model** per als nous workflows del pare (rsync + secrets `DINAHOSTING_*`).
- El blog's staging queda a GitHub Pages per ara (decisió: Opció B).

## Només s'executa des d'aquest repo amb permís de l'usuari

Tasques que afectin `pocallum.cat` es fan des del repo pare, no des d'aquí (norma del CLAUDE.md del blog). Aquest fitxer serveix per localitzar el document principal.