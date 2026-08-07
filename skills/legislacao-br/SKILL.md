---
name: legislacao-br
description: >
  Mapa verificado de fontes de legislação, jurisprudência e dados públicos
  brasileiros — como obter o TEXTO CONSOLIDADO de uma norma federal, o que
  responde só metadado e o que está bloqueado. Use SEMPRE que a tarefa envolver
  buscar, citar ou conferir norma federal (CF/88, leis, LC, decretos, EC),
  acórdão ou súmula (TCU, STF, STJ, TST, CARF), publicação no DOU ou diário
  municipal, dados de Câmara/Senado/TCU/transparência — e também quando Daniel
  pedir "acha o artigo X da lei Y", "essa lei ainda está em vigor", "o que o TCU
  decidiu sobre Z", "cita a fonte oficial disso", ou estiver montando questão,
  flashcard, vade mecum ou discursiva que dependa de dispositivo legal. Consulte
  ANTES de tentar buscar norma ou acórdão: diz qual fonte serve texto limpo hoje,
  qual responde só metadado, qual está quebrada, e as armadilhas de extração de
  cada uma. NÃO use para o método de estudo (concurso-prep) nem para planejamento
  de cronograma (estrategista-concurso).
---

# Legislação e dados públicos brasileiros — mapa de fontes

**Regra de ouro:** nunca cite dispositivo legal de memória. Modelo de linguagem
alucina número de artigo com fluência. Ou você resolve a fonte por aqui, ou você
diz explicitamente que não conferiu.

## O que funciona

Texto consolidado e Planalto reverificados ao vivo em **07/08/2026**;
jurisprudência e DOU, em **01/08/2026**. Cada seção abaixo repete a sua data —
quando divergirem, vale a da seção, que é onde o teste foi feito.

| Preciso de… | Use | Como |
|---|---|---|
| **Texto consolidado** de norma federal | `normas.leg.br`, encoding **Compilação Monovigente** | plano A — ver `referencias/consultar-norma.md` |
| Texto quando não há Monovigente | **Planalto por `curl` com User-Agent de navegador** | plano B — ver abaixo, exige separar o riscado |
| URN canônica + ementa + link oficial de uma norma | `normas.leg.br/api/public/normas` | idem |
| Acórdão do **TCU**, CARF | MCP `mcp-brasil` | `search_tools` → `call_tool` |
| Jurisprudência **STF, STJ, TST** | ⚠️ `mcp-brasil` **quebrado** — use Exa/Tavily sobre `portal.stf.jus.br` e Buscador Dizer o Direito | ver "Jurisprudência" abaixo |
| Publicação no DOU ou diário municipal | MCP `mcp-brasil` | `diario_oficial_dou_buscar` → `dou_ler_publicacao` |
| Proposições, votações, comissões (Câmara/Senado) | MCP `mcp-brasil` | features `camara`, `senado` |
| Dados de transparência, TCEs, PNCP, licitações | MCP `mcp-brasil` | 40 features, use `search_tools` |

## Planalto: funciona (reverificado em 07/08/2026)

A entrada anterior deste skill dizia que o `planalto.gov.br` estava bloqueado por
WAF. **Não está mais** — HTTP 200 em 01/08/2026 para CF/88, Lei 4.320, LC 101 e
CTN, e de novo em 07/08/2026 para CF/88 (1,8 MB) e Lei 14.133 (649 KB). Basta
mandar um User-Agent de navegador:

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

O `mcp-brasil` expõe 7 tools de entrada (`search_tools`, `call_tool`,
`listar_features`, `planejar_consulta`, `recomendar_tools`, `executar_lote`,
`listar_datasets_disponiveis`) e faz busca BM25 sobre ~435 tools internas.
Sempre comece por `search_tools` com a pergunta em português — não tente
adivinhar nome de tool. Ele **não serve texto de lei**: Câmara e Senado
devolvem URL do inteiro teor, não conteúdo; o DOU serve o texto *como
publicado*, sem consolidar alterações posteriores.

## Como obter o texto de uma lei

Três passos, nessa ordem. O detalhe de cada um está em
`referencias/consultar-norma.md`.

1. **Resolva a URN** e busque os metadados em `normas.leg.br` — o endpoint
   exige `&tipo_documento=maior-detalhe`, senão devolve `400 Bad Request`.
2. **Escolha a versão `Current`** em `encoding[]` — aparece com o nome
   "Compilação Monovigente", texto vigente já consolidado, sem riscado.
   **Corrija o path:** o `contentUrl` anunciado responde 404; insira
   `/public/` e mantenha o sufixo `/texto`:
   `/api/binario/<uuid>/texto` → `/api/public/binario/<uuid>/texto`.
3. **Se não houver Monovigente, caia para o Planalto** e limpe o texto riscado.

