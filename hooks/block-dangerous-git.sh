#!/bin/bash
# Guardrail PreToolUse: bloqueia comandos git destrutivos antes da execução.
# Adaptado de mattpocock/skills (git-guardrails-claude-code).
# DIFERENÇA DELIBERADA vs upstream: NÃO bloqueia `git push` — o fluxo do Daniel
# depende de push pelo Claude (vsync, "commita e pusha"). Bloqueia apenas
# operações que destroem trabalho local de forma difícil de reverter.

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

[ -z "$COMMAND" ] && exit 0

DANGEROUS_PATTERNS=(
  "git reset --hard"
  "reset --hard"
  "git clean -[a-zA-Z]*f"
  "git branch -D"
  "git checkout \."
  "git checkout -- \."
  "git restore \."
  "push --force( |$)"
  "push -f( |$)"
)

for pattern in "${DANGEROUS_PATTERNS[@]}"; do
  if echo "$COMMAND" | grep -qE "$pattern"; then
    echo "BLOQUEADO: '$COMMAND' bate no padrão perigoso '$pattern'. O usuário impediu esta operação via hook (~/.claude/hooks/block-dangerous-git.sh). Se ela for realmente necessária, peça para o usuário executá-la manualmente com '! <comando>'. Alternativas seguras: git stash (em vez de reset --hard/checkout .), git branch -d (em vez de -D), git push --force-with-lease (em vez de --force)." >&2
    exit 2
  fi
done

exit 0
