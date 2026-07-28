---
name: pivot-consistency-cascade
description: Quando uma decisão-mestre muda (pivô de estratégia/escopo), rodar auditoria em cascata com 3 classes (inconsistência real · histórico legítimo datado · dúvida), priorizando os artefatos operacionais de uso diário
metadata:
  pattern: project_specific
  origin: manual_estudo, reconcentração de portfólio 17/07/2026
  confidence: alta (auditoria achou ~40 arquivos defasados; padrão validado ponta a ponta)
---

**O caso:** o projeto pivotou de 4 alvos para 2. A prosa estratégica (README/plano) foi atualizada no
dia, mas os artefatos operacionais de consumo diário (guias de 1 página, cabeçalhos de verticalização,
bússola do planner, skill de planejamento) ficaram TODOS no estado antigo — exatamente os que o
usuário abre todo dia.

**O padrão (o que funcionou):**
1. Grep amplo pelos termos da decisão antiga, com whitelist do que é legítimo (subprojetos que não
   mudam, registros datados, conteúdo factual que só parece estratégia).
2. Classificar cada achado: (a) inconsistência real → corrigir; (b) histórico legítimo →
   subordinar com nota/callout DATADO, nunca reescrever o passado; (c) dúvida → decisão do dono.
3. Priorizar artefatos operacionais sobre prosa: são o que engana no dia a dia.
4. Corrigir também frontmatter/descrições de skills — elas anunciam o estado antigo em toda sessão.
5. Fechar com varredura de resíduo zero (grep com exclusões) + re-render/QA do que tem build.

**Anti-padrão a evitar:** "corrigir" menções históricas datadas (apaga rastreabilidade) e esquecer
material de contingência (rotular como dormente ≠ deletar).

**Recorrência confirmada (28/07/2026, pivô CGU→TCU de 24/07):** o padrão vazou de novo, e pelo
mesmo vetor — o passo 4. O cânone e a prosa foram atualizados no dia; ficaram para trás a
**descrição (frontmatter) do skill estrategista-concurso** (anunciava o portfólio antigo em toda
sessão, contradizendo o próprio reference dela), os **cabeçalhos das trilhas por banca** nos
references, a **bússola do planner** (fonte Typst + PDF) e o rótulo "contingência dormente" da
folha de discursiva Cebraspe — que o pivô tornou treino ativo, porque a nova banca entrou no
portfólio. **Lição nova:** um pivô que muda de banca vira o rótulo de material de contingência do
avesso — varra "dormente/contingência" também, não só o nome do alvo que saiu.
