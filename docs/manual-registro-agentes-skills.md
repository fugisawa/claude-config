# Manual do registro de agentes e skills

Como o Claude Code carrega `~/.claude/agents/` e `~/.claude/skills/`, como isso
quebra em silêncio, e as ferramentas que detectam a quebra.

Escrito em 07/08/2026, depois de uma faxina que encontrou 16 colisões de nome e
**11 agentes que não registravam havia meses sem ninguém perceber**.

---

## 1. As regras do loader

Apuradas na doc oficial (`code.claude.com/docs/en/sub-agents`) e confirmadas na
prática. Elas explicam quase todos os defeitos deste repo:

| Regra | Consequência |
|---|---|
| A varredura de `agents/` e `skills/` é **recursiva** | Subpasta não esconde nada. `_archived/` era carregado normalmente. |
| Identidade vem **só do campo `name:`** | Caminho e nome de arquivo são irrelevantes. Renomear arquivo é inócuo; mudar `name:` muda a identidade de invocação. |
| Nome duplicado na mesma árvore → o loader guarda **um**, *"chosen by filesystem read order rather than a documented precedence"* | Com nome repetido, **não se sabe qual definição está ativa**. É erro, não estilo. |
| Não existe forma suportada de excluir arquivo **dentro** da árvore | Sem `enabled: false`, sem `.claudeignore`. `permissions.deny: ["Agent(nome)"]` bloqueia *invocação* mas o agente **continua carregando no contexto**. A única saída é tirar do diretório. |
| Só `name` e `description` são obrigatórios | `tools:` ausente = herda **todas** as ferramentas. `model:` ausente = herda o modelo da sessão (o mais caro). Sempre declare os dois. |
| O watcher só cobre diretórios que existiam no **início da sessão** | Depois de mover/criar pasta, **reinicie o Claude Code**. Verificar antes dá falso negativo. |

A `description` entra no contexto de **toda** sessão. É o único sinal de
roteamento: em skill, decide se dispara; em agente, decide se é escolhido.
Bloco `<example>` de diálogo ali dentro é puro desperdício — e, pior, costuma
quebrar o YAML.

## 2. A assimetria agente × skill (importante)

Frontmatter malformado **não** tem a mesma gravidade nos dois acervos, e isso é
empírico, não preferência:

- **Agente com YAML quebrado pode não registrar de jeito nenhum.** Em 07/08/2026,
  11 agentes (`ux-researcher`, `brand-guardian`, `api-tester`, …) simplesmente não
  existiam para o harness; ao consertar o frontmatter, o harness anunciou os 11
  como "novos agentes disponíveis". → **ERROR**.
- **Skill com YAML igualmente quebrado continua carregando.** `alpha-vantage` tem
  uma linha solta `--- Unknown`, `animejs-animation` abre com `--- ` (espaço à
  direita), e as duas aparecem na lista de skills. → **WARN** (frágil, não quebrado).

**Corolário para qualquer checker daqui pra frente: nunca seja mais estrito que o
loader.** Um parser rígido reporta como defeito o que funciona, e aí o relatório
vira ruído que ninguém lê.

## 3. As ferramentas

Em `~/.claude/scripts/` (versionado — exceção `!/scripts/` no `.gitignore`):

```bash
uv run --with pyyaml python ~/.claude/scripts/doctor_agents.py   # exit 1 se houver ERROR
uv run --with pyyaml python ~/.claude/scripts/doctor_skills.py
cd ~/.claude/scripts && uv run --with pyyaml python -m unittest discover -p 'test_*.py'
```

`registry_lint.py` é o núcleo comum (severidades, leitor tolerante de
frontmatter, detector de duplicata, renderização). Os dois `doctor_*` são finos.
25 testes cobrem o seam **`scan(root) -> Report`** — a única fronteira que
importa: varre o filesystem, resolve `{name: arquivo vencedor}`, audita.

O leitor tolera o que o loader tolera: delimitador com espaço à direita, linha
`--- texto` solta e **block scalar** (`description: |`, `>`). Esse último detalhe
não é cosmético — ler só o marcador `|` devolve description de 1 caractere e faz
o checker acusar de "não roteável" uma família inteira de skills perfeitas.

### O que cada código significa

