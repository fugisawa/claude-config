---
description: Deep planning mode — research-first, sequential-thinking, auto-orchestrates agents/skills/MCPs, produces a phased plan before any code
argument-hint: <o objetivo a planejar>
---

# /ultraplan — plano profundo + auto-orquestração

Modo de planejamento profundo. **Pesquisa antes de desenhar, raciocina com sequential-thinking, instancia automaticamente os agentes/skills/MCPs certos, e entrega um plano em fases — sem escrever código até eu aprovar.**

Objetivo a planejar: **$ARGUMENTS**

## Processo

1. **Enquadrar.** Reafirme objetivo, restrições e critérios de sucesso. Liste premissas e incógnitas explicitamente. Se algo essencial estiver ambíguo, pergunte **antes** de planejar.

2. **Raciocinar fundo.** Use o MCP `sequential-thinking` na parte difícil (decomposição, trade-offs, ordem de ataque).

3. **Pesquisa-primeiro (obrigatório, antes de desenhar).** Antes de inventar solução nova:
   - `gh search repos` / `gh search code` por implementações existentes;
   - `exa` e `tavily` para prior art, padrões e dados;
   - `context7` para a doc **atual** de qualquer lib/framework/SDK em jogo;
   - registries (npm/PyPI/crates) por libs battle-tested.
   Prefira **adotar/portar** algo provado a escrever do zero.

4. **Auto-orquestrar (sem eu pedir).** Instancie o que ajudar:
   - **Skills** relevantes ao contexto (ex.: `forecasting-calibration`, `streamlit-apps`, `dataviz-storytelling`, `langchain-stack`, `senior-data-scientist`, `training-protocol`, `concurso-prep`);
   - **Subagentes em paralelo** para pesquisa/análise independentes (Task);
   - **MCPs** úteis (exa, tavily, context7, playwright).

5. **Seams de teste (antes de fechar o plano).** Esboce os *seams* — as fronteiras públicas onde a feature será testada. Prefira seams existentes a novos; prefira o seam mais alto possível (o ideal é um só). Confirme comigo que os seams batem com a expectativa antes de detalhar as tarefas.

6. **Plano em fases.** Entregue: objetivo + critérios; 2–3 abordagens com prós/contras → recomendação justificada; riscos + mitigação; plano a nível de arquivo (o que muda onde); **user stories numeradas** ("Como <ator>, quero <feature>, para <benefício>") cobrindo todos os aspectos; **decisões de implementação** (módulos/interfaces afetados, schema, contratos — sem paths de arquivo nem snippets, que envelhecem rápido); **decisões de teste** (quais módulos, em quais seams, prior art de testes similares no codebase); **fora de escopo** explícito.

7. **Quebra em tracer bullets.** Divida em tarefas que sejam **fatias verticais** — cada uma atravessa todas as camadas de ponta a ponta (schema → lógica → UI → teste) e é demoável/verificável sozinha — nunca fatias horizontais de uma camada só. Marque dependências ("bloqueada por"). Prefactoring vem primeiro: "torne a mudança fácil, depois faça a mudança fácil".

8. **Parar para aprovação.** Apresente o plano e **aguarde o "ok" antes de implementar** — a menos que eu já tenha dito para seguir direto.

Respeite minhas regras: pesquisa-e-reuso antes de código novo; TDD; imutabilidade; arquivos pequenos e focados.
