---
name: pdf-print-quality-qa
description: PDFs deste usuário são IMPRESSOS (papel de alta gramatura) — QA visual deve caçar ativamente três defeitos: raster/pixelação, texto sobreposto (capas flex estouram) e corte de borda (margens <10mm); legibilidade em tela não basta
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

**Como aplicar:** QA de PDF ≠ "dá pra ler?". É um checklist de impressão: vetorial? nada
sobreposto (zoom na capa e em cada figura)? borda direita/esquerda íntegra? Um validador
textual (validate.py) NÃO pega nenhum dos três — só o olho no PNG pega.
Memória-espelho no projeto: memory/impressao-qualidade-pdfs.md.
