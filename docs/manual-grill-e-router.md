# Manual — grill, modelagem de domínio e o router `/ask-daniel`

## A ideia em 30 segundos

O modo de falha nº 1 com agentes é **desalinhamento**: você acha que o agente entendeu; ele constrói; não era aquilo. O antídoto é inverter o fluxo — antes de construir, o agente **te entrevista** (grilling) até haver entendimento compartilhado. E, enquanto isso acontece, as decisões e o vocabulário do projeto são **escritos na hora** (CONTEXT.md + ADRs), para que as próximas sessões comecem sabendo o que esta aprendeu. O router `/ask-daniel` é o mapa de qual ferramenta usar em cada situação.

## As peças

| Skill | O que faz | Como dispara |
|---|---|---|
| `grilling` | O primitivo: entrevista implacável, **uma pergunta por vez**, cada uma com resposta recomendada | Sozinha, ao dizer "grill"/"me grile" — ou via wrappers abaixo |
| `/grill-me` | Grilling puro, sem docs | Você digita. Para trabalho **sem codebase**: planos, textos, decisões |
| `/grill-with-docs` | Grilling + modelagem de domínio: atualiza `CONTEXT.md` e oferece ADRs conforme decisões cristalizam | Você digita. Para trabalho **com codebase** — é o que deixa rastro |
| `domain-modeling` | A disciplina ativa: desafiar termos vagos, testar cenários-limite, cruzar fala × código, escrever o glossário na hora | Chamada pelo grill-with-docs; ou sozinha ("registre essa decisão como ADR") |
| `codebase-design` | Vocabulário de design: module, interface, **seam**, depth, leverage, locality | Ao projetar/refatorar interfaces de módulos |
| `/ask-daniel` | Router do acervo: qual skill/agente/comando usar, e quem vence quando acervos colidem | Você digita |

## Como se comporta uma sessão de grill

1. Você traz a ideia ("quero adicionar backtest walk-forward no wc2026") e digita `/grill-with-docs` (ou `/grill-me` se não há código).
2. O agente pergunta **uma coisa por vez**, sempre com a resposta que ele recomenda. Você pode: aceitar, corrigir, ou mandar ele descobrir sozinho ("explora o código e me diz").
3. Perguntas que o código responde não são feitas a você — ele explora antes.
4. Quando um termo vago aparece ("conta", "sync", "potencializador"), ele propõe o termo canônico e grava no `CONTEXT.md` **na hora**, não no final.
5. Quando uma decisão difícil de reverter é tomada por um trade-off real, ele oferece um ADR (1–3 frases).
6. A sessão termina quando não resta pergunta aberta — não quando a paciência acaba. Se quiser encerrar antes, diga; o que ficou aberto fica registrado.

**Dica**: quanto mais você discordar das recomendações, melhor o resultado — o grill existe para extrair o que só você sabe.

## O fluxo completo (ideia → código)

```
ideia ──► /grill-with-docs ──► /ultraplan ──► implementar (TDD) ──► revisar ──► entregar
              │                    │                │                  │
        CONTEXT.md + ADRs    seams + user     sessão FRESCA      /code-review ou
        (rastro durável)     stories + fatias  por fatia;         agente code-reviewer
                             verticais         red→green          (Standards × Spec)
```

- **Alinhamento e plano na mesma janela de contexto** — não compacte nem limpe entre o grill e o plano; um alimenta o outro.
- **Implementação em sessão nova por fatia** — cada tracer bullet do plano é autocontido; contexto fresco raciocina melhor. O `CONTEXT.md` garante que a sessão nova fala a língua do projeto.
- Trabalho pequeno pode pular o `/ultraplan` e ir do grill direto à implementação.
- Revisão e verificação: `/code-review` no diff; `/verify` exercita o fluxo de verdade; o hook de guardrail impede git destrutivo no caminho.

## CONTEXT.md e ADRs — as regras que importam

**CONTEXT.md** (raiz do repo) é **só glossário**, nunca spec ou rascunho:

```md
**Fatia**: janela de treino/teste no walk-forward.
_Evitar_: fold, split, janela
```

- Opinativo: um termo canônico, os sinônimos em `_Evitar_`.
- Só conceitos do domínio do projeto — nada de conceitos genéricos de programação.
- Criado preguiçosamente: só quando o primeiro termo é resolvido.

**ADRs** (`docs/adr/0001-slug.md`) têm filtro triplo — só existem se as **três** valem:
1. difícil de reverter; 2. surpreendente sem contexto; 3. resultado de trade-off real.

Formato mínimo: título + 1–3 frases (contexto, decisão, porquê). O valor é registrar **que** se decidiu e **por quê** — não preencher seções. ADRs impedem que a mesma discussão volte em seis meses.

**Payoff acumulado**: conversas mais curtas ("o problema é na cascata de materialização" em vez de três linhas), nomes consistentes no código, e decisões que não são re-litigadas.

## /ask-daniel — o router

**Quando usar**: na dúvida sobre qual skill/agente/comando aplicar, ou quando dois acervos parecem cobrir a mesma coisa (temos 5: próprios, superpowers, ECC, nativos, vendored).

**Como usar**: digite `/ask-daniel` seguido da situação —

```
/ask-daniel quero revisar o diff dessa branch
/ask-daniel bug intermitente no streamlit, só acontece às vezes
/ask-daniel preciso de um PDF de briefing sobre data centers
```

O agente consulta o mapa (fluxo principal, debug, design, pesquisa, domínios seus, meta) e as **regras de precedência** (ex.: debug comum → superpowers auto; bug difícil → `/diagnosing-bugs` à mão; pesquisa profunda → `/deep-research`).

**Regra de manutenção**: ao criar/renomear/remover skill user-reachable, atualize `skills/ask-daniel/SKILL.md` na mesma mudança — um router desatualizado mente, e mentira de router custa mais que ausência de router.

## Anti-padrões

- **Grill em pergunta trivial** — se a tarefa cabe numa frase sem ambiguidade, só peça. Grill é para quando o custo de construir errado supera o custo de 10 perguntas.
- **CONTEXT.md como spec** — se tem detalhe de implementação, está errado; corte para o glossário puro.
- **ADR para tudo** — decisão reversível e óbvia não gera ADR; gera ruído que enterra os ADRs que importam.
- **Compactar no meio do grill→plano** — quebra o fio; se a janela apertar (~120k), peça um handoff explícito e continue em sessão nova.
- **Dois acervos na mesma tarefa** (dois TDDs, dois fluxos de review) — consulte o router e escolha um.
