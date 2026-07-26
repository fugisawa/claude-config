# Anki para concurso — método banca-dupla (FGV × Cebraspe)

> v2 (26/07/2026). Contrato de evidência: `manual_estudo/build/_pesquisa-anki-2026.md` (rótulos [EVIDÊNCIA]/[HEURÍSTICA] lá). Substitui a cadência fixa 24h/7d/15d/30d da v1 — era doutrina pré-FSRS.

## Papel no sistema (fronteiras duras)

- **O Caderno de Erros é o sistema primário do erro; o Anki é o pedágio de FATOS.**
- **Gate (antes de qualquer card):** o que eu não sabia era um FATO (prazo, quórum, artigo, rótulo, exceção, par confundível)? → card. Era interpretação/raciocínio/estratégia? → caderno de erros e questões — **nunca card**. Procedimento ("como resolver") não vira card; a regra pontual que o procedimento usa, sim (ex.: "condicional só é F em V→F" é fato; "traduza os conectivos antes de julgar" é gatilho→ação da ficha, não card).
- Dose, teto e realocação = `estrategista-concurso` (check-in/meso). Sequência de conteúdo = trilhas do projeto. Esta skill **cria e valida** cards.
- **Pipeline de geração por LLM (obrigatório):** gerar *grounded* no material-fonte ("pule se não estiver no texto") → validar mecanicamente → **revisão do usuário lote a lote** → inserir. Esperar ~30% de rejeição/edição é normal (evidência 2025-26); a revisão é parte do método. Nunca "gere 100 cards do capítulo X".

## As 3 trilhas (origem do card)

| Trilha | Quando | Dose | Vida |
|---|---|---|---|
| 1 Bootstrap | disciplina nível-0, semanas 1–2 | 50–100 cards | temporária |
| 2 Teoria elaborativa | durante o estudo | 3–5/sessão | temporária |
| 3 Questão errada | após erro real (gate), em ≤24h | 1–3/questão | **permanente, fonte principal (~60%)** |

- Bootstrap: pretesting fixa **só o que é perguntado** (meta-análises 2023/25: g≈0,6 específico, transferência ≈0) — dirigir às 6 categorias do doc de substrato (terminologia, estrutura, números, **pares confundíveis** ← prioridade, fluxos, expressões), nunca "aquecimento amplo".
- Trilha 2: o "por quê" precisa ser **auto-gerado** — o hábito é tentar produzir a explicação ANTES de virar o card; o verso é feedback, não substituto (elaboração lida pronta não gera o ganho).

## Design de card (regras duras)

1. **Atômico**: 1 fato/exceção/par por card; frente 8–25 palavras; máx 3 linhas; artigo com N incisos = N cards; **proibido cloze múltiplo de fatos independentes** (c1..c4 numa nota = 4 cards ruins, não 1 bom).
2. **Cloze esconde O DADO decisivo, nunca o contexto** — e a lacuna deve ser irrecuperável sem saber o conteúdo (se a sintaxe entrega, o card é ruim).
3. Verso/Extra sempre com: por quê + fonte (lei/artigo) + questão-origem quando houver (ancora no contexto de prova).
4. **Tags flat 4-dim**: `disciplina` · `topico` · `trilha` (bootstrap/teoria/questao-errada) · `banca` (fgv/cebraspe/ambas). **Decks flat por disciplina** (AFO, RLM, …); modelos "Concurso Basic"/"Concurso Cloze".
5. Teste "esse card presta?": uma pergunta↔uma resposta? resposta objetiva? eu erraria sem saber o conteúdo? tem por quê + fonte? me faz acertar uma questão?

## Cebraspe C/E — item → card (5 padrões)

Regras duras: **nunca** card "julgue Certo/Errado" puro (retrieval fraco, preso ao formato) — exceção única: padrão 3; **nunca clozar a versão errada do item** (consolida falsa memória — reescreva para a versão correta antes); **regra geral no verso é obrigatória** (sem feedback, o distrator persiste).

