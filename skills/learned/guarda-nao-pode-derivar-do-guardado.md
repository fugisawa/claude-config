---
name: guarda-nao-pode-derivar-do-guardado
description: Verificador que reimplementa a regra do código que ele guarda herda o ponto cego dele — as duas cópias concordam, e concordar é o que torna a guarda inútil; a verdade tem de vir por um caminho independente, e o mais barato é perguntar ao disco em vez de reexecutar o parser
metadata:
  pattern: debugging_techniques
  origin: manual_estudo, sessão de 14/08/2026 — duas ocorrências na mesma noite
  confidence: alta (uma escondeu 15 arquivos da medição; a outra inflou o painel em 6 tópicos)
---

**O padrão.** Uma guarda existe para dizer se o código está certo. Quando ela decide o que
conta usando **a mesma regra que o código usa**, ela deixa de ser um segundo par de olhos e
vira um eco: onde o código não enxerga, ela também não enxerga, e o resultado é uma saída
verde que afirma cobertura inexistente.

O que torna isto diferente de [[a-segunda-copia-da-regra-diverge-calada]] é o sinal. Lá o dano
vem das duas cópias **divergirem** com o tempo. Aqui elas **concordaram** — e a concordância é
justamente o defeito, porque uma guarda que concorda por construção não pode reprovar. O
remédio também se inverte: em produção, elimine a segunda cópia; na guarda, **exija a segunda
via**.

E também não é [[checagem-que-nao-pode-falhar]]. As três regras de lá — nascer com um teste
que a vê reprovar, excluir por regra verificável e não por lista de nomes, ter universo de
tamanho conhecido — **não pegam este caso**. A varredura abaixo era capaz de reprovar, não
excluía nada por nome, e varria as dezenove disciplinas do projeto. Ela falhava por herança.

## Ocorrência 1 — a varredura que copiou o `endswith` do extrator

O projeto tem um extrator que resolve, a partir de um campo de texto, qual arquivo da
prateleira ele nomeia. Ele exigia que o campo **inteiro** fosse um nome de arquivo
(`strip("`")` mais `endswith((".pdf", ".md"))`), e a trilha escreve

    ▸ **Leia:** `Controle-Externo-05-Processo.pdf` (33pp — a folha própria: a cadeia…)

que termina em parêntese. Resultado: **quinze folhas próprias saíam como "não medido"**, e a
folha do dia anunciava sem tamanho um arquivo de trinta e três páginas que custa três janelas
de estudo.

A varredura que existia para pegar exatamente isso — *"nenhuma sessão de teoria pode dizer
'não medido' sobre arquivo que está no disco"* — reimplementava, dentro do teste,
`strip("`")` e `endswith(".pdf")`. Ela rodava, ficava verde, e **não podia** ver o caso, pela
mesma razão que o extrator não via.

**O conserto foi de fonte, não de regex.** A varredura passou a listar o que está na
prateleira e perguntar se algum daqueles nomes aparece no campo. Nenhuma regra de parsing é
recriada, e por isso ela sobrevive à próxima mudança de forma do campo — que é o ponto.

## Ocorrência 2 — a guarda com a sua própria lista de rótulos

O leitor canônico das trilhas reconhece quatro rótulos de teoria; a guarda de autossuficiência
trazia a **sua própria lista** de três, escrita à mão. Os campos do quarto rótulo ficavam fora
do campo de visão dela.

Medido no painel, antes e depois de a guarda passar a derivar os rótulos do leitor:

    material próprio ....  57/167  →  63/167
    falta construir ..... 110      → 104
    Direito Administrativo  0/12   →   4/12   ← saía como "sem material nenhum"

Uma disciplina inteira aparecia como não construída **com quatro arquivos no disco**.

## O corolário que explica a sobrevida: erro que INFLA dívida não dispara nada

A ocorrência 2 errava para o lado de **cobrar mais trabalho do que existe**, e é por isso que
durou. Um painel que reporta dívida a mais parece diligente; ninguém audita quem cobra demais.
A intuição de "errar para o lado seguro" trai aqui: em instrumentação, o falso positivo de
dívida não é conservador — é **invisível**, porque não há nenhum evento que force alguém a
conferir.

O sinal do erro decide quanto tempo ele vive. Falso negativo alguém acaba topando ao usar o
sistema; falso positivo de dívida só é achado por auditoria deliberada.

## A regra

**Antes de escrever uma guarda, pergunte por qual caminho ela chega à verdade — e se for o
mesmo caminho do guardado, troque.** As vias independentes costumam ser mais baratas do que
parecem: listar o diretório em vez de reproduzir o parser; ler o produto compilado em vez do
código que o gera; derivar do dono único da regra em vez de recopiá-la.

Relacionado: [[checagem-que-nao-pode-falhar]] · [[a-segunda-copia-da-regra-diverge-calada]] ·
[[negative-finding-vs-broken-probe]]
