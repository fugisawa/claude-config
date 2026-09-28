# Modo explorar: que conexões esta fonte tem com o argumento

O modo aberto. Serve para decidir o que vale ler a fundo e para achar o que o argumento não
previu: a conexão inesperada, a contradição, o que a fonte cobre e o artigo ainda não. Não
confirma nada; aponta onde olhar.

## Passos

1. **Declare o alvo antes de abrir a fonte.** O argumento inteiro (`docs/argumento.md`), uma
   seção dele ou uma afirmação; e as perguntas abertas do caderno (`docs/caderno.md`) que
   possam tocar a fonte. Sem alvo declarado, a exploração herda o viés de quem a pediu, e não o
   da fonte. Escreva o alvo no topo do bloco.
2. **Primeira passada de Keshav**: título, resumo, introdução, cabeçalhos, figuras e tabelas
   por alto, conclusão. `fichar.py mapa` dá os cabeçalhos; `janela --pagina 1` e a última página
   dão resumo e conclusão, e na cópia sem paginação, que o `mapa` anuncia na primeira linha,
   `janela --secao` faz as vezes da página. Em cópia de duas colunas, use `--corrido` no `mapa` e na `janela`, e
   confirme a página de cada trecho pelo `janela --termo` antes de gravar. Esse é o mínimo. Em artigo curto (até umas quinze páginas de texto),
   leia-o inteiro por páginas, porque a conexão inesperada costuma estar no corpo e não no resumo;
   em livro ou relatório longo, fique na primeira passada e nas seções que o mapa indicar. O que
   pedir conferência vira pedido de `responder` ou `verificar`.
3. **Classifique o tipo de fonte** (teórica, experimental, observacional, revisão, relatório,
   ensaio), porque o modo seguinte e a lista de apreciação dependem disso.
4. **Leia contra o argumento**, afirmação por afirmação do alvo, com quatro perguntas: a fonte
   **contradiz**, **estende**, **refina** ou **não cobre** isto? Cada resposta vira uma conexão
   candidata com o rótulo `(apoia)`, `(contraria)` ou `(menciona)`, o trecho curto e a página.
5. **Anote o que a fonte cobre e o argumento não**: a variável, a população, o desenho, a
   objeção que o argumento ainda não enfrenta. É aqui que aparece o que ninguém pediu.
6. **Marque tudo como candidato.** Nenhum número e nenhum trecho deste modo é "conferido";
   a exploração diz onde olhar, e o `verificar` diz o que está lá.
7. **Feche com as perguntas ao autor**: o que ele deveria mandar verificar, e o que deveria
   decidir sobre o alvo.

## Modelo do bloco

```markdown
**Alvo.** <argumento inteiro | seção | afirmação> · perguntas do caderno: <datas ou "nenhuma">

**Tipo de fonte:** <tipo> · **Mapa:** <seções principais com página>

**Conexões candidatas.** (a âncora é a página do periódico, `(p. N)`; a página da cópia, `(p. N da cópia)`, quando a versão lida não tem a paginação do periódico, como a prova tipográfica, o manuscrito aceito ou a publicação antecipada que o registro cita pela numeração dela; a posição no arquivo, `(p. N do PDF)`, na página fora dessa numeração, como a capa; ou a seção, `(seção …)`, quando a cópia não tem página nenhuma, como a que vem de XML ou de HTML)
- <afirmação do alvo> ← "<trecho curto>" (p. N) (apoia) — <o que estende ou refina>
- <afirmação do alvo> ← "<trecho curto>" (p. N) (contraria) — <em quê>
- <afirmação do alvo> ← <paráfrase> (p. N) (menciona) — <por que vale olhar>

**O que a fonte cobre e o argumento não.**
- <variável, população, desenho, objeção> (p. N)

**O que a fonte não cobre**, do que o alvo pedia: <lista, ou "nada relevante ficou de fora">

**Vale ler a fundo?** sim, em <seções> | não, porque <razão> · candidatos a `verificar`: <alegações>

**Perguntas ao autor:**
1. <…>
2. <…>
```
