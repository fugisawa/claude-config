#!/usr/bin/env bash
# retomar_maquina.sh — põe em dia uma máquina que ficou meses fechada, ou uma máquina nova,
# MEDINDO antes de agir. O par dele, que roda na máquina que está em dia, é
# empacotar_para_outra_maquina.sh; o roteiro humano está em docs/retomada-de-maquina.md.
#
#   bash ~/.claude/scripts/retomar_maquina.sh                       # mede, e faz só o que é seguro
#   bash ~/.claude/scripts/retomar_maquina.sh --instalar            # idem, mais o que se instala sem senha
#   bash ~/.claude/scripts/retomar_maquina.sh --pacote ~/viagem-claude-AAAA-MM-DD.tgz
#   bash ~/.claude/scripts/retomar_maquina.sh --so-medir            # relatório; nada muda
#
# Numa máquina em que ~/.claude ainda não é clone, ou é clone velho sem este arquivo, o script
# vem de fora — o repositório é público, e o clone de ~/.claude é a primeira coisa que ele faz:
#   curl -fsSL https://raw.githubusercontent.com/fugisawa/claude-config/main/scripts/retomar_maquina.sh \
#     | bash -s -- --instalar
#
# O QUE ELE FAZ SOZINHO, porque é reversível e idempotente: clona ou avança os três repositórios
# (claude-config, dotfiles, manual_estudo) quando o avanço é fast-forward e a árvore está limpa;
# aponta o hooksPath de cada um para githooks/; roda o install.sh dos dotfiles (symlinks, com
# backup dos originais); alinha o arquivo de skills pelo inventário; aplica o pacote da outra
# máquina SEM sobrescrever o que já existe; e roda os doutores, que são quem diz o que falta.
#
# O QUE ELE NUNCA FAZ: sudo, login, rebase, stash, merge com commit, push, apagar. O que exige
# senha ou navegador sai na lista de PENDÊNCIAS do fim, com o comando pronto para colar.
#
# Por que ele mede em vez de presumir: as duas máquinas declaradas em docs/ambiente-por-maquina.md
# já divergiram em três de quatro afirmações escritas de memória (10/08/2026). Uma máquina fechada
# por meses é pior, porque ninguém sabe o que ela tem. Aqui cada linha de "feito" nasce de um
# comando que rodou, e cada pendência, de um que falhou ou que só uma pessoa pode rodar.
#
# Os quatro estados de um clone (em sincronia, só atrás, só à frente, divergiu) são os mesmos que
# hooks/sync-on-start.sh classifica no início de cada sessão; aquele gancho é a autoridade dentro
# da sessão, e este script é o irmão de fora dela — por isso avança só o fast-forward limpo, como
# ele, e manda o resto para /repo-sync.
set -uo pipefail

REPO_CLAUDE=https://github.com/fugisawa/claude-config.git
REPO_DOTFILES=https://github.com/fugisawa/dotfiles.git
REPO_ESTUDO=https://github.com/fugisawa/manual_estudo.git

INSTALAR=0; SO_MEDIR=0; PACOTE=""; REDE=0; PY_PYENV=0; MID="?"
FEITO=(); PENDENTE=(); APT_FALTA=()

uso() {
  cat <<'EOF'
uso: retomar_maquina.sh [--instalar] [--pacote ARQUIVO.tgz] [--so-medir]
  --instalar   instala também o que não pede senha: claude pelo bun, pacotes Python do pipeline
               no python do pyenv, marketplaces de plugin
  --pacote     aplica o pacote gerado por empacotar_para_outra_maquina.sh (nunca sobrescreve)
  --so-medir   só o relatório; nenhum arquivo muda
EOF
}

feito()    { FEITO+=("$*");    printf '  feito     %s\n' "$*"; }
pendente() { PENDENTE+=("$*"); printf '  PENDENTE  %s\n' "$*"; }
nota()     {                   printf '  nota      %s\n' "$*"; }
ok()       {                   printf '  ok        %s\n' "$*"; }
secao()    { printf '\n== %s ==\n' "$*"; }
tem()      { command -v "$1" >/dev/null 2>&1; }
pode_mudar() { [ "$SO_MEDIR" -eq 0 ]; }

