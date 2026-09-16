# A escada de acesso

Cada degrau diz o que se tenta, com qual ferramenta, qual etiqueta a cópia ganha e o que decide
parar. A ordem é a do custo e da qualidade da cópia: primeiro o que uma chamada de API resolve,
depois o que exige busca, depois o que exige outra pessoa. **Duas chamadas por degrau, no
máximo, e parar no primeiro sucesso**: a escada existe para não tentar às cegas. Sci-Hub, LibGen
e Anna's Archive não são degrau; são a rota D, e a seção final diz por quê.

## As quatro etiquetas

Todo recibo diz por qual rota a cópia veio. A etiqueta responde "com que direito eu leio isto",
e a resposta muda o que se pode fazer com o arquivo.

| Etiqueta | O que é | Exemplos |
|---|---|---|
| **A — licenciada** | quem serve o arquivo tem licença para servi-lo | acesso aberto em qualquer cor (ouro, híbrido, bronze, verde, diamante); manuscrito aceito em repositório, que a política da editora permite; Share Link; assinatura própria; empréstimo entre bibliotecas; COMUT; cópia enviada pelo autor, que a política de compartilhamento da editora autoriza |
| **B — exceção legal** | trecho, não obra: um só exemplar de pequeno trecho para uso privado, ou a citação | o `search_literature` do scite com `term`; a janela de `grep` no texto; nunca o PDF inteiro por esta via |
| **C — cinzenta** | cópia que alguém pôs em público sem ser o titular, e que se lê sem redistribuir | o PDF da editora no site pessoal do autor ou no ResearchGate; a cópia que um colega encaminhou. Foi o caso de 16/09/2026 |
| **D — excluída** | redistribuição sem licença, credencial alheia, contorno de medida técnica | biblioteca-sombra e espelhos; senha de outra pessoa no portal; ferramenta que passa a barreira de pagamento. A skill não usa, não cita endereço e não instrui |

Degrau automático é sempre A: as APIs só apontam para quem serve o arquivo abertamente. Degrau
manual é A ou C, e quem registra declara (`artigo.py registrar … --etiqueta`).

## 1. APIs abertas (`artigo.py abrir`) — etiqueta A

O script consulta, nesta ordem, e junta os candidatos:

- **Crossref** (`/works/{doi}`): metadados de referência e os links de mineração de texto que
  a editora declara; quase sempre exigem assinatura, mas custam uma chamada.
- **OpenAlex** (`/works/doi:{doi}`): `oa_status` (`gold`, `hybrid`, `bronze`, `green`,
  `diamond`, `closed`), `best_oa_location.pdf_url`, todas as `locations` com `pdf_url` (é por
  elas que SciELO, HAL, Zenodo, RePEc e os repositórios institucionais entram), PMID, PMCID e o
  autor de correspondência.
- **Unpaywall** (`/v2/{doi}?email=`): a base mais completa de cópias legais; só roda com
  e-mail (`ARTIGOS_EMAIL` ou `--email`), porque a API rejeita endereço de mentira com 422.
- **Semantic Scholar** (`/paper/DOI:{doi}?fields=openAccessPdf,externalIds`): mais um
  `pdf_url`, e os identificadores arXiv e PMC quando o OpenAlex não os trouxe.
- **Europe PMC** (`/search?query=DOI:"…"` e depois `/{PMCID}/fullTextXML`): o XML JATS do
  texto integral, que responde 404 honesto quando o artigo não é aberto. É o degrau que salva
  quando a editora está atrás de Cloudflare.
- **arXiv** (`/pdf/{id}`): quando algum dos anteriores trouxe o identificador.

O CORE e o OpenAIRE não entram: o CORE responde o desafio do Cloudflare a script desta máquina
(medido em 16/09/2026), e o que o OpenAIRE agrega já chega pelas `locations` do OpenAlex.

Os candidatos são ordenados por formato (PDF, XML, página), versão (publicada, aceita,
submetida) e degrau, e o primeiro que é texto de verdade vence. **Pare aqui** quando o diário
imprimir `ABERTO`. Quando imprimir `NÃO OBTIDO`, o diário lista o que cada API respondeu; leve
esse diário adiante, porque ele já elimina degraus manuais (`oa_status=closed` no OpenAlex e
nada no Unpaywall significam que não há cópia em repositório indexado).

## 2. Cópia do autor — etiqueta A ou C

Autores depositam a versão aceita, e às vezes a publicada, no site pessoal, no repositório da
universidade e em redes acadêmicas. Foi o degrau que resolveu o caso de 16/09/2026: o coautor
Brady Roberts guarda o PDF da versão publicada em `bradyrtroberts.ca`.

- `WebSearch` com o título exato entre aspas e `filetype:pdf`; depois o título com `pdf` e
  `site:.edu`; depois o nome de cada autor com "publications" ou "papers"; no Google Scholar,
  "todas as versões" do registro.
