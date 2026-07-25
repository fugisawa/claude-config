# Alvos, bancas e matriz de prioridades — snapshot de 24/07/2026

Sumário: Portfólio · Os 2 alvos · Fora do portfólio · Datas-gatilho · Formato de treino (banca-dupla) · Diagnóstico baseline · Incidências e pesos · Prioridades (Tabela 4) · Eixos e pisos · Atualização

Portfólio **repactuado por Daniel (24/07/2026): Senado e TCU — 2 alvos, banca-dupla FGV × Cebraspe, pesos 0,50/0,50.** A CGU saiu do portfólio e virou **contingência dormente** (material hibernado, nunca deletado). Racional registrado do pivô: (i) dominar **as duas bancas** como método de aprendizado — o contraste FGV×Cebraspe aprofunda o domínio; (ii) força pessoal em **Estatística/Análise de Dados** (~20–25% dos específicos do TCU-2021, lido como piso), que voltou à matriz; (iii) o **Dossiê TCU** de 24/07 (`manual_estudo/pdf/plano/Dossie-TCU-Carreiras-e-Concurso.pdf`), que recomendava não *somar* TCU à reta CGU — a *substituição* elimina a colisão. Outros certames (Câmara, TCDF, TCE-SP etc.) não entram na matriz; se surgirem na conversa, roteie ao radar-concursos e pergunte se o portfólio muda antes de tocar nos pesos. *(Substitui o snapshot de 17/07/2026, que tinha Senado+CGU 0,55/0,45 e treino 100% FGV.)*

## Os 2 alvos

| Alvo · cargo | Banca | Fase do ciclo (24/07/2026) | Inicial (bruto) |
|---|---|---|---|
| **Senado** — Analista Legislativo (Processo Legislativo) **e Consultor Legislativo** (peso 0,50; âncora) | FGV em 2022; próxima **indefinida** → prior FGV | Represamento: lista de 2022 zerada em 10/06/2026; validade expira jun/2027; Lei 15.350/2026 reajustou a carreira (vetos nas parcelas 2027–29) | Analista ~R$ 36,7 mil · Consultor ~R$ 46,3 mil (dossiê 24/07, Quadro vigente desde 04/2026) |
| **TCU** — Auditor Federal de Controle Externo (AUFC), **área geral/Controle Externo** (peso 0,50) | **Cebraspe muito provável** (contrato vigente até 2028; TEFC-2025 e AUFC-TI-2025/26 foram Cebraspe) | **~100 vagas anunciadas 2× pelo presidente do TCU e autorizadas; edital provável (55–80%) ≤ início/2027**; Lei 15.351/2026 reescreveu a carreira | ≈ R$ 27,6 mil com GDAE no piso de 40% (banda até ~R$ 33,7 mil se GDAE 100%; ver dossiê) |

## Fora do portfólio

- **Câmara** — saiu em 17/07/2026 (ciclo Cebraspe dela correu no início de 2026).
- **CGU** — saiu em **24/07/2026 → contingência dormente**: pesos e material preservados (`cgu-organizacao/` 💤 hibernada; pesos CGU nos git history dos 8 arquivos). O edital dela (≤ dez/2026) dispara **reavaliação — decisão de Daniel, nunca reativação automática**.
- **Condicionais TCU** (entram só se o edital confirmar; lista completa em `manual_estudo/disciplinas/README.md`): Economia do Setor Público (provável), Dir. Civil/Proc. Civil, Dir. Penal; Mat. Financeira acopla em RLM/Estatística, não vira pasta. **Condicionais Consultor:** Eleitoral vs Tributário+Economia — decide quando a inscrição/edital definir a área.

## Datas-gatilho (disparam o modo Replanejar)

