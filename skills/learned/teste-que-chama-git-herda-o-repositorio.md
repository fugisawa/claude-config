---
name: teste-que-chama-git-herda-o-repositorio
description: Teste que monta repositório temporário e chama `git` com `cwd` continua escrevendo no repositório REAL — `GIT_DIR` e `GIT_INDEX_FILE` vencem o `cwd`, e o gancho de pre-commit define essas variáveis
metadata:
  pattern: error_resolution
  origin: manual_estudo, sessão 09/08/2026
  confidence: alta (derrubou três commits seguidos; medido antes e depois)
---

**O caso.** Um teste montava um repositório git em diretório temporário e chamava
`subprocess.run(["git", "add", "-A"], cwd=tmp)`. Correto na aparência, e errado: **o `git` lê
o repositório em que opera de variáveis de ambiente**, e elas vencem o `cwd`.

O gancho de pre-commit roda a suíte com `GIT_DIR` e `GIT_INDEX_FILE` apontando para o
repositório de verdade. Então o `git add` do teste gravava **no índice real** uma entrada
para um caminho que existe nos dois lados, apontando para um objeto que morria no
`tearDown`.

**O sintoma engana:**

```
error: invalid object 100644 35b442bb… for 'disciplinas/afo/trilha.md'
Error building trees
```

Parece corrupção do repositório, e não é — é um teste escrevendo fora do próprio diretório.
Derrubou três commits seguidos antes de alguém desconfiar do teste em vez da concorrência
entre sessões.

Medido antes e depois, porque diagnóstico sem medida é palpite: a entrada ia de `848ba228`
para `35b442bb`, e o segundo não existia naquele repositório.

## O que fazer

```python
SEM_GIT_HERDADO = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
subprocess.run(["git", *args], cwd=tmp, env=SEM_GIT_HERDADO)
```

**Apontar `GIT_INDEX_FILE` para um índice privado não protege** — o teste envenena justamente
o índice que a variável indica. Isso isola de outra sessão; não isola do próprio gancho.

## A guarda, porque consertar o arquivo não impede o próximo

Um teste que varre os arquivos de teste e reprova quem chama `git` sem passar `env=`. Sem
ela o defeito volta na próxima vez que alguém precisar de um repositório temporário, e nada
o impede — é a mesma razão pela qual se trava a direção dos imports em vez de confiar.

Relacionado: [[checagem-que-nao-pode-falhar]] · [[git-desfazer-restaura-do-indice]]
