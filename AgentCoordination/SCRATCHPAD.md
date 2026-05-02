# Scratchpad — Agent Transient Working Area

`AgentCoordination/Scratchpad/` is the **single shared scratch directory** for
all agents (Claude Code, OpenCode, subagents, anything else) running in this
repo. It is **gitignored** — contents are local-only and may be deleted at
any time.

This file is the rulebook. The directory itself ships empty in clones.

## The Rule

**Agents must not write transient files outside the repo.** Plans, reviews,
reports, handoffs, and any intermediate scratch go in
`AgentCoordination/Scratchpad/<category>/`, not in `~/.claude/plans/`,
`/tmp/`, the desktop, or any other ad-hoc location.

If a file needs to persist beyond the current scratch lifecycle, it belongs
in a tracked location:

- Architectural plans / projects → `Projects/active_projects/PROJ-XX/`
- Tickets → `Tracking/` or GitHub Issues (`/claude-gi-add`)
- Review reports worth keeping → `Reviews/results/<dated-dir>/`
- Documentation → `docs/`

If you're not sure whether something belongs in Scratchpad or in a tracked
location, default to Scratchpad. The user moves it out if it should persist.

## Layout

```
AgentCoordination/Scratchpad/
├── plans/      — plan-mode markdown, design notes, draft proposals
├── reviews/    — peer review staging, drafts, findings before final report
├── reports/    — subagent reports during a multi-step task
├── handoffs/   — multi-session continuity files (next-agent context)
└── tmp/        — truly throwaway one-shot intermediate state
```

First-time setup on a fresh clone (the dirs are gitignored, so they don't
ship):

```bash
mkdir -p AgentCoordination/Scratchpad/{plans,reviews,reports,handoffs,tmp}
```

Or just `mkdir -p` whichever subdir you need before writing.

## Naming

Freeform, but include enough context to identify it later:

- `Scratchpad/plans/2026-05-02_github-issues-migration.md`
- `Scratchpad/reviews/req_20260502_201926_5ac40b_findings_draft.md`
- `Scratchpad/reports/proj-313-audit_<agent-name>_finding-3.md`
- `Scratchpad/handoffs/proj-300_phase_4_to_phase_5.md`
- `Scratchpad/tmp/issue_body_127.md`

Date-prefixed names sort chronologically and survive a "delete files older
than X" sweep cleanly.

## Cleanup

The user deletes files manually whenever they want. There is no automated
sweep. **Therefore: do not put anything in Scratchpad that you would mind
losing tomorrow.** If it matters, it belongs in a tracked directory.

## Exceptions

The one harness-imposed exception is **Claude Code's plan-mode**: the harness
specifies an absolute plan-file path under `~/.claude/plans/`. Agents in pure
plan-mode (no edit access elsewhere) must write to that path. Once the agent
has edit access (bypass-permissions or post-ExitPlanMode), all subsequent
plan-related work goes in `Scratchpad/plans/`. If a plan is worth keeping,
copy it into a tracked location (`Projects/`, `docs/`) at the end of the
session and let `~/.claude/plans/` be cleaned by you separately.

## Discoverability

Pointed to from:
- `CLAUDE.md` — the agent-instruction primer
- `AGENTS.md` — the cross-agent reference
- This file is the canonical rules — link here, don't duplicate.
