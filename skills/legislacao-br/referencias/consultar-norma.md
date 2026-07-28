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
| Lei 8.112/90 | `urn:lex:br:federal:lei:1990-12-11;8112` |
| Lei 14.133/21 | `urn:lex:br:federal:lei:2021-04-01;14133` |
| Lei 8.429/92 | `urn:lex:br:federal:lei:1992-06-02;8429` |
| Lei 9.784/99 | `urn:lex:br:federal:lei:1999-01-29;9784` |
| Lei 8.443/92 (LO do TCU) | `urn:lex:br:federal:lei:1992-07-16;8443` |

A data é a de **assinatura** da norma, não a de publicação. Errar a data devolve
404 — se acontecer, confira a data no `mcp-brasil` (feature `senado` ou `camara`)
antes de tentar outra combinação.

## O que volta

```bash
curl -s -G "https://normas.leg.br/api/public/normas" \
  --data-urlencode "urn=urn:lex:br:federal:lei.complementar:2000-05-04;101" \
  --data-urlencode "tipo_documento=maior-detalhe" \
  -H "Accept: application/json" | jq '{headline, legislationIdentifier, keywords}'
```

Campos úteis:

| Campo | Serve para |
|---|---|
| `headline` | Nome oficial ("Lei Complementar nº 101, de 04 de maio de 2000") |
| `legislationIdentifier` | URN canônica — use isto ao citar |
| `@id` | Link permanente em normas.leg.br |
| `keywords` | Indexação temática oficial; boa fonte de termos para busca |
| `legislationRepeals` | O que **esta** norma revogou (não o inverso) |
| `hasPart` | Árvore de dispositivos, quando existe — só a estrutura |
| `encoding[].additionalType` | Versões: `PublicacaoOriginal`, `CompilacaoMonoVigenteNaCD` |

## Limites medidos em 28/07/2026

- `hasPart` só apareceu em 2 das 8 normas testadas (CF/88 e Lei 14.133).
- Onde `hasPart` existe, os nós trazem a URN de cada dispositivo
  (`...;1988!ementa`, `...!art5`) e **`text` vazio**.
- `encoding[].contentUrl` aponta para `/api/binario/<uuid>/texto`, que responde
  **404** — testado nas duas versões da LRF.
- `dateModified` veio `None` nas normas testadas: **não sirva este endpoint como
  prova de que uma lei está em vigor.**

Ou seja: metadado e endereçamento, sim; texto, não.

## Verificar se ainda vale

Este mapa é uma medição datada, não uma garantia. Se algo aqui falhar, refaça o
teste e atualize o arquivo — a API pode ter melhorado (ou piorado) desde então.
