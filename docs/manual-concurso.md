# Manual — estudo para concurso com skills e agentes

## A divisão de trabalho em 10 segundos

Duas skills carregam a preparação, com papéis que **não se misturam**:

- **`estrategista-concurso`** decide **o quê, quando e quanto** — cronograma (macro/meso/micro), check-in semanal, leitura de métricas, matriz de prioridades, replanejamento pós-edital. Nunca produz conteúdo.
- **`concurso-prep`** executa **o como** — método questões-first, trilhas FGV × CEBRASPE, verticalização de edital, geração de questões estilo banca, Anki (erro→card), treino e correção de discursivas, simulados.

Elas compõem: o estrategista aloca a semana; o concurso-prep preenche cada bloco. Se o pedido é sobre **seu progresso ou seu tempo**, é estrategista; se é sobre **a matéria ou a técnica**, é concurso-prep.

## As peças de apoio

| Ferramenta | Papel na preparação | Como chega |
|---|---|---|
| `/deep-research` | Dossiê verificado de concurso/banca/órgão (equivale ao radar do acervo web) | Você digita |
| MCPs Exa/Tavily | Checagem pontual: "saiu edital?", retificações, PDF do edital | O agente usa em passo separado |
| `briefing-designer` | Versão PDF do plano/relatório mensal — só sob pedido explícito | Auto, ao pedir PDF |
| `senior-data-scientist` | Dataset grande de desempenho (planilha/CSV extenso) | Auto |
| `/teach` | Aprender domínio novo com learning-records (fora do ciclo do edital) | Você digita |
| LifeOS: `daily-capture`, `obsidian-note` | Registrar sessão de estudo/tracker no vault | Auto |
| `/schedule` | Rotina recorrente (ex.: lembrete do check-in de domingo) | Você digita |

**Fronteira rígida**: sinais psicológicos (evitação, ruminação, depleção) têm condução **só no Claude web** (`kit-sobrevivencia-atipica`). No Code, o estrategista nomeia o sinal, protege o dia (piso) e sugere pauta de terapia — nunca conduz técnica.

## O loop semanal

```
DOMINGO   check-in: cole o bloco canônico → régua verde/amarelo/vermelho
          → semana seguinte preenchida (slots, tópicos, primeira ação por bloco)
          + discursiva semanal (inegociável; correção via concurso-prep)
SEG–SÁB   executa os blocos → método e conteúdo via concurso-prep
          erros do dia → caderno de erros → cards Anki (fluxo erro→card)
QUINZENA  simulado (cadência da fase) → cola o resultado → modo Diagnóstico
MÊS       virada: meso template (cor do mês, marcos, matriz recalculada)
EDITAL    "saiu o edital, replaneja" (+ link/PDF) → protocolo 72h:
          D0 ler como contrato · D1 engenharia reversa + matriz · D2 novo meso
```

## O check-in na prática

Digite "check-in" e cole o bloco canônico (formato completo em `skills/estrategista-concurso/references/metricas-e-checkin.md`):

```
CHECK-IN — semana de DD/MM a DD/MM
Presença: _/7 verdes · dias-piso: _ · DMV: _
Horas: __,_ · Questões: ___ · acerto por disciplina: SIGLA __% (n=__)
Anki: retenção __% · atrasados: __ · Discursiva: S/N · nota __/__
Erros por tipo: C__ M__ L__ D__ N__ · Ânimo (0–10): __ · alertas: [...]
```

Campos vazios são aceitáveis — o agente pergunta só o decisório e nunca trava o check-in por dado faltante. A resposta fecha em ~5 linhas: cor · o que muda · o que observar. Máximo 3 achados por check-in.

## Modos do estrategista (gatilhos)

| Você diz | Modo | Sai |
|---|---|---|
| "check-in" + bloco | Check-in | Leitura → régua → próxima semana preenchida |
| "monta o cronograma", "planeja agosto" | Planejar | Meso mensal / macro pela matriz de prioridades |
| "saiu o edital", "vou viajar", semana vermelha | Replanejar | Protocolo 72h / deload / retomada |
| "como estou?", "analisa meu simulado" + dados | Diagnóstico | Erro por assunto × tipo, calibração N1–N3, realocação |
| "monta meu tracker/planner" | Ferramentas | Uma das 4 vias de registro com o bloco canônico |

## Pedidos que vão direto ao concurso-prep

- "verticaliza esse edital" · "gera 15 questões estilo CEBRASPE de ProcLeg"
- "monta os cards dos erros dessa semana" · "corrige essa discursiva com critérios FGV"
- "qual a diferença de abordagem FGV × CEBRASPE em Português?" · "monta meu simulado híbrido"

## Acervo web ↔ Claude Code

O mesmo estrategista existe nos dois acervos (paralelos de propósito). As skills-satélite do web mapeiam assim no Code:

| Web | No Claude Code |
|---|---|
| `radar-concursos` | Pesquisa Exa/Tavily em passo separado; `/deep-research` para dossiê |
| `anki-concursos`, `discursivas-concursos`, `gramatica-concursos`, `esquematizador-juridico` | `concurso-prep` |
| `kit-sobrevivencia-atipica` | **Sem equivalente** — usar no web; aqui só nomear + proteger o dia |
| `briefing-designer`, `data-analyst` | `briefing-designer` (mesmo nome), `senior-data-scientist` |

## Anti-padrões

- **Replanejar por um dia ruim** — a régua decide a escala da resposta; um dado isolado não reestrutura nada.
- **Medir por horas ou compensar dobrando** — questões analisadas são a métrica; "dobrar amanhã" é a porta do burnout.
- **Pedir métrica sem fonte** — sem check-in/simulado colado, o agente trabalha qualitativo e diz que é qualitativo.
- **Usar o estrategista para ensinar matéria** — conteúdo é concurso-prep; o estrategista só aloca.
- **Conduzir protocolo psicológico no Code** — é fronteira do kit (web); aqui: nomear, piso, terapia.
- **Pular o check-in e pedir "o que estudar hoje"** a frio — funciona, mas degrada: sem bloco canônico a resposta é heurística.
