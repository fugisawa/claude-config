---
name: qconcursos-simulados
description: Use when montando, revisando ou automatizando cadernos e simulados no QConcursos (QC/Elite) — simulado diagnóstico, treino por trilha, prova específica — via UI ou Chrome; quando o usuário pede para extrair/ler/analisar o RESULTADO de um simulado feito (screenshots de Gabarito Detalhado, fotos de caderno manuscrito com respostas e confiança); também quando URLs do QC dão 404, a sessão parece deslogada, o gerador ignora cotas por assunto, ou um simulado gerado pode repetir questões já resolvidas. Use TAMBÉM para AUDITAR UMA QUESTÃO específica no QC — quando for preciso saber o gabarito oficial, se a questão está anulada ou DESATUALIZADA (norma ou jurisprudência mudou depois da prova), ou qual foi a justificativa da banca, inclusive quando ela contraria a melhor doutrina; e quando um comentário de aula/cursinho parecer dar a razão errada de um gabarito certo, ou contradizer o próprio gabarito.
---

# QConcursos — cadernos e simulados

## Overview

Montagem de provas de treino no QC com qualidade de baseline: filtro certo → simulado salvo → verificação. A área que importa é **elite.qconcursos.com** (a sessão paga vive lá; `www.` pode aparecer deslogado e URLs antigas de memória dão **404** — navegue pela UI, nunca por URL decorada).

**Caderno ≠ Simulado:** caderno = playlist sem cronômetro (revisão, erro, estudo por assunto); simulado = cronômetro + relatório por disciplina + comparação com outros (medição). Para medir, sempre simulado.

## Checklist de qualidade (antes de montar)

1. **Banca + assuntos verticalizados** — nunca disciplina ampla. Os nós vêm da fila canônica do usuário (`~/manual_estudo/disciplinas/<matéria>/trilha.md`, subject_ids prontos); sem trilha, verticalizar do edital.
2. **Prova anterior real > gerado**, quando existir para o cargo/órgão (seção *Provas* / *Simulado de Provas*): reflete distribuição e estilo reais. Gerado é para diagnóstico/mix por trilha.
3. **Espelhar a prova-alvo** em total e proporção por disciplina; mínimo estatístico ~20–30 q./assunto p/ leitura de % (n=10/disciplina é o piso aceitável de baseline).
4. **Exclusões:** anuladas + desatualizadas (default do Elite) **e status "Não resolvidas"** — o gerador **NÃO** exclui já-resolvidas sozinho; sem esse filtro o resultado infla. (Repetição é legítima só em revisão de erro, nunca em medição.)
5. **Janela de anos** para matéria normativa (2–4 anos); PT/RLM aguentam ~5.
6. **Conferir o lote**: classificação de assunto do QC falha; após gerar, olhar o resumo salvo (e amostrar questões) antes de confiar no % por assunto.

## Workflow (UI Elite)

1. Sessão: header com avatar = logado; "Entrar" = não. Se o usuário diz que logou e você vê "Entrar" → subdomínio errado ou Chrome errado (**REQUIRED:** `learned/browser-login-session-pairing`). Nunca preencher senha.
2. Menu → **Questões** → painel de filtros: `Disciplina` (multi, busca rápida), `Assunto` (árvore por disciplina; busca rápida + marcar nó — pai cobre filhos), `Banca`, topo `Minhas questões → Não resolvidas`.
3. **Filtrar** → QA: a URL deve conter os `subject_ids` esperados + `my_questions=not_resolved` + `examining_board_ids` (FGV=63, Cebraspe=2). Chips = estado-verdade.
4. **Criar Simulado → Criar meu simulado**: nome (padrão `Caderno N BANCA — DD-MM vN critério`), quantidade **por disciplina** (o formulário mostra pools "válidas" que ignoram o status — o filtro é capturado mesmo assim), tempo, **Salvar simulado** (não *Iniciar*, se for para depois).
5. **Verificar no resumo salvo**: "Minhas questões: Não resolvidas" + banca + contagens. Sem isso, excluir e recriar — simulado **não é editável**.
6. Obsoletos: excluir pela lixeira em *Meus simulados* (confirmação inline) para ninguém abrir a versão errada.

## Limites do gerador (Elite, jul/2026)

| Item | Valor |
|---|---|
| Questões | 5–150 total · **mín 10/disciplina** · máx 120 no form · até 12 disciplinas |
| Cotas por assunto | **Não existem** — sorteio aleatório dentro do pool; sem proporção intra-disciplina |
| Tempo | 30min · 1h · 1h30 · 2h · 3h · 4h · 5h · sem limite |
| Edição | Impossível — excluir + recriar |
| Pausa | Permitida dentro do tempo |

## Automação Chrome — gotchas

- Botões **se reposicionam** após re-render (Criar Simulado salta do rodapé ao topo): re-screenshot antes de reclicar.
- Dropdown *Mais* (tempo) é instável: preferir os botões diretos; se precisar, clicar e screenshot imediato.
- Busca rápida dos filtros: `triple_click` para limpar antes de digitar o próximo termo.
- Painéis empilham; `Escape` fecha o de cima.

