---
name: pandoc-pdf-pipeline-gotchas
description: Montar pipeline md→PDF/DOCX com pandoc defaults files (-d perfil) e xelatex — gotchas vividos: defaults SEMPRE vence o YAML do doc (fallback via filtro Lua), -V concatena em vez de sobrescrever ("fonte AB" not found), fontes OTF do texlive invisíveis ao fontconfig no Ubuntu, Eisvogel 3.x exige pandoc recente, -o /dev/null não testa engine
metadata:
  pattern: workarounds
  origin: construção do md-export-kit (perfis abnt/apa/eisvogel/docx/html, 26/07/2026)
  confidence: alta (cada gotcha foi batido e a correção validada com pdffonts/regressão)
---

**O caso:** perfis de export em `~/.local/share/pandoc/defaults/` (uso: `pandoc doc.md -d abnt
-o doc.pdf`). Kit vivo nesta máquina: `~/Documents/md-export-kit/GUIA.md`. Gotchas na ordem
em que morderam:

**1. Precedência: defaults file VENCE o documento.** Tanto `variables:` quanto `metadata:`
do defaults sobrepõem o YAML do doc (verificado empiricamente com pdffonts). Para perfis
com defaults sobrescrevíveis: declarar chaves `fallback-<chave>` no `metadata:` do perfil +
filtro Lua que copia `fallback-X → X` só quando o doc não define X (usar sentinela-tabela
para remoção, não `false` — MetaBool false é valor legítimo). Filtro vivo:
`~/.local/share/pandoc/filters/profile-fallbacks.lua`.

**2. Override one-off na CLI é `--metadata chave=valor`, NUNCA `-V`.** `-V` sobre um perfil
que já define a variável CONCATENA: `fontspec Error: The font "TeX Gyre PagellaSource Sans
Pro" cannot be found`.

**3. Ubuntu: OTFs do texlive-fonts-extra são invisíveis ao fontconfig** (o pacote não as
registra) → xelatex/fontspec não acha por nome de família, embora `fc-match` pós-fix resolva.
Fix user-level, sem sudo: `~/.config/fontconfig/conf.d/09-texlive-opentype.conf` com
`<dir>/usr/share/texlive/texmf-dist/fonts/opentype</dir>` (+truetype) e `fc-cache -f`.
Beneficia xelatex, Typora e LibreOffice de uma vez.

**4. Eisvogel 3.x + pandoc velho = quebra nas referências** (`\end{CSLReferences}`, pandoc
3.1.3 do Ubuntu 24.04). Fix sem sudo: tarball linux-amd64 do pandoc release → `~/.local/bin`
(vence o apt no PATH).

**5. Teste de PDF exige `-o arquivo.pdf`.** `-o /dev/null` não tem extensão → pandoc nem
chama o engine LaTeX → "passou" sem testar nada.

**6. Verificação de fonte real: `pdffonts saida.pdf`.** Atenção: nomes têm prefixo de subset
aleatório (`XQOZBG+SourceSansPro`) — filtrar com grep pelo nome da família, não `sort | head`.

**Bônus HTML autocontido:** `embed-resources: true` + `html-math-method: mathml` (KaTeX/
MathJax remotos quebram o embed; MathML renderiza offline em browser moderno).
