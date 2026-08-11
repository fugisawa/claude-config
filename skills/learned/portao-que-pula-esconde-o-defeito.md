---
name: portao-que-pula-esconde-o-defeito
description: O predicado de um portão condicional pergunta só a condição cuja negativa merece pular — quando ele pergunta "funcionou?", funde "o ambiente não está aqui" com "o ambiente está aqui e o código está quebrado", e o segundo se esconde atrás do primeiro por tempo indefinido
metadata:
  pattern: debugging_techniques
  origin: manual_estudo, sessão 11/08/2026
  confidence: alta (um caso de cinco meses, medido na fonte, mais um quase-caso na mesma sessão)
---

**O padrão.** Todo teste de integração tem um portão que decide se ele roda, e o portão é
escrito para poupar quem não tem o ambiente. O defeito nasce quando o predicado desse portão
pergunta **mais** do que precisava: em vez de "o ambiente está aqui?", ele pergunta "a
operação inteira deu certo?". As duas perguntas parecem a mesma e não são. A primeira tem uma
negativa só, e pular é a resposta certa para ela. A segunda tem duas — *o ambiente não está
aqui* e *o ambiente está aqui e o código está quebrado* — e as duas caem no mesmo `skip`.

O mecanismo é o booleano. **Um `bool` não tem espaço para dois motivos**, e um
`except Exception: return False` colapsa causas distintas num valor só. Qualquer portão
construído sobre esse valor herda a fusão, e o defeito passa a se esconder atrás da ausência
pelo tempo que for preciso.

## O caso, e os cinco meses que ele durou

O `config.json` do add-on AnkiConnect passou a exigir chave de API em **11/03/2026**. O
cliente do projeto montava o pedido com `action`, `version` e `params`, sem `key`, de modo que
toda ação voltava com `valid api key must be provided` — inclusive `version`. O
`--ankiconnect` estava, portanto, **inteiramente morto**.

Ninguém percebeu, e a razão é o portão:

```python
def _conectado() -> bool:
    try:
        return AnkiConnect().testar_conexao()   # devolve False para os DOIS estados
    except Exception:
        return False

pytestmark = pytest.mark.skipif(not _conectado(), reason="Anki/AnkiConnect não está acessível")
```

Em **11/08/2026**, com o Anki desktop aberto na mesma máquina e um `curl` autenticado
listando os decks **no mesmo minuto**, a suíte imprimia:

```
22 passed, 2 skipped
```

Trocado o predicado por uma pergunta de um estado só — a porta 8765 aceita conexão? —, os
três testes de integração reprovaram na hora, todos com a mesma mensagem. Corrigido o
cliente, a suíte foi para `25 passed`, sem nenhum pulo.

## Por que os dois registros vizinhos não pegam este

[[checagem-que-nao-pode-falhar]] trata de verificador **incapaz** de reprovar: o curinga que
casa tudo, o universo vazio, o padrão sem segmento literal. A regra de lá — *toda checagem
nova nasce com um teste que a vê reprovar* — **não teria pego este caso**, e é isso que
justifica registro novo em vez de emenda. Os três testes eram perfeitamente capazes de
reprovar, e reprovaram no primeiro instante em que puderam. Eles nunca rodaram.

[[negative-finding-vs-broken-probe]] é o parente próximo: `testar_conexao()` devolvendo
`False` é exatamente uma sonda quebrada lida como ausência. A diferença é o que cada registro
governa. Lá, como se **documenta** um achado negativo em pesquisa, onde o remédio é separar
observação de conclusão. Aqui, código de guarda que roda a cada suíte, onde o remédio é
escolher outro predicado.

## A regra

**O predicado pergunta só a condição cuja negativa merece pular, e no nível mais baixo que
separe os dois estados.** Uma porta que aceita conexão, um arquivo que existe, um binário no
`PATH`, uma variável de ambiente definida. Nunca "a operação inteira funcionou", porque essa
pergunta arrasta o defeito para dentro da condição de dispensa.

**O que o portão escondia vira teste dentro do portão.** Se antes ele pulava quando o
handshake falhava, agora existe um teste que afirma que o handshake funciona. Foi o menor
conserto possível e o que devolveu o sinal:

```python
def test_conexao_autenticada():
    """Porta aberta e handshake falhando é reprovação, nunca skip."""
    assert AnkiConnect().testar_conexao() is True
```

## O mesmo erro pelo outro caminho, na mesma sessão

Quase escrevi uma declaração em `~/.claude/docs/ambiente-por-maquina.md`, cujo doutor confere
apenas os comandos de uma tupla fixa e **ignora o resto de propósito** — "não declarado é
silêncio, não erro: a lista é curadoria". Declarar ali um comando fora da tupla produziria uma
linha que ninguém confere, com toda a aparência de estar coberta.

É a mesma família com outro predicado: lá o portão funde dois estados, aqui a declaração não
está ligada a quem a confere. A pergunta de projeto que pega as duas é uma só — **quais
estados do mundo este predicado funde, e algum deles é defeito?**

## Como aplicar

- Ao escrever um `skipif`, um `if:` de integração contínua ou um sinalizador de
  funcionalidade, escreva o predicado no nível mais baixo que separe presença de
  funcionamento. Se você precisou chamar a operação de negócio para decidir se pula, o
  predicado está no nível errado.
- Desconfie de `except Exception: return False` em qualquer função que alimente um portão.
  O booleano é onde os motivos morrem.
- **Leia o número de pulos.** `2 skipped` é o tipo de saída que ninguém lê, e era o único
  lugar onde estes cinco meses estavam escritos. Suíte que pula com o ambiente presente é
  suspeita, não conforto.
- Ao herdar um portão, rode a suíte **com** o ambiente montado e confira que o número de
  pulos cai a zero. Se não cair, o portão está respondendo outra pergunta.

Relacionado: [[checagem-que-nao-pode-falhar]] · [[negative-finding-vs-broken-probe]] ·
[[verify-claimed-state]]
