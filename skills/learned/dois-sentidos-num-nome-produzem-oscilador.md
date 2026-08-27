---
name: dois-sentidos-num-nome-produzem-oscilador
description: Quando uma saída oscila mais do que as entradas justificam, suspeite do NOME antes do cálculo — dois conceitos distintos sob a mesma palavra produzem instabilidade que parece do sistema e é do vocabulário
metadata:
  pattern: debugging_techniques
  origin: manual_estudo, 26-27/08/2026 — dois casos na mesma sessão
  confidence: alta (o primeiro custou três recomendações contraditórias em seis horas)
---

**O padrão.** Uma saída muda três vezes num dia e você atribui isso ao sistema ser sensível
— aos dados serem ruins, ao modelo ser instável, aos parâmetros estarem mal calibrados.
Nenhuma dessas. **Duas grandezas diferentes estavam usando a mesma palavra**, e cada leitura
pegava uma delas. O sistema estava certo; o vocabulário é que não distinguia.

O diagnóstico tem uma assinatura reconhecível: **a saída se move mais do que as entradas
justificam.** Se você corrigiu um parâmetro e a resposta virou de ponta-cabeça, ou o modelo
é caótico — raro — ou você trocou de grandeza sem perceber, porque as duas atendem pelo
mesmo nome.

## Ocorrência 1 — "prioridade" eram duas coisas

Um modelo de alocação respondia à pergunta "quais matérias entram agora". Em seis horas ela
mudou **três vezes**, e a explicação que eu dava era que o modelo era sensível a parâmetro.

Eram duas grandezas chamadas *prioridade*:

- **horas do cenário base** — quanto o otimizador dá a cada item num conjunto fixo de
  parâmetros. **Move a cada parâmetro corrigido**, e naquele dia foram vários.
- **robustez entre cenários** — em quantos dos nove cenários testados o item recebe hora.
  **Não move** quando um parâmetro muda, que é exatamente a propriedade que uma composição
  de semanas precisa ter.

O consumidor usava a primeira e chamava de "valor esperado". Separadas, a oscilação parou.

## Ocorrência 2 — um campo fazendo o trabalho de três

Na mesma sessão, um campo chamado `p_prova_no_horizonte` carregava, sozinho:
**importância** (quanto o dono quer aquele alvo — afirmação de valor), **janela** (quem
consome recurso agora — restrição de prazo) e, por consequência, a proporção de treino.

O efeito era enganoso de um jeito específico: **um alvo aparecia valendo pouco quando valia
igual.** O que ele não tinha era prazo, e o número baixo dizia "vale pouco". A pessoa que
lia o cálculo tirava a conclusão errada sobre a própria preferência dela.

## Como aplicar

**A pergunta de diagnóstico:** *a saída se moveu mais do que a entrada justifica?* Se sim,
antes de mexer no cálculo, liste os nomes que aparecem nos dois lados e pergunte de cada um
se ele significa a mesma coisa nos dois.

**O sinal de alarme no código:** uma função devolve X e quem chama a usa como Y, com um
comentário explicando a equivalência. O comentário é a confissão — se fossem a mesma coisa,
não precisaria explicar.

**O conserto não é escolher uma.** As duas grandezas costumam ser legítimas e necessárias.
O conserto é **nomear as duas** e declarar qual pergunta cada uma responde, no ponto em que
alguém vai escolher entre elas.

**Trave com teste que leia o código, não só o valor.** As duas grandezas podem coincidir
hoje por acaso, e um teste de valor passaria. O teste que segura é o que exige que a função
consulte a fonte certa — por inspeção do fonte, se preciso.

Relacionado: [[a-segunda-copia-da-regra-diverge-calada]] — lá a mesma regra está escrita
duas vezes; aqui a regra é uma só, e o **nome** é que é duplo.
