---
name: texto-para-impressao
description: Use quando o Daniel quiser IMPRIMIR um texto de leitura corrida para ler com gosto — ensaio, artigo, capítulo, texto longo de terceiro já em Markdown ou texto puro — e pedir "melhora a fonte, o espaçamento, a organização, gera um PDF para impressão", com a condição de que o conteúdo não mude. Produz PDF em LuaLaTeX com tipografia de livro (EB Garamond de corpo 13 pt com entrelinha 17 pt, mancha de 118 mm ≈ 68 caracteres por linha, notas no rodapé, margens espelhadas, cabeçalho corrente) por um script que inventaria o texto, verifica o escape LaTeX por ida e volta e mede páginas e caracteres por linha. Use TAMBÉM quando um PDF de leitura já gerado saiu com linha longa demais, título em sem-serifa, fórmula em fonte destoante, espaço irregular entre parágrafos ou nota de rodapé fora da página em que é citada. NÃO use para relatório com capa, quadro lateral e gráfico (`briefing-designer`), artefato de estudo (`artefatos-estudo`, no `manual_estudo`), trabalho acadêmico ABNT/APA (perfis pandoc), Word (`docx`) nem para o caminho inverso, PDF de terceiro → Markdown (`pdf-to-markdown`).
---

# Texto para impressão

O pedido é sempre o mesmo: "vou imprimir para ler melhor; não altere o conteúdo; melhore
fonte, organização, espaçamento, tamanho". O entregável é **tipográfico**, e o conteúdo é
intocável. Tudo aqui deriva dessa divisão: a forma pode mudar quanto for preciso, e cada
mudança visível — um nome de autor acrescentado, uma aspa reta que virou curva, uma
fórmula recomposta — é declarada na entrega, nunca feita em silêncio.

Medido em 12/09/2026, sem este método, o agente entregou linha de 75–85 caracteres e
achou aceitável, pôs os títulos em sem-serifa negrito, fez a margem interna maior que a
externa, não pôs cabeçalho corrente, pôs a citação em itálico e "conferiu" a fidelidade com
uma razão de similaridade de 0,91. Cada regra abaixo fecha um desses buracos.

Dois termos valem para o documento inteiro. **Mancha** é o retângulo de texto impresso na
página, e **corpo/entrelinha** (13/17) é o tamanho da letra em pontos sobre a distância
entre linhas, também em pontos.

## Quando usar

- Texto que o Daniel vai **ler no papel**: ensaio, artigo, capítulo, texto longo de
  terceiro salvo em Markdown ou texto puro (parágrafo por linha ou com quebra dura).
- Reimpressão de um PDF que saiu ruim: linha longa, título destoante, notas no fim quando
  se queria no rodapé, espaço irregular entre parágrafos.

**Não é o lugar de** relatório para circular, com capa e gráfico (`briefing-designer`); de
artefato de estudo memorável (`artefatos-estudo`); de acadêmico com norma (perfis pandoc
`-d abnt|apa`); nem de tabela ou imagem como parte central do texto (o conversor não as
trata: avise e componha à mão no `.tex`).

## O fluxo

### 1. Inventarie antes de decidir

```bash
python3 ~/.claude/skills/texto-para-impressao/scripts/md2livro.py texto.md --inspecionar
```

O inventário diz o que o conversor **entendeu**: título, linhas curtas depois dele lidas
como autor (sem dígito) ou data (com dígito), idioma adivinhado por contagem de palavras
funcionais, blocos (parágrafos, `##`, `###`, quebras por linha em branco dupla ou `* * *`,
citações `>`, versos indentados, listas), estilo das notas (`[n]` + seção "Notes/Notas" ao
estilo Paul Graham, ou `[^id]` do Markdown), quantas substituições de glifo fará e os
avisos, que saem como linhas `AVISO:` depois da contagem `avisos: N`. **Leia os avisos.**
Nota citada sem definição, nota citada duas vezes, aspas em número ímpar e asterisco solto
são defeitos do arquivo de origem que o PDF vai carregar; o arquivo de origem não se edita
— corrija por `--titulo`, `--autor`, `--data`, `--lang`, ou relate o aviso na entrega.

