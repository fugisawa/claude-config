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
  tentar buscar norma ou acórdão: diz qual fonte responde hoje (Planalto voltou
  a funcionar por curl; jurisprudência STF/STJ/TST pelo mcp-brasil está
  quebrada) e as pegadinhas de extração. NÃO use para o método de
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
| Acórdão do **TCU**, CARF | MCP `mcp-brasil` | `search_tools` → `call_tool` |
| Jurisprudência **STF, STJ, TST** | ⚠️ `mcp-brasil` **quebrado** — use Exa/Tavily sobre `portal.stf.jus.br` e Buscador Dizer o Direito | ver "Jurisprudência" abaixo |
| Publicação no DOU ou diário municipal | MCP `mcp-brasil` | `diario_oficial_dou_buscar` → `dou_ler_publicacao` |
| Proposições, votações, comissões (Câmara/Senado) | MCP `mcp-brasil` | features `camara`, `senado` |
| Dados de transparência, TCEs, PNCP, licitações | MCP `mcp-brasil` | 40 features, use `search_tools` |
| URN canônica + ementa + link oficial de uma norma | `normas.leg.br/api/public/normas` | ver `referencias/consultar-norma.md` |
| **Texto** de lei federal | **Planalto por `curl` com User-Agent de navegador** | ver abaixo — voltou a funcionar |

## Planalto: funciona (reverificado em 01/08/2026)

A entrada anterior deste skill dizia que o `planalto.gov.br` estava bloqueado por
WAF. **Não está mais** — reverificado ao vivo em 01/08/2026: HTTP 200 para CF/88,
Lei 4.320, LC 101 e CTN. Basta mandar um User-Agent de navegador:

```bash
curl -sS -A "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36" \
  -o cf88.html "https://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm"
```

Duas pegadinhas ao processar:

- O HTML declara `charset=utf-8` mas há páginas servidas em **Latin-1** — tente
  `utf-8` e caia para `latin-1`, senão o texto sai corrompido.
- O texto **compilado** traz as redações revogadas empilhadas junto com a
  vigente, na ordem cronológica. Ao extrair um dispositivo alterado por EC, a
  **última** ocorrência é a vigente — pegar a primeira devolve texto revogado.
  (Ex.: o art. 167, IV da CF aparece quatro vezes; só a quarta, da EC 42/2003,
  vale.)

Extraia com `beautifulsoup4` + `lxml`, não com regex sobre o HTML.

## Jurisprudência STF/STJ/TST: o `mcp-brasil` está quebrado (01/08/2026)

O módulo `jurisprudencia` do `mcp-brasil` chama endpoints internos dos tribunais
obtidos por engenharia reversa, e os três colocaram proteção anti-bot na frente
deles: STF devolve 202 com `x-amzn-waf-action: challenge`, STJ devolve 403 do
Cloudflare, TST devolve 503. Como o cliente embrulha tudo em `except: return []`,
**a falha aparece como "nenhum resultado", não como erro** — não gaste tempo
reformulando a query. As features `tcu` e `dou` do mesmo MCP seguem normais.

Rota que funciona: Exa/Tavily sobre `portal.stf.jus.br` (a seção "A Constituição
e o Supremo" é curadoria oficial por artigo), `buscadordizerodireito.com.br`,
`noticias.stf.jus.br`, e a busca de súmulas em
`portal.stf.jus.br/jurisprudencia/sumariosumulas.asp`.

Pacote: `mcp-brasil` 0.14.0 (PyPI), código em `github.com/Mcp-Brasil/mcp-brasil`.
Reportado upstream: [issue #26](https://github.com/Mcp-Brasil/mcp-brasil/issues/26)
— checar se foi corrigido antes de tentar de novo. Possível saída melhor que
reverse-engineering: a feature `datajud` do próprio mcp-brasil (API oficial do
CNJ, cobre STF/STJ/TST) está hoje pulada só por faltar `DATAJUD_API_KEY` — vale
pedir a chave gratuita ao CNJ se isso virar dor recorrente.

O `mcp-brasil` expõe só 7 tools de entrada (`search_tools`, `call_tool`,
`listar_features`, `planejar_consulta`, `recomendar_tools`, `executar_lote`,
`listar_datasets_disponiveis`) e faz busca BM25 sobre ~533 tools internas.
Sempre comece por `search_tools` com a pergunta em português — não tente
adivinhar nome de tool.

## Não existe **API** pública de texto consolidado — mas há o HTML do Planalto

Continua não havendo API que sirva texto consolidado. O que mudou (01/08/2026) é
que o HTML do Planalto voltou a ser acessível, e é por ele que se lê a norma:

| Fonte | O que acontece de fato |
|---|---|
| `planalto.gov.br` | **HTTP 200** com User-Agent de navegador (reverificado 01/08/2026; antes devolvia bot-challenge). É a rota boa — ver seção acima. |
| `lexml.gov.br` (SRU/OAI-PMH) | Devolve página "Verificação de segurança — Senado Federal". |
| `normas.leg.br` | Responde 200 e serve metadados ricos, mas o campo de texto vem **vazio**. A CF/88 traz 2.262 nós de estrutura com a URN de cada dispositivo e nenhum texto. |
| `mcp-brasil` / DOU | Serve o texto **como publicado** no diário, não o consolidado, e a busca privilegia publicações recentes. |

**Consequência prática:** para ler o texto de uma lei, primeiro o `curl` no
Planalto; depois o corpus local (PDFs e materiais do `manual_estudo`); o
navegador via `claude-in-chrome` virou plano C, não plano A.

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
