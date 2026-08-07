---
name: subagent-attribution-drift
description: Relatório de subagente erra por ATRIBUIÇÃO mais que por invenção — o fato existe, mas colado no sujeito errado; conferir pessoalmente toda afirmação que vá virar decisão de arquitetura ou linha de skill
metadata:
  pattern: error_resolution
  origin: manual_estudo, pesquisa de prior art do vade mecum, sessão 07/08/2026
  confidence: alta (3 de 3 afirmações checadas estavam erradas, todas plausíveis)
---

**O caso:** um agente de pesquisa entregou relatório denso e útil sobre extração de legislação. Três
afirmações de alto impacto, conferidas por mim antes de virarem código:

1. *"`normas.leg.br` manda `Last-Modified` e responde 304 a `If-Modified-Since`"* — **inverso**. Quem
   manda `ETag`/`Last-Modified` e responde 304 é o **Planalto**; o endpoint de binário do
   `normas.leg.br` não manda nenhum dos dois. O agente mediu no host A e escreveu no host B.
2. *"a anotação `(Revogado…)` fica DENTRO do `<strike>`, então remover o riscado apaga o registro"* —
   medido: fica **fora** em 72 dos 77 casos na CF/88.
3. *"âncora com ponto final (`name="art6."`) é versão histórica, use para descartar"* — o `art6.` da
   CF traz o texto **vigente**, e a âncora sem ponto também existe. Heurística de descarte que
   apagaria texto bom.

**O padrão:** o erro típico não é alucinação — é **deriva de atribuição**. O fato é real, a medição
foi feita, e na hora de escrever o sujeito trocou: host A vira host B, "fora" vira "dentro", a
exceção vira a regra. Isso é muito mais difícil de pegar que invenção pura, porque tudo soa
plausível e o relatório é internamente coerente.

**Como aplicar:**
- Toda afirmação de subagente que vá virar **decisão de arquitetura, regra de parser ou linha de
  skill** é hipótese até você rodar. O custo de conferir aqui foi um `curl -I` por item.
- Priorize a conferência pelo que é caro se errado: afirmação que fecha uma rota, que define
  heurística de descarte, ou que entra em documento que outros vão ler como fato.
- Suspeite especialmente de afirmação com **sujeito trocável** — "a fonte X manda o header Y" quando
  o relatório fala de duas fontes; "o marcador Z fica dentro/fora" quando há duas convenções.
- O agente pode ser honesto sobre isso: o meu declarou "verifiquei pessoalmente as de maior impacto;
  não reexecutei cada item da tabela". Essa ressalva é o mapa de onde conferir.
