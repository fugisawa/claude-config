# Perfil operacional e janelas

Sumário: Regras do perfil · Orçamento e janelas · Dia furado e DMV · Protocolos P1–P15 · Se-então pré-decididos · Sinais que roteiam ao kit

Fonte: *Plano de 18 Meses* e *Arranque* (jun/2026), com a forma do tempo revista em 08/08/2026. Estas regras valem em **qualquer** plano gerado — não são opcionais nem negociáveis semana a semana.

> **Renome de 12/08/2026.** O item numerado da fila de cada matéria passou a se chamar
> **tópico**, e a unidade de execução, **sessão** — decisões `0010` e `0011` do
> `manual_estudo`. Onde este arquivo dizia "folha de passo", agora diz "folha do tópico".
> A regra não mudou; o nome, sim. **A transcrição destas linhas no `estudo/dia.py` é
> conferida por comando** (`python3 estudo/canone.py`, decisão `0012`): as duas pontas
> não podem mais divergir em silêncio, que foi como esta própria linha envelheceu.

> **O que mudou de nome, e por quê.** Este arquivo se chamava `perfil-e-semana.md` e trazia uma semana-modelo com hora cravada (pico 6h10, sala de manhã, Anki 19h45). A grade foi substituída em 08/08/2026: ela pressupunha rotina estável, e com o trabalho pesado o dia deixou de caber no molde. O perfil não mudou; a forma do tempo, sim.

## Regras do perfil (por que o plano tem esta forma)

Daniel: perfil 2e (TEA + AH/SD, com laudo), aprovado ABIN 2008, recomeço após 10+ anos. Três traços comandam todo o desenho:

1. **Aprende pelo porquê.** Memoriza acima da média quando o conteúdo tem lógica; esquece rápido o arbitrário sem explicação. Decoreba crua trabalha contra a neurologia → lei seca passa pelos 3 baldes (metodologias.md) e só o resíduo genuinamente arbitrário vira mnemônica.
2. **Estrutura externa pronta.** Monotropismo (atenção funda em uma coisa por vez) + inércia de iniciação: o plano decide **antes**, cada bloco tem a primeira ação definida, e o ponto de partida é sempre **inteiro** (uma ação completa com começo óbvio — nunca lascas soltas nem amontoados vagos). Trocar de tarefa custa caro: dentro do bloco varia a **atividade** (teoria → questões → cartão), nunca a matéria.
3. **Falta expectativa de resultado, não autoeficácia.** Ele não duvida de que executa; duvida de que o esforço converte. O remédio é progresso visível (mural de vitórias, curva de acerto, linha de resultado diária) — nunca discurso motivacional, que desmotiva este perfil.

Risco nº 1: **desistência** (confiança declarada de não desistir: 2/5), não burnout. Quando piso e teto competem, **o piso vence**: em 18 meses, quem nunca quebra a corrente bate quem estuda heroicamente e some por três semanas.

Tetos de foco: Anki 10–15 min · matemática/cálculo 40–50 min. Máximo 2–3 matérias por dia; intercalação **entre dias**, não dentro do dia.

## Orçamento e janelas

Alvo **22 h/semana** (faixa saudável 20–25) · piso **10 h**. A folga entre alvo e piso é proposital: semanas boas acumulam crédito contra semanas ruins, e ele nunca zera.

**O diagnóstico "falta tempo" é falso, e isso foi medido.** Em 08/08/2026: 15–20 h nos dias úteis e mais 10–11 no fim de semana somam **25–31 h por semana**, acima do alvo e no topo da faixa saudável. O que a rotina de trabalho pesado tirou não foi a quantidade de tempo — foi a **contiguidade** dele.

Duas formas de tempo, e elas não se substituem:

| | Dia útil | Fim de semana |
|---|---|---|
| Forma | janelas picadas de **30–60 min**, imprevisíveis | blocos contíguos de **5–5h30** |
| Total | 3–4 h/dia | 5–5h30/dia |
| Serve para | uma unidade completa por janela | o que não sobrevive a ser picado |

**A unidade tem de caber inteira na janela.** Retomar pelo meio é o que faz perder o ponto de partida, e ponto de partida é justamente o que este perfil não pode perder (traço 2). Por isso a **seção da folha do tópico** virou a unidade de teoria: a folha já nasce partida assim, um conceito e seu cue por seção.

