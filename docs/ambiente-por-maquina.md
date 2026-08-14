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

Ubuntu 24.04.4 LTS, sem rede corporativa no caminho — o apt resolve direto.

```decl
machine-id: 8b4740ec
rotulo: casa · Dell Precision Tower 5810
medido-em: 2026-08-11
node-interativo: nvm v24
node-nao-interativo: apt v18
node-apt: apt v18
presentes: batcat, fdfind, rg, nvm, uv, pyenv, bun, brew
ausentes: bat, fd, conda, magick, convert
```

**Armadilha desta máquina, e é a mesma do trabalho com outro elenco:** o `node` do terminal
é v24, servido pelo nvm, e o de dentro de um script é v18, do apt. Seis versões de diferença
entre o que o Daniel vê e o que o script recebe.

**A preferência do Daniel bateu com o estado, e isso foi sorte, não confirmação.** Ele disse
tender à estável mais nova e o terminal entrega v24 — mas quem entrega é o nvm, que ele
acreditava não ter instalado. Medir era a única forma de saber, e a coincidência do
resultado não valida o palpite.

**A GPU desta máquina derruba aplicação Qt/Chromium nova, e o sintoma não diz isso
(14/08/2026).** A placa é uma **Quadro M4000**, de 2015, e o driver dela não oferece a
extensão Vulkan que a Qt 6.11 pede. Quem paga é toda aplicação que embute o QtWebEngine: o
Anki 26.08.1 instalou sem erro, imprimiu `Install complete`, e **abortou com core dump** na
primeira abertura. O rastro diz `GLOzone not found for unknown` depois de o EGL falhar nos
dois caminhos, OpenGL e OpenGLES — nenhuma das linhas nomeia a placa nem sugere o conserto,
e o `coredumpctl` não registrou nada. O conserto é escolher o renderizador por software no
perfil do próprio aplicativo (no Anki, `Preferências → driver de vídeo`, que se materializa
em `~/.local/share/Anki2/gldriver6`). Registrado aqui porque é traço de **hardware**, e vai
reaparecer na próxima aplicação Electron/Qt que chegar — e porque o perfil não é versionado,
de modo que trocar de perfil ou reinstalar traz o defeito de volta sem aviso nenhum.

---

## O que já é comum às duas

Com a Máquina B medida em 11/08/2026, o comum passa a ser isto, e só isto:

`uv`, `pyenv`, `bun`, `brew`, `rg`, `fdfind` e **`nvm`** existem nas duas; `conda`, `magick`
e `convert` não existem em nenhuma. O `node` do terminal interativo é **v24 pelo nvm** nos
dois lados.

**Dois achados que só apareceram com as duas medidas na mesa.** O primeiro é que a
instrução "sem nvm / não instale nvm" estava errada **nas duas** — não era desvio de uma
máquina, era afirmação falsa desde sempre, e a preferência declarada do Daniel batia com o
estado por coincidência. O segundo é `bat` × `batcat`: em casa só existe `batcat`, no
trabalho só existe `bat`. Uma inversão perfeita, do tipo que uma máquina sozinha nunca
detecta, porque de cada lado a instrução parece certa.

**O que continua divergindo, e por isso não sobe para o `CLAUDE.md`:** o `node` de dentro de
script (v18 em casa, v26 no trabalho), o node do apt, a presença de `fd`, e a rede.

**Nada volta a ser escrito como "esta máquina".**
