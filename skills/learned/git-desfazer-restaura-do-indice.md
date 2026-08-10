---
name: git-desfazer-restaura-do-indice
description: "`git checkout --` de um arquivo restaura do ÍNDICE e não do HEAD — se ele já foi para o stage, o comando de desfazer devolve exatamente a versão que se queria desfazer, com sucesso e sem aviso"
metadata:
  pattern: error_resolution
  origin: manual_estudo, sessão 09/08/2026
  confidence: alta (duas ocorrências no mesmo dia, uma com custo real)
---

**O caso.** Para conferir que um verificador novo era capaz de reprovar, uma sessão trocou o
título de um passo numa `trilha.md`, deu `git add` para o gancho enxergar o arquivo, viu o
gancho barrar, e mandou desfazer restaurando o arquivo. O comando **saiu zero e não desfez
nada**: ele restaura a partir do índice, e o índice já tinha a versão contaminada.

O canário ficou no acervo. E como aquele arquivo é a fonte de um índice gerado, o defeito se
propagou: o PDF publicado passou a estampar `02 · CANARIO` no lugar do nome do passo.

**Aconteceu duas vezes no mesmo dia, com o mesmo comando.** Na primeira, um `assert False`
esquecido num módulo — custo zero, porque o próprio gancho o pegou no commit seguinte. Na
segunda o custo foi real, porque **arquivo de conteúdo não tem gancho que o leia como
conteúdo**: ele é fonte, e o derivado herdou o defeito em silêncio.

## O que fazer

```bash
git checkout HEAD -- <arquivo>
git restore --source=HEAD --staged --worktree <arquivo>    # equivalente moderno
```

## A lição que generaliza além do comando

**Conferir um verificador com canário exige que o canário saia no mesmo comando**, ou que se
use cópia temporária em vez do arquivo real. Canário esquecido no acervo é indistinguível de
conteúdo — quem ler depois não tem como saber que aquilo era teste.

E o risco de deixá-lo é maior que o de publicar uma checagem não conferida, o que inverte a
intuição de quem está sendo cuidadoso.

## Um efeito colateral que vale saber

O hook `block-dangerous-git.sh` deste ambiente barra o padrão perigoso pelo texto do comando.
Ele **também barra a menção dele dentro de um documento** — escrever esta skill por heredoc
no shell foi bloqueado. Não é defeito do hook: é o preço de uma guarda textual, e a saída é
gravar o arquivo pela ferramenta de escrita em vez do shell.

Relacionado: [[verify-claimed-state]] — "desfiz" também é alegação, não fato.