| Código | Sev. agentes | Sev. skills | O que é |
|---|---|---|---|
| `duplicate-name` | ERROR | ERROR | dois arquivos com o mesmo `name:` — qual roda é indefinido |
| `invalid-frontmatter` / `malformed-yaml` | ERROR | WARN | YAML inválido (ver §2) |
| `missing-key` | ERROR | ERROR | falta `name` ou `description` |
| `no-frontmatter` | WARN | ERROR | em `agents/` há `.md` que não são agentes; em `skills/` um `SKILL.md` sem frontmatter é defeito |
| `echo-description` | — | WARN | description só repete o nome (`build` → "build") — **não há como rotear** |
| `thin-description` | — | WARN | < 25 chars: não diz quando disparar |
| `long-description` | > 800 | > 1500 | tripwire contra bloco `<example>` colado |
| `unslugged-name` | — | WARN | nome com espaço/maiúscula (`Agent Development`) — invoca-se por essa string exata |
| `name-*-mismatch` | WARN | WARN | `name:` ≠ arquivo/diretório: legal, mas impossível de achar pelo nome |

## 4. Convenções

- **Aposentar é mover, nunca apagar.** Boa parte de `skills/` está **fora do git**
  (o whitelist não cobre), então `rm` é irreversível de verdade. Destinos fora da
  árvore varrida, cada um com README explicando o critério e o comando de purga:
  hoje `agents-archive/` e `_retired-duplicates/`. O padrão é
  `_retired-<motivo>/`, que o Daniel purga com `rm -rf` quando tiver certeza —
  foi o que aconteceu com `_retired-mobile/`.
- **Ao mover algo com homônimo já no arquivo**, sufixe a origem
  (`backend-architect.root.md`, `ai-engineer.engineering.md`) — nunca sobrescreva.
- **Agente e skill com o mesmo nome não colidem tecnicamente** (namespaces
  distintos: ferramenta `Agent` vs `Skill`). Medi os 14 pares homônimos: só
  `legal-advisor` era o mesmo artefato (86%); os outros 13 tinham 1–6% de
  similaridade — conteúdos diferentes com nome igual. Portanto **renomear é a pior
  opção** (churn que quebra referências e não resolve nada) e **merge está errado**
  quando os dois modos servem a propósitos distintos: skill = instruções no
  contexto atual; agente = contexto próprio que devolve resultado. A saída certa é
  roteamento — desambiguar no `/ask-daniel`.
- **Skills citam subagentes por nome** (`subagent_type="x"`). Ao aposentar um
  agente, verifique: `grep -rn 'subagent_type="nome"' ~/.claude/skills/`.

## 5. Onde o contexto realmente é gasto

Medição de 07/08/2026, depois da faxina:

| Acervo | Itens | `description` carregada |
|---|---|---|
| agentes | 73 | ~15 mil chars (~3,8k tokens) |
| skills | 1.311 | ~224 mil chars (~56k tokens) |

**Os dois acervos têm doenças diferentes.** Os agentes estavam *inflados*: 56 deles
carregavam blocos `<example>` de diálogo, e cortar isso levou de ~27k para ~3,8k
tokens sem perder sinal de roteamento. As skills **não** estão infladas — mediana
de 175 chars, p95 de 272. O custo delas é **população**, não gordura.

Daí a regra: em agente, corte texto; em skill, curadoria — só sai skill inteira, e
isso é decisão do Daniel, não do checker. Foi assim que saíram 36 skills de
mobile/iOS/Expo/HIG (ele não faz app) e 3 duplicatas byte a byte.

## 6. Histórico

- **07/08/2026** — 139 → 73 agentes; 16 → 0 erros; description de ~27,4k → ~3,8k
  tokens. 11 agentes voltaram a existir. `_archived/` (48 arquivos) saiu da árvore.
  Merge de `backend-architect`/`frontend-developer` (corpo `engineering/` + pin
  `sonnet`). Aposentados: pacote studio (26), podcast alheio (4), twitter, e
  `legal-advisor`. `academic-researcher` tinha ~90 ferramentas — incluindo escrita
  no GitHub e dois MCPs inexistentes — e nenhuma de pesquisa; refeito com Consensus
  /Exa/Tavily. Skills: 3 duplicatas byte a byte removidas, 36 de mobile aposentadas.
  Nasceram `doctor_agents.py`, `doctor_skills.py`, `registry_lint.py`.
