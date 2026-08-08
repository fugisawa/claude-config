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

A data é a de **assinatura**, não a de publicação.

**Errar a URN NÃO devolve 404** — devolve **200 com um eco de si mesma**, e essa é a
falha mais perigosa deste endpoint. Medido em 08/08/2026:

```
urn inventada  → 200, 62 bytes: { "urn": "urn:lex:br:federal:lei.complementar:2025-01-01;224"}
urn lixo       → 200, 51 bytes: { "urn": "urn:lex:br:federal:lei:1500-01-01;99999"}
urn correta    → 200, 5.424 bytes com legislationPassedBy, encoding[], ementa…
```

O envelope vazio atravessa qualquer parser: `encoding[]` sai `[]`, o seletor de versão
devolve `None`, e o chamador conclui **"esta norma não tem Monovigente, vou para o
Planalto"** — quando a verdade é "esta norma não existe, ou a data está errada". Aí ele
baixa a `fallback_url`, que aponta para outra lei, e serve texto errado com cara de acerto.

**Guarde antes de olhar `encoding`:** se as chaves do objeto forem só `{"urn"}`, falhe
alto. Não é ausência de versão consolidada; é URN que não resolveu.

```python
if set(md.keys()) <= {"urn"}:
    raise SemNorma(f"URN não resolve: {urn} — confira a data de assinatura")
```

Se a data for a dúvida, confira no `mcp-brasil` (feature `senado` ou `camara`).

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

O que volta é HTML limpo, UTF-8, **zero tags de riscado**. Em **lei ordinária e
complementar** vêm também as anotações de alteração ancoradas na unidade certa, o
que é melhor que o Planalto:

```
(Inciso com redação dada pela Lei nº 9.165, de 19/12/1995)
(Alínea com redação dada pela Lei Complementar nº 214, de 16/1/2025, produzindo efeitos a partir de 1º/1/2026)
(Artigo acrescido pela Lei Complementar nº 224, de 26/12/2025)
```

**3. A CF/88 é a exceção, e é a que mais dói.** O Monovigente da Constituição vem
**sem nenhuma anotação de emenda**. Contagem de 08/08/2026 sobre o texto extraído
das duas fontes:

| Fonte | Tamanho | Anotações de alteração |
|---|---|---|
| `normas.leg.br` Monovigente | 412 KB | **0** |
| Planalto (compilado) | 864 KB | **2.087** |

O Monovigente dá o texto **vigente e limpo** da Constituição, ótimo para citar, e
**não diz qual emenda mudou o quê**. Para material de concurso isso é metade do que
se precisa, porque a banca cobra a autoria da emenda ("a EC 109/2021 incluiu…").

**Regra prática:** texto vigente da CF pelo Monovigente; **autoria de emenda, só
pelo Planalto**, que empilha as redações e anota cada uma. Foi assim que se apurou,
no art. 163, que o inciso V antigo ("fiscalização das instituições financeiras")
caiu com a **EC 40/2003** e que o inciso IX entrou com a **EC 135/2024** — nada
disso aparece no Monovigente, que mostra só a lista final.

E é a mesma pilha que produz o erro clássico do material de cursinho: quem copia o
compilado sem separar as camadas transcreve **as duas** redações do inciso V como
se fossem dois incisos distintos. Caso real medido numa aula de AFO do IGEPP.

**4. A requisição da CF/88 é grande e o timeout curto a mata.** O JSON de
`maior-detalhe` da Constituição tem **4,7 MB** (2.262 nós de estrutura). Com
`timeout=90` a leitura estoura em `http.client.IncompleteRead`, e a exceção carrega
o conteúdo parcial — se alguém a capturar e usar `e.partial`, processa JSON truncado.
Use `timeout=180` e **repita** em caso de `IncompleteRead`; três tentativas bastaram
em todos os testes. E não troque `maior-detalhe` por um valor "mais leve": qualquer
outro `tipo_documento` responde **200 com zero byte**, mais uma falha silenciosa.

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
browser. Mas o HTML embute a redação vencida junto da vigente, e extrair dali tem
oito modos de falhar **em silêncio** — decodificação, riscado, remissão contada
como dispositivo, rubrica engolida, lei alterada assumindo a autoria da
alteradora, anexo republicado no fim.

**→ `extrair-planalto.md`.** Não improvise: cada item de lá custou uma leitura de
PDF para ser encontrado.

Duas coisas que ficam aqui por serem sobre endereçamento, não extração:

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
