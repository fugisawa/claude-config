---
name: arvore-suja-pode-nao-ser-sua
description: Em clone com duas sessões, o estado do disco num instante não é necessariamente seu — antes de commitar ou de consertar uma suíte vermelha, compare o mtime dos arquivos com o horário do seu último commit, porque o remédio para trabalho alheio em voo é esperar, não editar
metadata:
  pattern: error_resolution
  origin: manual_estudo, 11/08/2026 — duas ocorrências no mesmo dia, uma evitada por margem de 12 minutos
  confidence: média (duas instâncias medidas; a primeira foi evitada por sorte e não por método, que é justamente o que originou a lição)
---

**O padrão.** Quando duas sessões trabalham no mesmo clone, `git status` deixa de responder
"o que eu fiz" e passa a responder "o que existe agora". As duas perguntas coincidem quase
sempre, e é por isso que a diferença morde: o hábito de tratar a árvore suja como sua está
certo 95% das vezes e destrói trabalho nas outras. **O sinal que separa as duas é o relógio** —
`ls -l --time-style=+%H:%M` contra o horário do seu último commit.

Isto é distinto de [[fronteira-de-arquivo-nao-cria-dono-da-coerencia]]. Lá o problema é de
**conteúdo**: dois artefatos, cada um coerente consigo mesmo, afirmando coisas opostas. Aqui é
de **tempo de escrita**: o arquivo está correto, só não é seu ainda.

**Ocorrência 1 — o commit que quase absorveu trabalho alheio.** A decisão `0007` do
`manual_estudo` proíbe `git add` solto seguido de `git commit`, porque o segundo publica o
índice inteiro. Eu respeitei a letra e violei o espírito: rodei `git add -A disciplinas/` e
depois `git commit … disciplinas/ …`. Commit por caminhos, sim — mas o caminho era um
diretório, e tudo o que estivesse sujo lá dentro entraria. Meu commit saiu **13:26**; a outra
sessão começou a escrever em `disciplinas/afo/` às **13:38**. Margem de doze minutos, e nenhuma
delas foi minha por mérito.

**Ocorrência 2 — a suíte vermelha que não era minha.** Um `git push` foi recusado pelo
`pre-push` com a suíte vermelha, segundos depois de eu ter rodado a mesma suíte verde. A outra
sessão tinha salvado o **arquivo de teste às 13:56** e o **módulo às 13:57**; meu push caiu no
minuto do meio, quando o teste já cobrava uma capacidade que o módulo ainda não tinha. Se eu
tivesse "consertado" o vermelho, teria desfeito trabalho correto pela metade.

**O procedimento, e ele custa dois comandos:**

1. Antes de commitar, `git status --short` e, para tudo que você não reconhece,
   `ls -l --time-style=+%H:%M <arquivos>` contra `git log -1 --date=format:'%H:%M'`. O que é
   mais novo que o seu último commit e você não escreveu, **não é seu**.
2. Commit por **arquivo**, não por diretório, quando a árvore tem coisa que você não escreveu.
   `git commit <dir>/` é commit por caminhos e ainda assim varre tudo o que estiver sujo lá.
3. Suíte vermelha logo após ter passado verde: suspeite de escrita em voo antes de suspeitar
   de você. Rode de novo em vez de editar — um salvamento em duas etapas fica inconsistente
   por segundos.

**O que funcionou como guarda, e vale registrar:** o `pre-push` recusou publicar sobre árvore
vermelha que nem era minha. É o argumento a favor de gancho lento na saída — o `pre-commit`
mantém o teto de ~1s e deixa a suíte completa para o `pre-push`, que é onde o custo se paga.