- Repositórios institucionais respondem bem ao `WebFetch`, e a versão aceita que eles servem
  é **A**. ResearchGate e Academia.edu pedem conta para baixar, mas a página confirma que a
  cópia existe (e aí vale o pedido ao autor); o PDF da editora que o próprio autor pôs lá, ou
  no site pessoal, é **C**: leitura pessoal, sem redistribuir, e o recibo diz isso.
- Achou um PDF: baixe-o com `WebFetch` ou `curl -L -o`, confira o cabeçalho antes de acreditar
  na versão (periódico, DOI, datas, paginação) e registre:
  `artigo.py registrar <doi> --arquivo copia.pdf --url <de onde veio> --origem "site do coautor X" --etiqueta C --versao publicada`.

**Pare aqui** quando o cabeçalho confirmar a versão. Cópia sem cabeçalho de periódico é versão
aceita ou pré-publicação, e o recibo carrega a ressalva.

## 3. Pré-publicação — etiqueta A

- **OSF Preprints** (cobre PsyArXiv, EdArXiv, SocArXiv, MetaArXiv): a API
  `https://api.osf.io/v2/preprints/?filter[title]=<título>` lista; cada item tem
  `links.preprint_doi` e o arquivo em `relationships.primary_file`. O site `osf.io` rende
  página vazia no navegador da app; use a API.
- **arXiv**: `https://export.arxiv.org/api/query?search_query=ti:"<título>"`, Atom XML; depois
  `/pdf/{id}`. Pelo conector Hugging Face, `hf_fs` com `cat hf://papers/<arxiv-id>/paper.md`
  devolve o texto do artigo que o Hub indexa, para ler sem baixar.
- **SciELO Preprints** (`preprints.scielo.org`) aparece nas `locations` do OpenAlex.
- **SSRN** (economia, direito, ciências sociais): só página; `WebSearch` com o título.

Pré-publicação confere a existência e o método; número de pré-publicação que não bate com a
versão publicada é a versão publicada que manda.

## 4. Conectores com texto integral — etiqueta A (B, quando é trecho)

- **scite `read_fulltext`**: texto corrido de artigo aberto com licença permissiva, 8.000
  caracteres por chamada; `source` precisa ser `"fulltext"`, porque `"abstract"` significa que
  o texto não foi servido. `search_literature` com `dois` e `term` devolve cinco trechos que
  contêm o termo, e é o modo mais barato de conferir um número.
- **PubMed/PMC**: só biomedicina e ciências da vida; `convert_article_ids` do PMID ao PMCID e
  `get_full_text_article`.
- **Consensus** e o conector de corpus (`semanticSearch`): passagens e metadados, não o texto;
  servem para achar o DOI e para saber que há contestação.

## 5. Navegador da app — não abre, mas mostra

`browser_batch` com `navigate` para `https://doi.org/<doi>` e `get_page_text`. Ele passa o
portão de cookies que trava o `WebFetch` (Springer, Nature, Elsevier) e mostra o que a editora
mostra a quem não assina: resumo, referências, datas de recebimento e aceite, material
suplementar (muitas vezes aberto), às vezes uma prévia com as primeiras páginas, e o e-mail do
autor de correspondência, que o degrau 8 precisa. Não passa a barreira de pagamento, e a skill
não tenta.

## 6. Dados e código do artigo

Meta-análise e estudo empírico costumam depositar dados e código no OSF, no GitHub ou no
Zenodo, com o endereço no artigo ou na página do DOI. A API do OSF
(`https://api.osf.io/v2/nodes/<id>/files/osfstorage/`) lista os arquivos, cada um com
`links.download`. Com o `.csv` e o `.R` dá para recomputar o tamanho de efeito, que é uma
conferência mais forte que reler o número e não substitui a leitura da frase onde ele está.

## 7. O acesso do perfil — etiqueta A, e só o que o perfil declara

O bloco *Perfil de acesso* do `SKILL.md` diz o que o Daniel tem: vínculo, CAFe, bibliotecas,
orçamento. Campo vazio é degrau pulado, sem perguntar e sem tentar credencial. Com perfil:

- Portal de Periódicos da CAPES pela CAFe, e a biblioteca da instituição, com empréstimo entre
  bibliotecas para o que a assinatura não cobre.
- **COMUT**, do IBICT: entrega paga de cópia pela rede de bibliotecas parceiras. Está ativo
  (971 pedidos em 2025, 61% atendidos, pelo balanço do IBICT de janeiro de 2026, que o funde na
  plataforma Pinakes); entra só com biblioteca cadastrada e orçamento no perfil.
- Compra ou aluguel do artigo na editora: só com orçamento declarado, e citando o preço antes.

## 8. Pedido ao autor — etiqueta A

`artigo.py pedido <doi> --tema "<motivo concreto>" --para <e-mail>` redige; a sessão cria o
rascunho no Gmail com `create_draft`; o Daniel envia. As regras (um autor por artigo, 30 dias,
120 palavras, o idioma do autor) e os modelos estão em `pedido-ao-autor.md`. Quando a editora é
a Elsevier, o pedido inclui a alternativa do Share Link. Em paralelo, o botão de pedido do
ResearchGate.

## Quando nada abre — o recibo

