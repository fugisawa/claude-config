---
name: guarda-de-idempotencia-precisa-de-identificador
description: Guarda de idempotência que procura string derivada do próprio efeito falha nos dois sentidos — se a string muda ao aplicar, o script reaplica; se ela já existia por outro motivo, ele pula em silêncio; o guarda tem de perguntar pela ESTRUTURA que ele mesmo cria, e a prova de que ele funciona é uma contagem derivada, não a saída do script
metadata:
  pattern: error_resolution
  origin: manual_estudo, 30/08/2026 — duas instâncias da mesma forma em minutos, uma reaplicando em 21 arquivos e outra pulando 2 em silêncio
  confidence: alta (duas instâncias medidas na mesma sessão, com falhas em sentidos opostos, e nenhuma das duas visível na saída do próprio script)
---

**O padrão.** Script que edita muitos arquivos precisa saber se já rodou naquele arquivo, e a
tentação é perguntar ao texto: *"a marca que eu escrevo já está aí?"*. A pergunta parece
segura e tem duas maneiras de errar, opostas entre si:

- **A marca muda ao ser aplicada.** O guarda procura a forma que ela tinha *antes*, não a
  encontra depois, e o script **reaplica**.
- **A marca já existia por outro motivo.** O guarda a encontra sem que o script tenha rodado,
  e ele **pula em silêncio**.

A regra que separa: **o guarda tem de perguntar pela estrutura que o script cria, e nunca por
uma palavra que qualquer prosa pode conter.** Estrutura é identificador; palavra não é.

**Instância 1 — o guarda que comparava um número que ele mesmo mudava.** O script inseria uma
seção `## N · Escreva` antes da seção `## N · Onde treinar`, renumerando esta para `N+1`. O
guarda era:

```python
i, n = achado[0]                                    # n = número de "Onde treinar" AGORA
if any(re.match(rf"^## {n} · Escreva\s*$", l) for l in linhas):
    return 0                                        # já rodou
```

Depois da primeira passada, "Onde treinar" virou `N+1`, então o guarda passou a procurar
`## N+1 · Escreva` — que não existe, porque a seção inserida se chama `## N · Escreva`. Rodei
o laço duas vezes por engano e ele **inseriu tudo duas vezes em 21 capítulos**. O conserto foi
trocar o número pela existência: `r"^## \d+ · Escreva\s*$"`.

**Instância 2 — o guarda que procurava uma frase de prosa.** O segundo script acrescentava uma
terceira condição a um bloco, e se protegia assim:

```python
if "E há uma terceira" in texto:
    return 0
```

**Dois dos 21 capítulos já continham essa frase** por motivo inteiramente alheio — um falava de
três agravantes de um tema jurídico, o outro de um terceiro teste de fechamento. Os dois foram
pulados, ficaram sem a régua, **e o script imprimiu `pulado` como se tivesse trabalhado**.

**O que revelou o defeito, e é a parte que mais vale.** Nenhuma das duas falhas aparecia na
saída do script: a primeira imprimia `OK` 21 vezes (corretamente, ela de fato inseriu), e a
segunda imprimia `pulado`, que é uma palavra tranquilizadora. O que as pegou foi um **registro
derivado** que contava os itens produzidos e devolveu **84 onde deviam existir 42**; a segunda
só apareceu ao varrer os arquivos procurando quem **não** tinha a marca final.

Daí o corolário operacional: **script de edição em massa nasce com um contador derivado ao
lado**, e a conferência é o contador, nunca a saída do script. `grep -L` — os arquivos que
**não** casam — é o comando que pega o pulo silencioso, e ele é o inverso do que a intuição
manda rodar.

**Por que não é [[guarda-nao-pode-derivar-do-guardado]].** Lá o defeito é de arquitetura: um
verificador reimplementa a regra do código que guarda, as duas cópias concordam, e concordar é
o que torna a guarda inútil. Aqui a guarda é uma cláusula dentro do próprio mutador, e o
defeito é de **escolha de chave**: ela usa como identificador algo que não identifica.

**Por que não é [[checagem-que-nao-pode-falhar]].** Aquela trata de verificador cuja saída
limpa afirma cobertura inexistente. Esta trata de mutador que **aplica duas vezes ou nenhuma**,
e cuja saída é honesta sobre o que fez — só não é capaz de dizer que fez errado.
