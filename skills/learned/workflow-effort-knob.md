---
name: workflow-effort-knob
description: Pedido de "agente com modelo X e esforço máximo/alto" — a tool Agent só expõe model; o knob de reasoning effort vive no Workflow (agent(prompt, {model, effort})), legítimo até para agente ÚNICO quando o usuário pede a configuração explicitamente
metadata:
  pattern: project_specific
  origin: manual_estudo, pesquisa competitiva Anki com "sonnet esforço máximo" (26/07/2026)
  confidence: média-alta (usado uma vez, funcionou como esperado)
---

**O caso:** usuário pediu "crie um agente que pesquise usando o sonnet com esforço máximo". A tool `Agent` tem parâmetro `model` mas **não tem `effort`**.

**O padrão:** o knob de esforço existe no orquestrador `Workflow` — `agent(prompt, {model: 'sonnet', effort: 'max'})` (valores: low/medium/high/xhigh/max). Um **Workflow de agente único** é a forma correta de honrar o pedido literal; o pedido explícito do usuário pela configuração conta como opt-in de orquestração. Script mínimo:

```js
export const meta = { name: 'pesquisa-x', description: '...', phases: [{ title: 'Pesquisa' }] }
phase('Pesquisa')
return await agent(`...prompt completo e autocontido...`, {label: 'pesquisa-x', model: 'sonnet', effort: 'max'})
```

**Gotchas:** o resultado longo chega TRUNCADO na task-notification — o valor integral está em `<transcriptDir>/journal.jsonl` (linha `{"type":"result",...}`); extrair de lá antes de sintetizar. Declarar no prompt quais MCPs estão sem cota (Tavily/Consensus etc.) para o agente não queimar chamadas.
