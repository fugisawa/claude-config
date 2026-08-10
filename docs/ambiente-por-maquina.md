# Ambiente por máquina — a declaração

Este arquivo existe porque `~/.claude` é **um clone em mais de uma máquina**, e o
`CLAUDE.md` é carregado inteiro nas duas. Toda frase que diga "**esta** máquina" num arquivo
compartilhado é infalsificável: "esta" resolve diferente conforme quem lê, então nenhuma das
máquinas consegue detectar que a frase está errada *para ela*. A prosa vira segunda cópia do
estado real e diverge calada — ver
[`skills/learned/a-segunda-copia-da-regra-diverge-calada.md`](../skills/learned/a-segunda-copia-da-regra-diverge-calada.md).

**Aconteceu, e não foi sutil.** Achado de **10/08/2026**, na máquina do trabalho — registro
datado, que não se edita depois: das quatro afirmações que o `CLAUDE.md` fazia sobre "esta
máquina", **três estavam erradas**. Dizia "não instale nvm" com o nvm instalado e quatro
versões no disco; dizia "node do sistema é 18" onde o apt tinha v20.20.2; e mandava usar
`batcat`, **que não existe ali** — seguir a instrução falharia. Só "sem ImageMagick" era
verdade.

## A regra deste arquivo

**Um bloco ` ```decl ` por máquina, e ele é a fonte única.** A prosa em volta explica e
adverte, mas **nunca repete um valor** — valor repetido em prosa é a segunda cópia que este
arquivo existe para eliminar.

Declara-se **comportamento, não leitura**: o dono do node e o *major* (`nvm v24`), jamais o
patch. `v24.18.0 → v24.19.1` não muda nada para quem lê a instrução, e reprovar isso faria o
gancho apanhar `--no-verify` em uma semana. O que muda comportamento é comando que aparece
ou some, dono que troca, major que anda.

A chave é o **`machine-id`**, não o `hostname`: as duas máquinas se chamam `fugisawa`, e
chave que colide faz uma ler a seção da outra como sua, em silêncio.

Guarda: `uv run --with pyyaml python scripts/doctor_ambiente.py` (exit 1 na divergência),
que roda no `pre-commit`. Sem ele esta declaração envelheceria exatamente como a prosa que
ela substituiu.

## Como preencher a sua seção

```bash
echo "machine-id: $(cut -c1-8 /etc/machine-id)"
echo "rotulo: $(cat /sys/devices/virtual/dmi/id/sys_vendor) $(cat /sys/devices/virtual/dmi/id/product_name)"
bash -ic 'command -v node; node --version'          # interativo (o do terminal)
command -v node && node --version                    # não-interativo (o dos scripts)
/usr/bin/node --version 2>/dev/null                  # o do apt
for c in bat batcat fd fdfind rg conda uv pyenv bun brew magick convert; do
  printf '%s: %s\n' "$c" "$(command -v $c >/dev/null && echo presente || echo AUSENTE)"; done
[ -s ~/.nvm/nvm.sh ] && echo "nvm: presente" || echo "nvm: AUSENTE"
```

**Só entra o que foi medido.** Preferência ("tendo a usar a estável mais nova") vai para a
prosa, nunca para o bloco — as duas não podem ocupar a mesma célula, senão daqui a um mês
ninguém sabe qual das duas está lendo.

---

## Máquina A — trabalho · Dell OptiPlex 7070

Ubuntu 24.04.4 LTS. Rede corporativa com **TLS interceptado** (`fw.abin.gov.br`): o apt
quebra em repositório de VPN, e o contorno é `--fix-missing`. Não é defeito da máquina.

```decl
machine-id: 19aeb4de
rotulo: trabalho · Dell OptiPlex 7070
medido-em: 2026-08-10
node-interativo: nvm v24
node-nao-interativo: brew v26
node-apt: apt v20
presentes: bat, fd, fdfind, rg, nvm, uv, pyenv, bun, brew
ausentes: batcat, conda, magick, convert
```

**Armadilha desta máquina:** o node muda conforme o shell — o interativo vem do nvm, o
não-interativo vem do brew. Script que assuma uma versão só quebra num dos dois modos, e o
`command -v node` de dentro de um script **mente** sobre o que aparece no terminal.

---

## Máquina B — casa

> **RECADO PARA A SESSÃO DE CASA.** Esta seção nunca foi medida. A máquina do trabalho não
> tem como saber o que existe aí, e **inventar valor plausível seria pior que deixar
> pendente**, porque a tabela pareceria completa e o doctor aprovaria uma mentira. Rode o
> bloco *Como preencher a sua seção*, substitua o bloco abaixo pelo resultado, e commite.
> Depois disso, o que coincidir com a Máquina A sobe para o `CLAUDE.md` como fato comum, e
> o item ⏳ de lá se apaga.
>
> Sabe-se **por declaração do Daniel, não por medição**: conda não é usado em casa também;
> e ele *tende a preferir* a versão estável mais atual do node — mas não sabe qual está
> instalada nem em que estado está o ambiente. **Preferência não é estado:** preencha o que
> a máquina responder, mesmo que contrarie a preferência. Se contrariar, isso é o achado.

```decl
machine-id: pendente
rotulo: casa
```

---

## O que já é comum às duas

`uv` + `pyenv` + `bun` são o stack de fato, e **conda não é usado** em nenhuma das duas —
esta é a parte que o `CLAUDE.md` pode afirmar sem mentir para uma delas. O resto espera a
Máquina B. **Nada volta a ser escrito como "esta máquina".**
