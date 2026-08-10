---
name: escopo-do-grep-nao-e-escopo-da-pergunta
description: Um único acerto de busca parece confirmação e não é — quando a pergunta tem escopo (hoje, este cliente, esta versão), abra o artefato que o ESCOPO nomeia, e não o que a palavra-chave casou
metadata:
  pattern: user_corrections
  origin: manual_estudo, sessão 09/08/2026
  confidence: alta (bronca explícita do usuário; a resposta inteira saiu do dia errado)
---

**O padrão.** A busca por palavra-chave devolve um acerto só, e o acerto único **se disfarça
de confirmação**: se houvesse outro lugar, teria aparecido. Não teria — o outro lugar diz a
mesma coisa com outras palavras, ou diz o mesmo número em outro formato. Quando a pergunta
tem recorte (hoje, esta semana, este cliente, esta versão), o recorte é que decide qual
arquivo abrir, e a palavra-chave decide só onde procurar dentro dele.

## O caso

O usuário perguntou como conduzir "as 20 questões" do dia. Eu rodei um `grep` por
`20 quest` nos planos, bateu **um** arquivo — o plano de **terça** — e respondi a partir
dele: matéria errada, banca não decidida, link genérico, conselho de bloco errado. Era
domingo. O plano de domingo existia, estava ao lado, e mandava outra coisa: outra matéria,
banca já fixada, o endereço do lote embutido e uma tática específica para um déficit medido.

A resposta dele foi de uma linha: *"de onde você tirou que eu vou fazer hoje direito
administrativo?"*

O plano de domingo **não continha a string "20 questões"** — dizia "uma leva de 20 questões".
O grep não errou. Eu é que tratei o acerto único como se fosse o único lugar possível.

## A regra

**Quando a pergunta tem escopo, o escopo abre o arquivo — a busca só navega dentro dele.**
Data, cliente, ambiente, versão e sprint são escopos. Se o escopo nomeia um artefato
previsível (`plano-<data>.md`, `config.<env>.yaml`, `CHANGELOG` da versão), abra-o
**primeiro**, antes de qualquer busca por conteúdo.

**Acerto único não é evidência de exclusividade.** É evidência de que uma redação casou.
Antes de responder a partir dele, faça a pergunta barata: *existe um artefato cujo NOME
responde a esta pergunta?* Um `ls` do diretório custa uma chamada e teria mostrado
`plano-domingo-09-08.md` ao lado do de terça.

**Formulação idêntica é o pressuposto mais frágil de uma busca.** "20 questões" contra "uma
leva de 20 questões" já basta para o arquivo certo sumir. Buscar por token raro e estável —
um identificador, um número de norma, um slug — vale mais que buscar pela frase.

## O sinal de que aconteceu

A resposta fica **coerente demais e específica demais** para uma pergunta vaga: você
descreve banca, link e tática que o usuário não mencionou. Coerência interna alta com
verificação de escopo zero é o formato exato deste erro.

Relacionado: [[verify-claimed-state]] · [[canonical-sequence-first]] · [[negative-finding-vs-broken-probe]]