1. **Edital TCU AUFC-geral** — o mais provável do horizonte (≤ início/2027). Dispara o **protocolo 72h**: banca, áreas, formato e engenharia reversa da incidência real (a atual é provisória).
2. **Confirmação da banca do TCU antes do edital** — hoje Cebraspe muito provável; surpresa → protocolo 72h recalibra a divisão de treino.
3. **Edital CGU** (≤ dez/2026 sob pena de caducidade da autorização; prova ≥ 2 meses após) — **não reativa nada sozinho**: dispara a pergunta de reavaliação da contingência a Daniel.
4. **Atos do Senado** — validade da lista de 2022 expira jun/2027; nomeações via CR/LOA-2026 reduzem o represamento que sustenta a aposta-âncora.
5. *(Remuneratórios, informam mas não replanejam)* ato da GDAE do TCU e eventual derrubada dos vetos das Leis 15.350/15.351 — ver dossiê.

Notícia e probabilidade são do radar-concursos; este arquivo só registra o snapshot que a matriz consome.

## Formato de treino (banca-dupla, desde 24/07/2026)

- **FGV** (Senado): 5 alternativas, "incompleto ≠ incorreto" (buscar a alternativa sem nada errado), enunciados longos e questões-caso, subsunção caso→norma, discursiva por quesitos cronometrada em tempo −20% → trilha FGV em metodologias.md.
- **Cebraspe** (TCU): padrão 2025 = **200 itens C/E (−1/+1) + discursiva com peça técnica**. Riscar restritivos fisicamente; política de marcação por valor esperado (N1/N2 marcam, N3 em branco — confirmar a regra de pontuação no edital) → trilha CEBRASPE em metodologias.md, **reativada em 24/07** (material de método Cebraspe reviveu sem retrabalho).
- **Proporção de treino ≈ pesos (50/50), alternando banca por sessão/dia** (Semana 1 do plano: banca alterna por dia). **Nunca misturar bancas no mesmo lote de questões** (regra de `disciplinas/README.md`); trocar banca num link QC = trocar `examining_board_ids%5B%5D=63` (FGV) por `=2` (Cebraspe).
- Simulados: calendário do plano alterna formato; o diagnóstico de 25/07 foi **misto por desenho** (baseline por banca).
- Anki: decks etiquetados por **banca** e por regimento — **RISF ≠ RICD, nunca no mesmo baralho**.

## Diagnóstico baseline

Autoavaliação 0–5 (01/07/2026; Estatística acrescentada em 24/07) vale **até o dado medido chegar**. O **simulado diagnóstico misto de 25/07/2026** (30q FGV + 30 itens C/E; AFO, Português e RLM — 10/disciplina em cada banca) gera o **baseline POR BANCA**, registrado no **check-in nº 1 (dom 26/07/2026)**, que substitui a autoavaliação nessas 3 disciplinas. Tratar como calibração, não veredito.

> **SLOT A PREENCHER (check-in nº 1, 26/07):** AFO __% FGV · __% C/E líquido — PT __% · __% — RLM __% · __% (+ erros por tipo e N1). Até lá, vale a tabela abaixo.

| Disciplina | Nível | Déficit (5 − n) |
|---|---|---|
| Estatística & Análise de Dados | 3 (força; material próprio) | 2,0 |
| RLM | 3 | 2,0 |
| Português | 2–3 | 2,5 |
| Constitucional | 2 | 3,0 |
| TI & Dados (varia por assunto) | 1–2 | 3,5 |
| Administrativo | 1 | 4,0 |
| Processo Legislativo (RISF/CF 59–69) | 1 | 4,0 |
| AFO | 0 → em curso desde M1 | 5,0 |
| Administração Pública & PP | 0 | 5,0 |
| Controle Externo / Auditoria | 0 (entra M3) | 5,0 |
| Contabilidade Pública (CASP) | 0 (entra M2) | 5,0 |

## Incidências por alvo e pesos de portfólio

Pesos (repactuação 24/07/2026): **Senado 0,50 · TCU 0,50.**

Incidência 0–3 por alvo. Coluna Senado: engenharia reversa dos editais FGV-2022 (estável). Coluna TCU: **PROVISÓRIA** — engenharia reversa dos editais 2015/2021/2025-TI (pesquisa 24/07; detalhe por tópico nos `mapa-incidencia.md` de cada disciplina); refaz-se inteira no protocolo 72h quando o edital sair.

