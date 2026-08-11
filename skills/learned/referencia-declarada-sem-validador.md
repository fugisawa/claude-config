---
name: referencia-declarada-sem-validador
description: Identificador escrito à mão em configuração — id de plugin, caminho de hook, exceção de .gitignore, caminho que embute o nome do usuário — nomeia um alvo enumerável que nenhum comando confere, e por isso a falha é sempre silenciosa; a defesa é listar o alvo e cruzar, não desconfiar
metadata:
  pattern: debugging_techniques
  origin: ~/.claude e manual_estudo, sessão de 11/08/2026 — quatro ocorrências no mesmo dia
  confidence: alta (quatro instâncias medidas, todas silenciosas, uma delas viva há semanas)
---

**O padrão.** Configuração está cheia de identificadores escritos à mão que apontam para um
alvo em outro lugar: um id `plugin@marketplace`, um caminho de script dentro de um hook, uma
exceção de whitelist no `.gitignore`, um caminho absoluto que embute o nome do usuário. Todos
têm a mesma propriedade e o mesmo defeito: **o alvo é enumerável — dá para listar e cruzar por
comando — e ninguém cruza.** Quando o identificador erra, nada reclama. O arquivo continua
dizendo `true`, o `jq` continua validando o schema, e o mecanismo simplesmente não existe.

É diferente de prosa que alega ("o cânone foi atualizado"), que é o caso do
[[verify-claimed-state]]. Lá a defesa é desconfiar e conferir à mão. **Aqui a defesa é uma
comparação de listas**, e é por isso que a lição vale: o custo de escrever a checagem é baixo,
e sem ela a coisa fica quebrada por semanas sem sintoma.

**As quatro ocorrências de 11/08/2026:**

| Onde | Declarava | O que era |
|---|---|---|
| `settings.json` → `enabledPlugins` | `everything-claude-code@everything-claude-code: true` | marketplace inexistente — foi renomeado para `ecc` lá em cima e a entrada nunca acompanhou. `installed_plugins.json` vazio, `plugins/repos/` vazio, e a pasta de dados do plugin nunca criada |
| `.gitignore` (whitelist) | `!skills/continuous-learning` | casa o nome exato e **não** cobre `-v2`; como o `settings.json` é versionado e o runtime não seria, a outra máquina receberia hook apontando para script inexistente |
| `CLAUDE.md` do projeto | memória em `projects/-home-danielfugisawa-…` | o nome da pasta deriva do caminho absoluto: existe numa máquina e não na outra |
| `build/charts/*.py` | `sys.path.insert(0, "/home/danielfugisawa/…")` | usuário morto; o script morria com `ModuleNotFoundError`, **culpando o pacote e não o caminho** |

**A pergunta que encontra os quatro:** *este identificador nomeia algo que eu consigo listar?*
Se sim, liste e cruze — `known_marketplaces.json` contra `enabledPlugins`, `git ls-files`
contra os caminhos citados em hooks, `ls` do diretório contra a whitelist. Se o alvo embute o
nome do usuário ou da máquina, ele já está errado numa das duas: derive de `Path.home()`, ou
declare a REGRA (o nome deriva do caminho, logo difere por máquina) em vez de um dos valores.

**O agravante, e é o que faz a falha durar:** o erro chega disfarçado de outra coisa. O caminho
morto acusou o pacote Python. O plugin quebrado não acusou nada — ele *parecia* ligado, e a
skill que dependia dele simplesmente não aparecia na lista, o que se lê como "ainda não
instalei" e não como "está quebrado".

**Onde isso vira mecanismo:** no `manual_estudo` a mesma classe já tinha dono para PDF
(`estudo/destino.py` deriva o caminho em vez de deixá-lo ser digitado) e ganhou dono para o
catálogo de matérias (`estudo/disciplinas.py`, que levanta em vez de devolver o slug). A
escada de `decisoes/0003` diz o porquê: convenção escrita é nível 0 e depende de alguém
lembrar; derivar é nível 3 e torna o erro impossível. Ver [[checagem-que-nao-pode-falhar]] para
a regra irmã — a checagem nova nasce com um teste que a vê reprovar.
