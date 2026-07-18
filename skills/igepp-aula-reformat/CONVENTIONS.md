# Convenções do Markdown da aula

O `scripts/md_to_html.py` parseia ESTE formato. Fora dele, o bloco vira parágrafo comum.
O MD é a fonte única da verdade: a versão Obsidian e o PDF saem do mesmo arquivo.

## Frontmatter (usado na capa do PDF)

```yaml
---
title: "Aula 01 — Orçamento Público: conceitos e princípios orçamentários"
subtitle: "Orçamento-programa — fundamentos e técnicas"   # opcional
disciplina: "Administração Financeira e Orçamentária"
concurso: "CGU — Auditor Federal de Finanças e Controle (AFFC) — Pré-Edital"
kicker: "Concurso CGU · AFFC — Pré-Edital"                # opcional; default = concurso
footer: "Orçamento Público · AFO · CGU/AFFC"              # rodapé das páginas; default = title
autor: "Paulo Lacerda"
edicao: "2026"
tipo: "Aula em PDF autossuficiente (teoria e questões comentadas)"
tags: [concurso, cgu, afo]
---
```

## Estrutura

- `#` título (1×, só para o MD/Obsidian — o PDF usa o frontmatter), depois blockquote
  de cabeçalho e um Sumário manual em lista. **Tudo antes do primeiro `##` é ignorado
  pelo conversor** (a capa e o sumário do PDF são gerados).
- `##` seções (`1.`, `2.`), `###` subseções (`2.1`), `####` sub-subseções (`2.2.1`).
  `##`/`###` entram no sumário do PDF; `##` abre página nova.
- Listas: `- ` com aninhamento por **2 espaços**; numeradas `1. `. Cada item em UMA linha.
- Tabelas GFM. Célula da última coluna exatamente `**Sim**`/`**Não**` ganha selo
  colorido; `<br>` literal é permitido dentro de célula para quebra de linha.
- Callouts Obsidian: `> [!warning] Título` (âmbar) e `> [!tip] Título` (azul);
  outros tipos (`[!note]`, `[!info]`...) renderizam com o estilo base azul.
- Blockquote comum (`> `) para citações de lei e notas de rodapé de tabela.
- Ênfases: `**negrito**`, `*itálico*`, `~~tachado~~` (para correções didáticas do
  autor), `\*`/`\_` para literais.
- Última linha do arquivo: parágrafo `*Material original: IGEPP — ...*` (vira colofão).

## Diagramas

- No MD: bloco ```mermaid (valide a sintaxe; Obsidian renderiza nativamente).
- No PDF: o N-ésimo bloco mermaid é substituído por `diagramaN.svg` se o arquivo
  existir na pasta do HTML. Redesenhe o SVG à mão (Inter, navy #1B2A4E, fundo claro,
  viewBox ~900 de largura) — fiel ao conteúdo, não ao estilo do original.
- Quadros comparativos "de caixinhas" do original quase sempre ficam MELHORES como
  tabela do que como diagrama. Redesenhe como tabela. Quadro com título + caixa
  "Atenção" abrangendo as colunas (padrão "Lei 4.320/64"): callout `[!warning]` +
  tabela de 2 colunas logo abaixo.

## Bloco de questão (formato exato)

```markdown
---

**Questão 12** — FGV · 2023 · CGE-SC · Auditor do Estado — Administração

Enunciado corrido...

- **A)** alternativa;
- **B)** alternativa;

**Comentários:** texto do professor...

**Gabarito:** A

---
```

- Numeração sequencial 1..N no documento inteiro (o conversor conta e põe na capa).
- Linha de metadados: normalize para `Banca · Ano · Órgão · Cargo — Área` na ordem
  em que os dados existirem no original; omita o que faltar; não invente campos.
- Certo/Errado: sem lista de alternativas; no gabarito use o rótulo VERBATIM do
  autor (`Certa`, `Errada`, `Errado`, letra) — o formato só exige a linha `**Gabarito:** X`.
- Itens V/F ou de relacionar: lista `- ( ) ...` / `- I. ...`.
- A linha `**Gabarito:**` FECHA o bloco — tudo entre a linha `**Questão N** — ...`
  e ela fica dentro da caixa no PDF.

## Fidelidade ao conteúdo

- Texto do autor é verbatim. Corrigir SOMENTE erros mecânicos evidentes
  (ex.: "DESEMPNEHO", parêntese não fechado, duplicação de layout) — nunca
  reescrever, "melhorar" ou completar afirmações, mesmo que pareçam erradas.
- Inconsistência real no original (ex.: gabarito que contradiz o comentário):
  manter como está e AVISAR o usuário no resumo final.
- Sublinhados do original → `**negrito**`; tachados didáticos → `~~...~~`
  (recupere-os do dump do pymupdf4llm, que emite `<u>`/`~~` mesmo mutilando o texto).
- Lead-ins duplicados/frases truncadas por erro de diagramação do original podem
  ser removidos (anote no resumo).
- Emojis/dingbats de template do original (🧠, 📖, ➢, setinhas) são decoração:
  NÃO os copie para o MD (viram artefatos no PDF); o título do callout basta.
- Headings ALL CAPS do original: normalize para caixa normal (siglas ficam maiúsculas).
- Sumário do original: descarte números de página e artefatos de Word
  ("Erro! Indicador não definido."); o sumário do MD usa âncoras e o do PDF é gerado.
