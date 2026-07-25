# Métricas e o bloco de check-in canônico

Sumário: Bloco canônico · Como ler os campos · Limiares e regras de decisão · O que NUNCA fazer com métricas

## Bloco canônico

É o que Daniel cola na conversa — e o que **toda** ferramenta de registro (ferramentas-registro.md) gera, campo a campo, para que qualquer via desemboque no mesmo check-in:

```
CHECK-IN — semana de DD/MM a DD/MM
Presença: _/7 verdes · dias-piso: _ · DMV: _
Horas: __,_ (alvo 22 · piso 10)
Plano: blocos __/__ · adiados: __ · mesmo bloco 2×? S/N
Questões: ___ · acerto geral __% · por disciplina: SIGLA __% (n=__), ...
Anki: retenção __% · reviews/dia ~__ · atrasados: __
Discursiva: S/N · nota __/__ · quesito fraco: ______
Simulado (se houve): formato FGV/CEBRASPE · % por disciplina · erros N1: __
Erros por tipo: C__ M__ L__ D__ N__
Ânimo (0–10): __ · alertas: [nenhum | planilha | hiperfoco migrou | "não vai dar" | 3+ pisos | pulei domingo]
Eventos: ______
```

## Como ler os campos

- **Campos vazios são aceitáveis.** Pergunte só o que for decisório para a régua e para a semana seguinte; nunca trave o check-in por dado faltante.
- **n < 10 numa disciplina**: não conclua nada — é ruído amostral. Registre e espere acumular.
- **Presença** é o painel emocional (verde/piso/cinza); **horas** são log técnico. Não misturar: cobrar horas alimenta a autocrítica, e autocrítica alimenta desistência.
- **Acerto por disciplina** alimenta as zonas; **erros por tipo** alimentam a terapêutica; **N1** alimenta a calibração. São três leituras diferentes do mesmo caderno.
- **Plano** (novo, 25/07/2026) mede aderência: blocos executados ÷ planejados do Plano-Semana/Dia. **Antecipar bloco conta a favor** — a ordem dentro da semana é livre; o que importa é o bloco acontecer. O dado decisório não é o %, é **qual** bloco repete adiamento (evitação localizada). % baixo sem causa externa apenas reforça o amarelo das horas — não é régua nova.

## Limiares e regras de decisão

| Sinal | Limiar | Resposta |
|---|---|---|
| Presença | 2 cinzas seguidos | Vermelho → protocolo de retomada (ciclos-e-templates.md) |
| Horas | < 10 na semana sem causa externa | Amarelo → encolher para o núcleo |
| Aderência ao plano | Mesmo bloco adiado 2× na semana | Sinal de **evitação** → método anti-evitação no subtema (dose menor, exemplo resolvido — metodologias.md), nunca cobrança; conferir se é matéria nível-0 |
| Zona de acerto | ≥ 70% confirmado em 2 simulados | Manutenção: só FSRS; realocar o tempo de estudo novo |
| | 60–70% | Consolidação: mantém no ciclo de questões; retestar em 2 semanas |
| | < 60% | Aprofundar: teoria do subtema + questões acima do nível |
| Erros de Leitura | ≥ 30% por 2 semanas (lote ≥ 20) | Trocar conteúdo por treino de interpretação de enunciado |
| Erros de Conceito | > 50% do lote | Regressão teórica focada no subtema |
| Erros de Desatenção | Predomínio no lote | Automaticidade: ruído + cronômetro + riscar restritivos; checar sono |
| Erros N1 | Qualquer recorrência | Prioridade máxima da semana: investigar um a um |
| Anki retenção | > 95% numa disciplina | Podar/subir retenção-alvo; realocar tempo |
| Anki atrasados | Crescendo por 2 semanas | Reduzir novos/dia (redimensionar com anki-concursos) |
| Discursiva | Estrutura não fecha no tempo −20% por 2 semanas | Gargalo é estrutura: repetição de arquitetura cronometrada, não mais leitura |
| Discursiva | Nota por quesito estagnada 3+ peças | Levar o quesito fraco ao discursivas-concursos como foco do treino |
| Ânimo | ≤ 4 por 2 semanas | Pauta de terapia + checar depleção (perfil-e-semana.md → kit) |
| Alertas | 2+ simultâneos | Vermelho, mesmo com números bons |

## Prontidão por disciplina×banca (leitura mensal — só no meso)

Porte aprovado em 25/07/2026 (avaliação Gurujá): projeção honesta de convergência, feita na virada de meso — **nunca no check-in semanal**.

- **Métrica:** limite **inferior** do intervalo de Wilson 95% sobre o acerto das últimas 4–6 semanas (questões + simulados), por disciplina×banca. **"Convergindo" = limite inferior ≥ corte de referência** (default 70% = zona de manutenção; recalibrar com o corte real quando o edital sair). Cebraspe: % de acerto sobre itens respondidos, reportando % de brancos ao lado.
- **Regras:** n ≥ 10 por célula (abaixo disso: "sem dado", não "ruim"); vale o teto de 3 achados; a saída é decisão de **alocação** (dose sobe/desce/mantém), nunca prognóstico — "chance de aprovação" é a vanity metric que o sistema rejeita.
- **Tabela de referência** (limite inferior de Wilson 95%, para ler sem calcular):

| n \ acerto | 60% | 70% | 80% | 90% |
|---|---|---|---|---|
| 10 | 31% | 40% | 49% | 60% |
| 20 | 39% | 48% | 58% | 70% |
| 30 | 42% | 52% | 63% | 74% |
| 40 | 45% | 55% | 65% | 77% |
| 60 | 47% | 57% | 68% | 80% |

Leitura: 80% de acerto com n=20 garante só ≥58% — amostra pequena não sobe ninguém de zona; o intervalo alarga sozinho (honestidade estrutural). Com n≥40 e limite inferior ≥ corte, a disciplina está convergida para manutenção — confirmando com a regra dos 2 simulados (metodologias.md).

## O que NUNCA fazer com métricas

- Concluir tendência com n pequeno ou a partir de uma única semana ruim.
- Comparar Daniel a "média de concurseiro" — a régua é ele contra ele mesmo; a curva do mural é a evidência de que o esforço converte, e é disso que a expectativa de resultado se alimenta.
- Converter métrica em cobrança moral: número informa **alocação**, nunca valor pessoal.
- Auditar tudo: máximo 3 achados por check-in; o resto espera o meso.
- Usar a nota agregada de simulado para decidir qualquer coisa — a decisão sai do erro por assunto × tipo × convicção.
- Ler prontidão fora do meso, com n < 10, ou como "chance de aprovação" — é régua mensal de alocação, não termômetro semanal.
