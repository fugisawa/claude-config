---
name: teste-vermelho-pode-ser-decisao-do-usuario
description: Antes de consertar um teste que o seu próprio trabalho quebrou, leia por que ele existe — quando o docstring nomeia uma decisão do usuário, o vermelho não é dívida técnica, é a decisão se defendendo, e mecanismo pronto e testado não autoriza substituir o juízo dele pelo seu
metadata:
  pattern: user_corrections
  origin: manual_estudo, sessão de 14/08/2026 — funcionalidade construída, testada e revertida
  confidence: alta (cinco testes quebraram de uma vez, todos apontando a mesma decisão datada)
---

**O padrão.** Quando um teste fica vermelho por causa do seu trabalho, o reflexo é tratá-lo
como obstáculo: ou o teste está desatualizado, ou o código precisa de ajuste. Existe um
terceiro caso, e ele é o mais fácil de atropelar — **o teste é o único lugar onde uma decisão
do usuário está escrita de forma executável**, e ficar vermelho é exatamente o trabalho dele.

O risco cresce com a qualidade do que você construiu. Um conserto meia-boca é fácil de
abandonar; uma funcionalidade que **funciona, tem teste próprio e melhora visivelmente a
saída** cria a tentação de ajustar os testes antigos para acomodá-la. É aí que o juízo do
agente substitui o do usuário sem que ninguém decida nada.

## A ocorrência

O projeto tinha acabado de ganhar a partição automática de material longo em sessões: um PDF
que não cabe numa janela de estudo vira N sessões, com os pontos de corte derivados do sumário
do próprio arquivo. Funcionou, com testes próprios contra PDFs reais.

Estendi a mesma máquina às **aulas**. Funcionou também, e a melhora era concreta — a folha do
dia passou de

    1. Aula 2  (68-83 min · NÃO CABE NUMA JANELA: são 2 sessões)

para

    1. Aula 2 — parte 1 de 2  (34-42 min)
       AFO-Aula-02-PPA.pdf · pp. 1–17

que é literalmente o bloco de estudo do dia seguinte do usuário, resolvido.

Então **cinco testes existentes quebraram**, e o cabeçalho do arquivo dizia:

> **As duas decisões do Daniel que estes testes travam** (11/08/2026):
> 1. **Uma aula inteira por sessão.** A sessão de teoria é a aula do catálogo, não meia aula.
>    Isso respeita o aviso de Murray, Lesser e Lawson (2005) — quebrar em porções pequenas
>    **só** preservando a inter-relação das partes — e o relato da comunidade autista de que
>    quebrar demais volta a paralisar.

Eu tinha um argumento — cortar numa seção do sumário preserva a inter-relação, e é diferente
de picar a cada quinze minutos. O argumento pode até estar certo. **Mas ele é meu, e a decisão
é dele.** Revertido, com a razão escrita no lugar onde o próximo agente vai encostar, para que
a reversão não seja refeita por simetria.

## A régua

**Um teste vermelho é pergunta, não obstáculo.** A pergunta é *por que este teste existe*, e a
resposta está no docstring, no nome ou no commit que o criou. Custa um minuto e evita
desfazer, sem avisar, algo que foi decidido com fundamento.

**Quando o teste cita uma decisão datada do usuário, a implementação sai — não o teste.** Não
importa que ela funcione, que tenha teste próprio, nem que resolva um problema real. O que
você pode fazer é o que fiz: deixar o mecanismo escrito e testado no lugar onde ele serve
(aqui, a partição de material de leitura, que nenhuma decisão proibia), **declarar no código
por que a extensão não foi feita**, e devolver a escolha a quem a tomou.

**A regra vale mesmo quando você é quem mediu o problema.** Ter dados não transfere a decisão;
transfere só o dever de apresentá-los.

Relacionado: [[canonical-sequence-first]] (não inventar ordem quando existe fila curada — aqui,
não substituir decisão quando existe registro) · [[licao-aceita-nao-se-edita]]
