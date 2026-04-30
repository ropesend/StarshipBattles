# Why these Antigravity skills are staged

The user's stated priority for Antigravity (Gemini in a VS Code fork) is tooling and asset generation; it is **lower priority** than Claude Code, Codex, and OpenCode/DeepSeek for code work.

Before this cleanup, `.agent/skills/` contained 33 hand-maintained `anti-*` skill copies that paralleled `.claude/skills/claude-*`. Per the support-systems audit, this was 33 SKILL.md files of maintenance burden with no automated mirror generator and no enforcement that they stayed in sync.

The 6 `anti-*` skills that **stayed** in `.agent/skills/` were chosen as those most likely to serve Antigravity's actual role:

| Kept | Reason |
|---|---|
| `anti-validate-designs` | Design QA — fits asset/tooling. |
| `anti-fix-crash` | Crash diagnosis is broadly useful regardless of agent. |
| `anti-loc` | LOC counter is generic tooling. |
| `anti-qa-feedback` | QA session feedback handling. |
| `anti-qa-triage` | QA session triage. |
| `anti-analysis-sweep` | Codebase sweep for tooling-heavy reviews. |

The other 27 are staged here for the 30-day cooling-off period. If you discover Antigravity actually needs one of them, restore with:

```bash
git mv _marked_for_deletion_2026-05-29/.agent/skills/anti-<name> .agent/skills/anti-<name>
```

Restored skills should also be added back to the inventory by re-running:

```bash
python Tools/agent_coordination/inventory_agent_surfaces.py
```

After 2026-05-29, the staged skills are recoverable only from git history.

## Staged skills

```
anti-analysis-complexity
anti-analysis-dead-code
anti-debug-sequential
anti-deep-dive-sequential
anti-proj-add-to-plan
anti-proj-archive
anti-proj-audit
anti-proj-close
anti-proj-continue
anti-proj-extract-phase
anti-proj-manage-plan
anti-proj-reset-baseline
anti-proj-review
anti-proj-revise
anti-proj-sequential
anti-proj-start
anti-ticket-add
anti-ticket-answer
anti-ticket-batch-close
anti-ticket-close
anti-ticket-continue
anti-ticket-deep-dive
anti-ticket-next
anti-ticket-reject
anti-ticket-update
anti-ticket-work
anti-triage-to-proj
```
