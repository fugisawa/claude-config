---
name: ocr-com-evidencia
description: >
  Use quando houver imagem com texto para transcrever ou extrair — foto de página de livro,
  caderno, comprovante ou quadro; digitalização; captura de tela; PDF sem camada de texto
  (o `validate_pdf.py` acusa cobertura abaixo de 100%); lote de fotos; PDF pesquisável — e
  sempre que a transcrição vá servir de FONTE: estudo, citação, dado, número. Use TAMBÉM
  quando você já leu a imagem pelo `Read` e está prestes a entregar o texto como pronto: a
  leitura por visão é candidato, não prova. Sinais: "transcreve essa foto", "passa para
  texto", "OCR", acento sumido ou inventado (`Acäo`, `6rgao`), pontilhado de sumário virando
  lixo, verso da folha transparecendo. NÃO use para PDF que já tem texto (`pdf-to-markdown`)
  nem para mecânica de PDF — formulário, merge, split, validação (`pdf-processing-pro`).
---

# OCR com evidência

OCR é reconhecimento, não prova — e isso vale para a sua própria visão. Uma leitura isolada,
seja de um motor, seja sua pelo `Read`, é um **candidato**. Vira transcrição quando outra
leitura independente concorda com ela, ou quando você a conferiu contra a imagem e deixou
escrito o que conferiu e o que ficou em aberto. O que esta skill produz não é só texto: é
texto **com proveniência** (de onde veio, por qual caminho, com que grau de verificação).

A linha de base que motivou o método, medida em 06/09/2026 com duas fotos reais de sumário:
um agente competente girou a foto, recortou, validou a monotonicidade dos números de página
— e entregou "transcrição concluída" como fonte de estudo sem segunda leitura, sem
proveniência no arquivo, sem marca de incerteza por linha e sem dizer que portão atingiu.
Tudo o que ele fez estava certo; o que ele *não* fez é o que esta skill exige.

## Três rotas, e o critério que escolhe

| Situação | Rota | Por quê |
|---|---|---|
| Até três imagens, texto impresso nítido, resultado **não** vira fonte (ler para responder agora) | Visão direta, com a disciplina da seção *Visão direta* | O custo dos motores não se paga |
| Manuscrito, quadro, anotação de caderno | Visão direta, obrigatoriamente com marca `[?]` no que não estiver claro | Tesseract e RapidOCR não leem manuscrito |
| Resultado vira fonte, ou há mais de três imagens, ou pt-BR com acento importa, ou material sensível que não sai da máquina, ou se pede PDF pesquisável | **Scripts + revisão visual** (seção seguinte) | Segunda leitura independente é a única evidência barata que existe |
| PDF sem camada de texto | `pdftoppm -r 300 -png doc.pdf paginas/p` e depois a rota dos scripts sobre `paginas/` | O PDF é só um envelope de imagens |

Regra que resolve a dúvida: **se alguém vai citar, estudar ou somar o que você transcreveu,
use os scripts.** Dois motores locais rodam em cerca de um minuto por página; a sua visão
entra depois, onde eles divergem.

## Fluxo com scripts

Todos os scripts aceitam `--help`, e o primeiro comando de cada máquina é o diagnóstico:

```bash
S=~/.claude/skills/ocr-com-evidencia/scripts
uv run --script $S/preflight.py --lang por          # o que falta nesta máquina, e a receita
uv run --script $S/batch_ocr.py FOTOS/ --output-dir LOTE/ --lang por
uv run --script $S/review_sheet.py LOTE/            # review.md, review.json, transcricao.md
```

1. **`preflight.py`** diz se há `uv`, `tesseract` com o pacote `por`, `pdftoppm` e `ocrmypdf`, e
   imprime a receita sem `sudo` quando falta algo. Sem Tesseract `por`, o lote sai com
   `language_applied_by: []` e saída 2 — e o RapidOCR sozinho **destrói o português**:
   medido em 06/09/2026, 1 acento em 16 sobreviveu e `órgão` virou `6rgao`.
2. **`batch_ocr.py`** preserva os originais, tenta retificar a perspectiva (e **se abstém**
   quando não acha um contorno de página confiável — foto sem borda é abstenção, não erro),
   detecta foto deitada — celular de lado, sem EXIF; nenhum motor compensa sozinho — pela
   geometria das caixas do RapidOCR e gira antes de reconhecer (`rotation_applied` por
   imagem; `--rotate 0` desliga; de cabeça para baixo só se resolve com Tesseract presente),
   roda RapidOCR e Tesseract sobre quatro variantes de pré-processamento, e grava
   `batch_manifest.json` com hash, rota, candidatos e avisos. Saída 0 só quando toda imagem
   completou **e** o idioma pedido foi aplicado por algum motor.
