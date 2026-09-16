# Conferir um número no artigo, e escrever o que se conferiu

Conferir é ler a frase onde o número está, na versão certa do artigo, e deixar registrado o
caminho para que outra pessoa repita. Resumo, comentário de questão, texto de divulgação e a
memória do modelo não conferem nada.

## O protocolo

1. **Saiba qual versão está lendo.** O cabeçalho da primeira página diz o periódico, o DOI, as
   datas (recebido, aceito, publicado) e a paginação. Cópia diagramada pela editora com esses
   dados é a **versão publicada**. Manuscrito com a formatação do autor é a **versão aceita**,
   e o número pode ter mudado na revisão de provas; pré-publicação pode diferir ainda mais.
   O `abrir` grava a versão que a fonte declarou em `versao_do_texto`; quando ela vem vazia,
   decida pelo cabeçalho e escreva o que decidiu.
2. **Procure no texto, nunca só na tabela, nunca só no resumo.** Use
   `artigo.py conferir <slug>.txt "g = -0,36" "k = 48" "p < .001"`: a busca tolera sinal de
   menos tipográfico, vírgula decimal e espaçamento. Leia a linha e o contexto que ele imprime;
   se precisar de mais, `grep -n -C3 "playback" <slug>.txt`, ou `Read` com `offset` e `limit`
   numa janela. **Não leia o arquivo inteiro para o contexto**: um artigo de 27 páginas tem
   uns 25 mil tokens, e cada leitura dessas entra na próxima compactação.
3. **Anote os companheiros do número.** Para um tamanho de efeito: o modelo de onde ele saiu
   (categórico, linear, spline), `k` (quantos tamanhos de efeito o alimentam), o intervalo de
   confiança de 95% e o `p`. Um `g` sem `k` e sem intervalo é meio número.
4. **Quando texto e tabela divergem, registre os dois e diga qual fecha.** No caso de 16/09/2026,
   a Tabela 2 imprimia `k = 37` e `49` para 1,5× e 2×, e o texto dizia `36` e `48`; só o texto
   fechava com o `QE(95)` do modelo, então o texto mandou. Escreva isso no material, porque
   quem for conferir depois vai tropeçar na mesma tabela.
5. **Leia a ressalva dos autores.** O número raramente é a conclusão: em Tharumalingam e col.,
   os custos abaixo de 2× "não são estatisticamente distinguíveis de zero", mas 1,25× e 1,5×
   somados dão `g = −0,12` com `p = 0,041`, e os autores pedem cautela. "Sai de graça" foi
   corrigido para "custa pouco, e provavelmente não custa zero" por causa dessa frase.
6. **Feche com a data.** Conferência sem data envelhece calada: correções e retratações saem
   depois. `--conferido-em AAAA-MM-DD` põe a data no registro e no parágrafo.

## O que se escreve no material

O `abrir` imprime o parágrafo `Fonte:` já no padrão. A forma:

> Fonte: Tharumalingam e col. (2025), "Increasing Video Lecture Playback Speed Can Impair Test
> Performance – A Meta-Analysis", *Educational Psychology Review* 37(2), 35, DOI
> 10.1007/s10648-025-10003-9. Cópia obtida por Unpaywall em <url>, versão publicada, 27 páginas,
> SHA-256 fece3dafc697…; valores conferidos no texto em 2026-09-16.

Quando a cópia veio de degrau manual (site do autor, navegador, pedido), o script não sabe
disso: escreva a origem à mão, com o endereço e o que provou que é a versão publicada. Exemplo
do caso de 16/09/2026, gravado em `disciplinas/_infra/videoaulas.md`:

> A página da Springer mostra só o resumo; a conferência foi feita no PDF da versão publicada
> que o coautor Brady Roberts deposita no site dele (bradyrtroberts.ca), com o cabeçalho, o
> DOI, a data de aceite e a paginação do periódico.

No corpo, a frase que carrega o número diz que foi conferida: "valores conferidos no artigo em
16/09/2026". Sem isso o leitor não distingue o número lido do número lembrado.

## Quando nada abre

A bandeira fica: `⚑ não conferido em fonte primária`. Fonte secundária entra rotulada como
secundária ("segundo o resumo", "segundo Fulano (2026), que cita"). Não se escreve o número
com a confiança de quem leu. E registre o que foi tentado, com data, para que a próxima sessão
não repita a escada do zero: o diário do `abrir` serve para isso.

## O que vai para o repositório

- O parágrafo `Fonte:` e a frase com a data: sempre.
- O `.procedencia.json`: fica ao lado da cópia, no diretório de trabalho; entra no repositório
  só se a cópia entrar.
- A cópia do artigo: só quando a licença permite redistribuir (CC BY, CC BY-SA, domínio
  público), e aí pelas regras das decisões 0019 e 0020 do `manual_estudo` (fonte incorporada
  e o que ela pesa). Cópia sob licença exclusiva da editora, inclusive a que o autor deposita
  no site dele, **não entra**: o repositório guarda o endereço, o hash e a data.