1. **Correção Produtiva** (item ERRADO): frente = a frase **já corrigida**, cloze exatamente no detalhe que a banca trocou (a pegadinha Cebraspe muda UM detalhe pequeno). Ex.: item "a dotação global da reserva de contingência ofende a especificação" (E) → `A dotação global da reserva de contingência é {{c1::exceção legítima}} ao princípio da especificação (LRF art. 5º, III, b).` Verso: "Banca vende exceção legal como violação — o item nega a exceção ou troca o princípio?"
2. **Sentence Mining do Certo** (item CERTO): cloze na palavra que sustenta a assertiva. Ex.: `A vigência da LOA limita-se, em regra, ao exercício financeiro de {{c1::um ano}} (anualidade).`
3. **Confiança Calibrada** (erro com conf 4–5 registrado no caderno): única exceção com julgamento C/E na frente — o valor é o choque metacognitivo (hipercorreção). Verso abre com `⚠️ você errou isto com conf N no simulado de DD/MM` + correção + regra. (A frente reproduz o item e por isso PODE exceder as 8–25 palavras — comprimir só até onde os conectivos-armadilha sobrevivem.)
4. **Distrator/Discriminação** (par confundível): **1 par por card**, nunca mais. Ex.: `"Todas as receitas e despesas no orçamento" é {{c1::universalidade}} — não unidade (unidade fala do documento único).`
5. **Micro-habilidade Atomizada**: assertiva de 3 linhas com 2–3 microrregras → 2–3 cards, cada um com UMA (generaliza a doutrina de PT — conectivos/tom/referenciação — para AFO/CE/CASP).

## FGV 5 alternativas — cards

- Par confundível → padrão 4 (idêntico). Rótulo/sinônimo de banca ("pureza" = exclusividade) → card de rótulo.
- Distrator inteligente de questão errada → card "por que X está errado" — **1 distrator por card; nunca as 5 alternativas juntas** (revisar muitos distratores de uma vez fixa distrator como verdade).
- O card estilo C/E "afirmação quase-certa" também treina a discriminação FGV [aposta fundamentada, sem contra-evidência].

## Revisão de pares confundíveis (interleaving)

- O deck já intercala; o que não é automático: ao revisar par confundível, perguntar ativamente **"qual é a diferença?"** (instruir isso quase triplica o aproveitamento).
- Distinção que depende de **regra explícita** (típico de direito): consolidar a regra em bloco primeiro (aula + lote de questões), intercalar depois [condição de contorno 2025].

## Configuração (Anki ≥25.07 · FSRS-6)

- **FSRS ON**, retenção-alvo **0,90** (faixa saudável 85–90). Learning steps **curtos**: `10m` (ou `10m 30m`) — **nunca steps ≥1 dia**; FSRS não modela memória de curto prazo e steps de dias brigam com o agendador. **Não existe cadência manual** (24h/7d/15d/30d era doutrina pré-FSRS — abolida).
- Intervalo máximo: deixar o default; se capar, capar **conscientemente na data-horizonte da prova**, nunca "90/120/180 dias" por hábito.
- "Compute optimal retention" **foi removido do Anki** (25.07) → usar **"Help Me Decide"** para simular carga na virada de meso; **otimizar parâmetros FSRS 1×/mês**.
- **15 novos/dia (teto 25)** [escolha de carga — FSRS é agnóstico; ~20 novos ⇒ ~200 rev/dia]; pedágio-alvo 20–35 min/dia; revisões sem limite; bury siblings ON; zerar atrasados à noite.
- Leech: default (8 lapsos → suspende); leech = card mal formulado → **reescrever** ou devolver ao caderno, não repetir.
- Sync: 1 perfil ↔ 1 conta AnkiWeb; **backup `.colpkg` antes do primeiro sync de cada dispositivo** (a resolução de colisão upload×download é destrutiva numa direção). Revisão móvel: AnkiWeb + Anki Mobile (iPhone).

## Economia do deck (antídoto à Anki-dependência)

- Teto global e cotas por disciplina: re-derivados no meso pelo estrategista — não são desta skill.
- **Protocolo de crise**: >150 rev/dia OU >45 min/dia OU backlog >200 → zerar novos + retenção 0,85 + suspender tag `prioridade-baixa`; backlog >500 = "falência do Anki" → reconstruir com o estrategista.
- Auditoria dominical (10 min): leeches, taxa de Again, cards que nunca erram (podar).

## Common mistakes

| Erro | Correção |
|---|---|
| Steps `1d 7d 15d` / "garantir 1ª revisão em 24h" com FSRS | steps só de minutos; o FSRS agenda o resto |
| Card "CERTO ou ERRADO:" puro | padrões 1/2/5 (produção); C/E puro só no padrão 3 |
| Cloze da assertiva errada como está | reescrever para a versão correta antes de clozar |
| Nota com c1..c4 de fatos independentes | 1 fato por card |
| "Gere N cards do capítulo" sem revisão | pipeline com revisão lote a lote (~30% de edição esperada) |
| "Qual o artigo?" isolado | regra + exceção + onde a banca ataca; nº do artigo no verso/junto |
| Card de procedimento/raciocínio | gate: procedimento → caderno/questões, não Anki |
| Deck hierárquico/cotas inventadas na hora | decks flat por disciplina; dose vem do estrategista |
