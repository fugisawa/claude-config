# Agent Orchestration

## Available Agents

**Where these come from — the rule, not a guess.** An agent's identity is its
`name:` field, and it may be served by two different providers: `local` means a
file under `~/.claude/agents/`; `ecc` means the `everything-claude-code` plugin.
The distinction is not cosmetic. A plugin-served agent disappears the moment the
plugin is uninstalled or its `enabledPlugins` entry stops being `true` — and it
disappears **silently**, leaving this file ordering the use of something that no
longer loads. Until 11/08/2026 this table claimed all nine lived in
`~/.claude/agents/`; eight of them did not.

The `Provider` column below is a declaration, and `scripts/doctor_rules.py`
checks it against the disk on every commit. Change a provider here without the
disk agreeing and the hook fails.

| Agent | Provider | Purpose | When to Use |
|-------|----------|---------|-------------|
| planner | ecc | Implementation planning | Complex features, refactoring |
| architect | ecc | System design | Architectural decisions |
| tdd-guide | ecc | Test-driven development | New features, bug fixes |
| code-reviewer | local | Code review | After writing code |
| security-reviewer | ecc | Security analysis | Before commits |
| build-error-resolver | ecc | Fix build errors | When build fails |
| e2e-runner | ecc | E2E testing | Critical user flows |
| refactor-cleaner | ecc | Dead code cleanup | Code maintenance |
| doc-updater | ecc | Documentation | Updating docs |

When an agent named here does not resolve, do not silently substitute another
one and do not pretend the step ran. Say which agent is missing and why the
check failed — that message is the whole point of the guard.

## Immediate Agent Usage

No user prompt needed:
1. Complex feature requests - Use **planner** agent
2. Code just written/modified - Use **code-reviewer** agent
3. Bug fix or new feature - Use **tdd-guide** agent
4. Architectural decision - Use **architect** agent

## Parallel Task Execution

ALWAYS use parallel Task execution for independent operations:

```markdown
# GOOD: Parallel execution
Launch 3 agents in parallel:
1. Agent 1: Security analysis of auth module
2. Agent 2: Performance review of cache system
3. Agent 3: Type checking of utilities

# BAD: Sequential when unnecessary
First agent 1, then agent 2, then agent 3
```

## Multi-Perspective Analysis

For complex problems, use split role sub-agents:
- Factual reviewer
- Senior engineer
- Security expert
- Consistency reviewer
- Redundancy checker
