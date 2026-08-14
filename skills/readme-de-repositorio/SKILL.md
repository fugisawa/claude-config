---
name: readme-de-repositorio
description: Use ao escrever, refatorar ou avaliar o README de um repositório — decidir o que vai nele e o que vai no CLAUDE.md, no ARQUITETURA.md ou num comando; escolher e ordenar as seções; instalar sumário e âncoras; consertar README longo em que o leitor não acha o que precisa. Use TAMBÉM quando o README trouxer contagem escrita à mão, transcrição colada de saída de comando, lista de pendências virando registro de mudanças, cabeçalho que não diz o que há embaixo, ou quando dois documentos de governança do mesmo repositório se sobrepuserem e o leitor não souber qual abrir. NÃO use para documentação de API, tutorial ou site de docs — pelo modelo Diátaxis, o README não é o lugar deles —, nem para revisar a prosa em si, que é o agente `revisor-prosa-ptbr`.
---

# README de repositório

O README é a **porta de entrada**, e não o manual. Ele existe para que alguém que chega
decida, em pouco tempo e sem rolagem inútil, o que isto é, se serve para ele, o que fazer no
primeiro minuto e para onde ir depois. Toda regra abaixo deriva dessa frase: quando uma
decisão ficar em dúvida, pergunte o que serve a quem chega, não o que seria completo.

