---
name: pdf-print-quality-qa
description: "PDFs deste usuário são IMPRESSOS — QA visual caça cinco defeitos que nenhum validador textual pega: raster/pixelação, texto sobreposto (capas flex estouram), corte de borda (margens <10mm), meia página em branco por quebra fixa no código, e palavra partida por overflow-wrap anywhere"
metadata:
  pattern: user_corrections
  origin: manual_estudo, dossiê TCU (24/07/2026) — bronca do Daniel mid-turn
  confidence: alta (requisito explícito do usuário + 2 bugs reais pegos na mesma sessão)
---

**O caso:** dossiê editorial (briefing-designer) passou no validate.py e "parecia pronto",
mas a capa tinha texto sobreposto (RESUMO por cima do byline) e o gráfico dumbbell tinha
rótulo colidindo com nome de categoria. O usuário interrompeu para exigir: impressão em
papel de alta gramatura, modo normal/alta qualidade, sem pixelação, sem sobreposição, sem
corte de milímetros nas bordas.

**Os três defeitos a caçar no QA visual (ler o PNG SEMPRE, procurando isto):**
1. **Raster/pixelação:** conteúdo deve ser vetorial (texto WeasyPrint/Typst + SVG). Raster
   só se inevitável, e ≥300dpi. Gráfico: embutir o `.svg` do make_charts, nunca o PNG.
2. **Sobreposição de texto:** a capa do briefing-designer é flex com
   `.cover-abstract{margin-top:auto}` — quando deck+byline+abstract passam da altura A4,
   o abstract SOBE POR CIMA do byline (não gera página 2). Sintoma: rótulo "RESUMO"
   riscando texto. Fix: encurtar deck/byline/abstract e/ou `<style>` local reduzindo
   margens da capa. Análogo em gráficos: `dumbbell_chart(show_values=True)` colide o
   valor com o nome da categoria quando o mínimo encosta no eixo → `show_values=False`
   e valores na tabela do texto.
3. **Corte de borda:** margens <10mm arriscam corte em impressora comum (os 1-páginas de
   campanha usam 7-9mm — conferir a borda direita no PNG toda vez; design_system editorial
   usa 20-24mm, seguro).

**Dois defeitos a mais, medidos em 09/08/2026** — a mesma família (só o olho no PNG pega):

4. **Meia página em branco por quebra FIXA no código.** `#pagebreak()` (Typst) e
   `break-before` (CSS) escritos quando o texto era maior sobrevivem ao texto encolher, e aí
   cada seção acaba no meio da folha. Um guia de 3 páginas tinha as três pela metade e
   virou 2 páginas cheias só tirando as duas quebras. **A quebra é automática por padrão;
   fixá-la é decisão que precisa de motivo.** Se um título ficar órfão no pé da página
   depois disso, o conserto é agrupar título + primeiro bloco num contêiner não-quebrável,
   nunca voltar a quebrar à mão.
5. **`overflow-wrap: anywhere` parte palavra no meio.** Ele quebra em qualquer caractere,
   não só quando a palavra sozinha não cabe: saiu impresso `cl-asse 6`. Para célula estreita
   use `break-word`, que só age quando não há alternativa. E hifenização automática em
   coluna estreita com texto justificado é o cenário onde isso aparece.

**Um alerta que não é defeito:** o aviso "N páginas — comprima para 1" dos renderizadores
é esperado em documento multipágina e em folha desenhada para duplex. Não persiga.

**Como aplicar:** QA de PDF ≠ "dá pra ler?". É um checklist de impressão: vetorial? nada
sobreposto (zoom na capa e em cada figura)? borda direita/esquerda íntegra? **última página
cheia ou pela metade?** palavra partida em lugar impossível? Um validador textual
(validate.py) NÃO pega nenhum dos cinco — só o olho no PNG pega.
Memória-espelho no projeto: memory/impressao-qualidade-pdfs.md.
Relacionado: [[formato-de-revisao-nao-e-primeiro-contato]]
