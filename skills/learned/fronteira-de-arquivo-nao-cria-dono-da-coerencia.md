---
name: fronteira-de-arquivo-nao-cria-dono-da-coerencia
description: Dividir trabalho concorrente por arquivo evita colisão de escrita e não evita contradição — dois agentes podem estar certos cada um no próprio lado enquanto o conjunto mente sobre a mesma pergunta
metadata:
  pattern: project_specific
  origin: manual_estudo, sessões paralelas 08-09/08/2026
  confidence: alta (o pior defeito do período; 15h37 quebrado, 9h35 conhecido e não consertado)
---

**O caso.** Duas sessões dividiram o trabalho por arquivo — combinação sensata, e funcionou
para não pisarem uma na outra. Publicaram, **com 23 minutos de diferença**, dois artefatos
que diziam coisas opostas sobre a única pergunta que importava na manhã seguinte: em que
passo da trilha o dono do projeto estava. Um dizia **Passo 3**, o outro **Passo 1**.

**Nenhuma das duas estava errada dentro do próprio lado.** Cada arquivo era coerente consigo
mesmo, cada sessão respeitou a fronteira, e o conjunto mentia. O erro não era cosmético:
pular do Passo 1 para o 3 abandonaria as 142 questões que treinavam o único déficit medido.

Ficou quebrado 15h37 — das quais **9h35 conhecido e não consertado**, porque o diagnóstico
foi escrito numa mensagem de commit em vez de virar conserto.

## As três regras que ficaram

**Quem publica um artefato confere os outros que respondem à MESMA pergunta**, não só o que
está editando. A pergunta é a unidade de coerência, não o arquivo.

**Achar defeito no lado do outro não autoriza reportar em vez de consertar**, quando o custo
do erro cai sobre o usuário antes de a mensagem ser lida. Fronteira existe para evitar
atropelo, não para virar a razão de alguém acordar com o artefato errado na mão.

**A saída definitiva não é coordenar melhor — é eliminar a segunda cópia.** Enquanto a
posição fosse afirmada em prosa em cada artefato, todo artefato novo era uma chance de
errar. Derivada de uma fonte única, com verificação que reprova a divergência, a contradição
deixou de ser possível em vez de detectável.

## Um efeito de segunda ordem, sobre agentes efêmeros

Uma das sessões trabalhou o dia inteiro e encerrou. **Sobreviveu dela exatamente o que virou
arquivo versionado, e nada mais** — o código, os ganchos, e as lições que foram escritas em
arquivo. Sumiu tudo que ficou só na conversa.

Coordenação síncrona resolve colisão de escrita. Ela **não** resolve perda de contexto na
troca de turno, que é o modo de falha de sistema onde os agentes são efêmeros e o
repositório é permanente. A regra que cobre isso: **se o registro precisa sobreviver a um
clone, ele é arquivo versionado** — nota do git não serve, porque `refs/notes/*` não vem no
refspec padrão e nenhuma interface web a mostra.

Relacionado: [[pivot-consistency-cascade]] · [[verify-claimed-state]] · [[subagent-attribution-drift]]
