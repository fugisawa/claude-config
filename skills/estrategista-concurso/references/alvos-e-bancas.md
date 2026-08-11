# Alvos, bancas e prioridades — regras de decisão

Sumário: O que este arquivo é (e não é) · Os 2 alvos · Fora do portfólio · Datas-gatilho · Treino banca-dupla · O que foi medido · Prioridades · Eixos e pisos

## O que este arquivo é — e o que ele deixou de ser

**Ele guarda regra de decisão, não estado.** Até 09/08/2026 este arquivo era uma cópia da matriz dos painéis, e acumulou dez contradições internas em três semanas: Direito Eleitoral declarado "pasta a criar" depois de a pasta existir, AFO ainda chamada de "transversal" depois de sair do Senado, Administrativo um tier abaixo do que a própria fórmula calculava, o baseline mandando preencher um slot já preenchido oitenta linhas acima. Nenhuma dessas divergências foi descuido: **é o que acontece com número copiado para um lugar sem verificação.**

O estado de cada alvo mora nos painéis, que têm build, QA visual e um doutor que confere o declarado contra o disco:

| Preciso saber | Abra |
|---|---|
| Estrutura da prova, matriz medida, datas duras, o que está em aberto | `~/manual_estudo/pdf/plano/Painel-Senado-Consultor.pdf` · `Painel-TCU-AUFC.pdf` |
| Incidência por tópico dentro de uma disciplina | `disciplinas/<matéria>/mapa-incidencia.md` |
| Fases, datas duras e **restrições de ordem** (o que a sequência não pode fazer) | `pdf/plano/Calendario-Mestre-18-Meses.pdf` — desde 09/08/2026 ele **não atribui mais matéria a mês**; quem aloca é a matriz |
| Tese completa da campanha | `pdf/plano/Plano-18-Meses-Daniel.pdf` |

Quando um fato novo chegar pela conversa, ele **prevalece** sobre qualquer coisa escrita aqui, e o que estiver aqui deve ser declarado envelhecido.

## Os 2 alvos

Portfólio repactuado por Daniel em **24/07/2026**: Senado e TCU, **pesos 0,50/0,50**, treino em banca-dupla. Racional: dominar as duas bancas como método (o contraste aprofunda o domínio), força pessoal em Estatística/Dados, e o Dossiê TCU, que recomendava não *somar* TCU à reta CGU — a substituição elimina a colisão.

| Alvo | Banca | Situação |
|---|---|---|
| **Senado — Consultor Legislativo**, especialidade Assessoramento Legislativo, área *Direito Constitucional, Administrativo, Eleitoral e Processo Legislativo* | FGV em 2022; a próxima é indefinida, prior de trabalho FGV | Lista de 2022 zerada em 06/2026. Validade do cadastro do Consultor: **27/04/2027** |
| **TCU — Auditor Federal de Controle Externo, área geral** | ⚠ **A definir** — ver abaixo | ~100 vagas anunciadas e autorizadas; edital não publicado |

> ⚠ **A banca do TCU é uma aposta, e menor do que o cânone dizia.** A formulação anterior — "Cebraspe muito provável" — apoiava-se em dois certames recentes do órgão, que são o **Técnico** e o **AUFC-TI**. Mas o último concurso de **AUFC área geral**, em 2021, **foi FGV**, e as fontes de acompanhamento listam a banca da área geral como "a definir". Isso não derruba nada: é o argumento mais forte que a decisão de treinar banca-dupla já recebeu. O que muda é o que se pode afirmar — trate como **aberta**, com Cebraspe à frente por contrato vigente e formato recente, e não como resolvida. *(Triangulado em cinco fontes, 09/08/2026.)*