3. **`review_sheet.py`** põe lado a lado a melhor leitura de cada motor e marca, linha a
   linha, se a outra leitura concorda — comparação **frouxa** (sem acento, pontuação e
   espaço, porque o RapidOCR nunca emite acento; ainda pega `O`/`0`, dígito trocado e
   palavra perdida). Gera `transcricao.md` com frontmatter de proveniência, um marcador por
   imagem e `<!-- REVISAR: … -->` em toda linha sem segunda leitura igual. Lista também o que
   **só o outro motor leu** — a variante-base pode ter engolido meia página (aconteceu com
   um capítulo inteiro), e essas linhas entram no rascunho como `REVISAR` para você situar
   na imagem. Concordância é evidência, não prova: dois motores erram juntos em numeral.
4. **Revisão visual, que é sua.** Abra pelo `Read` a evidência que o `review.md` aponta
   (imagem retificada ou original, e a variante `_color.png`) e confira **as âncoras**:
   acentos (`ção`, `ã`, `ç`, `é`), números, datas, títulos, numeração de seção, número de
   página. Resolva cada `REVISAR` olhando a imagem, não escolhendo a leitura mais bonita. Em
   sumário com pontilhado, o Tesseract transforma o pontilhado em lixo e o RapidOCR lê
   limpo sem acento — a resposta certa costuma ser o texto do Tesseract com o número do
   RapidOCR, conferidos na imagem. **Confira a cobertura antes das linhas:** conte na
   imagem o que existe (entradas, parágrafos, números) e compare com o rascunho mais as
   linhas "só o outro motor leu"; falta silenciosa não gera `REVISAR`. **Critério de
   parada por linha:** um recorte estreito (uma linha, com o número dela) resolve quase
   tudo; se dois recortes diferentes ainda derem leituras diferentes, pare, marque `[?]` e
   registre em *Divergências não resolvidas* — o terceiro recorte é onde se inventa
   confiança. Em página curva perto da lombada, o número que parece da linha é da vizinha:
   use a caixa da linha, não a altura aparente.
5. **Promova o rascunho.** Só depois da revisão troque `status: revisar` por
   `status: revisado`, mantenha o frontmatter e os marcadores de imagem, e mova o que não
   conseguiu resolver para uma seção final `## Divergências não resolvidas`, com a imagem e
   a linha. Nunca apague um `REVISAR` sem ter olhado a imagem.
6. **Reporte o portão** (abaixo) e os números do lote: imagens, retificadas, abstenções,
   motores que aplicaram o idioma, linhas com segunda leitura, linhas em aberto.

O que fica no disco depois de um lote: `rectified/` (imagens retificadas, evidência),
`ocr/<imagem>/candidates/` (todas as leituras, cruas), `ocr/<imagem>/preprocessed/`
(variantes), `batch_manifest.json`, `review.md`, `review.json`, `transcricao.md`. Não apague
nada disso ao entregar; é o que permite a outra pessoa refazer o seu caminho.

## Visão direta, com disciplina

Quando a rota é a visão, o resultado ainda carrega proveniência e incerteza:

```markdown
---
fonte: img_1839b37cb5fd.jpg
sha256: <sha256sum do arquivo>
metodo: visão direta (Read), sem motor de OCR
status: revisar
verificado: acentos dos títulos, números de página em ordem não decrescente
---
```

- Foto deitada: gire antes de ler (`uv run --with pillow python -c 'from PIL import Image; …'`)
  e diga no frontmatter que girou; ler de lado multiplica erro de pareamento.
