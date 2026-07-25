---
name: canonical-sequence-first
description: Antes de montar qualquer plano operacional (semana/dia/sprint), procurar no projeto um artefato curado de sequência (trilha/fila/backlog/roadmap) — ele decide a ordem dos tópicos; nunca inventar sequência própria
metadata:
  pattern: user_corrections
  origin: manual_estudo, sessão 17-19/07/2026
  confidence: alta (bronca explícita do usuário + regra gravada em 4 camadas)
---

**O erro:** montei a grade da semana de estudo derivando tópicos de planos anteriores e da análise
de verticalização, sem abrir as `trilha.md` — o artefato que o usuário construiu (com pesquisa cara)
exatamente para decidir "o que vem agora". Resultado: pulei um passo da fila e adiantei outro em 4
posições. Bronca dura ("por que diabos você fez as trilhas??").

**O padrão:** quando um projeto tem um artefato de sequência curado (fila, trilha, backlog ordenado,
roadmap), ele é a fonte única da ordem — o plano operacional CONSOME o próximo item não-concluído e
o CITA ("Passo N"). Planos que inventam ordem anulam o investimento do artefato e dessincronizam o
progresso marcado nele.

**Como aplicar:** antes de qualquer grade/cronograma, `Grep`/`Glob` por trilha/fila/backlog/roadmap
no projeto; ler o(s) relevante(s); construir o plano a partir do primeiro item aberto; divergência da
fila só com decisão explícita do dono, registrada no próprio plano. Corolário: também verificar o
ESTADO real ("o que já foi feito") com o usuário — o registro pode estar errado (aqui, o "feito" do
piloto era outro passo da trilha).