### 2. Faça as quatro perguntas que mudam o resultado

Se o Daniel não disse, pergunte (`AskUserQuestion`), pondo o padrão recomendado como
primeira opção de cada pergunta:

| Decisão | Opções | Padrão e razão |
|---|---|---|
| Notas | rodapé da página × fim, como no original | **rodapé**: lê sem ir e voltar; o texto da nota não muda, só a posição |
| Impressão | A4 frente e verso × A4 só frente × Carta | **frente e verso**: margens espelhadas, número na borda externa |
| Anotação à mão | margens de livro × margem externa larga | **livro**: mais compacto; anotação empurra a mancha para dentro |
| Fonte | EB Garamond × Crimson Pro × Charter × Alegreya | **Garamond**; Charter para impressora fraca (traço firme, minúscula alta) |

Se ele disse "faz aí", use os padrões e liste-os na entrega. **Não prometa número de
páginas antes de medir**: a estimativa de 18–20 páginas para o ensaio do Graham deu 32
(11,8 mil palavras ≈ 350 palavras por página em Garamond 13/17 numa mancha de 118 mm).

### 3. Gere

```bash
python3 ~/.claude/skills/texto-para-impressao/scripts/md2livro.py texto.md \
  --autor "Nome do Autor" [--fonte garamond|crimson|charter|alegreya] [--notas rodape|fim] \
  [--papel a4|carta] [--so-frente] [--margem-anotacao] [--lang pt|en] \
  [--mancha 118] [--corpo 13] [--entrelinha 17] [--sem-cabecalho] [--sem-controle] [--tex saida.tex] [-o saida.pdf]
```

O PDF nasce ao lado do arquivo de origem, com o mesmo nome; `-o` muda isso. O script grava
o `.tex`, o `.log` e as páginas de controle em PNG numa pasta de compilação, cujo caminho
ele imprime na linha `build:`; `--tex` guarda uma cópia do `.tex` onde você disser, e é
nela que se faz ajuste fino à mão (fórmula, tabela) antes de recompilar com `lualatex` duas
vezes.

### 4. Confira antes de entregar (obrigatório)

São cinco conferências. O relatório do script traz as três primeiras; as duas últimas você
faz à parte:

- **Log**: `overfull: 0` e `glifos ausentes: nenhum`. Overfull é linha que estourou a
  mancha e invadiu a margem; glifo ausente é caractere que a fonte não tem e saiu em branco
  no papel.
- **Caracteres por linha**: mediana entre 60 e 72. Fora disso o script sugere a mancha;
  não aceite 80 porque "coube".
- **Notas**: `citadas` = `definidas`, e as notas geradas a partir de link vêm contadas à
  parte na mesma linha. Nota citada duas vezes sai como aviso e recebe só a chamada na
  segunda vez, sem repetir o texto ao pé da página.
- **Fontes**: `pdffonts saida.pdf` lista só a família escolhida (regular, itálico, e o
  negrito se o texto o usa). Aparecer `CMR`, `CMMI` ou `CMSY` é fórmula `$…$` composta
  em Computer Modern: recomponha no `.tex` com `\textit{}` e `\textsuperscript{}`.
  `LMMono` é trecho de `código` em monoespaçada, esperado.
- **Páginas de controle**: o script renderiza a 1, a 2, a 3, a primeira com nota e a
  última. Olhe todas com `Read`: a página de rosto; a par, com o autor no cabeçalho e o
  número à esquerda; a ímpar, com o título e o número à direita; a nota na mesma página da
  chamada. Procure espaço entre parágrafos uniforme, os três asteriscos da quebra de seção
  não sozinhos no pé da página e citação sem itálico.

### 5. Entregue

Entregue o PDF ao lado do arquivo de origem, enviado com `SendUserFile`, e escreva uma
recapitulação que diga o número de páginas **medido** e declare toda decisão tipográfica
que acrescentou ou alterou algo visível: autor posto no rosto e no cabeçalho quando o
arquivo de origem não o trazia, aspas retas que viraram curvas, `--` e `---` que viraram
meia-risca (–) e travessão (—), fórmula recomposta, link que virou nota com a URL. Se o
Daniel quiser guardar a origem para ajustes futuros, o `.tex` é o que se guarda; o PDF não
é fonte de nada.

