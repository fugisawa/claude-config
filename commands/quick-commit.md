---
description: Quick git commit with formatted message
argument-hint: <commit message>
allowed-tools: Bash
---

# Quick Commit

Create a git commit with a properly formatted message:

$ARGUMENTS

!git add -A && git commit -m "$ARGUMENTS"