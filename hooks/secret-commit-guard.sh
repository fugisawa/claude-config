#!/usr/bin/env bash
# secret-commit-guard.sh — PreToolUse(Bash) hook.
# Blocks a `git commit` when the STAGED additions look like they contain a real
# secret (per Daniel's security rule: no hardcoded secrets before any commit).
# High-confidence patterns only + placeholder exclusion → near-zero false positives.
# Fails OPEN on any error (never blocks legitimate work). Exit 2 = block + tell Claude.

INPUT=$(cat)

# Fast path: if the input doesn't even mention "commit", do nothing (no node/git spawn).
case "$INPUT" in *commit*) ;; *) exit 0 ;; esac

NODE="$(command -v node 2>/dev/null || echo /home/linuxbrew/.linuxbrew/bin/node)"
[ -x "$NODE" ] || command -v node >/dev/null 2>&1 || exit 0

# Extract the command string from the hook JSON.
CMD=$(printf '%s' "$INPUT" | "$NODE" -e "let d='';process.stdin.on('data',c=>d+=c);process.stdin.on('end',()=>{try{process.stdout.write(JSON.parse(d).tool_input?.command||'')}catch{}})" 2>/dev/null)
[ -z "$CMD" ] && exit 0

# Confirm it's genuinely a `git commit` (token walk per segment; handles env prefix,
# -C <path>, -c <cfg>, full-path git). Avoids firing on `git log --grep commit` etc.
"$NODE" -e '
const cmd=process.argv[1]||"";
const isCommit=cmd.split(/&&|\|\||;|\|/).some(seg=>{
  const t=seg.trim().split(/\s+/).filter(Boolean); let i=0;
  while(i<t.length && /^[A-Za-z_][A-Za-z0-9_]*=/.test(t[i])) i++;
  while(i<t.length && t[i].split("/").pop()!=="git") i++;
  if(i>=t.length) return false; i++;
  while(i<t.length){const x=t[i];
    if(["-C","-c","--git-dir","--work-tree","--namespace"].includes(x)){i+=2;continue;}
    if(x.startsWith("-")){i++;continue;} return x==="commit";}
  return false;
});
process.exit(isCommit?0:1);
' "$CMD" || exit 0

# Scan only the staged ADDITIONS.
DIFF=$(git diff --cached -U0 --no-color 2>/dev/null) || exit 0
[ -z "$DIFF" ] && exit 0
ADDED=$(printf '%s\n' "$DIFF" | grep -E '^\+' | grep -vE '^\+\+\+')
[ -z "$ADDED" ] && exit 0

HITS=$(printf '%s\n' "$ADDED" | grep -nEi \
  -e '-----BEGIN [A-Z ]*PRIVATE KEY-----' \
  -e '\bAKIA[0-9A-Z]{16}\b' \
  -e 'tvly-[A-Za-z0-9_-]{16,}' \
  -e 'ctx7sk-[A-Za-z0-9-]{16,}' \
  -e '\bsk-[A-Za-z0-9]{20,}' \
  -e '\b(ghp|gho|ghu|ghs)_[A-Za-z0-9]{30,}' \
  -e 'github_pat_[A-Za-z0-9_]{30,}' \
  -e '\bAIza[0-9A-Za-z_-]{35}\b' \
  -e '\bxox[baprs]-[A-Za-z0-9-]{10,}' \
  -e 'glpat-[A-Za-z0-9_-]{16,}' \
  -e '(api[_-]?key|secret|passwd|password|access[_-]?token|auth[_-]?token)[[:space:]]*[:=][[:space:]]*["'"'"'][A-Za-z0-9_./+-]{16,}["'"'"']' \
  | grep -viE 'your[_-]|<[^>]+>|example|changeme|dummy|placeholder|xxxx+|redacted|\bfake\b' || true)

if [ -n "$HITS" ]; then
  {
    echo "[secret-guard] Commit BLOCKED — staged changes look like they contain secret(s):"
    printf '%s\n' "$HITS" | sed -E 's/(tvly-|ctx7sk-|sk-|ghp_|gho_|github_pat_|AKIA|AIza|glpat-)[A-Za-z0-9_-]+/\1<redacted>/g' | head -6
    echo "Remove/rotate them and use env vars or a secret manager (your security rules)."
    echo "False positive? Unstage the file, or commit outside Claude Code."
  } >&2
  exit 2
fi
exit 0
