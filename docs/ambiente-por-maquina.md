# Ambiente por máquina — a declaração

Este arquivo existe porque `~/.claude` é **um clone em mais de uma máquina**, e o
`CLAUDE.md` é carregado inteiro nas duas. Toda frase que diga "**esta** máquina" num arquivo
compartilhado é infalsificável: "esta" resolve diferente conforme quem lê, então nenhuma das
máquinas consegue detectar que a frase está errada *para ela*. A prosa vira segunda cópia do
estado real e diverge calada — ver
[`skills/learned/a-segunda-copia-da-regra-diverge-calada.md`](../skills/learned/a-segunda-copia-da-regra-diverge-calada.md).

**Aconteceu, e não foi sutil.** Em 10/08/2026 o `CLAUDE.md` afirmava quatro coisas sobre
"esta máquina"; três estavam erradas na máquina do trabalho:

| Afirmação no `CLAUDE.md` | Medido em 10/08/2026 (OptiPlex) |
|---|---|
| "sem conda/**nvm**" · "Não instale nvm" | nvm presente, **4 versões**, bloco vivo no `.bashrc` |
| "Node do sistema é **18**" | `/usr/bin/node` é **v20.20.2** |
| "`bat`=`batcat`" | **`batcat` não existe**; `bat` responde direto (brew) |
| "Sem ImageMagick" | ✅ verdadeiro (`magick`/`convert` ausentes) |

Seguir a instrução do `batcat` **falharia**; a do nvm mandava não instalar o que já estava
instalado. Por isso os fatos que variam por máquina moram aqui, com **uma seção por
máquina**, e o `CLAUDE.md` guarda só o que é verdade nas duas.

## Como preencher a sua seção

A chave é o **machine-id**, não o `hostname` — as duas máquinas se chamam `fugisawa`, e chave
que colide faz a máquina de casa ler a linha do trabalho como sua, em silêncio.

```bash
# identidade
echo "$(cat /sys/devices/virtual/dmi/id/sys_vendor) $(cat /sys/devices/virtual/dmi/id/product_name) · id=$(cut -c1-8 /etc/machine-id) · $(hostname)"
# ambiente
bash -ic 'node --version'; command -v node; /usr/bin/node --version 2>/dev/null
ls ~/.nvm/versions/node 2>/dev/null; for c in conda bun uv pyenv brew bat batcat fd fdfind rg magick convert; do printf '%s: %s\n' "$c" "$(command -v $c || echo AUSENTE)"; done
```

Regra ao preencher: **só entra o que foi medido.** Preferência ("eu tendo a usar a estável
mais nova") vai para a linha *Preferência declarada*, nunca para a coluna do estado — as duas
não podem ocupar a mesma célula, senão daqui a um mês ninguém sabe qual das duas se está
lendo.

---

## Máquina A — trabalho · Dell OptiPlex 7070 · `id=19aeb4de`

**Medido em 10/08/2026.** Ubuntu 24.04.4 LTS.

| Item | Estado |
|---|---|
| node (shell **interativo**) | **v24.18.0**, via nvm |
| node (**não**-interativo, o que os scripts pegam) | **v26.7.0**, `/home/linuxbrew/.linuxbrew/bin/node` |
| node do apt | v20.20.2 (`/usr/bin/node`) |
| nvm | **presente** — v24.14.0, v24.16.0, v24.17.0, v24.18.0; bloco vivo no `.bashrc` |
| conda | ausente |
| uv · pyenv · bun | 0.12.3 · 2.8.3 · 1.3.14 |
| brew | 6.0.16 (`/home/linuxbrew`) |
| `bat` | responde **direto** (brew) — **`batcat` não existe aqui** |
| `fd` | responde **direto** (`~/.local/bin/fd`); `fdfind` também existe (apt) |
| ImageMagick | **ausente** — imagem via `uv run --with pillow python` |
| rede | corporativa, **TLS interceptado** (`fw.abin.gov.br`) — apt quebra em repo de VPN; contorno `--fix-missing` |

**Armadilha desta máquina:** o node muda conforme o shell. Interativo dá v24 (nvm);
não-interativo dá v26 (brew). Script que assume uma versão só quebra num dos dois modos, e o
`command -v node` **mente** sobre o que você vê no terminal.

---

## Máquina B — casa · `PENDENTE`

> **RECADO PARA A SESSÃO DE CASA.** Esta seção nunca foi medida — a máquina do trabalho não
> tem como saber o que existe aí, e **inventar um valor plausível seria pior que deixar
> vazio**, porque a tabela pareceria completa. Rode o bloco *Como preencher a sua seção* aí em
> cima, substitua esta seção pelo resultado, e commite. Quando as duas seções existirem,
> decidimos o que é comum às duas (sobe para o `CLAUDE.md`) e o que é local (fica aqui).
>
> Já se sabe, **por declaração do Daniel e não por medição**:
> - conda **não** é usado em casa também;
> - *Preferência declarada:* ele tende a preferir a versão estável mais atual do node — mas
>   **não sabe** qual está instalada lá, nem em que estado está o ambiente. Preferência não é
>   estado: preencha o que a máquina responder, mesmo que contrarie a preferência. Se
>   contrariar, isso é justamente o achado.

| Item | Estado |
|---|---|
| node (interativo / não-interativo / apt) | `pendente` |
| nvm | `pendente` |
| conda | ausente (declarado pelo Daniel, não medido) |
| uv · pyenv · bun · brew | `pendente` |
| `bat` / `fd` | `pendente` — confira se é `bat`/`batcat` e `fd`/`fdfind` |
| ImageMagick | `pendente` |
| rede | doméstica — sem interceptação de TLS conhecida |

---

## O que já é comum às duas (e por isso vive no `CLAUDE.md`)

- **conda não é usado** em nenhuma das duas.
- `uv` + `pyenv` + `bun` são o stack de fato.
- `rg` (ripgrep) responde direto nas duas.

Quando a Máquina B for medida, o que coincidir sobe para cá; o que divergir fica na seção de
cada uma. **Nada volta a ser escrito como "esta máquina".**
