---
name: igepp-aula-reformat
description: Use when converting or reformatting an IGEPP course PDF (aula em PDF, CGU/Senado pré-edital) into clean Markdown/Obsidian and/or a printable PDF — or when any cursinho/TCPDF-generated PDF yields garbled extraction from a rotated watermark ("Edição 20xx"), repeated banner/footer furniture, or low-quality diagrams that need redrawing.
---

# Reformatar aula em PDF do IGEPP

## Overview

Aulas do IGEPP (gerador TCPDF) têm marca d'água rotacionada, banner/rodapé em toda
página e diagramas raster ruins. Este pipeline extrai o texto íntegro, produz um
**Markdown** (fonte única, Obsidian-friendly, diagramas em Mermaid) e dele um
**PDF imprimível** (Lora+Inter, sumário paginado, caixas de questão, bookmarks).

**Armadilha central:** NÃO use `apply_redactions` para remover a marca d'água e NÃO
rode `pymupdf4llm` direto no PDF original — os retângulos diagonais da marca d'água
engolem/poluem o texto do corpo. A extração correta é por spans, filtrando linhas
rotacionadas (`scripts/extract_spans.py`).

## Workflow

1. **Diagnóstico** — `pdfinfo` (Producer TCPDF? nº de páginas), `pdfimages -list`
   (o que é banner repetido vs diagrama de conteúdo), folha de contato de TODAS as
   páginas (`scripts/contact_sheet.py`) para mapear e CONTAR diagramas, tabelas e
   questões (essa contagem é o gabarito da verificação do passo 7).
2. **Extração** — `uv run --with pymupdf python ~/.claude/skills/igepp-aula-reformat/scripts/extract_spans.py aula.pdf dump.txt`
   (audite a lista "mobília detectada" no stderr; `--pages A-B` existe para testes parciais —
   nesse caso a numeração de questões e a checagem de contagem valem só para o trecho).
   Rode também `pymupdf4llm` num arquivo à parte SÓ para recuperar sublinhados/tachados
   (`<u>`, `~~`); o texto dele vem mutilado, use apenas as marcas.
3. **Transcrição visual** — renderize páginas com diagramas/tabelas a 200 dpi e
   transcreva o conteúdo olhando a imagem (não confie no dump para tabelas).
4. **Autoria do MD** — escreva o Markdown seguindo `CONVENTIONS.md` (obrigatório:
   é o formato que o conversor parseia). Valide blocos mermaid (tool MCP do Mermaid,
   se disponível — o retorno é grande: salve e leia só `.valid` com jq; sem a tool,
   mantenha sintaxe básica de flowchart e confira no Obsidian).
5. **Diagramas do PDF** — redesenhe cada diagrama como `diagramaN.svg` (N = ordem
   dos blocos mermaid) na pasta de saída do HTML.
6. **Conversão e render** —
   `python ~/.claude/skills/igepp-aula-reformat/scripts/md_to_html.py aula.md saida/aula.html`
   (o script copia `aula.css` sozinho se faltar), depois
   `python ~/.claude/skills/briefing-designer/templates/render.py saida/aula.html saida/Aula.pdf`
   (WeasyPrint e pypdf já instalados nesta máquina via briefing-designer; senão,
   `uv run --with weasyprint --with pypdf python .../render.py ...`).
7. **Inspeção visual (obrigatória)** — folha de contato de TODAS as páginas do PDF
   gerado + zoom em capa, sumário, cada diagrama, cada tabela grande e 1-2 questões.
   Confira: nº de questões = original; sem texto da marca d'água; tachados presentes.
8. **Entrega no manual_estudo** (se aplicável) — MD em
   `~/manual_estudo/disciplinas/<disciplina>/aulas/`, PDF em
   `~/manual_estudo/pdf/aulas/<Disciplina>/` (convenção no CLAUDE.md do projeto).

## Quick reference

Caminhos abaixo relativos à skill (`~/.claude/skills/igepp-aula-reformat/`).

| Passo | Comando |
|---|---|
| Folha de contato | `uv run --with pillow python scripts/contact_sheet.py in.pdf /tmp/sheets` |
| Extrair texto | `uv run --with pymupdf python scripts/extract_spans.py in.pdf dump.txt` |
| Marcas u/tachado | `uv run --with pymupdf --with pymupdf4llm python -c "import pymupdf4llm,sys;open('u.md','w').write(pymupdf4llm.to_markdown(sys.argv[1]))" in.pdf` |
| Páginas p/ olhar | `pdftoppm -png -r 200 -f N -l N in.pdf pg` |
| MD → HTML | `python scripts/md_to_html.py aula.md out/aula.html` |
| HTML → PDF | `python ~/.claude/skills/briefing-designer/templates/render.py out/aula.html out/Aula.pdf` |
| Conferir PDF | `pdftoppm -png -r 60 out/Aula.pdf chk` + folha de contato |

## Common mistakes

- **Redação/pymupdf4llm direto** → texto mutilado no meio das questões (ver Overview).
- Confiar no dump para tabelas → células embaralhadas; transcreva da imagem.
- Esquecer `diagramaN.svg` → o conversor pula a figura (ele avisa no stderr; leia!).
- Não recuperar `~~tachados~~` dos comentários → perde-se a didática do professor
  ("o orçamento ~~tradicional~~ programa...").
- Contagem de questões diferente do original → sumiu bloco na autoria; compare
  `grep -c '^\*\*Questão'` com a contagem feita no diagnóstico.
- Reescrever o conteúdo do autor (ver política de fidelidade em `CONVENTIONS.md`).
- PDF de outra origem (Word/PowerPoint, sem marca d'água rotacionada): este pipeline
  não se aplica; extraia normalmente e use só as etapas 4-8 se quiser o mesmo visual.

## Arquivos

- `scripts/extract_spans.py` — extração span-level imune à marca d'água
- `scripts/contact_sheet.py` — folha de contato de PDF para inspeção visual
- `scripts/md_to_html.py` — conversor MD→HTML (parseia `CONVENTIONS.md`)
- `assets/aula.css` — folha de impressão (A4, Lora+Inter, TOC paginado, questões)
- `CONVENTIONS.md` — formato exato do MD (frontmatter, questões, diagramas, fidelidade)
