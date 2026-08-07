---
name: measurement-broke-not-the-code
description: Quando a métrica despenca logo DEPOIS de você mudar a representação do objeto medido, suspeite primeiro do instrumento — a mesma edição que muda o render costuma quebrar o harness de medição em silêncio
metadata:
  pattern: debugging_techniques
  origin: manual_estudo, formato norma do vade mecum, sessão 07/08/2026
  confidence: alta (quase reescrevi CSS correto por causa disso)
---

**O caso:** eu media o alinhamento de dispositivos legais no PDF pegando o x0 do caractere N da
linha, com N = comprimento do rótulo (`"§ 1º"` → índice 4). Ao corrigir o alinhamento, troquei o
rótulo para `position: absolute` — o que o tira do fluxo e **muda a ordem dos caracteres** que o
extrator devolve para aquela linha. A medição passou a reportar **0/47 parágrafos alinhados**,
catastrófico e logo após a mudança. Ia reescrever o CSS. Remedindo por PALAVRA (`extract_words`)
em vez de índice de caractere: **47/47 alinhados**. O CSS estava certo desde a primeira tentativa;
quem quebrou foi a régua.

**O padrão:** um harness de medição faz suposições sobre a REPRESENTAÇÃO do objeto (ordem de
caracteres, contagem de nós, formato do texto extraído). Mudar o render costuma violar exatamente
essas suposições — e o harness não avisa, só passa a mentir. O sinal característico é temporal:
a métrica não degrada, ela **despenca**, e despenca na edição em que você mexeu no objeto.

**Como aplicar:**
- Métrica que vai de "quase tudo certo" para "quase tudo errado" numa só edição: suspeite do
  instrumento antes do código. Degradação gradual é bug; colapso súbito costuma ser régua quebrada.
- Meça pela unidade semântica mais alta disponível (palavra, elemento, nó), não por índice/offset.
  Índice é frágil a qualquer mudança de layout ou de serialização.
- Confirme com um segundo método independente antes de agir sobre uma medição ruim. Aqui bastou
  trocar índice-de-caractere por palavra.
- Não escreva a medição ruim como fato no relatório antes de checá-la. Eu anunciei "0/47
  desalinhados" ao usuário e tive de me corrigir na mensagem seguinte.

**Parente:** vale também quando o objeto muda de fonte (outro parser, outra origem do HTML) — a
régua calibrada na fonte A não vale na fonte B sem reconferir.