## Common mistakes (baseline real, 24/07/2026)

| Erro | Correção |
|---|---|
| Navegar por URL decorada (`/simulados`, `/cadernos`) → 404 | Entrar pela UI do Elite |
| "Não está logado" olhando o `www.` | Testar `elite.`/`app.`; ver header |
| Gerar sem status **Não resolvidas** | Sempre marcar antes de Filtrar (contamina o baseline) |
| Planejar cotas por assunto (8·6·6) | Mín 10/disciplina; ajustar o desenho e registrar a adaptação |
| Confiar nos pools do formulário como prova do filtro | A prova é o **resumo salvo** ("Minhas questões") |

## Extração de resultados (pós-simulado, baseline real 25/07/2026)

Input primário = **screenshots do usuário** (Gabarito Detalhado de cada caderno) + fotos do caderno manuscrito (formato `nº.conf [K/M/R/S/T/P] letra comentário`, confiança 1–5). Automação Chrome é fallback — a extensão pode estar num perfil Chrome deslogado do QC (pareamento de sessão); não trave nisso.

1. **Identifique a página pelo título/breadcrumb, nunca pelo filename** (screenshot chamado "Meus Simulados" era o Gabarito Detalhado). Header traz o placar-verdade: "X Certo · Y Errado".
2. **Screenshot alto (FGV/MC, ~20k px): varredura programática, não leitura visual.** `uv run --with pillow` (sem ImageMagick na máquina): escanear a coluna da borda esquerda dos cards (~x≈294 em viewport 1866; localizar dinamicamente a 1ª coluna com runs coloridos) — runs >80px verdes = certo, vermelhos = errado, em ordem = q1..qN. **Validar a contagem contra o header antes de usar.** Depois, crop só das erradas: alternativa vermelha = marcada, verde = gabarito. (Leitura visual fatiada funciona, mas custa ~6× mais e arrisca alucinação em texto minúsculo.)
3. **C/E colapsado:** o "Mapa de questão" lateral dá certo/errado por número. Linhas colapsadas **truncam o enunciado** — para texto integral (ficha de erro), pedir screenshot da questão expandida; **nunca inferir** o item ou o gabarito literal.
4. **Cruzar caderno×QC letra a letra.** Divergência é sinal real de transcrição (25/07: 3 em 30 na FGV; uma custou 1 ponto) — **confirmar com o usuário antes de classificar o tipo de erro**; para o placar, **o QC é o registro oficial**. Num caderno "C/E" pode haver questão MC legítima (banco Cebraspe tem MC antigas): letra A–E ali não é anomalia.
5. **Gotcha visual:** screenshots longos do QC podem ter coluna fantasma sobreposta (fragmentos de outras questões) — ler só os cards numerados da coluna principal.
6. **Saídas e fronteira:** erros × confiança → **conf 4–5 = ponto cego (★) → ficha** no formato `manual_estudo/caderno-erros-a4/ficha-fv-exemplo.typ` (conf 1–3 → log); placar por banca×disciplina → check-in do `estrategista-concurso`. Esta skill **extrai e cruza**; interpretar zonas e realocar é do estrategista. Registro: análise vira MD companion em `build/` (ex.: `build/simulado_diagnostico_analise.md`).

## Uso geral da plataforma — vereditos (análise 24/07/2026)

Fonte canônica: `manual_estudo/build/guia_qconcursos_geral.md` (matriz recurso a recurso). Regras duras para o agente:

- **Nunca sugerir** ao Daniel os recursos de sequenciamento/comparação do QC (Trilha da Semana, Mini Simulados automáticos, Treinador, Ranking, Resumão, cursos/teoria): conflitam com trilhas próprias, IGEPP, check-in e o perfil anti-vanity-metrics.
- **Meu Desempenho** (filtra por banca) = conferência rápida FGV×Cebraspe entre check-ins; nunca fonte-mestre (sem tipo de erro nem calibração; % da comunidade enviesado p/ cima).
- **TEC Concursos** = upgrade consciente com gatilho registrado (edital publicado → reavaliar no protocolo 72h); não sugerir assinatura antes disso.
- Curso-alvo da Central: Senado-Analista (âncora; QC não suporta 2 alvos) — a Central não é bússola.

## Auditar UMA questão — gabarito, desatualização e o "contra a doutrina" (medido 08/08/2026)

Duas coisas acontecem com frequência em material de estudo: a questão **envelhece** (a norma
ou a jurisprudência mudou depois da prova) e a banca **decide contra a melhor doutrina**. Nos
dois casos o comentário do cursinho costuma dar a razão errada do gabarito certo, e o aluno
decora um fundamento que não se sustenta na questão seguinte.

