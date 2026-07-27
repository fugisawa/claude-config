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
# opcionais — para material ORIGINAL (não-IGEPP) que reusa este pipeline:
atribuicao: "produzido em DD/MM/AAAA (não é material IGEPP)"   # default: "IGEPP — Edição {edicao}"
nota_capa: "frase da capa"   # default: nota "Edição reformatada: texto integral preservado…"
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
- Callouts: use a **gramática semântica da trilha de estudo** (ver seção "Marcação
  semântica" abaixo). `[!warning]`/`[!tip]`/`[!note]` continuam aceitos (aliases:
  warning→excecao, tip/note→dica), mas em aula NOVA prefira o tipo específico.
  Aviso SEU sobre a reformatação (duplicata, trecho mantido conforme o original) vai
  em `> [!edicao]`, nunca em `[!warning]`: `[!warning]` é a voz do autor.
- Blockquote comum (`> `) só para notas de rodapé de tabela; citação de norma
  vai em `> [!lei]`.
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

## Marcação semântica dos elementos (política de 26/07/2026)

Ao autorar o MD, **identifique ativamente** os trechos da apostila que correspondem
aos elementos da gramática da trilha de estudo e marque-os com o callout específico
(contrato completo em `~/manual_estudo/estudo/CONVENTIONS-ESTUDO.md`):

| No texto do autor | Elemento |
|---|---|
| "X é...", "conceitua-se...", "entende-se por..." | `> [!def] Termo` |
| transcrição de CF/lei/decreto/súmula/MTO | `> [!lei] Art. N, norma` |
| "por exemplo", caso concreto, aplicação | `> [!ex] contexto` |
| "a banca costuma...", "cuidado com...", troca clássica | `> [!pegadinha] título` |
| "salvo...", "exceto...", ressalva à regra | `> [!excecao] título` |
| macete, mnemônico, "guarde que..." | `> [!dica] título` |
| prazo, data, percentual, quórum memorizável | `> [!prazo] rótulo` |
| prosa argumentativa/expositiva | parágrafo comum (explicação) |
| **observação do REFORMATADOR** (duplicata de questão no original, trecho mantido conforme a fonte, nota de reformatação) | `> [!edicao] título` |

- **Na dúvida sobre a classificação — ou sobre a exatidão do conteúdo — pesquise em
  fontes fidedignas** (texto da norma no Planalto, MTO/SOF, jurisprudência STF/STJ,
  manuais oficiais) antes de decidir. Registre a fonte consultada no resumo final.
- Não force: trecho que não é claramente um elemento fica como prosa. Elemento
  errado é pior que elemento ausente.
- **`[!edicao]` é a única linha da tabela em que quem fala NÃO é o autor** — é o
  reformatador avisando o leitor. Antes dele esses avisos iam em `[!warning]` (âmbar,
  no vocabulário do conteúdo), e o leitor lia como exceção da matéria uma observação
  que não é da matéria. Sai quieto (hairline cinza, glifo `※`) e não ecoa na banda.
  Nunca use `[!edicao]` para conteúdo do autor.

## Fidelidade ao conteúdo (política de 26/07/2026 — substitui o verbatim estrito)

- **Substância do autor é preservada; clareza pode melhorar.** É permitido deixar o
  texto mais claro e melhor explicado — desfazer frase confusa, quebrar período
  quilométrico, explicitar um conectivo, completar frase truncada pela diagramação —
  **sem alterar muito o conteúdo**: mesmas afirmações, mesma ordem de ideias, mesma
  voz. NÃO é permitido: reescrever no seu estilo, acrescentar doutrina própria,
  cortar conteúdo, mudar o alcance de uma afirmação.
- **Corrigir SOMENTE erro crasso e evidente** — e confirmado (pesquise a fonte
  fidedigna antes): artigo de lei citado errado conferível no Planalto, troca
  patente de PPA/LDO contra a CF, erro mecânico ("DESEMPNEHO", parêntese aberto).
  Toda correção entra no resumo final (o quê, onde, fonte).
- Erro *suspeito* mas não evidente (ex.: gabarito que contradiz o comentário sem
  que se prove qual dos dois está certo): **manter como está e AVISAR** no resumo.
- `nota_capa` de aula com intervenções deve ser honesta: em vez de "texto integral
  preservado", use "conteúdo do autor com marcação semântica e ajustes pontuais de
  clareza; correções listadas no colofão".
- Sublinhados do original → `**negrito**`; tachados didáticos → `~~...~~`
  (recupere-os do dump do pymupdf4llm, que emite `<u>`/`~~` mesmo mutilando o texto).
- Lead-ins duplicados/frases truncadas por erro de diagramação do original podem
  ser removidos (anote no resumo).
- Emojis/dingbats de template do original (🧠, 📖, ➢, setinhas) são decoração:
  NÃO os copie para o MD (viram artefatos no PDF); o título do callout basta.
- Headings ALL CAPS do original: normalize para caixa normal (siglas ficam maiúsculas).
- Sumário do original: descarte números de página e artefatos de Word
  ("Erro! Indicador não definido."); o sumário do MD usa âncoras e o do PDF é gerado.
