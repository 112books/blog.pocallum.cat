# Generar els texts alt amb DeepSeek (runbook)

> Per fer-ho amb **OpenCode** (o a mà). Objectiu: omplir l'`alt` de les ~2.362 imatges dels posts que no en tenen.
> Script: `scripts/genera-alts.py` · drecera: `scripts/alts-deepseek.sh`

## 0. Prerequisits
- Python 3 amb **Pillow** i **requests** (`python3 -c "import PIL, requests"`).
- Una clau de DeepSeek (platform.deepseek.com). L'API és multimodal: `deepseek-flash` accepta imatges.
- Arbre de treball net: `git status` ha de sortir buit.

## 1. Deixa la clau en un fitxer privat
```bash
mkdir -p ~/.config/pocallum && chmod 700 ~/.config/pocallum
printf '%s' 'sk-…' > ~/.config/pocallum/deepseek.key
chmod 600 ~/.config/pocallum/deepseek.key
```
(L'alternativa és `export OPENAI_API_KEY=sk-…`.)

## 2. Mira l'abast (no crida l'API)
```bash
./scripts/alts-deepseek.sh --dry-run
```
Ha de dir al voltant de **2.362 imatges**. Si diu 0, algú ja les ha omplertes.

## 3. Pilot de 20 imatges
```bash
./scripts/alts-deepseek.sh --limit 20 --backup
git diff --stat
git diff content/posts | head -60
```
Revisa que:
- les frases siguin **en català** i descriptives (no «imatge de…»);
- tinguin sentit amb la foto (obre'n un parell al navegador);
- no hagin quedat buides ni amb caràcters rars.

Si el to no t'agrada, rebobina el pilot i ajusta el `PROMPT` dins `scripts/genera-alts.py`:
```bash
git checkout -- content/posts
```

## 4. Passada completa
```bash
./scripts/alts-deepseek.sh --backup | tee /tmp/alts.log
tail -3 /tmp/alts.log        # resum: generats / errors
```
- Triga uns **15–25 min** (una crida per imatge).
- Es pot aturar i reprendre: només toca les imatges amb `alt` buit (idempotent).
- Les imatges remotes que fallin queden com estaven i es reintenten en tornar a executar.

## 5. Comprova i publica
```bash
grep -rc '!\[\](' content/posts | awk -F: '{s+=$2} END {print "alts buits restants:", s}'   # 0 o gairebé
hugo --quiet --destination /tmp/build-alts && echo "build OK"
git status --short | head
git add content/posts
git commit -m "content(alt): omple el text alternatiu de les imatges del llegat"
git push origin develop
```
El push desplega a staging i producció (uns 3 minuts).

## 6. Neteja
Els `--backup` deixen `content/posts/*.md.bak`. Comprova que no s'han comès i esborra'ls:
```bash
find content/posts -name '*.md.bak' -delete
```

## Notes
- Cost: amb `deepseek-flash` i imatges de 512 px, la passada completa són **cèntims**.
- El script **no** reescriu les imatges del llegat a `/wp-content/uploads/`: només les descarrega per mirar-les.
- Per als posts nous: al CMS hi ha els camps **Text alt de la miniatura** i **Text alt de la imatge principal**; les imatges del cos es fan amb `![descripció](URL)`.
