# Ferramentas de registro (modo Ferramentas)

Sumário: Princípio · Via 1 Obsidian · Via 2 Google Calendar · Via 3 Planner imprimível · Via 4 Web app tracker

## Princípio

Todas as vias produzem o **mesmo bloco canônico** de metricas-e-checkin.md — leia-o antes de gerar qualquer uma. A ferramenta é a ponte entre a semana vivida e o check-in na conversa: se ela não desemboca no bloco, não serve. Gere sob demanda; confirme só as preferências mínimas antes (não interrogar). O tracker emocional é sempre **verde/piso/cinza por presença**, nunca por horas.

## Via 1 — Template Obsidian

Nota semanal `Check-in YYYY-WW.md`:

- **Frontmatter** (para Dataview futuro): `semana`, `verdes`, `pisos`, `horas`, `questoes`, `acerto`, `animo`, `cor_regua`.
- **Corpo**: o bloco canônico em code block (preenchível) + tabela seg–dom com colunas *verde/piso/cinza · assunto do dia · onde parei / próxima ação · linha de resultado* (a linha diária de "o que a sessão produziu" — é a evidência acumulada de que o esforço converte).
- Sugerir pasta no LifeOS dele: `1-Projetos/Concurso-2027/Check-ins/` — o portfólio tem dois alvos, e nome de um só envelhece na primeira mudança. Se ele pedir Dataview, dashboards ou reorganização de vault, leia o skill **obsidian-note** e siga as convenções de lá.
- Entregar o template pronto para colar + 1 exemplo preenchido **marcado como fictício**.

## Via 2 — Google Calendar

Criar os blocos da semana-modelo como eventos recorrentes via `Google Calendar:create_event`, em fluxo **plan-validate-execute**:

1. **Confirmar as janelas atuais** (treinos/yoga podem ter mudado — perfil-e-janelas.md) e quais blocos ele quer na agenda.
2. **Listar a proposta** antes de criar: título, dias (RRULE), horário, lembrete. Sugestão mínima: Bloco Pico (seg–sex 6h10), Questões·Sala (2×, horários dele), Anki Noite (19h45), Discursiva (dom 8h), Check-in (dom 11h30). Lembrete popup 10 min.
3. **Criar só após confirmação explícita**, um evento recorrente por bloco; reportar o que foi criado.

Nunca criar/alterar eventos sem a lista aprovada. Alterações posteriores: mesmo fluxo.

## Via 3 — Planner imprimível

PDF A5, uma semana por par de páginas: tracker verde/piso/cinza da semana, campos do bloco canônico, coluna "onde parei / próxima ação", os se-então essenciais na contracapa (colar à altura dos olhos). ⚠ **Antes de propor esta via, saiba que ela já existe:** o `Planner-Pessoal-Daniel.pdf` (A5, 6pp) está entregue desde 28/07/2026, e o sistema de design dele é **Typst, Lato, cantos retos, paleta CMYK fria** — fontes em `~/manual_estudo/planner-pessoal/`. Construir do zero produziria um planner que não combina com o que está na mesa. Só proponha mudança **incremental** sobre aquele, e a produção é `render.py` do próprio diretório, não pipeline novo.

## Via 4 — Web app tracker (artifact)

Página autocontida publicada pela ferramenta `Artifact`. ⚠ Aqui vale a política estrita do Claude Code: nada de recurso externo (tudo embutido), e **qualquer estado que persista ou seja compartilhado exige declarar capacidade de tempo de execução** — leia a skill `artifact-capabilities` ANTES de escrever o código, porque as instruções do gêmeo web (`window.storage`) não valem neste ambiente:

- **Chave**: `week:YYYY-WW` → um objeto único por semana (dias com estado verde/piso/cinza, horas, blocos do plano — concluídos/planejados/adiados —, questões, acertos por disciplina, Anki, discursiva, erros por tipo, ânimo, alertas, eventos). Um objeto por semana evita chamadas múltiplas de storage.
- **UI mínima**: grade seg–dom (toque alterna verde → piso → cinza), campos numéricos compactos, seletor de semana, e o essencial — **botão "Copiar check-in"** que serializa a semana no bloco canônico exato, pronto para colar na conversa. É a ponte com o skill sem estado.
- Storage pessoal (`shared=false`); try/catch em toda operação; chave inexistente lança erro (tratar como semana nova).
- Antes de construir, leia `artifact-design`; estética coerente com o planner que já existe (Lato, cantos retos, paleta fria).