Os quatro blocos, na ordem em que a energia que eles exigem se degrada:

| # | Bloco | Janela | Quando |
|---|---|---|---|
| 1 | Uma **seção da folha do tópico** | 30–40 min | o momento mais fresco do dia |
| 2 | Um **lote de 20 questões** (banca do dia) | 30–40 min | cansaço médio |
| 3 | **Triagem do caderno de erros** | 20–30 min | exige pouco |
| 4 | **Anki e microdose** | 15–20 min | dia atropelado — e o dia conta como verde |

**A ordem é a regra, e ela substitui o relógio.** O que importava do antigo "pico às 6h10" nunca foi o 6h10: era teoria pesada quando ele está mais fresco. A hora era só o jeito de garantir isso; a ordem garante melhor, porque sobrevive à semana difícil.

**A trava anti-fuga:** o item 1 vem na primeira janela decente do dia, ou não vem. Questão dá sensação de produtividade sem exigir cabeça, e por isso vira o jeito confortável de não fazer teoria.

> **Emenda de 12/08/2026, decisão do Daniel.** No dia útil o dia comporta **dois blocos de
> teoria**, de matérias distintas; **três** só em feriado ou fim de semana sem simulado e
> sem sessão pesada de discursiva. A trava anti-fuga vale para o **primeiro** bloco de
> teoria; o teto de 2–3 matérias por dia e os tetos de foco continuam como estão.
> **Implementada no `estudo/dia.py` na mesma data**: a segunda teoria vem do cursor da
> segunda matéria do rodízio — a unidade que a preenche é a que o cursor responde, seja
> qual for o nome que o modelo de vocabulário (em decisão) lhe der; o lote e a triagem
> seguem da matéria primária, e a terceira teoria de fim de semana segue manual.

**O fim de semana é outro bicho.** Cinco horas seguidas não são dez janelas de trinta minutos, e tratá-las como se fossem desperdiça a única coisa que a semana não oferece. Reserve o contíguo para: discursiva de 90 min cronometrados · simulado em bloco fechado · **folha inteira** de um tópico (em vez de uma seção por vez) · check-in de 40 min. O resto do fim de semana volta a ser fila normal, com a mesma ordem.

Regras que sobreviveram à troca de forma: teoria difícil nunca depois de dia cansativo; a sala de trabalho é lugar de **questões**, nunca de teoria nova (interrupção do expediente trava e contamina o lugar); exercício que faz suar fica na manhã do fim de semana, nunca à noite, porque o batimento demora a baixar e rouba o sono. **Quinta é dia de terapia: meta = piso, por definição — está previsto, não é fracasso.**

> **Sem data, pelo mesmo motivo que sem hora.** Data marcada cria atraso onde havia só uma semana difícil. A rodada anda quando ele puxa; o check-in acontece no primeiro fim de semana em que houver 40 minutos.

## Dia furado e DMV

Imprevisto **rebaixa**, nunca cancela — e o nível já está pré-decidido, porque decidir sob estresse é o que trava. No fundo da escala, o **Dia Mínimo Viável: ~20 min, sempre igual — 15 questões da banca + o Anki que vencer no dia + 1 linha no caderno de erros.**

O "sempre igual" é metade do valor: DMV que muda de conteúdo volta a exigir decisão, que é exatamente o que ele existe para evitar. É uma ação completa com primeiro passo óbvio. Fez o DMV → dia verde, corrente intacta. Frequentemente o começar destrava e ele segue; se parar nos 20 min, já venceu o dia.

## Protocolos P1–P15 (aplicar ao montar qualquer plano)

