# Estilo de Escrita (prosa em português)

> Par de [coding-style.md](./coding-style.md): aquele governa código, este governa texto
> que um humano vai ler.

## Quando vale

Vale para todo texto que **eu autoro** e que o Daniel vai ler ou entregar a outra pessoa:
respostas de conversa, artefatos de estudo, complementos, cheatsheets, fichas, guias
rápidos, briefings, planos, análises, mensagens de commit e descrição de PR.

**Não vale para texto alheio.** Em aula reformatada o conteúdo do autor é intocável, e o
padrão governa só o que eu acrescento — voz da edição, callouts, notas, colofão, sumário,
rótulo de figura e diagrama que eu redesenho. Lei seca não se edita nunca.

## Frase

- **Toda frase tem verbo finito.** Sem exceção em prosa corrida. Legenda, rótulo de tabela
  e item de lista curta não são prosa corrida.
- **Rótulo com dois-pontos não substitui oração.** "Três agravantes:" vira "Há três
  agravantes." ou entra na frase anterior.
- **Nada de cadeia de setas** (`A → B → falha`) nem de composto empilhado com hífen.
  Escreve a relação por extenso.
- Duas frases sem verbo em sequência são defeito mesmo que cada uma passasse sozinha.

## Palavra

Anglicismo com equivalente corrente em português é erro. Os que mais aparecem:

| Não | Sim |
|---|---|
| fetch | busca, leitura direta, baixar |
| snapshot | registro daquela data, captura |
| checkpoint | ponto de verificação, versão |
| peer-reviewed | revisado por pares |
| preprint | pré-publicação |
| pool | conjunto |
| insight | achado, percepção |
| overview | panorama, visão geral |
| feedback | retorno, devolutiva |
| trade-off | compensação, o que se ganha e o que se perde |
| baseline | linha de base, referência |
| gap | lacuna |
| output / input | saída / entrada |
| default | padrão |
| workflow | fluxo de trabalho |
| setup | configuração |

**Exceções, não traduzir:** termos já incorporados ao português (site, e-mail, online,
link, software, design, layout, bug, log, script, backup) e nomes de coisa no sistema do
Daniel (skill, prompt, briefing, planner, cheatsheet, token, commit).

**O registro não oscila.** Escolhida a forma, ela vale no documento inteiro. Escrever
"revisado por pares" numa linha e "peer-reviewed" na outra é defeito mesmo quando as duas
formas seriam aceitáveis isoladamente.

## Calibração ao leitor

Presumir demais e explicar o óbvio são o mesmo defeito errando para lados opostos, e
tratá-los como dois problemas leva a corrigir um piorando o outro. Um critério resolve os
dois:

> **O leitor precisa disto para decidir o próximo passo?** Se não precisa, corta. Se
> precisa e não está no texto, escreve.

- Termo técnico, sigla ou categoria estreia com a definição na mesma frase, inclusive os
  meus. Chamar algo de "declaração contra o próprio interesse" sem dizer que é uma classe
  de prova é petição de princípio.
- Não fazer o leitor voltar atrás para procurar rótulo, número ou apelido que inventei
  antes. Dizer a coisa no lugar onde ela é usada.
- Latinismo e jargão só entram se trabalharem. Um `non liquet` glosado três palavras
  depois não trabalha, só atrasa.

## Coesão e explicação

- Cada parágrafo deixa claro qual é a relação com o anterior. Salto sem conectivo é salto.
- **Escreva a ideia-núcleo do parágrafo antes de desenvolvê-la.** O ganho não é de estilo, é
  de controle: enunciada de saída, ela impede a digressão, porque tudo o que não a
  desenvolve fica visivelmente fora de lugar. É o remédio do salto lógico na origem, e não
  na revisão. (Othon Garcia, *Comunicação em Prosa Moderna*, cap. do parágrafo.)
- **Uma explicação boa vale mais que duas ruins.** Se a primeira não pegou, a segunda muda
  o **tipo** de desenvolvimento, não as palavras. Os tipos são sete: enumeração de detalhes,
  confronto (contraste ou paralelo), analogia, exemplo, causa e motivo, divisão em partes,
  definição. Repetir a mesma forma com sinônimos é a maneira mais comum de nenhuma das duas
  prestar.
- **Analogia explica o desconhecido pelo conhecido, o estranho pelo familiar.** Se o termo
  que explica for tão desconhecido quanto o explicado, não é analogia — é exemplo obscuro, e
  sai.
- Exemplo serve para iluminar. Exemplo que precisa de exemplo sai.
- **Fato tem causa e efeito; ato humano tem razão, motivo e consequência.** Decisão de
  tribunal, escolha de gestor e mudança de norma pedem "a razão de" e "as consequências de",
  não "a causa" nem "os efeitos".

## Passe de releitura

Antes de enviar resposta longa ou entregar arquivo de texto, **releia procurando esta
lista.** O passe separado vale mais que a boa intenção na hora de escrever: revisar em
segunda passada derrubou decalque de 43% para 25%, enquanto pedir naturalidade de antemão
piorou o resultado (Li et al., ACL 2025).

**O teste do resumo, que é o mais barato de todos.** Percorra os parágrafos extraindo a
ideia-núcleo de cada um, na ordem. Se a sequência ler como um sumário coerente, a estrutura
está de pé. Onde ela tropeçar, aquele parágrafo não tem ideia-núcleo ou tem duas — e é ali
que está o salto que o leitor vai sentir.

## O que esta regra não manda

- **Não é regra de brevidade.** Legível vale mais que curto. Encurtar se faz cortando o
  que não muda a decisão do leitor, nunca comprimindo a frase, porque comprimir produz
  exatamente a frase truncada que esta regra proíbe. Pedir concisão de forma cega aumentou
  a saída medida em 28% no Sonnet 5 e 42% no Opus 4.8.
- **Não impõe meta numérica** de palavras por frase ou por parágrafo. Em português o
  registro culto corre mais longo que em inglês, e meta de comprimento vira telegrama.
- **Não força uniformidade de formulação.** Conceito que reaparece em contexto novo é
  escrito diferente de propósito. Divergência de formulação é desejada; divergência de
  fato é erro.
