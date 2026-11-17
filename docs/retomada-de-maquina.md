# Retomar uma máquina que ficou meses fechada

Este roteiro nasceu em **07/10/2026**, quando o laptop do Daniel, um ThinkPad, precisou viajar
depois de meses fechado. O projeto não sabia nada sobre ele:
[`ambiente-por-maquina.md`](ambiente-por-maquina.md) declara duas máquinas, o desktop de casa e
o do trabalho, e o laptop é a terceira. Tudo o que está escrito aqui foi medido na Máquina B,
a de casa; **o laptop em si não foi medido**, e é por isso que o centro do roteiro é um script
que mede, e não uma lista de afirmações sobre uma máquina que ninguém abriu.

São três peças, e a divisão entre elas segue uma pergunta só: *o git leva isto?*

| Peça | Onde roda | O que faz |
|---|---|---|
| [`scripts/empacotar_para_outra_maquina.sh`](../scripts/empacotar_para_outra_maquina.sh) | na máquina em dia | junta num `.tgz` o que o git não leva: os servidores MCP de usuário, o `~/.mcp.json`, o `settings.local.json`, o `~/.ai_env` e a fonte Lora |
| [`scripts/retomar_maquina.sh`](../scripts/retomar_maquina.sh) | no laptop | mede a máquina, avança os três repositórios quando é seguro, instala ganchos e symlinks, aplica o pacote sem sobrescrever nada, roda os doutores e imprime as pendências com o comando pronto |
| este documento | quem lê | a ordem, o que exige senha ou navegador, e as armadilhas que o script não alcança |

## O que envelhece numa máquina fechada, e quem mede cada coisa

Nada aqui é presunção sobre o laptop: cada linha diz qual comando responde se o item está em
dia, e quem o conserta.

| O que envelhece | Quem mede | Quem conserta |
|---|---|---|
| os três clones: `~/.claude`, `~/dotfiles`, `~/manual_estudo` | `git fetch` e a contagem atrás/à frente | o script, quando é fast-forward limpo; senão `/repo-sync` numa sessão |
| o `core.hooksPath` de cada clone, que não viaja no clone | `git config` | o script |
| os symlinks do shell | `~/dotfiles/install.sh` | o script |
| a versão do Claude Code e o login | `claude --version` e a presença de `.credentials.json` | `--instalar` atualiza pelo bun; o login é seu |
| os marketplaces e os plugins ligados no `settings.json` | `claude plugin marketplace list` e `claude plugin list` | `--instalar` adiciona os marketplaces; os plugins entram pela primeira abertura do `claude` ou por `claude plugin install` |
| os servidores MCP locais, que moram em `~/.claude.json` e não são versionados | `claude mcp get` | o pacote |
| o arquivo de skills de terceiros, que também não é versionado | `scripts/apply_skills_archive.py` | o script |
| a declaração desta máquina | `scripts/doctor_ambiente.py` | você, com o bloco de coleta do `ambiente-por-maquina.md` |
| o ambiente do pipeline do `manual_estudo`: pacotes, binários, fontes, add-on | `estudo/doctor_ambiente.py` | `--instalar` instala os pacotes Python; o apt é seu, porque pede senha |
| o Anki: versão, add-on e a direção do primeiro sync | o doutor e o script | você |
| o sistema operacional | `~/system-maintenance/scripts/system-update.sh` | você, porque pede senha |

## Em casa, antes de sair, nesta ordem

A ordem existe porque as partes pesadas dependem de rede boa e de navegador: o clone do
`manual_estudo` pesa cerca de 430 MB no GitHub, o `apt upgrade` de meses é longo, o Anki novo
vem em tarball, e os dois logins abrem o navegador. Na rede de hotel é exatamente aí que a
retomada emperra.

**1. Na máquina em dia**, gere o pacote e leve-o por pendrive ou por `scp`:

```bash
bash ~/.claude/scripts/empacotar_para_outra_maquina.sh
```

**2. No laptop, na tomada e na rede de casa**, atualize o sistema. Se os dotfiles já estiverem
lá, o comando é `~/system-maintenance/scripts/system-update.sh`; senão, `sudo apt update &&
sudo apt upgrade`.

**3. Entre no GitHub**, porque `manual_estudo` e `dotfiles` são privados e o `.gitconfig` dos
dotfiles delega a credencial ao `gh`:

```bash
gh auth login
```

**4. Rode a retomada.** O script vem de fora na primeira vez, porque o clone velho de
`~/.claude`, se existir, ainda não o tem — e o `claude-config` é público, então o `curl` não
precisa de login:

```bash
curl -fsSL https://raw.githubusercontent.com/fugisawa/claude-config/main/scripts/retomar_maquina.sh | bash -s -- --instalar --pacote ~/viagem-claude-<data>.tgz
```

Quem quiser ver antes de deixar mexer roda primeiro com `--so-medir`, que só imprime o
relatório. Depois da primeira vez o script está no clone, e a chamada é
`bash ~/.claude/scripts/retomar_maquina.sh`, com os mesmos argumentos.

**5. Feche as pendências que ele imprimiu.** As que o script nunca fecha sozinho são estas, e
cada uma sai com o comando pronto:

- a linha `sudo apt install -y …`, uma vez só, com tudo o que faltou de binário, fonte e
  biblioteca do WeasyPrint;
