# continuous-learning (runtime do hook — não é skill invocável)

Cópia de `plugins/cache/everything-claude-code/.../skills/continuous-learning/` (v1.8.0),
criada 19/07/2026 porque o hook `Stop` do `settings.json` aponta para
`~/.claude/skills/continuous-learning/evaluate-session.sh` e o cache do plugin é
versionado (quebraria a cada update). Sem `SKILL.md` de propósito — o skill invocável
continua sendo `everything-claude-code:continuous-learning`; aqui vive só o runtime.
Ao atualizar o plugin, re-copiar `evaluate-session.sh` + `config.json` se mudarem.
