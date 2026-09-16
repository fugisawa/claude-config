#!/usr/bin/env bash
# SessionStart: fetch + fast-forward SEGURO do repositório em que a sessão abre.
#
# Por que existe (16/09/2026). Duas máquinas commitaram no mesmo dia sem sincronizar no
# meio, e o primeiro `git push` do dia custou catorze minutos: rebase de quatro commits
# sobre três, regeneração da cascata de derivados e duas passagens de gancho. A ordem do
# Daniel foi "da próxima vez faz o pull antes de começar qualquer coisa". Memória não
# executa nada no início da sessão; gancho executa. Este é o gancho.
#
# O que ele faz, e só isso: `git fetch` (no máximo 20 s, sem pedir credencial) e, quando o
# clone está APENAS atrás e a árvore não tem alteração rastreada, `git merge --ff-only`.
# Em qualquer outro estado ele só descreve o que encontrou — à frente, divergido, árvore
# suja — e diz o que fazer. Ele nunca faz rebase, merge com commit, stash ou push.
#
# Mais de uma sessão no mesmo clone (pedido do Daniel, 16/09/2026): o trabalho da outra
# sessão aparece como árvore suja, e árvore suja DESLIGA o avanço. Um `flock` não
# bloqueante impede dois ganchos de mexerem no mesmo .git ao mesmo tempo, e index.lock,
# rebase ou merge em andamento também desligam. Falha de rede, de lock ou do git nunca
# derruba a sessão: a saída é sempre 0, e a mensagem diz o que não foi conferido.
#
# Só nos eventos `startup` e `resume`. Em `compact` e `clear` a sessão está no meio do
# trabalho, e mover a árvore debaixo dela é exatamente o que não se quer.
#
# Saída: JSON com `systemMessage` (uma linha para o Daniel) e `additionalContext` (o mesmo
# estado, para a sessão agir: divergiu → /repo-sync antes de tocar em arquivo).

INPUT=$(cat 2>/dev/null)
SOURCE=$(printf '%s' "$INPUT" | jq -r '.source // "startup"' 2>/dev/null)
CWD=$(printf '%s' "$INPUT" | jq -r '.cwd // empty' 2>/dev/null)
[ -n "$CWD" ] || CWD=$PWD

case "$SOURCE" in
  startup|resume) ;;
  *) exit 0 ;;
esac

emitir() {  # $1 = mensagem para o Daniel · $2 = contexto para a sessão (opcional)
  local msg=$1 ctx=${2:-$1}
  jq -n --arg m "$msg" --arg c "$ctx" \
    '{systemMessage: $m, hookSpecificOutput: {hookEventName: "SessionStart", additionalContext: $c}}'
  exit 0
}

cd "$CWD" 2>/dev/null || exit 0
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || exit 0
GITDIR=$(git rev-parse --git-dir 2>/dev/null) || exit 0
BRANCH=$(git branch --show-current 2>/dev/null)
[ -n "$BRANCH" ] || exit 0                                   # HEAD solto: nada a avançar
UP=$(git rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>/dev/null) || exit 0
REPO=$(basename "$(git rev-parse --show-toplevel 2>/dev/null)")
ROTULO="sync [$REPO · $BRANCH]"

# Duas sessões abrindo ao mesmo tempo no mesmo clone: uma sincroniza, a outra só avisa.
if command -v flock >/dev/null 2>&1; then
  exec 9>"$GITDIR/claude-sync.lock"
  flock -n 9 || emitir "$ROTULO: outra sessão está sincronizando este clone agora — não mexi."
fi
if [ -e "$GITDIR/index.lock" ] || [ -d "$GITDIR/rebase-merge" ] || [ -d "$GITDIR/rebase-apply" ] \
   || [ -e "$GITDIR/MERGE_HEAD" ]; then
  emitir "$ROTULO: há operação git em andamento neste clone (outra sessão?) — não mexi."
fi

if ! GIT_TERMINAL_PROMPT=0 timeout 20 git fetch --quiet --prune >/dev/null 2>&1; then
  emitir "$ROTULO: o fetch falhou (sem rede?). Estado contra $UP NÃO conferido." \
         "$ROTULO: fetch falhou; antes de commitar ou empurrar, rode /repo-sync."
fi

read -r BEHIND AHEAD < <(git rev-list --left-right --count "$UP...HEAD" 2>/dev/null || echo "0 0")
SUJA=$(git status --porcelain --untracked-files=no 2>/dev/null)

if [ "$BEHIND" -eq 0 ] && [ "$AHEAD" -eq 0 ]; then
  emitir "$ROTULO: em sincronia com $UP."
elif [ "$BEHIND" -gt 0 ] && [ "$AHEAD" -eq 0 ]; then
  if [ -n "$SUJA" ]; then
    emitir "$ROTULO: $BEHIND commit(s) atrás de $UP e a árvore tem alteração não commitada (outra sessão?) — não avancei." \
           "$ROTULO: $BEHIND atrás, árvore suja. Não use stash nem rebase sobre trabalho alheio; commite só os seus caminhos e rode /repo-sync."
  elif timeout 20 git merge --ff-only --quiet "$UP" >/dev/null 2>&1; then
    emitir "$ROTULO: avancei $BEHIND commit(s) até $UP ($(git rev-parse --short HEAD))."
  else
    emitir "$ROTULO: $BEHIND atrás e o fast-forward falhou — rode /repo-sync antes de começar."
  fi
elif [ "$AHEAD" -gt 0 ] && [ "$BEHIND" -eq 0 ]; then
  emitir "$ROTULO: $AHEAD commit(s) à frente de $UP, ainda não empurrado(s). Empurre ao terminar: git push." \
         "$ROTULO: $AHEAD à frente. Ao terminar o trabalho, git push — divergência entre máquinas nasce de commit não empurrado."
else
  emitir "$ROTULO: DIVERGIU — $BEHIND atrás / $AHEAD à frente de $UP. Rode /repo-sync ANTES de começar qualquer trabalho." \
         "$ROTULO: DIVERGIU ($BEHIND atrás / $AHEAD à frente). Rode /repo-sync antes de tocar em arquivo; com árvore suja de outra sessão, o caminho é merge, nunca stash nem rebase."
fi