Essa distinção tem nome no modelo Diátaxis, que separa documentação em quatro espécies por
duas perguntas — *ação ou cognição?* e *aquisição ou aplicação?* ([diataxis.fr/compass](https://diataxis.fr/compass/)).
O README é predominantemente **guia de tarefa** (ação aplicada) com um pouco de
**explicação** (por que existe). Ele **não** é referência, porque referência se consulta e se
gera; **não** é tutorial completo, salvo pelo primeiro uso; e **não** é manual do mecanismo.
Cada linha que empurra o README para as outras três espécies é uma linha que pertence a
outro arquivo.

---

## 1. A decisão de fronteira

Antes de escrever qualquer seção, cada fato passa por três perguntas, **nesta ordem**. A
primeira elimina mais texto do que as outras duas juntas.

**Pergunta 1 — um comando responde isto?** Se responde, o documento não guarda o valor:
guarda o comando. Contagem de matérias, número de páginas de um PDF, quantos tópicos há,
onde a fila parou, qual é a data de hoje da campanha — nada disso se escreve. Escrever o
valor cria a segunda cópia que envelhece numa das duas e não na outra, e nenhuma avisa.
Quando o valor for indispensável para o argumento, ele entra **datado e com a medição
citada** ("medido em 13/08/2026, no censo"), o que o transforma de afirmação viva em registro
histórico — e registro histórico não envelhece.

**Pergunta 2 — quem precisa disto, e em que momento?** A resposta escolhe o arquivo:

| O leitor está… | Documento | Do que ele é dono |
|---|---|---|
| chegando ao repositório | `README.md` | O que é, por que existe, como se usa hoje, e para onde ir |
| prestes a fabricar ou regerar um artefato | `CLAUDE.md` | Pipelines, comandos exatos, armadilhas medidas, convenções de build |
| prestes a alterar um mecanismo | `ARQUITETURA.md` | Quem garante o quê, quem deriva de quem, o que **não** tem dono |
| procurando um número ou um estado | um comando | O valor, recalculado a cada leitura |

**Pergunta 3 — isto muda sozinho quando o trabalho anda?** Se muda, o README fica com o
**ponteiro** e o vizinho fica com o **conteúdo**. Estado de campanha, fila de pendências e
inventário de artefatos mudam toda semana; o README aponta o plano, o catálogo gerado ou o
comando, e nunca reproduz a linha.

**Regra de desempate.** Quando duas respostas empatarem, o conteúdo vai para o vizinho e o
README recebe uma frase mais o link. A razão é assimétrica: o README é o documento **mais
lido e menos revisado** do repositório, de modo que um erro nele sobrevive mais tempo e
alcança mais gente do que o mesmo erro em qualquer outro lugar.

---

## 2. A estrutura recomendada

A ordem abaixo combina a especificação *Standard Readme*
([spec](https://github.com/RichardLitt/standard-readme/blob/main/spec.md)), as cinco
perguntas que a GitHub declara ([about-readmes](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes))
e o que a medição empírica mostra estar faltando na prática (§7).

| # | Seção | Estado | Por que está aqui, e nesta posição |
|---|---|---|---|
| 1 | **Título e frase única** | obrigatória | Diz o que é em uma frase. A *Standard Readme* pede menos de 120 caracteres e proíbe título próprio para essa frase. É a única linha que **todo** leitor lê |
| 2 | **Por que existe, e para quem** | obrigatória | Responde o "por quê" e delimita o que o projeto **não** é. Vem cedo porque decide se o leitor continua |
| 3 | **Estado atual** | obrigatória em projeto vivo | Uma linha, e ela aponta o comando ou o plano que a calcula. Sem isto, quem chega descobre o inacabado por acidente |
| 4 | **Sumário ancorado** | obrigatória acima de 100 linhas | A régua é literal da *Standard Readme*. Detalhe em §3 |
| 5 | **Como começar** | obrigatória | O primeiro minuto: o que instalar uma vez, o que imprimir, o primeiro comando. É a lacuna clássica — todo fluxo documentado presume o ciclo já rodando |
| 6 | **Como se usa no dia** | obrigatória em sistema operado | Organizada **por momento de uso**, nunca por pasta: no dia, ao errar, na revisão, no rito semanal, quando algo muda, quando trava |
| 7 | **O que há dentro** | opcional | Mapa de pastas em uma linha cada. Vira defeito quando cresce em inventário |
| 8 | **Como se fabrica** | opcional, delegável | Uma tabela de "o quê → qual oficina", e os comandos exatos ficam no `CLAUDE.md` |
| 9 | **Onde procurar o resto** | obrigatória acima de ~5 documentos | A tabela de donos. Cada documento do repositório aparece nela, sem exceção |
| 10 | **Licença, manutenção, contribuição** | obrigatória em repositório público | A *Standard Readme* exige licença como última seção. Em repositório pessoal e privado, cai |

**A ordem carrega um argumento, e não uma convenção.** As seções 1 a 3 respondem *se* o
leitor continua; a 4 dá o mapa; as 5 e 6 respondem *o que ele faz*; da 7 em diante vem o que
só se consulta depois de já se ter entrado. Inverter isso põe referência na frente da
decisão, que é exatamente o erro que o modelo Diátaxis descreve.

**Sobre a seção de estado (nº 3), que é a que mais apodrece.** Ela é legítima e rara — vale a
pena tê-la —, mas só sobrevive sob três travas: **cada item aponta o plano ou o comando que o
possui**, nenhum item repete o detalhe que vive lá, e **item resolvido sai**. Histórico de
resolução não é estado; é registro de mudanças, e registro de mudanças tem arquivo próprio.
Uma seção de estado que acumula itens riscados empurra para baixo justamente o que decide.

---

## 3. Réguas de navegabilidade

Cada régua abaixo se confere, e o comando que as mede está no fim da seção. Duas delas são
citadas de fonte; as outras são derivadas, e isso vem dito.

**R1 — Sumário ancorado acima de 100 linhas.** A régua é literal da *Standard Readme*:
o sumário é obrigatório, exceto em README com menos de cem linhas, e deve ligar a todas as
seções. **Ancorado no próprio arquivo**, e não confiado à interface: a GitHub gera um
"Outline" automático a partir dos cabeçalhos, mas ele fica atrás de um ícone de menu e **não
existe no clone, no editor nem no terminal** — que é onde o dono do repositório efetivamente
lê. Fonte da funcionalidade e do seu lugar: a documentação da GitHub citada acima.

**R2 — A primeira tela responde três coisas: o que é, para quem, e qual é o primeiro
comando.** A base é medida: em estudo de rastreamento ocular da Nielsen Norman Group,
**57% do tempo de leitura de uma página fica acima da dobra**, 74% nas duas primeiras telas,
e **mais de 42% no primeiro quinto do documento** ([nngroup.com/articles/scrolling-and-attention](https://www.nngroup.com/articles/scrolling-and-attention/)).
A conclusão do estudo — "quanto mais perto do topo, maior a chance de ser lido" — significa
que o espaço mais caro do README é o que se costuma gastar com contexto. Se o primeiro
comando copiável só aparece na terceira tela, ele está no lugar errado.

**R3 — Nenhum trecho sem cabeçalho maior que uma tela.** Na régua desta skill, uma tela vale
aproximadamente **50 linhas de Markdown-fonte**; trecho maior que isso deixa o leitor que
está varrendo sem ponto de reentrada. **Esta conversão é derivada, não medida** — a medição
da NN/g é em pixels de página renderizada, e a correspondência com linhas de fonte é
estimativa desta skill. Use-a como alarme, não como veredito.

**R4 — Profundidade máxima `###`.** Um `####` num README é sinal de que aquela seção virou
manual, e manual sai para arquivo próprio. Derivada da fronteira da §1, não de fonte externa.

**R5 — Todo cabeçalho carrega a pergunta que responde.** O leitor decide se desce ou não pelo
cheiro do cabeçalho, no sentido técnico de *information scent* — o conjunto de pistas pelas
quais ele estima, antes de clicar ou rolar, se aquele caminho leva ao que procura (Pirolli e
Card, teoria do forrageamento de informação; panorama em
[nngroup.com/articles/information-foraging](https://www.nngroup.com/articles/information-foraging/)).
Daí a regra prática: "No dia" e "Quando algo mudar" têm cheiro; "Detalhes", "Notas" e
"Outros" não têm nenhum, e a seção embaixo deles não é encontrada.

**R6 — Nenhum documento do repositório fica fora da tabela de donos.** Documento que existe e
não é citado fica invisível, e nada acusa. Isto se confere com um comando, e por isso é a
única régua desta lista que pode virar guarda automática.

**O comando que mede as réguas:**

````bash
python3 - README.md <<'PY'
import re, sys
alvo = sys.argv[1] if len(sys.argv) > 1 else "README.md"
src = open(alvo, encoding="utf-8").read().split("\n")
fence, heads = False, []
for i, l in enumerate(src, 1):
    if l.lstrip()[:3] in ("```", "~~~"):
        fence = not fence
        continue
    if not fence and re.match(r"^#{1,6} ", l):
        heads.append((i, len(l) - len(l.lstrip("#")), l.strip()))
pos = [h[0] for h in heads] + [len(src)]
vaos = sorted(((pos[i+1] - pos[i], pos[i]) for i in range(len(pos) - 1)), reverse=True)
print(f"linhas ................. {len(src)}")
print(f"cabeçalhos reais ....... {len(heads)}   (h4 ou mais fundo: {sum(1 for h in heads if h[1] >= 4)})")
print(f"antes do 1o '##' ....... {pos[1] - 1 if len(pos) > 1 else len(src)} linhas")
print(f"sumario ancorado ....... {'sim' if any('](#' in l for l in src[:80]) else 'NAO'}")
for n, l in vaos[:5]:
    if n > 50:
        print(f"  vao sem cabecalho: {n} linhas a partir da L{l}")
PY
````

O comando conta apenas cabeçalhos **reais**: linha de comentário dentro de bloco de código
começa por `#` e é contada por um `grep` ingênuo, o que já produziu diagnóstico com quase o
dobro do número verdadeiro.

---

## 4. O teste de leitura

O leitor chega com sete perguntas. O README passa no teste quando cada uma se resolve em
**no máximo dois saltos** — a primeira tela, ou o sumário, e daí o destino.

| # | A pergunta, como ele a faria | Onde ela tem de se resolver |
|---|---|---|
| 1 | "O que é isto, e é para mim?" | Primeira tela, frase única |
| 2 | "Por que existe, e o que ele **não** é?" | Primeira tela |
| 3 | "O que eu faço no primeiro minuto?" | Seção "Como começar", alcançável pelo sumário |
| 4 | "Já cloneei; o que eu faço hoje?" | Seção "no dia", com o comando copiável |
| 5 | "Onde está a coisa X?" | Tabela de donos, um salto |
| 6 | "O que está quebrado ou inacabado?" | Seção de estado, sem eu precisar procurar |
| 7 | "E se esta página não bastar?" | Tabela de donos |

**Como aplicar o teste sem se enganar.** Não leia o README de cima a baixo perguntando se a
resposta está lá — ela quase sempre está em algum lugar, e essa leitura aprova tudo. Faça o
contrário: para cada pergunta, **conte os saltos** desde a linha 1 até a resposta, e anote o
número da linha. Pergunta que exige rolar procurando, ou que exige ler duas seções para
juntar a resposta, reprova mesmo com o conteúdo presente.

---

## 5. Anti-padrões, com o defeito que cada um causa

1. **Inventário no lugar de uso.** O documento lista o que existe, pasta por pasta, e não diz
   em que momento se abre cada coisa. *Defeito:* o leitor termina sabendo o que há e sem saber
   o que fazer. O remédio é a seção 6 da estrutura, escrita por momento.
2. **Número escrito à mão.** Contagem que um comando calcula, colada em prosa.
   *Defeito:* envelhece calada, porque nenhum verificador olha para prosa.
3. **Transcrição colada de saída de comando.** O bloco de exemplo mostra o que o programa
   imprimiu num dia. *Defeito:* é a segunda cópia de um valor derivado, sem guarda nenhuma, e
   passa a ensinar uma saída que o programa não produz mais. Quando o exemplo for necessário,
   reduza-o à **forma** da saída, sem os valores que mudam.
4. **Registro de mudanças disfarçado de estado.** Itens riscados, histórico de resolução,
   datas de conserto. *Defeito:* cresce sem teto e empurra para baixo o que decide hoje.
5. **Manual dentro da porta de entrada.** O README explica o mecanismo em vez de apontá-lo.
   *Defeito:* duplica o vizinho, e a cópia que envelhece é a do README, que é a menos revisada.
6. **Tabela de donos incompleta.** O mapa "onde procurar" não lista todos os documentos.
   *Defeito:* o documento que falta fica inalcançável para quem não sabia que ele existia.
7. **Vocabulário de duas gerações.** O termo antigo sobrevive em transcrição, em nome de
   arquivo citado ou em legenda, enquanto a prosa já usa o novo. *Defeito:* o leitor conclui
   que são duas coisas diferentes e procura a distinção que não existe.
8. **Primeira tela sem comando.** O documento abre com contexto, e o primeiro comando
   copiável aparece muito depois. *Defeito:* gasta o espaço mais caro da página com o que o
   leitor ainda não sabe se lhe interessa (R2).
9. **Cabeçalho sem cheiro.** "Detalhes", "Notas", "Outros", "Diversos". *Defeito:* o leitor
   não consegue prever o que há embaixo e abandona a página antes de chegar lá (R5).
10. **Estado sem data e sem dono.** "Atualmente estamos em X", "por enquanto isto não
    funciona". *Defeito:* a ressalva sobrevive ao fato que a causou, e nada a derruba.
11. **Título que não é o nome.** A *Standard Readme* exige que o título coincida com o nome do
    repositório e da pasta. *Defeito:* quem chega por busca não confirma que achou a coisa certa.

---

## 6. Como refatorar um README que já existe

Siga na ordem. O passo 1 antes de qualquer edição, porque diagnóstico feito de memória
inventa defeito e perde o que importa.

1. **Meça.** Rode o comando da §3 e anote os quatro números. Rode também os verificadores do
   próprio projeto, quando houver, porque eles pegam o que a medição estrutural não vê.
2. **Reparta o conteúdo em quatro montes** pela decisão de fronteira da §1: fica no README ·
   vai para o guia técnico · vai para o mapa de arquitetura · **sai de todo documento, porque
   um comando responde**. Faça isso parágrafo a parágrafo, e não seção a seção — a mistura
   costuma estar dentro do parágrafo.
3. **Devolva cada monte ao dono antes de reescrever o README.** Mover primeiro e reescrever
   depois evita a tentação de "aproveitar" o texto que já estava bom no lugar errado.
4. **Reconstrua a primeira tela** contra as perguntas 1 a 3 do teste de leitura.
5. **Instale o sumário ancorado**, se o arquivo passar de cem linhas, e conserte os cabeçalhos
   que não têm cheiro (R5).
6. **Passe o teste de leitura contando saltos**, anotando o número da linha de cada resposta.
7. **Meça de novo** e confira as seis réguas.
8. **Feche com a revisão de prosa** — o agente `revisor-prosa-ptbr` e o padrão de
   `rules/common/writing-style.md`. A estrutura estar certa não torna a prosa legível.

---

## 7. O que a medição empírica mostra estar faltando

O estudo que anotou à mão **4.226 seções de README em 393 repositórios** do GitHub
(Prana e col., *Categorizing the Content of GitHub README Files*, Empirical Software
Engineering, 2019 — lido na versão [arXiv:1802.06997](https://ar5iv.labs.arxiv.org/html/1802.06997))
classificou cada seção em oito categorias e mediu a presença de cada uma. Três resultados
mudam o que se escreve:

- O **"o quê"** aparece em 97% dos arquivos e o **"como"** em 88,5%, ocupando sozinho 58,4%
  de todas as seções. Instrução é o que a prática já cobre bem.
- O **"por quê"** — propósito, vantagem, comparação com a alternativa — aparece em apenas
  **25,7%** dos arquivos. É a lacuna mais comum, e por isso a seção 2 da estrutura é obrigatória.
- O **estado** (versão, situação, roteiro) aparece em **21,4%**. Os autores observam que ele é
  o que dá confiança a quem chega, e é o segundo item obrigatório desta skill.

O mesmo estudo recomenda a ordem "o quê e por quê primeiro, instrução depois", que é a da §2.

**Três READMEs reais, e por que funcionam.** Cada um resolve a navegação de um jeito
diferente, e a diferença é o tamanho:

- [Flask](https://github.com/pallets/flask/blob/main/README.md) — cerca de 45 linhas e quatro
  cabeçalhos. **Não tem sumário e não precisa**, porque não explica nada: descreve, mostra um
  exemplo de doze linhas e manda o resto para o site de documentação. É a porta de entrada em
  estado puro.
- [fd](https://github.com/sharkdp/fd) — longo, com um sumário **de três links** na primeira
  tela ("Installation • How to use • Troubleshooting"), acima de tudo o mais. Prova que o
  sumário útil é o das perguntas frequentes, e não o índice completo dos cabeçalhos.
- [ripgrep](https://github.com/BurntSushi/ripgrep) — longo, e abre com uma seção
  "Documentation quick links" que faz as duas coisas ao mesmo tempo: navega por dentro e
  **delega para fora**, mandando o guia de uso inteiro para `GUIDE.md` e as dúvidas para
  `FAQ.md`. É o modelo para README que não pode encurtar.

---

## 8. O que esta skill não resolve

Declarado, porque skill que promete tudo não é seguida.

- **Não decide o conteúdo do `CLAUDE.md` nem do mapa de arquitetura.** Decide apenas a
  fronteira: o que sai do README e para onde vai. O que o vizinho faz com o texto recebido é
  governança dele.
- **Não escreve documentação de API, tutorial nem site de documentação.** Pelo modelo
  Diátaxis, essas são outras três espécies, e o README não é o lugar de nenhuma delas.
- **Não julga a prosa.** Coesão, salto lógico, anglicismo e frase sem verbo são do agente
  `revisor-prosa-ptbr` e da regra `writing-style.md`. Esta skill decide o que entra e onde
  fica; o outro decide se está legível.
- **Não confere fato.** Número, norma e afirmação de estado se conferem na fonte que os
  produz, e esta skill só diz que eles não devem estar escritos à mão.
- **Não substitui verificador do projeto.** Onde houver comando que compare documentação com
  disco, ele continua sendo a guarda; a skill apenas evita criar o que ele teria de pegar.
- **Não cobre o aparato de repositório público com muitos colaboradores** — selos de estado,
  código de conduta, política de segurança, guia de contribuição. Para esse caso, a
  *Standard Readme* já traz a lista completa e ordenada.
- **A régua R3 é derivada e não medida.** A conversão de "uma tela" em cinquenta linhas de
  fonte é estimativa desta skill, e não resultado do estudo citado.
