# Extrair dispositivos do Planalto sem corromper o texto

Medido em 07/08/2026 extraindo a LC 200/2023 e a Lei 8.443/1992 de ponta a ponta, com
conferência visual do PDF resultante. Cada item abaixo **falha em silêncio**: o download
dá 200, o parser não reclama, e o erro só aparece na leitura — ou não aparece nunca.

## 1. Redação vencida embutida na mesma página

O Planalto publica a redação superada junto da vigente, riscada. Duas convenções convivem:
`<strike>` (dominante — 773 na CF/88, 44 na Lei 14.133) e `style="line-through"` (rara mas
real — 12 na 14.133, e a **única** usada na LC 200). Tratar só a dominante passa no
fixture errado. `<s>` não apareceu em nenhuma norma medida.

**Remova a subárvore, não a tag.** O riscado marca o ancestral: um
`<div style="line-through">` com parágrafos dentro esconde texto vencido em nós que,
isolados, não têm marca. `decompose()` do BeautifulSoup resolve; `unwrap()` vaza.

**O stub de revogação sobrevive à limpeza** — em 72 dos 77 casos na CF/88 a anotação
`(Revogado…)` está *fora* do riscado, como texto vivo (`a) (Revogada)`). Preserve: sem ele
o leitor não sabe que o dispositivo existiu, e a numeração dos vizinhos parece erro.

**Nunca deduplique por número.** Na LC 200 há um `§ 7º (VETADO). (NR)` riscado logo antes
do § 7º vigente, e um Art. 14 riscado cuja abertura é quase idêntica à do Art. 14 vigente.
Quem desempata por número tem 50% de chance de guardar o revogado. A limpeza decide.

## 2. Remissão não é dispositivo

Contar `Art. \d+` no texto corrido **superestima**: conta "nos termos do art. 3º", "art.
163 da Constituição". Na LC 200 isso dá 24 artigos; os reais são **19**. Conte só blocos
que ABREM com o rótulo. Mesmo erro vale para `§`.

## 3. Normalize o espaço antes de casar rótulo

O rótulo vem em span próprio (`<span>Art.</span><span> 1º`), então trocar tag por espaço
produz `"Art.  1º"` com dois espaços. Um `Art\.\s?\d` acha **zero** artigos na CF/88 — o
download deu certo, a contagem deu zero, e nada avisa.

## 3b. NÃO use `get_text(separator=" ")` — ele parte palavra ao meio

A fonte quebra palavra quando muda o estilo no meio dela. Real, na LOTCU servida pelo
`normas.leg.br`:

```html
(Express</span><span class="Hyperlink" style="font-style:italic">ão</span>
```

Um separador insere espaço em TODA fronteira de elemento e escreve `"(Express ão"` —
que **sai impresso assim**. Também vi `presta ç ão` e `Lei O rgânica`. Não é artefato de
extração: é o PDF.

Use `get_text()` sem separador e normalize o espaço depois (item 3). O caso oposto — o
rótulo em span próprio, `<span>Art.</span><span> 1º` — **não precisa** de separador: a
fonte já traz o espaço dentro do texto. Medido nas três normas: sem separador a contagem
de artigos é igual ou MAIOR (CF/88: 514 contra 512) e nenhum rótulo cola. Só o `<br>`
precisa virar espaço à mão, porque não carrega nenhum.

## 4. Artigo acrescido tem sufixo de letra

`5º-A`, `6º-B`, `14-A`. Um padrão só de dígitos os perde — e são os mais novos, logo os
mais cobrados em prova.

## 5. Rubrica de divisão vem em DOIS blocos

`TÍTULO I` / `CAPÍTULO II` / `SEÇÃO III` (o designador) e, no bloco seguinte, o nome em
caixa alta (`DAS METAS FISCAIS…`). Sem tratar, o par é absorvido pelo dispositivo anterior:
na LC 200 o § 3º do art. 1º terminava com "CAPÍTULO II DAS METAS FISCAIS COMPATÍVEIS COM A
SUSTENTABILIDADE DA DÍVIDA" colado no fim. Numa lei de 113 artigos, perder as rubricas
custa a navegação inteira.

## 6. Lei que altera outra lei TRANSCREVE os dispositivos alterados

O Art. 11 da LC 200 altera a LRF: os `§` e incisos que o seguem são **texto da LRF**, não
do arcabouço. Sem marcar, entram no material com a atribuição errada — corrupção pior que
desatualização (ali o texto é velho; aqui é de outra lei).

- **Abre** na fórmula da LC 95/1998: "passa a vigorar com as seguintes alterações".
- **NÃO fecha no `(NR)`** — a LC 95 manda pô-lo ao fim de *cada* artigo alterado, então
  num artigo que altera vários ele aparece no meio, várias vezes. Fechar ali deixa metade
  do bloco de fora.
- **Fecha quando a lei hospedeira retoma a própria numeração** (o artigo seguinte ao que
  altera). Foi a leitura do PDF que pegou: com a regra do `(NR)`, os arts. 12 a 14-A da
  LC 200 saíam impressos como se fossem da LRF.

## 7. O fim da norma não é o fim da página

Depois da fórmula de promulgação, o Planalto muitas vezes **republica a lei inteira** num
anexo (na LC 200, o de "partes vetadas"). Sem cortar, tudo isso é absorvido pelo último
dispositivo. Corte no marcador de encerramento, constante em toda página:
`Este texto não substitui o publicado n[oa]` ou `Brasília, <dia> de <mês> de <ano>;`.

## 8. Bot-defense injetado quebra hash de bytes

Toda página traz `<script id="f5_cspm">` com token aleatório por request: mesmo
`Content-Length`, bytes diferentes. Hashear o bruto acusa mudança **sempre** — e alarme que
dispara sempre é alarme que se aprende a ignorar. Remova `<script>` e normalize espaço
antes de hashear.

Para detectar mudança real o Planalto oferece caminho melhor: manda `ETag` e
`Last-Modified`, e responde **304 com 0 bytes** a `If-Modified-Since`. (O endpoint de
binário do `normas.leg.br` **não** manda nenhum dos dois — ali é hash do conteúdo.)

## Implementação de referência

`~/manual_estudo/normas/` implementa tudo isto com 34 testes offline sobre HTML salvo:
`estrutura.py` (limpeza + classificação), `corpus.py` (procedência + deriva). Portar de lá
é mais barato que redescobrir.
