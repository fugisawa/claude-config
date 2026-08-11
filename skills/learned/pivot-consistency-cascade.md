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

**Terceira recorrência (11/08/2026, saída do Analista em 08/08 e banca do TCU) — e ela ensina
o modo de falha do passo 1.** O grep amplo foi rodado três vezes e **se declarou completo nas
três**: a primeira achou 3 arquivos, a segunda 16, a terceira 17. Não foi desleixo — foi que
**o termo da decisão antiga tem sinônimos**, e cada varredura procurou a forma que quem a
escreveu imaginou. A mesma afirmação vivia como `TCU (Cebraspe)`, como
`TCU=Cebraspe provável` e como `Cebraspe (banca provável do TCU)`; um conserto anterior tinha
mirado só a primeira forma e passado, com razão, por completo.

**A terceira variante não foi achada por grep nenhum: apareceu ao ler o PNG do artefato
renderizado**, dentro de um box de pegadinhas. Daí a regra que faltava ao passo 5: quando o
defeito é de **prosa**, o render é parte da varredura e não a conferência final dela. Grep
acha o que você imaginou; o papel mostra o que está escrito.

Duas consequências práticas: (a) antes de declarar varredura completa, liste as **formas** do
termo, não só o termo — sigla, nome por extenso, o mesmo em posição de adjetivo; (b) para
artefato com build, releia o render **depois** do grep, porque é lá que a variante que ninguém
imaginou aparece.

Nesta rodada apareceu também uma classe que o passo 2 já previa e que é fácil apagar por
engano: **procedência**. Linhas como "Base: editais FGV 1/2022 (Analista) e 4/2022 (Consultor)"
citam o alvo que saiu e **devem ficar** — são de onde o dado veio. O código de alvo `SA` nas
tabelas foi **redefinido** (a legenda passou a dizer que o cargo está fora do portfólio) em vez
de arrancado, porque arrancar exigiria re-etiquetar cada linha e perderia a medição da prova.
