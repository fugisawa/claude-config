# Consultar uma norma em normas.leg.br

Endpoint único, sem chave, sem autenticação:

```
GET https://normas.leg.br/api/public/normas?urn=<URN>&tipo_documento=maior-detalhe
Accept: application/json
```

## Montar a URN

Padrão LexML: `urn:lex:br:federal:<tipo>:<AAAA-MM-DD>;<numero>`

| Norma | URN |
|---|---|
| CF/88 | `urn:lex:br:federal:constituicao:1988-10-05;1988` |
| Lei 4.320/64 | `urn:lex:br:federal:lei:1964-03-17;4320` |
| LRF (LC 101/00) | `urn:lex:br:federal:lei.complementar:2000-05-04;101` |
| LC 200/2023 (arcabouço) | `urn:lex:br:federal:lei.complementar:2023-08-30;200` |
| Lei 8.112/90 | `urn:lex:br:federal:lei:1990-12-11;8112` |
| Lei 14.133/21 | `urn:lex:br:federal:lei:2021-04-01;14133` |
| Lei 8.429/92 | `urn:lex:br:federal:lei:1992-06-02;8429` |
| Lei 9.784/99 | `urn:lex:br:federal:lei:1999-01-29;9784` |
| Lei 8.443/92 (LO do TCU) | `urn:lex:br:federal:lei:1992-07-16;8443` |
| Lei 12.527/11 (LAI) | `urn:lex:br:federal:lei:2011-11-18;12527` |
| Lei 13.709/18 (LGPD) | `urn:lex:br:federal:lei:2018-08-14;13709` |

A data é a de **assinatura**, não a de publicação. Errar a data devolve 404 — se
acontecer, confira a data no `mcp-brasil` (feature `senado` ou `camara`).

## Pegar o texto consolidado — as duas armadilhas

O texto vive em `encoding[]`, e **duas coisas dão errado em silêncio**:

**1. O `contentUrl` anunciado responde 404.** Falta `/public/` no caminho:

```
anunciado → https://normas.leg.br/api/binario/<uuid>/texto          # 404
correto   → https://normas.leg.br/api/public/binario/<uuid>/texto   # 200
```

**2. Há mais de uma entrada `Current`.** Na CF/88 são três: português, inglês e
francês. Pegar "a última" devolve a Constituição em francês. Filtre pelo nome:

```python
def escolher(encodings):
    for e in encodings:
        if e.get("version") == "Current" and "Traduzida" not in (e.get("name") or ""):
            return e["contentUrl"].replace("/api/binario/", "/api/public/binario/")
    return None   # sem Current — vá para o Planalto, NUNCA use Original no lugar
```

O que volta é HTML limpo, UTF-8, **zero tags de riscado**, com as anotações de
alteração ancoradas na unidade certa — melhor que o Planalto nesse ponto:

```
(Inciso com redação dada pela Lei nº 9.165, de 19/12/1995)
(Parágrafo acrescido pela Lei nº 13.866, de 26/8/2019)
```

**Normalize o espaço em branco antes de procurar artigo.** O rótulo vem em span
próprio (`<span>Art.</span><span> 1º …`), então trocar tag por espaço produz
`"Art.  1º"` com dois espaços. Um `Art\.\s?\d` acha **zero** artigos na CF/88;
depois de `re.sub(r'\s+',' ',txt)`, acha os 276 corretos. Falha silenciosa
clássica: o download deu certo, a contagem deu zero.

## Quando NÃO há `Current`

Medido em 07/08/2026 — **têm** `Current`: CF/88, Lei 4.320, LC 101, Lei 8.443,
Lei 8.429, Lei 9.784, Lei 12.527, Lei 13.709. **Não têm**: Lei 14.133/2021 e
LC 200/2023, que expõem só `Original` e `Intermediate` (esta é um aviso de veto
de poucos KB).

Falhe alto. Emitir `Original` no lugar entrega texto de 2021 com aparência de
sucesso — exatamente o erro que este skill existe para evitar.

## Fallback: Planalto

`https://www.planalto.gov.br/ccivil_03/...` responde 200 com User-Agent de
browser. Regras medidas em 07/08/2026 (CF/88, Lei 8.443, Lei 14.133):

- **Decodifique como `latin-1`.** O `<meta charset>` da página mente; o byte
  0xea quebra UTF-8 já na posição 475 da Lei 8.443.
- **Texto superado vem embutido na página**, marcado de duas formas: `<strike>`
  (dominante — 773 na CF/88, 44 na 14.133) e `style="line-through"` (raro mas
  real — 12 na 14.133, 7 na CF/88). Trate as duas. `<s>` não apareceu.
- **Os stubs de revogação sobrevivem à limpeza.** Em 72 dos 77 casos na CF/88, a
  anotação `(Revogado…)` está *fora* do riscado — o padrão `a) (Revogada)` é
  texto vivo. Remover o riscado não apaga o registro.
- **Âncora com ponto final não é versão histórica.** `name="art6."` traz o texto
  vigente do art. 6º, e a âncora sem ponto também existe. Não use isso como
  heurística de descarte.
- As âncoras batem com o fragmento da URN: `#art37i` ↔ `…;1988!art37i`.

## Detectar que a norma mudou

| Fonte | `Last-Modified` / `ETag` | Como revalidar |
|---|---|---|
| **Planalto** | sim, ambos | `If-Modified-Since` → **304, 0 bytes** |
| **normas.leg.br** (binário) | **não manda nenhum dos dois** | comparar hash do conteúdo |

`dateModified` nos metadados vem `None` — **não sirva esse campo como prova de
vigência.**

## Outros limites

- `hasPart` (árvore de dispositivos) aparece em poucas normas, e onde aparece os
  nós trazem URN mas **`text` vazio** — serve para endereçar, não para ler.
  *(medido em 28/07/2026, não reconferido em 07/08.)*
- `legislationRepeals` lista o que **esta** norma revogou, não o inverso.
- `keywords` traz a indexação temática oficial — boa fonte de termos de busca.

## Verificar se ainda vale

Este mapa é uma medição datada, não uma garantia. Se algo aqui falhar, refaça o
teste e atualize o arquivo com a data nova. A medição anterior (28/07/2026)
dava o Planalto como bloqueado por WAF e o `normas.leg.br` como sem texto —
ambas caíram em 07/08/2026, uma por mudança da fonte, outra por erro de
diagnóstico (o 404 era path malformado, não ausência de texto).