| # | Nome | Núcleo |
|---|---|---|
| P1 | Porquê-primeiro | Proibido criar cartão do que ele ainda não explica em voz alta; entender, depois fixar |
| P2 | Lei-seca-com-lógica | 3 baldes (lógico/semilógico/arbitrário); mnemônica e loci só no terceiro |
| P3 | Anki-sem-tédio | Só cartão de aplicação nascido de erro real; máx 20–25 novos/dia; retenção-alvo ~0,90; leech suspende |
| P4 | Quando-não-Anki | Compreensão, RLM e habilidade (discursiva) não vão para flashcard; baralho enxuto é antiabandono |
| P5 | A-pior-primeiro | O bloco de maior energia recebe a matéria temida da vez, entrando pela compreensão, com dose-teto |
| P6 | Emparelhamento | Matéria fraca em sanduíche entre blocos da forte; nunca dois blocos "chatos" seguidos |
| P7 | Dia Mínimo Viável | 20 min fixos e leves para que nenhum dia seja zero |
| P8 | Se-furar-então | Imprevistos típicos com resposta pré-decidida (tabela abaixo) |
| P9 | Ritual de reentrada | Voltar depois de furar sem espiral de culpa: entra pelo fácil, reancorando no porquê-maior |
| P10 | Bloco longo monomatéria | **Só no fim de semana**, 90–120 min alternando atividades. No dia útil a janela é de 30–60 min e a unidade é a seção da folha; máx 2–3 matérias/dia, intercalação entre dias |
| P11 | Ritual de transição | Fechar A com bilhete "onde parei / próxima ação", pausa sem tela, abrir B com primeira ação definida |
| P12 | Sprint de compreensão | Hiperfoco autorizado como exceção planejada (fim de semana) para montar a lógica de uma matéria-chave, com teto e alarme |
| P13 | Trava antidesbalanceamento | Teto semanal por matéria + check de cobertura no check-in + janela marcada para tangentes/outros interesses |
| P14 | Bolha sensorial | Fone com cancelamento, instrumental sem letra, luz quente indireta — checklist de 30 s antes do bloco |
| P15 | Accountability assíncrono | Cronograma rígido (cobrança impessoal) + mentor por texto 1×/sem; nunca grupo ou body-doubling |

## Se-então pré-decididos (cole no plano quando pertinente)

| Se | Então |
|---|---|
| A primeira janela decente passou sem o item 1 | O dia é de questões mesmo — e tudo bem. Não se remaneja teoria para a noite cansada |
| Trabalho comeu as janelas do dia | Noite: 30 questões + Anki — conta como piso |
| Sem ânimo / preso no celular | 5 questões de RLM (matéria-prazer) para entrar; se não engatar, dia-piso legítimo, sem culpa |
| Imprevisto quebrou o dia inteiro | Só DMV; não tenta recuperar o resto |
| Travei numa matéria, tensão subiu | 3 min de respiração → bloco de RLM para reganhar tração |
| "Não vale a pena / já me interessei por outra coisa" | Atenção migrou, não é veredito: 10 min no atual; se insistir, anota e marca horário (P13) |
| Veio "não vai dar certo" | É pensamento, não ordem ("estou tendo o pensamento de que…"); próxima ação mesmo assim |
| Errei questões de rotina | Segue em frente — erro comum é informação, não veredito |
| Empaquei num tópico difícil / dias seguidos de esforço alto | Desconforto = ponto quase aprendido; se for cansaço acumulado, folga antes de apagar |
| Perdi um dia inteiro | Amanhã ritmo normal — **nunca dobrar** |
| Perdi uma semana inteira | A sequência continua de onde parou; o que ficou para trás **não volta como dívida**. A campanha já renumerou uma vez em julho em vez de recomeçar |
| Vou adiar a discursiva | Primeira ação inteira: ler o enunciado e rascunhar a tese (a previsão de tédio é falsa) |
| Prova/tarefa exposta chegando | Antes, escrever uns minutos sobre um valor fora do que será julgado |

## Sinais que roteiam ao kit-sobrevivencia-atipica (nomear + rotear; nunca conduzir)

- **Evitação recorrente** de uma área inteira com energia preservada no resto → kit (ativação comportamental / WOOP).
- **Ruminação ativa**, remoendo derrota ou preocupação pré-sono → kit (autodistanciamento, adiamento de preocupação, ATT).
- **Ameaça avaliativa** com risco de autossabotagem (véspera de simulado/prova que pesa) → kit (afirmação de valores; experimento comportamental de valor é pauta de terapeuta).
- **Depleção**: exaustão profunda, perda de capacidades antes fáceis, descanso que não repõe → NÃO é preguiça nem amarelo comum: proteger o dia (piso), **não empurrar meta**, kit (discriminação evitação × burnout autista) + pauta de terapia.
- **Régua vermelha** (ciclos-e-templates.md) → sempre vira pauta de terapia, além do protocolo de retomada.

A frase de roteamento é curta: nomeie o sinal em 1 linha, proteja o dia, aponte o kit. O estrategista desenha o entorno; a condução da técnica é do kit e da terapeuta.