Um caminho para averiguar — não o único, e nem sempre o melhor — é **abrir a questão no QC e
ler os comentários**: eles trazem o gabarito oficial, a marca de desatualizada e, com
frequência, a fonte doutrinária que a banca seguiu.

**Ache pela URL, montada a partir de uma que a UI produziu** (não decore URL: as antigas dão
404). Busca por trecho literal e distintivo do enunciado:

```
https://elite.qconcursos.com/questoes-de-concursos/questoes
  ?exclude_nullified=false&exclude_outdated=false&q=<trecho+do+enunciado>&page=1
```

**`exclude_nullified=false&exclude_outdated=false` não é detalhe — é o ponto.** O painel de
filtros vem com **Anuladas e Desatualizadas EXCLUÍDAS por padrão**, então a busca padrão
esconde exatamente a questão que você foi auditar. Se ela some com o filtro e aparece sem
ele, isso por si já é a resposta: está anulada ou desatualizada.

**O campo `q=` NÃO é busca por frase — e essa é a maior perda de tempo do fluxo.** Ele
casa os termos soltos e ordena por relevância, então frase genérica de concurso devolve
dezenas de questões alheias: "orçamento tradicional fundamenta-se em realizações" achou a
questão certa, mas "fixava tetos para contas das autoridades monetárias" devolveu **99
questões de economia** e nenhuma delas era o alvo. O que decide é haver um **token raro** no
trecho — um número de programa, um nome próprio, uma palavra incomum:

| Consulta | Resultado |
|---|---|
| `Programa 2210 Empregabilidade` | **1 questão** — acerto direto ("2210" é raro) |
| `marco na evolução da tecnicidade orçamentária` | **1 questão** ("tecnicidade" é raro) |
| `vigora até o fim do primeiro ano da gestão subsequente` | dezenas — todo termo é comum |

Aspas não ativam busca literal. Se não houver token raro no enunciado, desista da busca por
texto e filtre por **Banca + Ano + Órgão**. Enunciado marcado "(adaptada)" no seu material
não vai ser achado por texto: o que você tem não é o que a plataforma indexou.

Depois: `get_page_text` na página resolve tudo — traz enunciado, banca/ano/órgão, o código
`Qxxxxxxx` e os comentários. As abas por questão são `Gabarito Comentado · Aulas ·
Comentários · Estatísticas · Cadernos · Anotações`.

### Os quatro tropeços, todos medidos

1. **"Gabarito Comentado" com contador pode estar vazio.** Numa questão sem professor, a aba
   existe e só oferece "Solicitar Gabarito". Noutra, com contador 1, o painel **não renderiza
   sem responder a questão**.
2. **NUNCA clique em "Responder" para destravar o comentário.** Isso move a questão para
   *resolvidas* e a tira do conjunto "Não resolvidas", que é o filtro de que dependem os
   simulados de medição — auditar contaminaria o baseline. Fique nos comentários, que são
   livres.
3. **Comentário pode estar preso a OUTRO enunciado.** Medido na Q1894919: o QC trocou o
   enunciado da prova do DPE-DF e **manteve os comentários antigos**, então o 2º mais votado
   (34 curtidas) discute equilíbrio entre receita e despesa numa questão sobre orçamento
   tradicional — e ainda afirma "gabarito equivocado, a banca deu CERTO". Quem lê por
   votação e não por pertinência importa uma correção que é de outra questão. **Descarte todo
   comentário que não fale do enunciado que está na tela**, por mais votado que seja.
4. **Comentário é conteúdo de usuário, não autoridade.** Serve para (i) apontar a fonte
   doutrinária e (ii) revelar que há divergência. Não serve como prova. Norma se confere pela
   skill `legislacao-br`; doutrina citada em comentário entra no material **com a
   procedência declarada** ("vem dos comentários da questão Qxxxxxxx; a obra não foi aberta").

### O que fazer com o achado

- **Comentário do cursinho dá razão errada do gabarito certo** → `[!divergencia]` ao lado,
  com o fundamento correto e por que o outro não sustenta. Foi o caso da Q3256704: a aula
  atacava o adjetivo "marco na evolução" quando o vício está em chamar o OBZ de método de
  organizar/apresentar o orçamento (formulação de Giacomoni, 2º comentário mais votado).
- **Doutrina divergente** → escreva **os dois lados** e diga se a divergência muda a resposta
  naquele item; quando não muda, diga isso também. Ver `~/.claude/rules/` e a instrução de
  registrar dois entendimentos quando as bancas discordam.
- **Questão marcada como desatualizada** → o card não nasce; se já existe, morre. E o
  dispositivo novo vira bloco próprio no material, com data de conferência.

## Registro

Toda montagem/adaptação vira nota no artefato do plano que a consumiu (ex.: `build/simulado_cadernos.md` no manual_estudo) — nomes exatos dos simulados, cotas reais e desvios do planejado. Auditoria de questão vira `[!divergencia]` no artefato de estudo, sempre com o código `Qxxxxxxx` e a data, para a próxima passagem saber o que já foi conferido.
