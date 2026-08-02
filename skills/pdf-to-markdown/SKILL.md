---
name: pdf-to-markdown
description: >
  Converte PDF de terceiro em Markdown limpo e FIEL, preservando o que o dump ingênuo
  perde — ênfase inline, tabelas, figuras — e removendo a mobília que ele traz junto
  (marca d'água, cabeçalho/rodapé repetido, número de página). Use ao transformar
  material alheio em texto de estudo, leitura ou base de conhecimento: aula de cursinho,
  apostila, capítulo de livro, relatório, norma, paper. Use TAMBÉM quando uma extração
  já feita saiu com texto embaralhado no meio de parágrafos, letras soltas de marca
  d'água, negrito sumido ou células de tabela fora de ordem — o método diz por que cada
  um desses acontece e qual passo corrige. NÃO use para PDF que você mesmo gerou (a
  fonte é o seu HTML/Typst, não o PDF), nem para preencher/juntar/dividir formulário e
  arquivo — isso é `pdf-processing-pro`.
---

# PDF de terceiro → Markdown fiel

O erro que este método existe para evitar: rodar um extrator, olhar o começo do arquivo,
ver que "está bom" e seguir. O que quebra em PDF real quebra **no meio** — uma tabela na
página 12, o negrito que sumiu de uma definição, a marca d'água que picou uma frase em
letras soltas. Você só descobre quando estuda por um material errado.

A regra que organiza tudo: **meça antes, meça depois, e nunca confie no dump para o que é
visual.**

## O ciclo, em sete passos

### 1. Inventarie a fonte antes de converter

Conte o que **precisa sobreviver** — páginas, tabelas, figuras, questões numeradas, seções.
Esse número é o seu contrato: no passo 7 ele tem de bater.

```bash
uv run --with pypdf python <skill>/../pdf-processing-pro/scripts/validate_pdf.py fonte.pdf
uv run --with pillow python scripts/contact_sheet.py fonte.pdf /tmp/folha
```

A folha de contato põe todas as páginas em uma ou duas imagens. **Olhe.** É onde você vê
que há marca d'água, que a página 12 tem tabela, que a 30 é um diagrama. Dois minutos aqui
economizam a conversão inteira.

Cobertura de texto < 100% no `validate_pdf` significa página sem camada de texto: é
digitalização, e o caminho passa por OCR (`pdf-processing-pro/OCR.md`), não por aqui.

### 2. Escolha o extrator medindo, não por hábito

```bash
uv run --with pymupdf --with pymupdf4llm --with pdfplumber python scripts/ab_extratores.py fonte.pdf --out /tmp/ab
```

O placar mostra caracteres, spans de **negrito**, tabelas detectadas, vazamento de marca
d'água e tempo, por extrator. Leia com um critério: **texto a mais não é melhor** — pode
ser mobília repetida; e **negrito zero é grave** em material jurídico ou de concurso, onde
o negrito marca justamente o que a banca troca.

### 3. Extraia por spans, não por página

É o passo que diferencia este método de "rodar um conversor". `extract_spans.py` lê o PDF
**linha a linha, com estilo**, e por isso consegue:

- **descartar linha rotacionada** → marca d'água diagonal, que é o que pica frases em
  letras soltas;
- **detectar mobília por repetição** → o que aparece na mesma altura em ≥40% das páginas é
  cabeçalho/rodapé, não conteúdo;
- **descartar número de página** em vários formatos;
- **preservar ênfase** → `**negrito**`, `*itálico*`, `***ambos***`.

```bash
uv run --with pymupdf python scripts/extract_spans.py fonte.pdf bruto.txt
# audite a mobília que ele imprime em stderr ANTES de aceitar
```

> **Nunca use redação (`apply_redactions`) para tirar marca d'água.** Os retângulos das
> linhas rotacionadas cobrem o texto do corpo por baixo, e ele some junto. Foi assim que
> este passo nasceu.

### 4. Trate tabela e figura à parte — o dump não serve

Célula embaralhada é o defeito mais caro, porque parece certo. Duas rotas, nesta ordem:

1. **Extração dirigida**: `extract_tables.py --strategy lines` (borda desenhada) ou
   `--strategy text` (alinhamento). Confira o resultado **contra a imagem da página**.
2. **Transcrição visual**: renderize a página a 200 dpi e transcreva olhando. Mais lento,
   e é o que sobra quando a tabela não tem borda nem alinhamento regular.

Figura: decida entre **redesenhar** (se o conteúdo é um quadro que se lê melhor como
tabela ou diagrama limpo) e **recortar a imagem**. Um quadro de caixinhas quase sempre vira
tabela melhor do que vira imagem.

### 5. Estruture, sem reescrever o autor

Agora o texto vira Markdown: títulos, listas, blocos. **Fidelidade é regra**: você
reformata, não reescreve. Não corrija o autor no corpo — se algo está errado ou faltando,
isso é voz da edição e precisa estar **marcado como tal**, nunca embutido no texto dele.

Num material de estudo, atribuição falsa vira memória falsa: quem relê seis meses depois
não tem como saber que aquele parágrafo não era do autor.

### 6. Converta e renderize

O Markdown é a fonte. O PDF de leitura, se houver, sai dele — não do PDF original.

### 7. Feche o contrato: o QA é visual e é obrigatório

Compare com o inventário do passo 1. **As contagens têm de bater.**

Rasterize e **leia** as páginas, procurando os quatro defeitos que sobrevivem a tudo:

- texto sobreposto;
- corte na borda;
- imagem pixelada onde devia ser vetor;
- **e o pior: conteúdo que sumiu em silêncio** — a tabela que não veio, a seção que o
  extrator engoliu. É por isso que a contagem do passo 1 existe.

```bash
pdftoppm -png -r 130 saida.pdf /tmp/qa/p   # e abra os PNGs
```

## Armadilhas conhecidas

| Sintoma | Causa | Passo que corrige |
|---|---|---|
| Frases picadas em letras soltas | marca d'água rotacionada no dump | 3 |
| Mesma linha repetida a cada página | cabeçalho/rodapé tratado como conteúdo | 3 |
| Negrito sumiu | extrator sem suporte a estilo (pdfplumber devolve texto puro) | 2 e 3 |
| Células fora de ordem | dump de tabela pela ordem do fluxo de texto | 4 |
| Texto some no meio de parágrafos | redação usada contra a marca d'água | 3 (nunca redija) |
| Saída vazia ou quase | PDF sem camada de texto | 1 → OCR |
| "Ficou ótimo" e faltam 3 seções | QA feito só no começo do arquivo | 1 e 7 |

## Scripts

| Script | Para quê |
|---|---|
| `contact_sheet.py` | todas as páginas em 1-2 imagens, para mapear a fonte |
| `ab_extratores.py` | placar comparando pymupdf4llm × pdfplumber × docling |
| `extract_spans.py` | a extração boa: sem marca d'água, sem mobília, com ênfase |

Para dividir, juntar, validar, extrair tabela ou preencher formulário, use os scripts de
`pdf-processing-pro` — esta skill cuida do **método de fidelidade**, aquela cuida da
**mecânica do arquivo**.

## Instância de referência

`igepp-aula-reformat` é este método aplicado a um caso concreto (aula de cursinho gerada
por TCPDF, com marca d'água "Edição 20xx"), com destinos e convenções de um projeto
específico. Leia como exemplo de como aterrissar estes sete passos num material recorrente.
