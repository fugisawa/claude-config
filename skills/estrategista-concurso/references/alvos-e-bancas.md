# Alvos, bancas e prioridades — regras de decisão

Sumário: O que este arquivo é (e não é) · Os 2 alvos · Fora do portfólio · Datas-gatilho · Treino banca-dupla · O que foi medido · Prioridades · Eixos e pisos

## O que este arquivo é — e o que ele deixou de ser

**Ele guarda regra de decisão, não estado.** Até 09/08/2026 este arquivo era uma cópia da matriz dos painéis, e acumulou dez contradições internas em três semanas: Direito Eleitoral declarado "pasta a criar" depois de a pasta existir, AFO ainda chamada de "transversal" depois de sair do Senado, Administrativo um tier abaixo do que a própria fórmula calculava, o baseline mandando preencher um slot já preenchido oitenta linhas acima. Nenhuma dessas divergências foi descuido: **é o que acontece com número copiado para um lugar sem verificação.**

O estado de cada alvo mora nos painéis, que têm build, QA visual e um doutor que confere o declarado contra o disco:

| Preciso saber | Abra |
|---|---|
| Estrutura da prova, matriz medida, datas duras, o que está em aberto | `~/manual_estudo/pdf/plano/Painel-Senado-Consultor.pdf` · `Painel-TCU-AUFC.pdf` |
| Incidência por tópico dentro de uma disciplina | `disciplinas/<matéria>/mapa-incidencia.md` |
| Fases, datas duras e **restrições de ordem** (o que a sequência não pode fazer) | `pdf/plano/Calendario-Mestre-18-Meses.pdf` — desde 09/08/2026 ele **não atribui mais matéria a mês**; quem aloca desde 11/08/2026 são as **fases do `planos/0004`** |
| Tese completa da campanha | `pdf/plano/Plano-18-Meses-Daniel.pdf` |

Quando um fato novo chegar pela conversa, ele **prevalece** sobre qualquer coisa escrita aqui, e o que estiver aqui deve ser declarado envelhecido.

## Os 2 alvos — e a ordem entre eles

Portfólio repactuado por Daniel em **24/07/2026**: Senado e TCU, os dois mantidos (decisão `0001`, que segue de pé). **Desde 11/08/2026 a alocação deixou de ser por peso e passou a ser por sequência — TCU primeiro** (`~/manual_estudo/planos/0004-tcu-primeiro.md`, aceito): estudar **tudo o que o TCU cobra**, mais **uma única matéria pelo Senado** (Processo Legislativo); Direito Eleitoral e os passos só-Senado ficam para **depois da prova do TCU**. A razão é de eficiência, não de desistência — a maior parte das matérias serve aos dois alvos, o TCU é o único prazo que existe, e o Senado só volta com edital novo, sem data conhecida. Os pesos 0,50/0,50 de 24/07 valem como registro do racional daquela época, e não mais como regra de corte.

| Alvo | Banca | Situação |
|---|---|---|
| **Senado — Consultor Legislativo**, especialidade Assessoramento Legislativo, área *Direito Constitucional, Administrativo, Eleitoral e Processo Legislativo* | FGV em 2022; a próxima é indefinida, prior de trabalho FGV | Lista de 2022 zerada em 06/2026. Validade do cadastro do Consultor: **27/04/2027** |
| **TCU — Auditor Federal de Controle Externo, área geral** | ⚠ **A definir** — ver abaixo | ~100 vagas anunciadas e autorizadas; edital não publicado |

> ⚠ **A banca do TCU segue aberta — e a probabilidade está medida: ~65% Cebraspe · ~25% FGV · ~10% outra** (`0004 §9`, apurado em 11/08/2026, quatro fontes). O que sustenta a Cebraspe é **histórico e gestão** (a gestão atual já a escolheu em maio de 2025, disputando com a FGV) — e **não contrato**: o ISC nº 13/2025 amarra o objeto ao concurso de **2025** (TI e Técnico), e a cláusula 13.2 desmente os seis arquivos que diziam "contrato vigente até 2028". O último AUFC-geral (2021) foi FGV. O número é de check-in: é função do mês em que o edital sair, e um 70/30 pressupõe que ele saia ainda sob a gestão atual.

