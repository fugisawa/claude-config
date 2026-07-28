---
name: legislacao-br
description: >
  Mapa verificado de fontes de legislação, jurisprudência e dados públicos
  brasileiros — o que funciona por API, o que está bloqueado por WAF e o que
  responde metadado mas não texto. Use SEMPRE que a tarefa envolver buscar,
  citar ou conferir norma federal (CF/88, leis, LC, decretos, EC), acórdão ou
  súmula (TCU, STF, STJ, TST, CARF), publicação no DOU ou diário municipal,
  dados de Câmara/Senado/TCU/transparência — e também quando Daniel pedir
  "acha o artigo X da lei Y", "essa lei ainda está em vigor", "o que o TCU
  decidiu sobre Z", "cita a fonte oficial disso", ou estiver montando questão,
  flashcard ou discursiva que dependa de dispositivo legal. Consulte ANTES de
  tentar qualquer scraping de Planalto, LexML ou JusBrasil: eles estão
  bloqueados e este skill diz o que usar no lugar. NÃO use para o método de
  estudo (concurso-prep) nem para planejamento de cronograma
  (estrategista-concurso).
---

# Legislação e dados públicos brasileiros — mapa de fontes

**Regra de ouro:** nunca cite dispositivo legal de memória. Modelo de linguagem
alucina número de artigo com fluência. Ou você resolve a fonte por aqui, ou você
diz explicitamente que não conferiu.

## O que funciona (verificado ao vivo em 28/07/2026)

| Preciso de… | Use | Como |
|---|---|---|
| Acórdão/jurisprudência TCU, STF, STJ, TST, CARF | MCP `mcp-brasil` | `search_tools` → `call_tool` |
| Publicação no DOU ou diário municipal | MCP `mcp-brasil` | `diario_oficial_dou_buscar` → `dou_ler_publicacao` |
| Proposições, votações, comissões (Câmara/Senado) | MCP `mcp-brasil` | features `camara`, `senado` |
| Dados de transparência, TCEs, PNCP, licitações | MCP `mcp-brasil` | 40 features, use `search_tools` |
| URN canônica + ementa + link oficial de uma norma | `normas.leg.br/api/public/normas` | ver `referencias/consultar-norma.md` |
| **Texto** de lei federal | **Fonte local ou navegador** | ver "O buraco" abaixo |

O `mcp-brasil` expõe só 7 tools de entrada (`search_tools`, `call_tool`,
`listar_features`, `planejar_consulta`, `recomendar_tools`, `executar_lote`,
`listar_datasets_disponiveis`) e faz busca BM25 sobre ~533 tools internas.
Sempre comece por `search_tools` com a pergunta em português — não tente
adivinhar nome de tool.

## O buraco: não existe API pública de texto consolidado

Testei os quatro caminhos plausíveis. Todos falham, cada um do seu jeito:

| Fonte | O que acontece de fato |
|---|---|
| `planalto.gov.br` | WAF/bot-challenge. Sem exceção, sem contorno legítimo. |
| `lexml.gov.br` (SRU/OAI-PMH) | Devolve página "Verificação de segurança — Senado Federal". |
| `normas.leg.br` | Responde 200 e serve metadados ricos, mas o campo de texto vem **vazio**. A CF/88 traz 2.262 nós de estrutura com a URN de cada dispositivo e nenhum texto. |
| `mcp-brasil` / DOU | Serve o texto **como publicado** no diário, não o consolidado, e a busca privilegia publicações recentes. |

**Consequência prática:** para ler o texto de uma lei, o caminho é o corpus
local (PDFs e materiais do `manual_estudo`) ou abrir o Planalto no navegador
com `claude-in-chrome`. Não gaste tempo tentando automatizar por API — já foi
tentado e medido.

O que o `normas.leg.br` **resolve bem** é citação: dá a URN canônica
(`urn:lex:br:federal:lei.complementar:2000-05-04;101`), a ementa oficial, as
palavras-chave e a lista do que a norma revogou. Serve para conferir se você
está falando da norma certa e para citar com precisão — não para ler.

## Como responder quando pedirem um artigo

1. Resolva a norma pela URN e confirme ementa e data (`referencias/consultar-norma.md`).
2. Procure o texto no corpus local do Daniel antes de qualquer coisa:
   `rg -n "Art. 165" ~/manual_estudo/disciplinas/` e os PDFs em `pdf/`.
3. Se não houver, abra o Planalto no navegador via `claude-in-chrome` e leia.
4. Ao citar, inclua a URN ou o link oficial. Se não conferiu, **diga que não
   conferiu** — para quem estuda para concurso, um artigo inventado é pior que
   nenhum artigo.

## Cuidados

- **JusBrasil não tem API pública.** É contrato enterprise. O MCP não-oficial
  que existia saiu do ar; scraping ali viola os Termos de Uso. Alternativa com
  free tier: `jurisprudencias.ai`.
- **Querido Diário** direto está atrás de Cloudflare; via `mcp-brasil` funciona.
- Legislação estadual e municipal não está coberta por nada disso.

## Referências

- `referencias/consultar-norma.md` — como chamar a API de normas, com exemplos
  reais e o que cada campo entrega.
