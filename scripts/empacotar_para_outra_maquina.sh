#!/usr/bin/env bash
# empacotar_para_outra_maquina.sh — junta o que o git NÃO leva e a outra máquina precisa.
#
# Roda na máquina que está em dia. O resultado é ~/viagem-claude-AAAA-MM-DD.tgz, com modo 600,
# que se leva por pendrive ou scp e se aplica na outra máquina com:
#
#     bash ~/.claude/scripts/retomar_maquina.sh --pacote ~/viagem-claude-AAAA-MM-DD.tgz
#
# O PACOTE CONTÉM SEGREDOS — as chaves de API dos servidores MCP e as do ~/.ai_env. Por isso ele
# nunca entra em repositório, nasce com modo 600 e deve ser apagado nas duas máquinas depois de
# aplicado. O que entra, e por quê:
#
#   mcp-servers.json     os servidores MCP de usuário (~/.claude.json → mcpServers), com o caminho
#                        do home trocado por __HOME__, porque o usuário pode ter outro nome lá
#   mcp.json             o ~/.mcp.json do home — servidores de projeto do diretório ~
#   settings.local.json  permissões e env locais do Claude (ARTIGOS_EMAIL entre eles)
#   ai_env               ~/.ai_env, as chaves que o .profile dos dotfiles exporta
#   fonts/lora/*.ttf     a Lora, a única fonte do pipeline que não vem do apt
#
# O que NÃO entra, de propósito: ~/.claude/.credentials.json (o login do Claude se refaz em um
# minuto, e um token copiado passa a valer por duas máquinas), a credencial do gh (idem), o
# rclone (o Drive se abre no navegador) e a memória do Claude (projects/, por máquina por desenho).
#
# Cada item só entra se existir aqui; o relatório do fim diz o que foi empacotado.
set -euo pipefail

DATA=$(date +%F)
OUT=$HOME/viagem-claude-$DATA.tgz
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
conteudo=()

if [ -f "$HOME/.claude.json" ] && command -v jq >/dev/null 2>&1; then
  jq --arg h "$HOME" \
     '.mcpServers // {} | walk(if type == "string" then (split($h) | join("__HOME__")) else . end)' \
     "$HOME/.claude.json" > "$tmp/mcp-servers.json"
  conteudo+=("mcp-servers.json — $(jq 'length' "$tmp/mcp-servers.json") servidores: $(jq -r 'keys | join(", ")' "$tmp/mcp-servers.json")")
elif [ -f "$HOME/.claude.json" ]; then
  echo "sem jq: os servidores MCP ficaram de fora (apt install jq e rode de novo)" >&2
fi

if [ -f "$HOME/.mcp.json" ]; then
  cp "$HOME/.mcp.json" "$tmp/mcp.json"; conteudo+=("mcp.json — o ~/.mcp.json do home")
fi
if [ -f "$HOME/.claude/settings.local.json" ]; then
  cp "$HOME/.claude/settings.local.json" "$tmp/settings.local.json"; conteudo+=("settings.local.json")
fi
if [ -f "$HOME/.ai_env" ]; then
  cp "$HOME/.ai_env" "$tmp/ai_env"
  conteudo+=("ai_env — $(grep -cE '^(export )?[A-Z_]+=' "$HOME/.ai_env" || true) chave(s)")
fi
if ls "$HOME"/.local/share/fonts/lora/*.ttf >/dev/null 2>&1; then
  mkdir -p "$tmp/fonts/lora"
  cp "$HOME"/.local/share/fonts/lora/*.ttf "$tmp/fonts/lora/"
  conteudo+=("fonts/lora — $(ls "$tmp/fonts/lora" | wc -l) arquivo(s)")
fi

cat > "$tmp/LEIA-ME.txt" <<EOF
Pacote de $(hostname), $DATA — o que o git não leva, para retomar outra máquina.
CONTÉM SEGREDOS (chaves de API). Aplique e apague:

    bash ~/.claude/scripts/retomar_maquina.sh --instalar --pacote ~/$(basename "$OUT")
    rm ~/$(basename "$OUT")

Nada aqui sobrescreve arquivo que já exista na outra máquina.
Roteiro: ~/.claude/docs/retomada-de-maquina.md
EOF

(cd "$tmp" && tar -czf "$OUT" .)
chmod 600 "$OUT"

printf 'pacote: %s (%s, modo 600)\n' "$OUT" "$(du -h "$OUT" | cut -f1)"
for c in "${conteudo[@]}"; do printf '  %s\n' "$c"; done
printf '\nLeve por pendrive, ou: scp %s <usuario>@<outra-maquina>:~/\n' "$OUT"
printf 'Lá: bash ~/.claude/scripts/retomar_maquina.sh --instalar --pacote ~/%s\n' "$(basename "$OUT")"
printf 'Depois de aplicar, apague o pacote nas DUAS máquinas: rm %s\n' "$OUT"