# ── a máquina ──────────────────────────────────────────────────────────────────────────────────
medir_maquina() {
  secao "a máquina"
  MID=$(cut -c1-8 /etc/machine-id 2>/dev/null || echo "?")
  local rotulo so
  rotulo="$(cat /sys/devices/virtual/dmi/id/sys_vendor 2>/dev/null) $(cat /sys/devices/virtual/dmi/id/product_name 2>/dev/null)"
  so=$(lsb_release -ds 2>/dev/null || sed -n 's/^PRETTY_NAME="\(.*\)"/\1/p' /etc/os-release)
  printf '  %s · machine-id %s · %s · %s · %s\n' "$(hostname)" "$MID" "${rotulo# }" "$so" "$(date +%F' '%H:%M)"
  [ "$SO_MEDIR" -eq 1 ] && nota "modo --so-medir: nada vai mudar"
  [ "$INSTALAR" -eq 1 ] && nota "modo --instalar: instala o que não pede senha"
  return 0
}

medir_rede() {
  secao "rede"
  if GIT_TERMINAL_PROMPT=0 timeout 20 git ls-remote -h "$REPO_CLAUDE" >/dev/null 2>&1; then
    REDE=1; ok "o GitHub responde"
  else
    REDE=0; pendente "sem rede até o GitHub — nada foi clonado nem avançado; conecte e rode de novo"
  fi
}