- o login do Claude Code: abra `claude` e entre pelo navegador;
- a declaração do laptop em [`ambiente-por-maquina.md`](ambiente-por-maquina.md): a seção
  **Máquina C** está lá com `machine-id: pendente`, e o § *Como preencher a sua seção* traz o
  bloco de coleta. Esse é o primeiro commit do laptop, e o pre-commit do `~/.claude` reprova
  qualquer outro enquanto a máquina não estiver declarada;
- o Anki, na seção abaixo.

**6. Feche o terminal, abra outro, e abra o `claude` em `~/manual_estudo`.** Skills, plugins e
servidores MCP só entram no início da sessão. A prova de que a máquina serve para estudar é
`python3 estudo/dia.py` imprimir a folha do dia, e o script já tenta isso no fim.

## As armadilhas que o script não alcança

**O Anki tem três, e a terceira destrói dados.** Primeira: um Anki anterior à 26.05 não
consegue mais se atualizar sozinho, porque o pacote que alimentava aquele lançador parou de
ser publicado; o conserto é o tarball de apps.ankiweb.net com `sudo ./install.sh`, e o doutor
do `manual_estudo` imprime a receita quando mede uma versão abaixo do piso. Segunda: o add-on
AnkiConnect (código 2055492159) vive dentro do Anki, não vem com ele, e sem ele o pipeline de
cards não conversa com a coleção. Terceira, e é a que importa: se o laptop tiver uma coleção
antiga e o Anki perguntar a direção do sync completo, **a resposta é baixar do AnkiWeb**. A
coleção boa é a do AnkiWeb, reconstruída do zero em 26/07/2026; enviar a do laptop a apagaria.
O script avisa quando encontra coleção local, mas quem clica é você.

**O Python do pipeline é o do pyenv, nunca o do sistema.** O Ubuntu bloqueia `pip install`
no Python do sistema (PEP 668), e o `--instalar` só instala os pacotes quando `python3`
resolve dentro de `~/.pyenv`. Se não resolver, o bootstrap dos dotfiles instala pyenv, Python,
uv e bun sem senha: `~/dotfiles/bin/setup-dev-environment.sh --python --node`. A opção
`--base` desse mesmo script atualiza o sistema e instala os pacotes de compilação, e essa pede.

**O `node` de cada máquina é um caso à parte.** Nas duas máquinas medidas o terminal entrega
v24 pelo nvm e o script recebe outra versão; o laptop pode ter qualquer coisa. É o bloco de
coleta da declaração que responde, não este texto.

**A memória do Claude no laptop está velha ou vazia, e é assim por desenho.** Ela mora em
`projects/`, fora do git, e por isso não sabe que a Câmara entrou no portfólio em 06/10/2026
(decisões 0034 e 0035 do `manual_estudo`) nem que a reta da Câmara está no plano 0022. O
repositório sabe. Quando a memória e o repositório discordarem, o repositório vence.

**O material da viagem já está em dois lugares.** O clone do `manual_estudo` traz todos os
PDFs em `pdf/`, e desde 07/10/2026 a pasta *Apostilas — Manual de Estudo* no Google Drive tem
as apostilas, os manuais de método e o plano, para qualquer aparelho com navegador.

## O que fica de fora de propósito

- **Credenciais do Claude e do `gh`.** Refazer o login leva um minuto; um token copiado passa a
  valer em duas máquinas, e revogar vira adivinhação.
- **O `rclone` e o Drive.** O laptop não precisa dele: o Drive se abre no navegador e os PDFs
  já vêm no clone.
- **As skills `gsd-*`.** São instaladas por máquina (`npx get-shit-done-cc@1.42.3`) e a linha
  está descontinuada; a migração é decisão a tomar nas máquinas de uma vez, registrada em
  [`skills-inventory.md`](skills-inventory.md). O laptop vive sem elas.
- **`~/planner`.** É a origem dos design systems Typst copiados para o `manual_estudo`; sem
  ele o doutor só avisa que a origem sumiu. Clone se for mexer no desenho do planner ou do
  caderno.
- **O cofre LifeOS.** As skills de Obsidian em `skills/` são symlinks relativos para
  `~/Documents/LifeOS/.claude/skills/` e ficam pendurados sem o cofre; o Claude as ignora. Elas
  só importam se a viagem incluir o cofre.

## Na volta

O laptop vai voltar com commits, porque marcar a trilha é commit. Empurre antes de fechá-lo:
o gancho `hooks/sync-on-start.sh` diz no início de cada sessão se o clone está à frente, e
`/repo-sync` resolve em três chamadas. Commit que fica sem push é a semente da divergência que
custou catorze minutos em 16/09/2026, e o desktop só fica sabendo do laptop pelo remoto.

## Como este roteiro envelhece

O que tem guarda: o script mede em vez de afirmar; a declaração da máquina tem o
`doctor_ambiente.py` no pre-commit; a lista de plugins sai do `settings.json` e a de servidores
MCP sai do pacote, nunca deste texto. O que é só prosa, e por isso pode envelhecer calado: a
ordem dos passos, as armadilhas do Anki e a lista do que fica de fora. Quem retomar uma máquina
e tropeçar em algo que não está aqui acrescenta o tropeço, com a data.