**Decisão de 08/08/2026 — o Senado deixou de ser dois cargos numa linha.** O alvo é o Consultor; o Analista saiu. Três consequências, todas apuradas na prova aplicada de 2022 e não só no Anexo I: AFO e Contabilidade **saem da coluna Senado** (o edital não dá o bloco de AFO àquela área) e passam a valer só pelo TCU; **Direito Eleitoral entra**, com 10 questões; e Constitucional mais Administrativo somam **46 das 70 específicas** — deixam de ser núcleo de peso médio e passam a ser a prova.

## Fora do portfólio

- **Câmara** — saiu em 17/07/2026.
- **CGU** — saiu em 24/07/2026 → **contingência dormente**. Material hibernado, nunca deletado. O edital dela **não reativa nada sozinho**: dispara a pergunta de reavaliação a Daniel. Pergunte; não assuma.
- **Literatura Nacional** — ficou **sem alvo** com a saída do Analista. Não entra em linha guarda-chuva nenhuma: disciplina com incidência 0 nos dois alvos não se estuda. Marcada, não deletada.
- **Condicionais do TCU** — deixaram de ser órfãs em 11/08/2026: o curso Gran **204948** cobre com PDF as quatro (Economia do Setor Público, Direito Civil, Processual Civil, Anticorrupção; inventário em `~/manual_estudo/disciplinas/_infra/catalogo-gran-tcu-204948.md`). São ~13 questões; entram por decisão de escopo, não por falta de material. **Matemática Financeira NÃO acopla em RLM: ela é disciplina do Bloco P1-I e vira pasta própria** (decisão do Daniel, 11/08/2026; a criação aguarda a decisão de vocabulário de 12/08). E **RLM saiu do escopo do TCU** — não está no edital de 2021; vale só pelo Senado, depois da prova.

## Datas-gatilho (disparam o modo Replanejar)

1. **Edital TCU AUFC-geral** — o mais provável do horizonte. Dispara o **protocolo 72h**: banca, áreas, formato e engenharia reversa da incidência real. **E planeja-se pela PROVA, não pelo edital**: nos nove certames levantados a prova veio de 51 a 136 dias depois dele, e os dois AUFC recentes ficaram em 121 e 136 (`0004 §6`) — ancorar o horizonte na data do edital foi o erro que derrubou o plano 0003.
2. **Definição da banca do TCU antes do edital** — hoje aberta; a definição recalibra a divisão de treino entre FGV e Cebraspe.
3. **Edital CGU** — dispara a pergunta de reavaliação, nunca reativação automática.
4. **01/01/2027 — vencimento da assinatura Gran.** É **prazo de trabalho**, não gatilho estratégico: a colheita e a conversão têm de estar fechadas até o fim de dezembro. Alarme uma semana antes, em **24/12/2026**, na pauta do check-in daquela semana. Detalhe em `~/manual_estudo/disciplinas/_infra/acervos-ativos.md`.

## Treino de banca — a proporção segue a probabilidade, não os pesos

**A alternância 50/50 por sessão morreu em 12/08/2026** (`0004 §9`, implementado em `~/manual_estudo/estudo/dia.py`): treina-se na proporção da probabilidade de banca do TCU — **~65% Cebraspe / ~35% FGV, por matéria** —, com a banca do dia derivada do log de lotes: escolhe-se a que puxa a fração acumulada de volta ao alvo. Continua inegociável **nunca misturar bancas no mesmo lote**, porque o que se mede é a diferença entre elas. O 65/35 revisa-se a cada check-in, junto com a probabilidade que o gera.

A discursiva prioriza a **peça técnica** — o gênero do TCU há vinte anos — nas folhas de **20 e 50 linhas**, e o treino não espera o edital: **na Cebraspe a discursiva cai no mesmo dia da objetiva** (na FGV de 2021 caiu 70 dias depois — quem se prepara pelo calendário da FGV e cai na Cebraspe perde setenta dias que achava que tinha; `0004 §10`). O **parecer** do Senado sai do horizonte até depois da prova do TCU.

## O que foi medido — e o que não foi

**Simulado misto de 25/07/2026**, único dado medido da campanha inteira, n=10 por célula:

| Banca | AFO | Português | RLM | Total |
|---|---|---|---|---|
| FGV (múltipla escolha) | **3/10** | 9/10 | 9/10 | 21/30 |
| Cebraspe (C/E) | 9/10 | 10/10 | 9/10 | 28/30 bruto · 26 líquido |

