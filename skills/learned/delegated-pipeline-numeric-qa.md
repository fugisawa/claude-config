---
name: delegated-pipeline-numeric-qa
description: Delegar pipeline de conversão/transcrição de documentos a agentes só funciona com contrato escrito (skill+conventions), auto-QA numérico (contagens como gabarito) e obrigação de reportar julgamentos — nunca inferir o que está só implícito
metadata:
  pattern: workarounds
  origin: manual_estudo, aulas IGEPP 02-03 em paralelo (19/07/2026)
  confidence: média-alta (2 agentes, 4 entregáveis, QA final limpo)
---

**O caso:** 2 agentes em paralelo converteram 2 aulas em PDF (27pp/16pp) + 2 decks de slides
(28pp/31pp) em MD+PDF limpos, com fidelidade verbatim, e o QA final do orquestrador passou
sem retrabalho.

**O que fez funcionar (padrão):**
1. **Contrato escrito antes de delegar:** o pipeline vivia num skill com CONVENTIONS.md
   (formato exato parseável) + um exemplar de referência pronto (aula-01). Agente lê os 3
   antes de tocar em arquivo.
2. **Auto-QA numérico com gabarito:** o diagnóstico (contact sheet) CONTA questões/diagramas/
   tabelas ANTES da autoria; a entrega só fecha quando `grep -c` no produto == contagem.
   Sem número-alvo, agente "acha que está completo".
3. **Regra de não-inferência explícita:** onde o original só IMPLICA a resposta (slides com
   destaque visual, sem gabarito escrito), o agente transcreve a evidência (destaques,
   fundamentação) e marca "não explícito" — nunca conclui por conta própria. Definir isso
   ANTES (inspecionando uma amostra do material) evita 27 gabaritos inventados.
4. **Julgamentos reportados, não silenciosos:** duplicatas no original, extensões de regra,
   correções mecânicas — tudo listado no relatório final para o dono validar. Dois agentes
   podem divergir num caso análogo (manter × fundir duplicata); com relatório, a divergência
   vira decisão do dono, não bug invisível.

**Como aplicar:** antes de delegar qualquer conversão em lote: (a) existe convenção escrita?
(b) qual é o número-gabarito do QA? (c) o que é inferível-mas-não-explícito e qual a regra?
(d) o prompt exige relatório de julgamentos? Faltou um dos 4 → fazer inline, não delegar.