# ── as ferramentas ─────────────────────────────────────────────────────────────────────────────
medir_ferramentas() {
  secao "ferramentas"
  local item cmd pacote
  for item in git:git curl:curl jq:jq gh:gh rg:ripgrep fdfind:fd-find \
              pdftoppm:poppler-utils pdfinfo:poppler-utils gs:ghostscript fc-list:fontconfig; do
    cmd=${item%%:*}; pacote=${item#*:}
    if tem "$cmd"; then ok "$cmd"; else APT_FALTA+=("$pacote"); printf '  falta     %s (apt %s)\n' "$cmd" "$pacote"; fi
  done
  local faltam_de_usuario=()
  for cmd in uv pyenv bun; do
    if tem "$cmd"; then ok "$cmd $("$cmd" --version 2>/dev/null | head -1)"; else faltam_de_usuario+=("$cmd"); fi
  done
  if [ ${#faltam_de_usuario[@]} -gt 0 ]; then
    pendente "faltam ${faltam_de_usuario[*]}: ~/dotfiles/bin/setup-dev-environment.sh --python --node (depois de clonar os dotfiles; --base atualiza o sistema e pede senha)"
  fi

  local py
  if py=$(command -v python3); then
    case "$(readlink -f "$py")" in
      */.pyenv/*) PY_PYENV=1; ok "python3 $("$py" --version 2>&1 | cut -d' ' -f2) do pyenv" ;;
      *)          PY_PYENV=0; ok "python3 $("$py" --version 2>&1 | cut -d' ' -f2) do sistema — o pip global é bloqueado pelo PEP 668; o pipeline quer o python do pyenv" ;;
    esac
  else
    pendente "falta python3"
  fi

  local node_i
  node_i=$(bash -ic 'node --version' 2>/dev/null | tail -1)
  if [ -n "$node_i" ]; then ok "node $node_i no shell interativo"; else nota "sem node no shell interativo (o Claude Code pelo bun não precisa dele)"; fi

  if tem gh; then
    if gh auth status >/dev/null 2>&1; then ok "gh autenticado"; else pendente "gh auth login (navegador) — sem isso os repositórios privados (manual_estudo, dotfiles) não clonam"; fi
  fi

  medir_claude
}

claude_veio_do_bun() { case "$(command -v claude 2>/dev/null)" in */.bun/*) return 0 ;; *) return 1 ;; esac; }

medir_claude() {
  if tem claude; then
    ok "claude $(claude --version 2>/dev/null | head -1) em $(command -v claude)"
    if [ "$INSTALAR" -eq 1 ] && pode_mudar && [ "$REDE" -eq 1 ] && tem bun && claude_veio_do_bun; then
      if timeout 600 bun add -g @anthropic-ai/claude-code@latest >/dev/null 2>&1; then
        feito "claude atualizado pelo bun: $(claude --version 2>/dev/null | head -1)"
      else
        pendente "a atualização do claude falhou — rode à mão: bun add -g @anthropic-ai/claude-code@latest"
      fi
    fi
    if [ -s "$HOME/.claude/.credentials.json" ]; then ok "claude tem credencial gravada"; else pendente "claude sem login nesta máquina — abra \`claude\` e entre pelo navegador"; fi
  elif [ "$INSTALAR" -eq 1 ] && pode_mudar && [ "$REDE" -eq 1 ] && tem bun; then
    if timeout 600 bun add -g @anthropic-ai/claude-code >/dev/null 2>&1; then
      feito "claude instalado pelo bun ($("$HOME/.bun/bin/claude" --version 2>/dev/null | head -1))"
      pendente "claude recém-instalado, sem login — abra \`claude\` e entre pelo navegador"
    else
      pendente "instale o claude: bun add -g @anthropic-ai/claude-code"
    fi
  else
    pendente "falta claude: bun add -g @anthropic-ai/claude-code (ou --instalar, com o bun presente e rede)"
  fi
}

# ── os repositórios ────────────────────────────────────────────────────────────────────────────
repo_sincronizar() {  # $1 rótulo · $2 diretório · $3 url · $4 1 = tem submódulos
  local nome=$1 dir=$2 url=$3 sub=$4
  if [ ! -e "$dir" ]; then
    if [ "$REDE" -eq 0 ] || ! pode_mudar; then pendente "$nome: não existe — git clone $url $dir"; return; fi
    local extra=()
    [ "$sub" = 1 ] && extra=(--recurse-submodules)
    if GIT_TERMINAL_PROMPT=0 timeout 1800 git clone --quiet ${extra[@]+"${extra[@]}"} "$url" "$dir" 2>/dev/null; then
      feito "$nome clonado em $dir"
    else
      pendente "$nome: o clone falhou — repositório privado sem gh auth? depois do login: git clone $url $dir"
      return
    fi
  elif ! git -C "$dir" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    pendente "$dir existe e NÃO é clone do git — guarde o que importa, mova (mv $dir $dir.pre-retomada) e clone: git clone $url $dir"
    return
  else
    repo_avancar "$nome" "$dir"
  fi
  if [ -f "$dir/.gitmodules" ] && pode_mudar && [ "$REDE" -eq 1 ]; then
    if git -C "$dir" submodule update --init --recursive --quiet 2>/dev/null; then ok "$nome: submódulos no lugar"; else pendente "$nome: git -C $dir submodule update --init --recursive falhou"; fi
  fi
  if [ -d "$dir/githooks" ]; then
    if [ "$(git -C "$dir" config core.hooksPath 2>/dev/null)" = "githooks" ]; then
      ok "$nome: hooksPath já aponta para githooks/"
    elif ! pode_mudar; then
      nota "$nome: hooksPath não instalado (instalaria)"
    elif git -C "$dir" config core.hooksPath githooks; then
      feito "$nome: core.hooksPath=githooks — o gancho não viaja no clone"
    fi
  fi
}

repo_avancar() {  # $1 rótulo · $2 diretório (clone que existe)
  local nome=$1 dir=$2 up behind ahead suja
  if [ "$REDE" -eq 0 ]; then pendente "$nome: sem rede, estado contra o remoto NÃO conferido"; return; fi
  if ! GIT_TERMINAL_PROMPT=0 timeout 120 git -C "$dir" fetch --quiet --prune 2>/dev/null; then
    pendente "$nome: o fetch falhou (credencial? rede?) — estado contra o remoto NÃO conferido"; return
  fi
  up=$(git -C "$dir" rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>/dev/null || true)
  if [ -z "$up" ]; then pendente "$nome: o ramo atual não rastreia nenhum ramo remoto — confira git -C $dir status"; return; fi
  read -r behind ahead < <(git -C "$dir" rev-list --left-right --count "$up...HEAD" 2>/dev/null || echo "0 0")
  suja=$(git -C "$dir" status --porcelain --untracked-files=no 2>/dev/null)
  if [ "$behind" -eq 0 ] && [ "$ahead" -eq 0 ]; then
    [ -n "$suja" ] && nota "$nome: em sincronia, mas a árvore tem alteração não commitada — veja git -C $dir status"
    ok "$nome em sincronia com $up"
  elif [ "$behind" -gt 0 ] && [ "$ahead" -eq 0 ] && [ -z "$suja" ]; then
    if ! pode_mudar; then
      nota "$nome: $behind commit(s) atrás de $up — avançaria por fast-forward"
    elif git -C "$dir" merge --ff-only --quiet "$up" >/dev/null 2>&1; then
      feito "$nome avançou $behind commit(s) até $up ($(git -C "$dir" rev-parse --short HEAD))"
    else
      pendente "$nome: $behind atrás e o fast-forward falhou — numa sessão do Claude, /repo-sync"
    fi
  elif [ "$behind" -gt 0 ] && [ "$ahead" -eq 0 ]; then
    pendente "$nome: $behind atrás e a árvore está suja (trabalho de outra época?) — leia git -C $dir status, commite ou descarte, e depois /repo-sync; nunca stash por cima"
  elif [ "$ahead" -gt 0 ] && [ "$behind" -eq 0 ]; then
    pendente "$nome: $ahead commit(s) locais nunca empurrados — numa sessão do Claude, /repo-sync (podem ser trabalho de meses atrás)"
  else
    pendente "$nome: DIVERGIU — $behind atrás / $ahead à frente de $up — numa sessão do Claude, /repo-sync ANTES de tocar em arquivo"
  fi
}

sincronizar_repositorios() {
  secao "repositórios"
  repo_sincronizar claude-config "$HOME/.claude" "$REPO_CLAUDE" 1
  repo_sincronizar dotfiles      "$HOME/dotfiles" "$REPO_DOTFILES" 0
  repo_sincronizar manual_estudo "$HOME/manual_estudo" "$REPO_ESTUDO" 0
  [ -d "$HOME/planner/.git" ] || nota "sem ~/planner (projeto-planners) aqui: o doutor do manual_estudo só AVISA sobre a origem das cópias Typst; clone se for mexer no design system"
}

# ── dotfiles ───────────────────────────────────────────────────────────────────────────────────
dotfiles_instalar() {
  secao "dotfiles"
  [ -x "$HOME/dotfiles/install.sh" ] || { pendente "sem ~/dotfiles/install.sh — os symlinks do shell não foram instalados"; return; }
  if ! pode_mudar; then
    nota "install.sh não rodou (--so-medir)"
  else
    local saida n_link n_bak
    saida=$("$HOME/dotfiles/install.sh" 2>&1)
    n_link=$(grep -c '^link' <<<"$saida" || true)
    n_bak=$(grep -c '^backup' <<<"$saida" || true)
    if [ "$n_link" -eq 0 ]; then ok "symlinks já estavam no lugar"; else feito "dotfiles: $n_link symlink(s) criados, $n_bak original(is) guardados como *.pre-dotfiles.*"; fi
  fi
  local prova; prova=$(bash -ic 'echo __ok__' 2>/dev/null || true)
  if grep -q __ok__ <<<"$prova"; then ok "o shell interativo carrega"; else pendente "o shell interativo não carregou limpo — rode: bash -ic 'echo ok' e leia o erro"; fi
  [ -x "$HOME/system-maintenance/scripts/system-update.sh" ] && pendente "atualize o sistema (pede senha): ~/system-maintenance/scripts/system-update.sh"
  return 0
}

# ── ~/.claude ──────────────────────────────────────────────────────────────────────────────────
claude_config_alinhar() {
  secao "claude-config (~/.claude)"
  local cc=$HOME/.claude saida
  git -C "$cc" rev-parse --is-inside-work-tree >/dev/null 2>&1 || { pendente "o ~/.claude não é clone — o resto desta seção depende dele"; return; }

  if tem uv; then
    # Só o dry-run, de propósito: o apply_skills_archive.py move toda skill que o inventário lista, e em
    # 07/10/2026 ele apontou a zotero-cli, que está ativa e em uso. Mover é decisão de quem lê a lista.
    saida=$(uv run --quiet --with pyyaml python "$cc/scripts/apply_skills_archive.py" --dry-run 2>&1 || true)
    if grep -q 'nada a fazer' <<<"$saida"; then
      ok "skills alinhadas com docs/skills-inventory.md"
    else
      pendente "skills fora do inventário — leia a lista e, se concordar, aplique: uv run --with pyyaml python ~/.claude/scripts/apply_skills_archive.py (dry-run abaixo)"
      printf '%s\n' "$saida" | grep 'dry-run' | sed 's/^/    /'
    fi
    saida=$(uv run --quiet --with pyyaml python "$cc/scripts/doctor_ambiente.py" 2>&1)
    if grep -q 'maquina-nao-declarada' <<<"$saida"; then
      pendente "declare esta máquina ($MID) em ~/.claude/docs/ambiente-por-maquina.md: a seção 'Máquina C' está lá com machine-id pendente — rode o bloco de coleta do § 'Como preencher a sua seção', substitua os valores, commite e empurre. Sem isso o pre-commit do ~/.claude reprova aqui"
    elif grep -q 'fato-divergente' <<<"$saida"; then
      pendente "a declaração desta máquina divergiu do disco — leia: uv run --with pyyaml python ~/.claude/scripts/doctor_ambiente.py"
    else
      ok "a declaração de ambiente bate com o disco"
    fi
  else
    pendente "sem uv não rodam os doutores do ~/.claude nem o alinhamento de skills"
  fi

  if python3 "$cc/scripts/definir_email_artigos.py" --verificar >/dev/null 2>&1; then
    ok "ARTIGOS_EMAIL definido em settings.local.json"
  else
    pendente "grave o e-mail do Unpaywall/Crossref/OpenAlex: python3 ~/.claude/scripts/definir_email_artigos.py <e-mail do Daniel>"
  fi

  tem claude || return 0
  local lista nome fonte m
  lista=$(timeout 60 claude plugin marketplace list 2>/dev/null || true)
  for m in "claude-plugins-official|anthropics/claude-plugins-official" \
           "everything-claude-code|affaan-m/everything-claude-code" \
           "obsidian-skills|kepano/obsidian-skills"; do
    nome=${m%%|*}; fonte=${m#*|}
    if grep -q "$nome" <<<"$lista"; then
      ok "marketplace $nome"
    elif [ "$INSTALAR" -eq 1 ] && pode_mudar && [ "$REDE" -eq 1 ]; then
      if timeout 300 claude plugin marketplace add "$fonte" >/dev/null 2>&1; then feito "marketplace $nome adicionado"; else pendente "claude plugin marketplace add $fonte"; fi
    else
      pendente "marketplace $nome falta: claude plugin marketplace add $fonte"
    fi
  done
  if tem jq; then
    local instalados pid
    instalados=$(timeout 60 claude plugin list 2>/dev/null || true)
    while IFS= read -r pid; do
      [ -n "$pid" ] || continue
      if grep -qF "$pid" <<<"$instalados"; then ok "plugin $pid"; else pendente "plugin $pid ligado no settings.json e não instalado: claude plugin install $pid"; fi
    done < <(jq -r '.enabledPlugins // {} | to_entries[] | select(.value == true) | .key' "$cc/settings.json" 2>/dev/null)
  fi
}

# ── o pacote da outra máquina ──────────────────────────────────────────────────────────────────
copiar_se_ausente() {  # $1 origem · $2 destino · $3 modo
  local src=$1 dst=$2 modo=$3
  [ -f "$src" ] || return 0
  if [ -e "$dst" ]; then ok "$dst já existe — não sobrescrevi"
  elif ! pode_mudar; then nota "$dst viria do pacote"
  elif mkdir -p "$(dirname "$dst")" && cp "$src" "$dst" && chmod "$modo" "$dst"; then feito "$dst copiado do pacote"
  else pendente "não consegui copiar $dst do pacote"; fi
}

pacote_aplicar() {
  [ -n "$PACOTE" ] || return 0
  secao "pacote da outra máquina"
  [ -f "$PACOTE" ] || { pendente "pacote não encontrado: $PACOTE"; return; }
  local tmp; tmp=$(mktemp -d)
  if ! tar -xzf "$PACOTE" -C "$tmp" 2>/dev/null; then pendente "não consegui abrir $PACOTE"; rm -rf "$tmp"; return; fi
  copiar_se_ausente "$tmp/ai_env"              "$HOME/.ai_env"                     600
  copiar_se_ausente "$tmp/settings.local.json" "$HOME/.claude/settings.local.json" 600
  copiar_se_ausente "$tmp/mcp.json"            "$HOME/.mcp.json"                   644
  if [ -d "$tmp/fonts/lora" ]; then
    local f dst n=0
    for f in "$tmp"/fonts/lora/*.ttf; do
      dst=$HOME/.local/share/fonts/lora/$(basename "$f")
      [ -e "$dst" ] && continue
      pode_mudar && mkdir -p "$HOME/.local/share/fonts/lora" && cp "$f" "$dst" && n=$((n + 1))
    done
    if [ "$n" -gt 0 ]; then fc-cache -f >/dev/null 2>&1; feito "fonte Lora: $n arquivo(s) em ~/.local/share/fonts/lora"; else ok "fonte Lora já estava em ~/.local/share/fonts/lora"; fi
  fi
  if [ -f "$tmp/mcp-servers.json" ]; then
    if tem claude && tem jq; then
      local nome json
      while IFS= read -r nome; do
        [ -n "$nome" ] || continue
        if claude mcp get "$nome" >/dev/null 2>&1; then ok "mcp $nome já existe"; continue; fi
        json=$(jq -c --arg n "$nome" --arg h "$HOME" '.[$n] | walk(if type == "string" then (split("__HOME__") | join($h)) else . end)' "$tmp/mcp-servers.json")
        if ! pode_mudar; then nota "mcp $nome viria do pacote"
        elif claude mcp add-json -s user "$nome" "$json" >/dev/null 2>&1; then feito "mcp $nome adicionado (escopo user)"
        else pendente "mcp $nome: claude mcp add-json -s user falhou — veja o pacote"; fi
      done < <(jq -r 'keys[]' "$tmp/mcp-servers.json" 2>/dev/null)
    else
      pendente "os servidores MCP do pacote precisam de claude e jq para entrar — rode de novo com --pacote depois de instalá-los"
    fi
  fi
  rm -rf "$tmp"
}

# ── manual_estudo ──────────────────────────────────────────────────────────────────────────────
manual_estudo_conferir() {
  secao "manual_estudo"
  local me=$HOME/manual_estudo saida rc req fam
  [ -f "$me/estudo/doctor_ambiente.py" ] || { pendente "o ~/manual_estudo não está aqui, ou está velho demais para ter o doutor"; return; }

  # A saída do fc-list é capturada UMA vez: `fc-list | grep -q` sob pipefail reprova sozinho, porque o
  # grep sai no primeiro acerto e o fc-list morre de SIGPIPE (learned/pipefail-com-consumidor-que-sai-cedo).
  local fontes; fontes=$(fc-list : family 2>/dev/null || true)
  for fam in "IBM Plex Sans:fonts-ibm-plex" "Lato:fonts-lato"; do
    grep -q "^${fam%%:*}" <<<"$fontes" || APT_FALTA+=("${fam#*:}")
  done
  for req in libpango-1.0-0 libpangoft2-1.0-0 libgdk-pixbuf-2.0-0; do
    dpkg -s "$req" >/dev/null 2>&1 || APT_FALTA+=("$req")
  done
  if grep -q '^Lora' <<<"$fontes"; then
    ok "fonte Lora presente"
  else
    pendente "fonte Lora (não há pacote apt): venha pelo --pacote, ou baixe em fonts.google.com/specimen/Lora, ponha os dois .ttf variáveis em ~/.local/share/fonts/lora/ e rode fc-cache -f"
  fi

  if [ "$INSTALAR" -eq 1 ] && pode_mudar && [ "$REDE" -eq 1 ] && [ "$PY_PYENV" -eq 1 ]; then
    req=$(python3 "$me/estudo/doctor_ambiente.py" --requirements | tr '\n' ' ')
    # A lista é de nomes de pacote separados por espaço, de propósito.
    # shellcheck disable=SC2086
    if timeout 900 python3 -m pip install --quiet $req >/dev/null 2>&1; then feito "pacotes Python do pipeline no python do pyenv: $req"; else pendente "pip install falhou: python3 -m pip install $req"; fi
  fi
  saida=$(cd "$me" && python3 estudo/doctor_ambiente.py 2>&1); rc=$?
  printf '%s\n' "$saida" | sed 's/^/    /'
  if [ "$rc" -eq 0 ]; then
    ok "ambiente do pipeline completo segundo estudo/doctor_ambiente.py"
  else
    pendente "estudo/doctor_ambiente.py listou faltas (acima): pacote Python entra com --instalar (no python do pyenv); binário e fonte entram pela linha de apt do fim"
    [ "$PY_PYENV" -eq 0 ] && grep -q 'falta  pacote' <<<"$saida" && pendente "o python3 não é do pyenv — instale-o antes do pip (~/dotfiles/bin/setup-dev-environment.sh --python), ou o PEP 668 bloqueia"
  fi
  grep -q 'aviso  Anki' <<<"$saida" && pendente "o Anki daqui não se atualiza mais sozinho — siga o conserto que o doutor imprimiu acima"

  anki_conferir
  if pode_mudar; then
    if (cd "$me" && timeout 180 python3 estudo/dia.py >/tmp/retomar-dia.txt 2>&1); then
      feito "a folha do dia roda nesta máquina (python3 estudo/dia.py)"
    else
      pendente "python3 estudo/dia.py falhou — veja /tmp/retomar-dia.txt ($(tail -1 /tmp/retomar-dia.txt 2>/dev/null))"
    fi
  fi
  return 0
}

anki_conferir() {
  local v
  if tem anki; then
    v=$(ls /usr/local/share/anki/app_packages 2>/dev/null | sed -n 's/^aqt-\([0-9.]*\)\.dist-info$/\1/p' | head -1)
    if [ -n "$v" ]; then ok "anki $v (instalado pelo tarball)"; else nota "anki presente, mas não pelo tarball de apps.ankiweb.net — o doutor acima diz se ele ainda se atualiza"; fi
    if [ -d "$HOME/.local/share/Anki2/addons21/2055492159" ]; then ok "AnkiConnect instalado"; else pendente "AnkiConnect (2055492159) não está neste Anki: Ferramentas > Complementos > Obter complementos"; fi
  else
    pendente "anki: baixe o tarball em apps.ankiweb.net, extraia e rode sudo ./install.sh de dentro da pasta (pede senha); depois o AnkiConnect (2055492159)"
  fi
  if ls "$HOME"/.local/share/Anki2/*/collection.anki2 >/dev/null 2>&1; then
    pendente "há coleção Anki antiga nesta máquina: no primeiro sync, se o Anki perguntar a direção, escolha BAIXAR do AnkiWeb — a coleção boa é a do AnkiWeb (reconstruída em 26/07/2026) e 'enviar' a apagaria"
  fi
  return 0
}

# ── resumo ─────────────────────────────────────────────────────────────────────────────────────
resumo() {
  secao "resumo"
  printf '  feito: %d · pendências: %d\n' "${#FEITO[@]}" "${#PENDENTE[@]}"
  if [ ${#APT_FALTA[@]} -gt 0 ]; then
    local unicos; unicos=$(printf '%s\n' "${APT_FALTA[@]}" | sort -u | tr '\n' ' ')
    pendente "pede senha, uma vez só: sudo apt install -y $unicos"
  fi
  if [ ${#PENDENTE[@]} -gt 0 ]; then
    printf '\nPENDÊNCIAS:\n'
    local i=0 p
    for p in "${PENDENTE[@]}"; do i=$((i + 1)); printf '  %2d. %s\n' "$i" "$p"; done
  fi
  printf '\nDepois de fechar as pendências: feche este terminal, abra outro, e abra o claude em ~/manual_estudo.\n'
  printf 'Skills, plugins e MCPs só entram no início da sessão; a prova de que a máquina serve é: python3 estudo/dia.py\n'
}

main() {
  while [ $# -gt 0 ]; do
    case "$1" in
      --instalar) INSTALAR=1 ;;
      --so-medir) SO_MEDIR=1 ;;
      --pacote)   shift; PACOTE=${1:-} ;;
      -h|--help)  uso; return 0 ;;
      *) printf 'argumento desconhecido: %s\n\n' "$1" >&2; uso >&2; return 2 ;;
    esac
    shift
  done
  medir_maquina
  medir_rede
  medir_ferramentas
  sincronizar_repositorios
  dotfiles_instalar
  claude_config_alinhar
  pacote_aplicar
  manual_estudo_conferir
  resumo
  [ ${#PENDENTE[@]} -eq 0 ]
}

# Tudo dentro de main, e main chamado na última linha: o bash lê o arquivo aos poucos, e este
# script avança o próprio clone (~/.claude) enquanto roda — se o corpo estivesse solto, o
# fast-forward trocaria o arquivo debaixo do interpretador.
main "$@"