O `abrir` imprime `⚑ Texto integral não obtido por via legal em <data>`, com o diário do que
cada API respondeu; `--pendencia "<a linha que o pedido imprime>"` e `--reavaliar-em <data>`
completam o recibo, e `--destino` o grava. A fonte secundária entra rotulada como secundária, e
a próxima sessão começa do degrau 8, não do 1. A data de reavaliar é o fim do embargo quando a
política da editora o diz (Open Policy Finder, pelo navegador da app: a API responde 403 a
script desta máquina) ou, sem embargo declarado, a data em que o pedido ao autor pode ser
repetido.

## A base legal brasileira, e o que foi conferido

A recusa da rota D não depende de direito comparado: depende da Lei 9.610/1998 e da licença que
cobre o arquivo. O que está abaixo foi conferido em 16/09/2026 na fonte indicada; o que não foi
está marcado, e entra como "não conferido" até alguém abrir a fonte.

- **Lei 9.610/1998, art. 46, II e III** (conferido no texto do Planalto): não ofende o direito
  autoral "a reprodução, em um só exemplar de pequenos trechos, para uso privado do copista,
  desde que feita por este, sem intuito de lucro" e "a citação em livros, jornais, revistas ou
  qualquer outro meio de comunicação, de passagens de qualquer obra, para fins de estudo,
  crítica ou polêmica, na medida justificada para o fim a atingir". É a rota B: trecho, não o
  PDF inteiro.
- **Lei 9.610/1998, art. 107, I e II** (conferido no Planalto): responde por perdas e danos
  quem altera, suprime ou inutiliza "dispositivos técnicos introduzidos nos exemplares das
  obras e produções protegidas para evitar ou restringir sua cópia". É o que põe o contorno da
  barreira de pagamento na rota D.
- **STJ, REsp 964.404/ES, 3ª Turma, rel. Min. Paulo de Tarso Sanseverino, j. 15/03/2011**
  (conferido pelo Informativo 466 do STJ e por fontes secundárias; o inteiro teor não foi
  aberto): o rol dos arts. 46 a 48 é exemplificativo, e as limitações se interpretam à luz dos
  direitos fundamentais e pela regra dos três passos (Convenção de Berna e TRIPS). É a leitura
  pró-acesso que sustenta a rota C: leitura pessoal de cópia que outro pôs em público.
- **STJ, REsp 2.008.122/SP, 3ª Turma, rel. Min. Nancy Andrighi, j. 22/08/2023, DJe 28/08/2023**
  (conferido pelo Informativo 785): o serviço pago de clipping não passa pelo teste dos três
  passos e viola o direito do titular. O teste corta nos dois sentidos: a mesma regra que abre a
  leitura privada fecha a redistribuição comercial, e é por ela que a rota D fica de fora.
- **Política de compartilhamento da Elsevier** (conferida na página `elsevier.com/about/policies-and-standards/sharing`):
  o autor pode compartilhar a versão publicada "with known research colleagues for their
  personal use". É a licença que faz do pedido ao autor uma rota A. O prazo de 50 dias do Share
  Link **não foi conferido**.
- **Delhi High Court, Elsevier e outros v. Elbakyan, ordem de 19/08/2025** (conferido em Bar and
  Bench e Digital Policy Alert): bloqueio do Sci-Hub, do Sci-Net e dos espelhos na Índia, com
  prazo de 72 horas. A "extensão aos espelhos em dezembro de 2025" que circula **não foi
  encontrada**; a ordem de agosto já os alcança.
- **Direito comparado** (Canadá, Estados Unidos, Alemanha, Reino Unido, União Europeia, Índia,
  Suíça): item a item, com o estado de verificação, em `mapa-juridico.md`. Vale como argumento
  persuasivo, nunca como licença no Brasil.
- **CF, art. 5º, XIV e XXVII, e art. 218; PIDESC, art. 15.1.b (Decreto 591/1992)**: citados no
  ensaio abaixo; **o texto não foi aberto hoje**. Reforma da LDA promulgada: **não conferi**.

## Por que o Sci-Hub não é degrau

Em 16/09/2026 o Daniel pediu que o Sci-Hub entrasse na escada, e depois escreveu um ensaio
com a tese de que qualquer artigo publicado deveria ser legível por quem já o financiou: bem
não rival, custo marginal zero, autores e revisores não remunerados, margens de 35–40% da
editora, mandatos do NIH, do Plan S e do Horizon Europe, o art. 15 do Pacto de Direitos
Econômicos, Sociais e Culturais e os arts. 5º, XIV, e 218 da Constituição. O argumento é sobre
**como a norma deveria ser**, e os financiadores estão de fato mudando a norma nessa direção.
A licença que hoje cobre um arquivo específico é outra coisa: o Sci-Hub redistribui cópias sem
ela, e a skill não executa esse ato, por decisão de quem a escreveu, não por dúvida sobre o
mérito do ensaio. É a rota D. O que a skill deve ao Daniel em troca é esgotar o acesso legítimo
de verdade (os oito degraus acima), redigir o pedido ao autor no mesmo minuto, e nunca fingir
que um número foi conferido quando não foi.