| Disciplina | Senado | TCU (provisória) |
|---|---|---|
| Português | 3 | 2 |
| Constitucional | 3 | 2 |
| Processo Legislativo (regimentos) | 3 | 0 |
| Administrativo (c/ 14.133) | 2 | 2 |
| AFO | 2 | 3 |
| Administração Pública & PP | 2 | 2 |
| Inglês | 2* | 1 |
| Controle Externo / Auditoria | 0 | 3 |
| Contabilidade Pública (CASP + Análise Demonstr.) | 0 | 3 |
| Estatística & Análise de Dados | 0 | 3 |
| TI & Dados | 0 | 1 (camada de dados migrou p/ Estatística) |
| RLM (+ Rac. Analítico) | 1 | 2 |

`*` Confirmado nos editais FGV-2022: Analista 7q, Consultor 8q + tradução EN→PT de 15 pts na discursiva; TCU cobra nas básicas.
Avaliação de PP, Ciência Política e Literatura entram **dentro das linhas guarda-chuva** (Adm. Pública & PP; Consultor-específicas; Português) — detalhamento em `manual_estudo/disciplinas/README.md`; ordem/dose no `Calendario-Mestre-18-Meses` v2.

## Prioridades (Tabela 4 do Plano v3 — fonte operacional)

A re-pesagem de 24/07 substituiu o ranking numérico por **tiers** (Tabela 4 do `Plano-18-Meses-Daniel.pdf` v3, que esta síntese espelha):

- **P1:** AFO (transversal, dose diária desde M1) · Processo Legislativo/Regimento (**âncora** — vence desempates por aderência e motivação) · Constitucional · Adm. Pública & PP (P1→P2).
- **P2:** Contabilidade/CASP (**entra M2**) · Controle Externo/Auditoria (**entra M3**; coração do TCU) · Português · Discursiva (contínua, 1 peça/semana) · Administrativo.
- **P3:** Estatística & Dados (**entra M2, dose leve** — nível 3, volume cronometrado direto, sem teoria longa) · TI & Dados · RLM (abre o dia; manutenção 2×/sem com teto — trava anti-hiperfoco).
- **P4:** Ética · Atualidades (áudio no deslocamento) · Inglês (manutenção por questões).

**Escalonamento dos níveis-0 (régua anti-evitação, vale mais que a ordem fina):** nunca duas matérias nível 0 abrindo no mesmo mês — AFO em curso → CASP M2 → CE/Auditoria M3. Cada uma entra pelo método anti-evitação (metodologias.md).

## Eixos e pisos (garantia do "Senado-first com equilíbrio")

| Eixo | Disciplinas | Piso por meso-ciclo |
|---|---|---|
| A — Jurídico-legislativo | Proc. Legislativo, Constitucional, Administrativo | ≥ 20% |
| B — Camada de controle | AFO, Adm. Pública, CE/Auditoria, CASP, Estatística, TI & Dados | ≥ 20% |
| C — Instrumentais | Português, RLM, Discursiva, Inglês | ≥ 20% |

Com a matriz banca-dupla, a média ponderada sozinha deixaria o **Processo Legislativo magro** — o piso do eixo A é a trava que garante o espaço da matéria-coração da âncora (era o eixo C o piso-ativo no snapshot de 17/07; o pivô inverteu o risco). A matriz aloca livremente (inclusive o pico da manhã), mas **nenhum eixo cai abaixo de 20% sem decisão explícita de Daniel**. A discursiva semanal é fixa e não conta contra piso nenhum.

## Atualização deste arquivo

Snapshot de **24/07/2026** (substitui o de 17/07/2026) — o skill é estático. *Nota de manutenção: o pivô de 24/07 foi executado nos artefatos (Plano v3, 1-Página v3, Calendário v2, 15 disciplinas v1.1) no próprio dia, mas este arquivo ficara no snapshot 17/07; materializado em 25/07/2026 (TB0 do plano aprovado por Daniel).* Quando um fato novo chegar (colado por Daniel ou trazido do radar), a informação da conversa **prevalece** e o snapshot deve ser declarado envelhecido. A engenharia reversa completa (incidência real por tópico) refaz-se com edital em mãos, no protocolo 72h. Slot de baseline por banca preenche no check-in nº 1 (26/07).
