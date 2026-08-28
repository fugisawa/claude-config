---
name: enumerar-o-territorio-e-nao-o-mapa
description: Guarda que percorre a DECLARAÇÃO — a trilha, o índice, o catálogo — confere só o que ela nomeia e é cega ao que ela omite, de modo que arquivo que chega sem entrar na declaração deixa tudo verde; pelo menos um guarda tem de enumerar o TERRITÓRIO e cobrar a declaração, e índice que se regenera do disco não serve para isso, porque absorve o intruso em vez de denunciá-lo
metadata:
  pattern: debugging_techniques
  origin: manual_estudo, sessão de 28/08/2026 — push da outra máquina, com rebase
  confidence: alta (16 capítulos órfãos e colisão de números em duas disciplinas passaram por seis guardas; um só pegou)
---

**O padrão.** Um projeto com muitos artefatos costuma ter um arquivo que declara quais são: a
trilha que lista os tópicos, o índice que lista os capítulos, o catálogo que lista os
entregáveis. As checagens nascem em volta dessa declaração, porque é ali que está a lista — e
todas herdam a mesma cegueira. **Elas conferem que tudo o que a declaração nomeia existe, e
nunca que tudo o que existe está na declaração.** As duas perguntas parecem a mesma e não são:
a primeira encontra o item que sumiu, a segunda encontra o item que chegou sem ser convidado.
Quando o defeito é do segundo tipo, o painel inteiro fica verde.

Isto não é [[guarda-nao-pode-derivar-do-guardado]], em que a guarda reimplementa a regra do
código e herda o ponto cego dele. Aqui as guardas estavam certas e eram independentes umas das
outras: o problema é a **direção da varredura**. Todas iam do mapa para o território, e a
diferença morava no território.

Também não é [[aviso-por-item-nao-diz-ausencia-total]], que trata da ausência de **todos** os
itens. Aqui não faltava nada: sobrava — e sobra é ainda mais invisível, porque nenhuma linha da
declaração aponta para o excedente.

## A ocorrência

Um `git push` da outra máquina trouxe, em três commits, **16 capítulos novos, 47 diagramas e 16
PDFs** para duas disciplinas. As mensagens dos dois commits de conteúdo anunciavam, na letra,
que a bússola havia sido corrigida primeiro — `trilha.md`, `00-indice.md`,
`mapa-incidencia.md`, `00-verticalizacao-mestre.md`. **Nenhum desses arquivos estava nos
commits.** O rebase na outra máquina descartou exatamente os arquivos que os dois lados haviam
editado, e ficou com a versão local deles; o que não teve conflito entrou inteiro.

O resultado no disco: duas disciplinas com **duas séries de capítulos ao mesmo tempo**,
colidindo nos números 01 a 08, e nenhuma trilha apontando para a série nova.

O que cada guarda disse, rodado logo depois do `pull`:

| Guarda | O que ele lê | Veredito |
|---|---|---|
| `panorama.py` | a trilha | verde |
| `marcas.py --verify` | a trilha e o mapa | **0 erros** |
| `doctor_docs.py` | o catálogo contra o disco | **0 erros · 0 avisos** |
| `doctor_material.py` | os capítulos que a trilha nomeia | avisos de sempre |
| `doctor_etiquetas.py` | a trilha | 1 aviso, de outro assunto |
| `catraca.py` | contadores de dívida | **0 erros** |
| `gerar_indice_disciplina --verify` | **a pasta** | **2 DIVERGE** |

Um em sete. E ele pegou por uma razão só: é o único que deriva do **conteúdo da pasta** em vez
de seguir a trilha.

## O agravante: o catálogo que se regenera do disco

O `doctor_docs` parece a exceção — ele confere o catálogo *contra o disco*, que é a direção
certa. Ele deu **0 erros e 0 avisos** mesmo assim, e a razão é a que mais dói: o commit final
do push regenerava o `ENTREGAVEIS.md` a partir do disco. **O catálogo absorveu os 16 órfãos como
entregáveis legítimos**, e a conferência passou a comparar o disco com uma cópia recente dele
mesmo.

Daí a segunda metade da regra: *índice que se regenera do território não pode ser o guarda do
território.* Ele é derivado, e derivado nunca acusa a fonte. Quem acusa é a comparação entre
**duas declarações independentes** — no caso, a pasta contra a trilha, que ninguém regenera uma
da outra.

## O que fazer

- **Toda coleção com uma declaração precisa de um guarda que ande no sentido inverso**: enumere
  a pasta e cobre a linha correspondente na declaração. Um só basta, e é barato.
- **Não conte com a mensagem de commit.** Ela anunciava quatro arquivos que não estavam lá, e
  ninguém mentiu: o rebase os tirou depois de a mensagem ter sido escrita. É o caso geral de
  [[verify-claimed-state]] — `git show --name-only` custa um segundo e responde.
- **Depois de um `pull` que traz trabalho da outra máquina, rode primeiro o guarda que varre a
  pasta.** Os que leem a declaração vão dizer que está tudo bem, e vão estar certos sobre a
  pergunta que fazem.
- **Colisão de número é o sintoma barato de procurar.** `ls` na pasta e olhar se dois arquivos
  reivindicam o mesmo prefixo custa nada e denuncia a espécie inteira. E cuidado com o glob por
  número na hora de consertar: `0[1-5]-*` casa com as **duas** séries, e foi o que quase levou
  os arquivos errados.
