---
name: verify-claimed-state
description: Documentação que AFIRMA "X foi atualizado" é uma alegação, não um fato — verificar contra o filesystem/git antes de confiar, principalmente entre repos ou máquinas diferentes
metadata:
  pattern: error_resolution
  origin: manual_estudo, sessão 17/07/2026
  confidence: alta (alegação falsa encontrada em auditoria)
---

**O caso:** o CLAUDE.md do projeto (commitado no mesmo dia) afirmava "estratégia canônica atualizada
em `estrategista-concurso/references/alvos-e-bancas.md`". Era falso: o arquivo vivia em OUTRO repo
(`~/.claude`), a mudança foi feita em outra máquina e nunca foi commitada/pushed — o arquivo local
estava 16 dias defasado, com a estratégia antiga inteira.

**O padrão:** quando um doc alega que outro artefato foi atualizado (especialmente em repo diferente,
máquina diferente ou fora do diff da sessão), tratar como hipótese: conferir mtime/`git log`/conteúdo
do alvo. Se o repo-alvo tem remoto, `fetch` antes — a atualização pode existir e só não ter chegado.

**Como aplicar:** em auditorias de consistência, todo "ver X"/"atualizado em X" vira item de
verificação com fonte real. A classe de bug: sessões multi-repo/multi-máquina atualizam A e
documentam em B — B chega, A não. Corrigir sempre nos dois lados: o artefato E a alegação.
