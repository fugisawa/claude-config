# Pedido de cópia ao autor

Autores podem enviar cópia do próprio artigo a quem pede: a política de compartilhamento das
editoras permite ao autor compartilhar o manuscrito aceito, e em geral a versão publicada, em
privado com colegas, para uso pessoal (a da Elsevier foi conferida em 16/09/2026; a de outra
editora se confere no Open Policy Finder, pelo navegador da app). A cópia que chega assim é
rota A. O pedido é curto, diz por que o artigo interessa e não pede nada além da cópia.

## Quem faz o quê

1. **A skill redige.** `python3 artigo.py pedido <doi> --tema "<motivo concreto>" --para <e-mail>`
   devolve `to`, `subject` e `body`; com `--json`, prontos para o conector.
2. **A sessão cria o rascunho** com o conector Gmail, `create_draft`, e diz ao Daniel onde
   está. `send_message` não entra na skill, por decisão e por teste: quem envia é o Daniel,
   depois de ler.
3. **A pendência vai para o material.** `artigo.py abrir <doi> --pendencia "<a linha que o
   pedido imprime>" --reavaliar-em <data>` põe no recibo o nome do autor, a data e a data antes
   da qual não se repete.
4. **Quando o Daniel enviar**, a linha da pendência troca "rascunhado" por "enviado", no recibo e
   no material; a data antes da qual não se repete não muda. Foi o que aconteceu em 16/09/2026
   com o pedido a T. Tharumalingam, enviado pelo `send_message` do conector com o `draftId` do
   rascunho, depois do "pode enviar" explícito.

## As regras

- Um pedido por autor por artigo; sem resposta, não repetir antes de 30 dias.
- Ao autor de correspondência: o OpenAlex marca `is_corresponding`, e sem a marca o `pedido`
  sugere o primeiro autor e avisa. O e-mail vem da primeira página do artigo ou da página do
  DOI no navegador da app; Crossref e OpenAlex não o têm, e o script não o procura.
- Até 120 palavras. Com título longo, o `pedido` retira sozinho a frase sobre a política da
  editora e diz quantas palavras ficaram.
- No idioma do autor: português para autor de país lusófono, inglês para os demais; `--idioma`
  força.
- Com o DOI, o motivo concreto (`--tema`, escrito no idioma do pedido, porque ele entra no corpo
  sem tradução), a promessa de uso pessoal, e sem pressão.
- Elsevier: o pedido inclui a alternativa do Share Link, que o autor gera e que dá acesso por
  prazo limitado (o prazo de 50 dias não foi conferido).
- Em paralelo, o botão de pedido do ResearchGate. Nunca Sci-Hub e espelhos.

## O que sai

O `scripts/pedido.py` é a fonte dos modelos; o que está abaixo é a saída dele.

Em inglês, assunto `Request for a copy of "<título>"`:

> Dear Dr. <sobrenome>,
>
> I am preparing study material on <tema> and would like to read your article "<título>"
> (<periódico>, <ano>), doi:<doi>. I have no institutional access to the journal, and the
> open-access routes I tried found no copy.
>
> Could you send me the accepted manuscript or the published version? Most publishers' sharing
> policies allow authors to share a copy privately with colleagues for personal use. I will use
> it for reading and citation only and will not redistribute it.
>
> Thank you,
> <assinatura>

Em português, assunto `Pedido de cópia do artigo "<título>"`:

> Prezado(a) Prof(a). <sobrenome>,
>
> Estou preparando material de estudo sobre <tema> e gostaria de ler o artigo "<título>"
> (<periódico>, <ano>), doi:<doi>. Não tenho acesso institucional ao periódico, e as vias de
> acesso aberto que tentei não têm cópia.
>
> Seria possível me enviar o manuscrito aceito ou a versão publicada? A política de
> compartilhamento da maioria das editoras permite ao autor enviar cópia a colegas para uso
> pessoal. O uso é só leitura e citação, sem redistribuição.
>
> Obrigado,
> <assinatura>

## Enquanto a resposta não chega

O valor fica com a bandeira `⚑ não conferido em fonte primária`, o recibo carrega a pendência,
e o material diz de onde veio o número que está lá (resumo, fonte secundária). A resposta
costuma vir em dias; quando vier, `artigo.py registrar <doi> --arquivo <a cópia> --url
"e-mail do autor" --origem "enviada pelo autor" --etiqueta A --versao <a que o cabeçalho diz>`,
depois `conferir`, e o parágrafo `Fonte:` substitui a bandeira.