## A especificação, para reproduzir à mão se faltar o LuaLaTeX

| Item | Valor | Razão medida |
|---|---|---|
| Corpo/entrelinha | Garamond 13/17; Crimson 12,5/16,5; Charter 11,5/15,5; Alegreya 12/16 | as quatro dão 66–68,5 caracteres por linha em 118 mm; Garamond tem minúscula baixa e a 12 pt em 132 mm deu 84 |
| Mancha e margens (A4) | 118 mm; interna 34, externa ≈ 58, topo 32 | proporção de livro; com anotação, interna 24 |
| Parágrafo | recuo 1,3 em, sem espaço entre parágrafos; sem recuo após título, quebra ou citação | ritmo de livro |
| Pé de página | `\raggedbottom`, viúva e órfã proibidas (linha solta de parágrafo no alto ou no pé da página) | `\flushbottom`, com a cola de estiramento que o `\parskip` então tinha, esticou o espaço entre parágrafos (badness 10000, o pior grau que o TeX registra) nas páginas com nota longa |
| Seção `##` | versalete (maiúscula da altura da minúscula) espaçado, centrado, 2 linhas acima e 1 abaixo, `\needspace` | mesma família do corpo; sem-serifa destoa |
| Quebra de seção | três asteriscos centrados, quando o arquivo de origem separa por ≥ 2 linhas em branco ou `* * *`/`---` | marca a pausa sem inventar título |
| Notas | rodapé no corpo menos 2,5 pt sobre a entrelinha menos 4 (10,5/13 no Garamond), número em recuo pendente de 1,6 em (o número sai para fora do bloco); chamada sobrescrita em algarismos alinhados; corpo em algarismos antigos | número em algarismo antigo sobrescrito fica ilegível |
| Cabeçalho | par: autor em versalete, ou o título se não houver autor, e número externo; ímpar: título; página 1 sem cabeçalho, número no pé | convenção de livro |
| Citação `>` / verso | `quote` no mesmo corpo, sem itálico / `verse` | itálico em bloco inteiro cansa e parece ênfase |
| Link `[texto](url)` | texto no corpo e a URL numa nota de rodapé (ou entre parênteses com `--notas fim`), na própria fonte do texto | URL em monoespaçada destoa e acrescenta família ao PDF |
| Fórmula `$…$` | passa direta (Computer Modern) | prefira `\textit{m}\textsuperscript{\textit{n}}` no `.tex`, como na nota 17 do Graham |

## O que o conversor garante, e o que não

A garantia de fidelidade vive no `.tex`, não no PDF. No `.tex` ela é forte: cada parágrafo
passa por escape LaTeX **verificado por ida e volta** (`assert`), as únicas substituições
são de glifo e vêm contadas no relatório (aspas, apóstrofo, reticência, risca), as notas
citadas são conferidas contra as definidas, e a estrutura duvidosa vira aviso. No PDF ela
não existe: `pdftotext` devolve palavra hifenizada em duas linhas, e por isso similaridade
sobre o PDF (`difflib`, 0,91) não prova nada.

Ele não protege de quatro coisas: a linha curta no início ser lida como autor ou data
quando era corpo (confira no inventário e force com as opções); a tabela e a imagem, que
ele não converte; a fórmula, que sai na fonte errada; e o Markdown fora do comum, com HTML
embutido ou notas dentro de citação.

## Armadilhas que custaram uma compilação

- `\vspace{\baselineskip plus 2pt}` dá "Missing number": TeX toma o registro `\baselineskip`
  como cola completa (cola é o espaço elástico do TeX, com valor fixo mais o quanto pode
  esticar e encolher) e não lê o `plus`. Escreva `1\baselineskip`.
- `geometry` rejeita `oneside` ("keyval Error: oneside undefined"); só a classe aceita.
  Frente única é a ausência de `twoside` no `geometry`.
- Cola de estiramento em `\parskip` com `\flushbottom` produz página com parágrafos
  visivelmente afastados; a correção é `\raggedbottom`, não mais cola.