Tempo não é gargalo em banca nenhuma. Seis erros vieram com confiança 4–5 (N1, prioridade máxima). A calibração é assimétrica: a base FGV está bem calibrada, e o Cebraspe mostra **subconfiança** — seis acertos com confiança 1–2.

> **O achado que manda na alocação: o déficit é de BANCA, não de matéria.** AFO deu 30% na FGV e 90% no Cebraspe, mesmos assuntos, mesma semana, e seis dos sete erros do lado FGV foram de discriminação fina entre alternativas próximas. O déficit correto se escreve **"AFO-FGV, discriminação entre alternativas"**, e não "AFO fraca" — escrever errado leva a estudar teoria de AFO, que não é o problema.

**Treze das dezesseis disciplinas nunca foram medidas**, e três delas são as de maior incidência do TCU: Estatística (nível 3 **autodeclarado, nunca medido**), Contabilidade e Controle Externo. Para essas, a primeira providência é **medir** — lote diagnóstico de 10–20 questões —, não presumir déficit. Nível autoavaliado entra na matriz com a marca *sem dado*, e "sem dado" nunca é "fraco" (regra-mãe 7).

## Prioridades — as fases do 0004 mandam

A alocação por tiers foi **superada em 11/08/2026 pelo escopo por bloco de prova** (`0004 §3 e §8`). A régua que a substituiu: **nota abaixo de 25 em P1 OU em P2 elimina** (edital 10.10, sem compensação), então cada fase roda os dois lados da prova ao mesmo tempo, nunca um só. A ordem aceita: **fase 1 = Estatística + Contabilidade** (os 19 passos prontos — um bloco de 25 questões mais metade de outro, sem depender de construção) → **2** = TI & Dados + AFO → **3** = Controle Externo → **4** = Constitucional + Administrativo → **5** = manutenção (Português, Inglês, RLM, Adm. Pública) → **6** = Processo Legislativo → **depois da prova**: Direito Eleitoral e o que for só-Senado. Contagens, executáveis e custo por fase moram no 0004 — copiá-los para cá é como este arquivo apodreceu da última vez.

**Direito Eleitoral: adiada para depois da prova do TCU** (decisão do Daniel, 11/08/2026, `0004 §1` — "não é o núcleo do Consultor nem a matéria fundante da carreira"). O registro de estado dela continua verdadeiro: tem `trilha.md` desde 09/08/2026 (dez passos tirados das dez questões da prova aplicada), e **falta material próprio** — nenhuma folha de passo, cinco dos oito arquivos do padrão ausentes, roteando inteira para fonte externa (Código Eleitoral Anotado do TSE, QConcursos). Quando voltar, entra pela regra-mãe 8 como questões e lei seca, nunca como "abrir a folha do Passo 1", que não existe.

**Escalonamento dos níveis-0 (vale mais que a ordem fina):** nunca duas matérias nível 0 abrindo no mesmo mês. Cada uma entra pelo método anti-evitação (metodologias.md).

**Processo Legislativo é a única matéria do Senado que permanece na fila** (`0004`, fase 6 — possivelmente com o RISF, a confirmar com o Daniel). A âncora antiga caiu com o Analista: no Consultor, o Bloco I traz *Processo Legislativo Constitucional*, que é processo pela CF e não pelo Regimento. O RISF continua valendo pela **discursiva** (parecer sobre proposição exige tramitação real) e pelo exercício do cargo — e o parecer está fora do horizonte até depois da prova do TCU.

## Eixos e pisos — aposentados pelo pareamento de blocos

A tabela de eixos A/B/C com piso percentual existia para impedir que o alvo sem edital minguasse enquanto a atenção puxava para o que tinha data. **Em 11/08/2026 ela foi substituída por uma garantia estrutural** (`0004 §8`): cada fase pareia blocos **da mesma prova do TCU** (P1×P2), porque a régua que passou a importar é a eliminação por bloco — abaixo de 25 pontos em qualquer um, sem compensação —, e piso percentual por eixo não protege contra isso; o pareamento protege. O escalonamento dos níveis-0 (nunca duas matérias nível 0 abrindo no mesmo mês) continua valendo por cima das fases.

A discursiva segue fixa, semanal, e não conta contra alocação nenhuma.
