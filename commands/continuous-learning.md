---
description: Extrai as lições desta sessão sob demanda — propõe, deduplica contra o acervo e só grava com o seu ok (o hook Stop já faz a passagem automática; este comando é o mid-session, com juízo)
argument-hint: "[assunto para focar] (vazio = a sessão inteira)"
allowed-tools: Read, Grep, Glob, Write, Edit, Bash(ls:*), Bash(git log:*), Bash(git diff:*)
---

# /continuous-learning — o que esta sessão ensinou

Foco: **$ARGUMENTS** (se vazio, a sessão inteira).

## O que já existe, e por que este comando não repete nada

O extrator automático **já está ligado** desde 19/07/2026: o hook `Stop` do `settings.json`
chama `~/.claude/skills/continuous-learning/evaluate-session.sh`, que varre a sessão no fim e
escreve em `~/.claude/skills/learned/`. Os limiares dele estão em
`~/.claude/skills/continuous-learning/config.json`.

O que o hook **não** faz, e é a razão deste comando: rodar **no meio da sessão**, quando a
lição ainda está quente e você pode dizer se ela é lição ou acaso; e **decidir onde** o
conhecimento mora, que é juízo e não varredura.

## Procedimento

### 1. Leia o acervo ANTES de propor
Não proponha nada sem ter lido o que já existe — a duplicata é o defeito, não o esquecimento:

- `ls ~/.claude/skills/learned/` e leia o `description:` de cada candidato próximo;
- `MEMORY.md` do projeto (`~/.claude/projects/<caminho-com-hífens>/memory/`);
- se estiver no `manual_estudo`: `decisoes/` e a tabela de lacunas do `ARQUITETURA.md`.

### 2. Selecione com a régua, não com entusiasmo
Uma lição entra se **o mundo a impôs**, e a prova disso é o defeito que a originou. Pergunte
de cada candidata:

- **Custou alguma coisa medida?** Quantas vezes mordeu, quanto tempo, o que quebrou. Sem isso
  é opinião, e opinião não vira lição.
- **Vai reaparecer?** Conserto de um caso é conserto; padrão é o que se repete.
- **Já está escrita?** Se sim, o certo é **estender a existente**, não criar irmã.

Rejeitar é o caso comum. Uma sessão que não ensinou nada é uma sessão normal, e forçar
extração produz exatamente o acervo inflado que a camada `skills-archive/` existe para conter.

### 3. Decida ONDE mora — e essa é a decisão que mais erra

| O conhecimento é… | Vai para |
|---|---|
| padrão de trabalho reusável entre projetos | `~/.claude/skills/learned/<slug>.md` |
| fato deste projeto (estado, alvo, decisão operacional) | memória do projeto + linha no `MEMORY.md` |
| **mudança de rumo** difícil de reverter, surpreendente e com alternativa real recusada | `decisoes/NNNN-*.md` do projeto — as três condições juntas |
| procedimento que a máquina executa | não é lição: é código, teste ou gancho |

A última linha é a que mais salva. Se dá para transformar em verificação, **transforme** — a
escada de `decisoes/0003` manda atacar no nível mais alto que a natureza da lacuna permite, e
convenção escrita é o nível 0, que depende de alguém lembrar.

### 4. Escreva no formato da casa
Frontmatter idêntico ao do acervo — o `name:` é a identidade do registro e não pode colidir:

```yaml
---
name: <slug-em-kebab>
description: <uma frase longa que É a lição, não o assunto dela>
metadata:
  pattern: error_resolution | user_corrections | workarounds | debugging_techniques | project_specific | knowledge_management
  origin: <de onde veio, com data>
  confidence: alta | média | baixa (<por quê, em poucas palavras>)
---
```

O corpo abre com **`**O padrão.**`** e traz o defeito que originou a regra, com número quando
houver. Lição sem o custo que a produziu é regra sem procedência.

### 5. Lição aceita não se edita
Se uma lição do acervo ficou errada, **escreva a nova declarando qual ela supera** e marque a
antiga como superada. Reescrever no lugar apaga a evidência que dava autoridade à regra e
esconde que houve mudança de ideia — ver `learned/licao-aceita-nao-se-edita.md`.

### 6. Portão: proponha, não grave
Apresente cada candidata como **título + a frase da lição + onde vai + por que não é duplicata
de X**. Grave só depois do ok. Se nada passou a régua, diga isso em uma linha — é resposta
legítima e a mais comum.

## Depois de gravar

- Skill nova user-reachable → atualize o router `skills/ask-daniel/SKILL.md`, senão ele mente.
- Rode `scripts/doctor_skills.py` e `scripts/doctor_router.py` (exit 1 = erro; o do router pega
  citação órfã, que não dá erro sozinha).
- **Reinicie o Claude Code** — o watcher só enxerga diretório que existia no início da sessão.