- Marque `[?]` no trecho que não leu com segurança; não complete pelo contexto sem dizer.
- Separe **transcrição** (o que está visível) de **inferência** (o que você deduziu — "a
  página esquerda é a 10 porque a direita é a 11"). Inferência vai em nota, não no corpo.
- Bleed-through, aba lateral, texto espelhado do verso: diga o que excluiu e por quê.
- Ao entregar, nomeie o portão atingido. Visão direta sem segunda leitura **nunca passa do
  portão B**.

## Portões de qualidade

- **A — pesquisável:** o texto existe e se acha por busca.
- **B — estruturalmente usável:** títulos, listas, ordem de leitura e página de origem
  sobrevivem à inspeção.
- **C — seguro para dado:** todo número, data, nome e acento importante foi conferido
  contra a imagem ou por segunda leitura, ou está marcado como incerto.
- **D — arquivável:** original preservado, hash e manifesto gravados, ferramentas e opções
  registradas, reprodutível.

Um lote pode passar em A e falhar em B–D. Reporte o **mais alto que atingiu de fato**, e
nunca escreva "completo", "preciso" ou "alta qualidade" sem nomear as checagens feitas e o
que ficou em aberto.

## Erros comuns

| O que se pensa | O que acontece |
|---|---|
| "A foto está nítida, li direto e está certo" | Nítida para você não é conferida. Sem segunda leitura ou âncoras conferidas, é portão B no máximo |
| "Validei a lógica dos números, então está certo" | Consistência lógica é inferência; ela não prova que o número lido é o número impresso |
| "Rodou sem erro, então o OCR está bom" | Saída 0 diz que o script terminou. `language_applied_by` vazio diz que o português não foi lido |
| "O candidato com mais linhas é o melhor" | Contagem de linhas inflaciona com lixo de pontilhado e verso. A folha de revisão escolhe por confiança total, e mesmo isso é diagnóstico |
| "Dois motores concordaram, está provado" | Concordância frouxa ignora acento de propósito; numeral pode estar errado nos dois |
| "Corrigi a acentuação pelo contexto" | Só com a imagem na frente. Correção contextual sem evidência é o `Acäo` de volta |
| "Não precisa guardar os candidatos" | Sem eles ninguém refaz o seu caminho; o lote deixa de ser arquivável |
| "Resolvi todos os REVISAR, está completo" | `REVISAR` marca divergência, não ausência. O que nenhum motor leu, ou só o outro leu, só aparece se você contar a página |
| "Mais um recorte e eu fecho essa linha" | Depois de dois recortes discordantes, o terceiro não decide: marca `[?]` e segue |

## Instalação por máquina

Rode `preflight.py` antes de qualquer lote em máquina nova; ele mede em vez de supor, e a
receita de Tesseract sem `sudo` (extrair os `.deb` em `~/.local/opt/tesseract` e expor um
wrapper em `~/.local/bin/tesseract`) sai dele. As dependências Python vêm do bloco PEP 723 de
cada script: `uv run --script` resolve na primeira execução, o que exige acesso ao PyPI;
onde a rede corporativa bloquear, `uv run --script … --help` falha cedo e diz por quê, e a
saída é um ambiente virtual criado num índice liberado, passado com `--python`. O estado por
máquina fica declarado em `docs/ambiente-por-maquina.md` (`tesseract`, `pdftoppm`), sob o
`doctor_ambiente.py`.

Testes de costura, a rodar antes e depois de mexer num script:

```bash
cd ~/.claude/skills/ocr-com-evidencia && uv run --with pytest --with pillow --with numpy \
  --with opencv-python-headless --with "rapidocr-onnxruntime>=1.3,<2" python -m pytest tests -q
```

## Checklist de entrega

- [ ] Original intacto; hash e manifesto gravados (rota dos scripts) ou frontmatter com
      fonte, hash e método (visão direta).
- [ ] `language_applied_by` nomeia um motor para o idioma pedido, ou o relatório diz que não.
- [ ] Toda linha sem segunda leitura foi conferida na imagem ou continua marcada.
- [ ] Âncoras conferidas: acentos, números, datas, títulos, numeração, páginas.
- [ ] Transcrição separada de inferência; exclusões (verso, aba, carimbo) declaradas.
- [ ] Portão nomeado, com o que ficou em aberto.

## Origem

Adaptada em 06/09/2026 da skill `ocr-and-documents` do Hermes (Daniel Fugisawa + Hermes
Agent, 29/08/2026), que segue existindo com o `SKILL.md` próprio e consome estes scripts
por symlink — o Hermes roda só numa máquina, esta cópia é a canônica e viaja pelo git. O
método de evidência veio de lá; o que foi cortado (Docling, MinerU, Marker, LandingAI, os
extratores de PDF) tem dono em `pdf-to-markdown` e `pdf-processing-pro` ou não está instalado
em máquina nenhuma; o que foi acrescentado (`preflight.py`, `review_sheet.py`, a rota de
visão com disciplina, os portões nomeados no relatório) responde ao que a linha de base
não fazia.
