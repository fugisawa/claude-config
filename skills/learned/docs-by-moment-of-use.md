---
name: docs-by-moment-of-use
description: README de sistema pessoal se organiza por MOMENTO de uso (job-to-be-done), não por pasta/estrutura — incluindo o bootstrap do primeiríssimo uso, que inventários nunca cobrem
metadata:
  pattern: user_corrections
  origin: manual_estudo README (19/07/2026) — pedido explícito do Daniel
  confidence: média-alta (2 pedidos consecutivos do usuário na mesma direção)
---

**O caso:** o README do sistema de estudo era um inventário correto (artefatos por pasta,
pipelines de build) e ainda assim inútil na hora H — o usuário pediu: "como eu CONSULTO e USO
os artefatos no meu dia, na revisão, na hora de avaliar o planejamento?" e, em seguida,
"e como começa no primeiríssimo dia?". Duas lacunas do mesmo tipo: taxonomia ≠ uso.

**O padrão:** para sistema operado por uma pessoa (não uma lib para devs), a porta de entrada
da documentação é uma seção "pelo momento, não pela pasta": para cada momento recorrente
(antes de sentar · em dúvida do que fazer · ao errar · na revisão · no rito semanal · no
balanço mensal · quando algo muda · quando trava), dizer O QUE ABRIR e O QUE FAZER, com 1-2
linhas cada. O inventário por pasta continua depois, como referência.

**A lacuna clássica:** o momento zero. Todo fluxo documentado assume o ciclo já rodando
("abra a folha do dia") — o bootstrap (imprimir o quê, setup único, onde começa o conteúdo,
regra do dia 1) precisa ser o PRIMEIRO momento listado, senão o sistema não tem entrada.

**Como aplicar:** ao documentar qualquer sistema pessoal/operacional, perguntar: "em que
momentos o dono abre isto, e o que ele precisa em cada um?" — e escrever um bloco por
momento, começando pelo primeiríssimo uso. Se a doc só responde "o que existe e onde",
está incompleta.
