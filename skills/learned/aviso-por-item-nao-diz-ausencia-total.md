---
name: aviso-por-item-nao-diz-ausencia-total
description: Guarda que avisa POR ITEM não sabe dizer que faltam TODOS — a ausência total é qualitativamente outra coisa e precisa de predicado de conjunto próprio, senão N avisos idênticos leem-se como ruído e o artefato vazio passa por completo
metadata:
  pattern: debugging_techniques
  origin: manual_estudo, 14/08/2026 — três PDFs publicados "limpos" com zero das suas 48 figuras
  confidence: alta (o defeito atravessou build, validador e leitura humana antes de ser visto)
---

**O padrão.** Uma guarda que emite um aviso **para cada item faltante** responde bem à
falta parcial e é cega para a falta total. Quando tudo falta, ela produz N avisos
idênticos — e N avisos idênticos, num relatório que já tem avisos, leem-se como ruído.
Pior: a linha de resumo continua dizendo *"0 erros"*, e o artefato vazio passa por
completo. **A ausência total merece predicado próprio**, com mensagem que diga o
conjunto ("nenhum de N"), e não a soma de mensagens sobre indivíduos.

O custo medido. Três folhas de Economia foram publicadas com paginação plausível — 11, 9
e 11 páginas —, `0 erros` no validador e **zero das suas 48 figuras**. O build emitiu 48
avisos `W-FIGURA-SEM-SVG`, um por bloco; eu li a linha de resumo, vi "0 erros" e declarei
os PDFs prontos. O documento parecia inteiro porque **paginação plausível é o disfarce
perfeito**: um PDF sem nenhuma figura não fica visivelmente truncado, fica *menor*, e
menor não dispara suspeita nenhuma.

**Por que a severidade não é a resposta.** O reflexo é promover o aviso a erro. Aqui isso
teria sido pior: o contrato *"figura ausente não pode bloquear o build"* existia, estava
testado, e serve a um fluxo legítimo — escrever o texto primeiro e gerar as figuras
depois, que é exatamente como os agentes desta noite trabalhavam. **Promover teria
quebrado o trabalho que a guarda deveria proteger.** O teste existente foi quem avisou; a
saída certa foi manter a severidade e trocar a *mensagem*, que passou a nomear o conjunto
e a dizer o que fazer.

**A regra que fica.** Ao escrever guarda que itera sobre uma coleção, pergunte-se: *como
ela se manifesta quando o cardinal do faltante é igual ao cardinal do total?* Se a
resposta for "igual, só que mais vezes", falta um ramo. E ao decidir o remédio, prefira
**mensagem distinta na mesma severidade** quando houver contrato deliberado de não
bloquear — a severidade é do fluxo, a clareza é da mensagem, e trocar uma pela outra
quebra usuário legítimo.

**A face humana do mesmo defeito.** Ler a linha de resumo em vez do corpo é o atalho que
torna a cegueira da guarda letal. `0 erros` responde a pergunta *"tem erro?"*, e nunca a
pergunta *"está pronto?"*. Vizinha de [[checagem-que-nao-pode-falhar]], que trata do
verificador cuja saída limpa afirma cobertura inexistente, e de
[[trabalho-de-agente-morto-esta-no-disco]], porque foi ao recuperar trabalho de agente
que o artefato meio-pronto entrou no repositório parecendo inteiro.
