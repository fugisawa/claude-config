---
name: conserto-de-falso-positivo-cria-falso-negativo
description: Guarda que acusa demais incomoda e por isso é consertada; guarda que acusa de menos não incomoda ninguém — todo conserto de falso positivo empurra a guarda para "passa em tudo", e a única defesa é o teste da metade contrária, o que ela NÃO PODE deixar de acusar
metadata:
  pattern: code_review
  origin: manual_estudo, 26/08/2026 — seis classes de falso positivo consertadas numa guarda, e o conserto da terceira criou um falso negativo em 35 documentos
  confidence: alta (só apareceu porque se foi conferir em vez de aceitar o verde)
---

**A assimetria que governa tudo.** Falso positivo **incomoda**: alguém vê o vermelho,
reclama, e o conserto acontece. Falso negativo **não incomoda ninguém** — a guarda fica
verde, e o que ela deixou de ver não tem quem reclame. Quer dizer que a pressão sobre uma
guarda é sempre num sentido só, e cada conserto a empurra para *"passa em tudo"*.

**Custo medido.** Uma guarda de integridade acusava **seis classes** de coisa que está
impressa e legível — bloco cercado, matemática em linha, rodapé corrente, hífen na quebra,
riscado, link. O conserto da terceira passou a ler **`R$` como abertura de equação** e
engolia da moeda até o cifrão seguinte: **enunciado inteiro desaparecia da conferência**.
Alcance real: **208 ocorrências de `R$` em 35 documentos**, e não só nas duas disciplinas
com equação onde o defeito foi notado.

⚠ **Ele só apareceu porque se foi conferir em vez de aceitar o verde.** A varredura já
tinha melhorado de um estado ruidoso para 130 documentos limpos. Parar ali teria fechado o
dia com a guarda **pior do que começou** — e com todas as luzes verdes.

## O gatilho

Sempre que você consertar um falso positivo. Sem exceção, e principalmente quando o
conserto for uma **supressão** — ignorar um padrão, pular um bloco, normalizar um
delimitador. Supressão é a forma em que o erro troca de sinal sem avisar.

## O remédio

**Escreva o teste em duas metades, e a segunda é a que importa:**

1. o que a guarda **deve** acusar — o caso real que a originou;
2. o que ela **não pode** deixar de acusar — um caso que, se passar, prova que a supressão
   comeu sinal junto com ruído.

Sem a segunda metade, cada conserto é um passo em direção a uma guarda que passa em tudo e
não protege ninguém. Com ela, a supressão fica presa entre duas afirmações.

E antes de dar o conserto por bom: **meça o alcance da supressão, não o do defeito.** O
defeito aparecia em 18 documentos; a supressão alcançava 35. São perguntas diferentes, e a
segunda é a que diz se você piorou alguma coisa.

⚠ **Cuidado com a superfície da conferência.** Na mesma sessão, um conserto foi "confirmado"
lendo o PNG de um documento em que o defeito **não podia aparecer** — quer dizer, conferiu-se
justamente onde a falha era impossível. A amostra da conferência precisa incluir o **caso
adversário**, e não o caso típico.

## O que isto NÃO é

Não é [[guarda-que-varre-nao-distingue-obra-de-defeito]], que é sobre a guarda confundir
trabalho em andamento com defeito. Aqui a guarda distingue bem; o que muda é **o sinal do
erro** depois do conserto.

Relacionado: [[guarda-que-varre-nao-distingue-obra-de-defeito]] ·
[[portao-que-pula-esconde-o-defeito]] · [[checagem-que-nao-pode-falhar]] ·
[[comando-verde-que-fez-menos-do-que-anuncia]] · [[negative-finding-vs-broken-probe]]