**Decisão de 08/08/2026 — o Senado deixou de ser dois cargos numa linha.** O alvo é o Consultor; o Analista saiu. Três consequências, todas apuradas na prova aplicada de 2022 e não só no Anexo I: AFO e Contabilidade **saem da coluna Senado** (o edital não dá o bloco de AFO àquela área) e passam a valer só pelo TCU; **Direito Eleitoral entra**, com 10 questões; e Constitucional mais Administrativo somam **46 das 70 específicas** — deixam de ser núcleo de peso médio e passam a ser a prova.

## Fora do portfólio

- **Câmara** — saiu em 17/07/2026.
- **CGU** — saiu em 24/07/2026 → **contingência dormente**. Material hibernado, nunca deletado. O edital dela **não reativa nada sozinho**: dispara a pergunta de reavaliação a Daniel. Pergunte; não assuma.
- **Literatura Nacional** — ficou **sem alvo** com a saída do Analista. Não entra em linha guarda-chuva nenhuma: disciplina com incidência 0 nos dois alvos não se estuda. Marcada, não deletada.
- **Condicionais do TCU** (entram só se o edital confirmar): Economia do Setor Público (provável), Direito Civil/Processual Civil, Direito Penal. Matemática Financeira acopla em RLM/Estatística e não vira pasta.

## Datas-gatilho (disparam o modo Replanejar)

1. **Edital TCU AUFC-geral** — o mais provável do horizonte. Dispara o **protocolo 72h**: banca, áreas, formato e engenharia reversa da incidência real.
2. **Definição da banca do TCU antes do edital** — hoje aberta; a definição recalibra a divisão de treino entre FGV e Cebraspe.
3. **Edital CGU** — dispara a pergunta de reavaliação, nunca reativação automática.
4. **01/01/2027 — vencimento da assinatura Gran.** É **prazo de trabalho**, não gatilho estratégico: a colheita e a conversão têm de estar fechadas até o fim de dezembro. Alarme uma semana antes, em **24/12/2026**, na pauta do check-in daquela semana. Detalhe em `~/manual_estudo/disciplinas/_infra/acervos-ativos.md`.

## Treino banca-dupla

Proporção ≈ pesos (50/50), **alternando por sessão**; nunca misturar bancas no mesmo lote de questões — o que se está medindo é justamente a diferença entre elas. A discursiva alterna as duas: parecer no formato FGV e peça técnica no formato Cebraspe (esta em folha de **50 linhas**, não 30).

## O que foi medido — e o que não foi

**Simulado misto de 25/07/2026**, único dado medido da campanha inteira, n=10 por célula:

| Banca | AFO | Português | RLM | Total |
|---|---|---|---|---|
| FGV (múltipla escolha) | **3/10** | 9/10 | 9/10 | 21/30 |
| Cebraspe (C/E) | 9/10 | 10/10 | 9/10 | 28/30 bruto · 26 líquido |

Tempo não é gargalo em banca nenhuma. Seis erros vieram com confiança 4–5 (N1, prioridade máxima). A calibração é assimétrica: a base FGV está bem calibrada, e o Cebraspe mostra **subconfiança** — seis acertos com confiança 1–2.

> **O achado que manda na alocação: o déficit é de BANCA, não de matéria.** AFO deu 30% na FGV e 90% no Cebraspe, mesmos assuntos, mesma semana, e seis dos sete erros do lado FGV foram de discriminação fina entre alternativas próximas. O déficit correto se escreve **"AFO-FGV, discriminação entre alternativas"**, e não "AFO fraca" — escrever errado leva a estudar teoria de AFO, que não é o problema.

**Treze das dezesseis disciplinas nunca foram medidas**, e três delas são as de maior incidência do TCU: Estatística (nível 3 **autodeclarado, nunca medido**), Contabilidade e Controle Externo. Para essas, a primeira providência é **medir** — lote diagnóstico de 10–20 questões —, não presumir déficit. Nível autoavaliado entra na matriz com a marca *sem dado*, e "sem dado" nunca é "fraco" (regra-mãe 7).

## Prioridades

Tiers, com a razão de cada um ao lado. Quando um tier discordar da fórmula da matriz, **diga qual está usando e por quê** — foi a divergência silenciosa entre os dois que manteve Administrativo um tier abaixo do que a conta mandava.

