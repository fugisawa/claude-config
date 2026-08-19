---
name: guarda-que-varre-nao-distingue-obra-de-defeito
description: Guarda que varre a árvore inteira reprova trabalho em curso com a mesma cara de defeito, e num clone com várias sessões e agentes isso vira rotina — o remédio não é rodar de novo nem escopar a guarda aos caminhos staged, é ler o vermelho junto com o mtime do arquivo acusado e esperar
metadata:
  pattern: error_resolution
  origin: manual_estudo, 18/08/2026 — três ocorrências numa sessão, duas sessões e nove agentes no mesmo clone
  confidence: alta (cinco instâncias medidas somando as duas de 11/08; a última travou o commit dos dois lados ao mesmo tempo)
---

**Estende [[arvore-suja-pode-nao-ser-sua]], e corrige um pedaço dela.** Aquela lição manda,
diante de suíte vermelha logo após ter passado verde, *"rode de novo em vez de editar"*.
Isso resolve o caso dela — o salvamento em duas etapas, que fica inconsistente por segundos.
**Não resolve o caso desta**, em que a árvore fica genuinamente inconsistente por dezenas de
minutos, porque alguém está escrevendo um documento de mil e trezentas linhas. Rodar de novo
devolve o mesmo vermelho a tarde inteira.

**O padrão.** Uma guarda que varre a árvore inteira responde *"o repositório está
consistente?"*. Essa é a pergunta certa, e ela **não distingue** duas causas de "não":
alguém errou, ou alguém está no meio de acertar. Com uma sessão sequencial as duas coincidem,
porque não existe "meio". Com duas sessões e nove agentes escrevendo em paralelo, o meio é o
estado normal do disco, e a guarda passa a reprovar obra em andamento com a mesma cara de
defeito.

**As três ocorrências de 18/08, em ordem de custo crescente.**

1. Um agente meu rodou `doctor_docs` e relatou quatro links quebrados num arquivo da outra
   sessão. Rodei um minuto depois: zero. O agente dela tinha fechado o arquivo no intervalo.
   Custo: uma mensagem de aviso desnecessária.
2. Ela mediu um arquivo meu e **commitou** um relatório que citava aqueles quatro erros como
   fato. Custo: uma correção pública, e a segunda cópia de um número que já não valia.
3. O `pre-commit` reprovou **os dois lados ao mesmo tempo**, por dois capítulos dela que
   existiam em Markdown e ainda não tinham PDF. Meu commit de 94 arquivos e o dela de dois
   ficaram parados no mesmo semáforo, nenhum dos dois pela própria causa.

**O conserto que parece óbvio e é errado.** A tentação é escopar a guarda aos caminhos que
estão no índice: "só me cobre pelo que eu vou commitar". Isso mataria exatamente a classe de
defeito que ela existe para pegar — fonte publicada sem PDF, link para arquivo que sumiu,
declaração que não resolve. Essas nunca aparecem no que você está commitando; aparecem na
relação entre o que você commita e o resto. **A guarda varre porque o defeito é de relação.**

**O procedimento, que é de leitura e não de código:**

1. Vermelho de guarda em clone compartilhado **não é diagnóstico até ser lido com o
   `mtime`**. `ls -l --time-style=+%H:%M` no arquivo acusado. Minutos atrás e não é seu:
   é obra, não defeito.
2. Obra alheia: **espere e avise**. Não conserte (desfaz trabalho correto pela metade), não
   contorne com `--no-verify` (o vermelho é real — a árvore está mesmo inconsistente; o que
   está errado é o instante), e não peça ao outro que engavete por conveniência sua.
3. Se a espera for longa, o outro lado é quem sabe estimá-la. Pergunte em vez de supor, e
   peça que ele avise **quando pousar** em vez de você ficar sondando.
4. Ao relatar resultado de guarda para outra sessão, **confira o `mtime` antes de mandar**.
   Foi assim que as ocorrências 1 e 2 nasceram: as duas eram relatos honestos de uma medição
   verdadeira num instante que já tinha passado.

**O que não se conclui daqui.** Que o gancho está errado, ou que varredura é desenho ruim.
Nas três ocorrências a guarda estava certa sobre o estado do disco; ela só não tinha como
saber que aquele estado tinha dono e prazo. Guarda mede o disco — quem tem o calendário é
quem está escrevendo, e por isso a correção é de protocolo entre as sessões, não de código.