Verificado ao vivo em 07/08/2026 com a CF/88: o `encoding[]` traz 4 entradas
(Publicação Original, Monovigente, e as duas traduções), o path anunciado dá
404 e o corrigido devolve **HTTP 200 com 962 KB**.

### Por que este skill já disse o contrário

A versão de 01/08 concluía que "não existe API de texto consolidado — o campo de
texto vem vazio". A observação estava certa e a conclusão não: o vazio é do campo
de texto **nos metadados** (a CF/88 traz 2.262 nós de estrutura com a URN de cada
dispositivo e nenhum texto). O texto vive noutro lugar — no binário de
`encoding[]` — e o `contentUrl` que os metadados anunciam para ele está errado.
Quem testasse só o caminho anunciado veria 404 e concluiria que não há texto.

| Fonte | O que acontece de fato |
|---|---|
| `normas.leg.br` binário | **Plano A.** Monovigente = consolidado, sem riscado. Path anunciado 404; ver acima. |
| `planalto.gov.br` | **Plano B.** HTTP 200 com User-Agent de navegador (reverificado 07/08/2026; antes devolvia bot-challenge). Exige separar redação vigente da revogada — ver seção acima. |
| `normas.leg.br` metadados | URN, ementa, datas, estrutura. **Não** serve texto. |
| `lexml.gov.br` (SRU/OAI-PMH) | Devolve página "Verificação de segurança — Senado Federal". |
| `mcp-brasil` / DOU | Serve o texto **como publicado** no diário, não o consolidado, e a busca privilegia publicações recentes. |

**Consequência prática:** para ler o texto de uma lei, primeiro o binário
Monovigente; se não houver, o `curl` no Planalto; depois o corpus local (PDFs e
materiais do `manual_estudo`); o navegador via `claude-in-chrome` é plano D.

### O buraco que importa

Nem toda norma tem `Current`. Medido em 07/08/2026: têm CF/88, Lei 4.320,
LC 101 (LRF), Lei 8.443 (LOTCU), Lei 8.429, Lei 9.784, Lei 12.527 (LAI) e
Lei 13.709 (LGPD). **Não têm: Lei 14.133/2021 e LC 200/2023** — só `Original` e
`Intermediate`, esta última um aviso de veto de poucos KB.

Isso é uma armadilha silenciosa: pegar `encoding[0]` ou "a última entrada"
devolve texto original de 2021 ou um stub de veto, com cara de sucesso.
**Falhe alto** quando não houver `Current` — nunca emita o que veio no lugar.

## Detectar que uma norma mudou

- **Planalto** manda `ETag` e `Last-Modified`; `If-Modified-Since` devolve
  **304 com 0 bytes**. É o caminho barato para revalidar em lote.
- **`normas.leg.br` não manda `ETag` nem `Last-Modified`** no endpoint de
  binário — só `Content-Length`. Ali, compare **hash do conteúdo**.
- `dateModified` nos metadados vem `None`: **não sirva esse campo como prova
  de que uma lei está em vigor.**

## Como responder quando pedirem um artigo

1. Resolva a norma pela URN e confirme ementa e data.
2. Baixe o texto `Current` (ou o fallback do Planalto) e **leia o dispositivo
   ali** — não de memória, não de material de cursinho.
3. Ao citar, inclua a URN ou o link oficial **e a data em que você conferiu**.
4. Se não conferiu, **diga que não conferiu**. Para quem estuda para concurso,
   um artigo inventado é pior que nenhum artigo.

Material de cursinho envelhece em silêncio e é a fonte de erro mais comum:
um vade mecum de 2021 ainda ensina "menos de sessenta e cinco anos" no
art. 73, §1º, I da CF — a EC 122/2022 mudou para setenta.

## Cuidados

- **Legislação estadual e municipal não está coberta por nada disso.**
- **JusBrasil não tem API pública.** É contrato enterprise; scraping viola os
  Termos de Uso. Alternativa com free tier: `jurisprudencias.ai`.
- **Querido Diário** direto está atrás de Cloudflare; via `mcp-brasil` funciona.
- **LexML SRU/OAI-PMH** (`lexml.gov.br/busca/SRU`) está atrás de verificação de
  segurança do Senado, e o `robots.txt` faz `Disallow: /busca/`. Não insista —
  o que você queria dali (URN) o `normas.leg.br` já dá.
- **Redistribuir texto de lei é seguro:** `normas.leg.br` declara CC-BY-4.0, e a
  Lei 9.610/98, art. 8º, IV, exclui leis e atos oficiais de proteção autoral.

## Referências

- `referencias/consultar-norma.md` — chamadas reais, seleção de versão, o path
  fix, a receita do fallback Planalto e os limites medidos.