- **P1 — o que é a prova:** Constitucional (28q no Senado, 2 no TCU) · **Administrativo** (18q; com a Lei 14.133 no TCU) · **Contabilidade/CASP** e **Controle Externo/Auditoria** (incidência 3 no TCU, e as duas em nível 0 — são o maior déficit do portfólio) · AFO (incidência 3 no TCU; **deixou de ser transversal** quando saiu da coluna Senado, mas o déficit medido em FGV a mantém no topo).
- **P2:** Estatística & Análise de Dados (incidência 3 no TCU, trilha inteira pronta em folhas de passo, e **sem medição**) · Português · Discursiva (1 peça por semana, contínua) · **Direito Eleitoral** — que antes de ser estudável precisa ser **construída** (ver abaixo).
- **P3:** Adm. Pública & PP · RLM (manutenção 2×/semana com teto — trava anti-hiperfoco) · Processo Legislativo · TI & Dados · Inglês (manutenção por questões, mais o treino de tradução).
- **P4:** Ética · Atualidades (áudio no deslocamento).

**Direito Eleitoral é o caso especial e não pode ser tratado como os outros.** Ela vale 10 questões medidas, tem pasta aberta como dívida declarada e **não tem `trilha.md`** — é a única das 17 nessa situação. Pela regra-mãe 8 ela **não é planejável**: a primeira entrada dela num plano é trabalho de construção (verticalizar), não conteúdo. A própria disciplina registra a ordem: não abrir antes de Controle Externo e Contabilidade, porque a régua anti-evitação proíbe duas matérias de nível 0 abrindo no mesmo mês, e abrir uma terceira frente porque ela é nova seria exatamente a evitação que a régua existe para impedir.

**Escalonamento dos níveis-0 (vale mais que a ordem fina):** nunca duas matérias nível 0 abrindo no mesmo mês. Cada uma entra pelo método anti-evitação (metodologias.md).

**Processo Legislativo perdeu a justificativa de âncora.** Ele era P1 e desempatava por aderência porque o RISF valia ~19/70 na prova do **Analista** — cargo que saiu do portfólio. No Consultor, o Bloco I traz *Processo Legislativo Constitucional*, que é processo pela CF e não pelo Regimento. O RISF continua valendo por dois caminhos, e nenhum deles é a objetiva: a **discursiva** (parecer sobre proposição exige tramitação real) e o exercício do cargo. Tratar como leitura de apoio até haver medição.

## Eixos e pisos

| Eixo | Disciplinas | Piso por meso-ciclo |
|---|---|---|
| A — Jurídico-legislativo (Senado) | Constitucional, Administrativo, **Eleitoral**, Proc. Legislativo | — |
| B — Controle e quantitativo (TCU) | Contabilidade, Controle Externo, AFO, Estatística, Adm. Pública & PP, TI & Dados | **≥ 30%** |
| C — Instrumentais (os dois) | Português, RLM, Inglês, Discursiva | ≥ 20% |

**O piso mudou de eixo em 09/08/2026, e a razão importa.** Ele protegia o eixo A, quando a preocupação era o Processo Legislativo ficar magro. Hoje o eixo A carrega 46 das 70 questões específicas do Senado — um piso ali não protege nada, é **teto disfarçado de piso**. O risco real inverteu: o eixo B reúne as três disciplinas de maior incidência do TCU, todas em nível 0 ou não medidas, e é o que perde espaço porque a atenção puxa naturalmente para o alvo cujo edital já existe. **O piso protege o alvo mais distante**, que é o que a regra-mãe 5 manda — cortar pela coluna, nunca pela média.

Direito Eleitoral entrou no eixo A: sem eixo, um plano podia satisfazer os três pisos e dar **zero** a uma disciplina de 10 questões sem que nada acusasse.

A discursiva é fixa e não conta contra piso nenhum.
