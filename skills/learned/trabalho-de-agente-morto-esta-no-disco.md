---
name: trabalho-de-agente-morto-esta-no-disco
description: Agente em segundo plano que morre (limite de sessão, erro de API) devolve um relatório que descreve a ÚLTIMA INTENÇÃO, não o trabalho feito — meça o disco antes de concluir que se perdeu, porque relançar do zero joga fora o que já está escrito
metadata:
  pattern: workarounds
  origin: manual_estudo, 14/08/2026 — três agentes de folha de Economia mortos no mesmo minuto por limite de sessão
  confidence: alta (medido em três casos simultâneos, com a diferença entre relatório e disco quantificada)
---

**O padrão.** Quando um agente de segundo plano morre por limite de sessão ou erro de
API, o texto que volta no lugar do relatório é **a última coisa que ele ia fazer**, não o
que fez. Ler esse texto como estado do trabalho leva a relançar do zero — e a jogar fora
o que já está gravado. Antes de qualquer decisão, **meça o disco**.

O custo medido. Três agentes escreviam, em paralelo, as folhas dos tópicos 8, 9 e 10 de
Economia. Os três morreram no mesmo minuto, e os três relatórios diziam variações de
*"Now I have the sources I need. Let me write the folha."* A leitura óbvia é que nada foi
produzido. O `wc -w` disse outra coisa:

    08-contas-nacionais…md      7.114 palavras
    09-modelo-keynesiano…md     6.257 palavras
    10-is-lm-bp…md              7.967 palavras

As três folhas estavam **inteiras**. Eles morreram no passo seguinte — a geração das
figuras. Relançar teria descartado vinte e um mil palavras e repetido o trabalho mais
caro da noite; recuperar custou um `wc`, um build e dois consertos de dez linhas.

**Por que o relatório mente sem mentir.** O que volta é o último turno do agente, e o
último turno de quem trabalha bem é o *anúncio* do próximo passo, não o resumo do
anterior. Quanto melhor o agente narra o que vai fazer, mais enganoso é o fragmento
final.

**O procedimento, em ordem de custo.**

1. **Liste os arquivos que o agente deveria produzir** e meça-os — existência, tamanho,
   contagem de palavras ou linhas. É segundos.
2. **Tente fechar o que ele deixou aberto** antes de reescrever: compile, rode, valide. O
   que falha aponta exatamente o passo em que ele morreu.
3. **Relance só o passo que falta**, com o contexto do que já existe — não a tarefa toda.
4. Se o artefato parcial não presta, aí sim descarte; mas isso é conclusão de medição, e
   não de leitura do relatório.

**A armadilha vizinha, que apareceu no mesmo caso.** O material recuperado pode compilar
"limpo" e ainda estar pela metade: as três folhas geraram PDF com paginação plausível e
**zero figuras**, porque figura ausente era só aviso. Recuperar não é o mesmo que
concluir — depois de medir o disco, meça o *conteúdo* do que saiu. Ver
[[aviso-por-item-nao-diz-ausencia-total]].

**Corolário para quem orquestra.** Peça ao agente que escreva o artefato em disco cedo e
o refine depois, em vez de segurar tudo em contexto até o fim. Trabalho que só existe no
contexto do agente morre com ele; trabalho em disco sobrevive à morte dele — e é a razão
pela qual a instrução "escreva o texto primeiro, gere as figuras por último" salvou esta
noite sem ter sido dada para isso.
