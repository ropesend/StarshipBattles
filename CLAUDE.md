# Claude Code Adapter

This file is the Claude-Code-specific delta over `AGENTS.md`. Read `AGENTS.md` first; it owns the non-negotiable rules, canonical commands, test infrastructure summary, conventions, architecture overview, and skill-usage policy. This file adds only Claude Code-specific behavior.

> **Note:** For automated CLI loop execution, see retired loop systems at `_marked_for_deletion_2026-05-29/Projects/`. The active workflow is interactive sessions; this file is the interactive-mode adapter.

---

## Your Role: Technical Consultant

When working in VS Code (or Antigravity), you are a **helpful technical consultant**, not an automated worker. Be conversational and collaborative:

- Explain your changes and reasoning.
- Ask clarifying questions when requirements are unclear.
- Suggest alternatives and trade-offs.
- Point out potential issues or improvements.
- Discuss design decisions.

---

## Estimate in LLM time, not human time

You are an LLM agent. You read at machine speed, edit dozens of files in parallel, and rarely block on anything other than test runs and subprocess waits. **Calibrate effort estimates to your actual pace, not a human developer's.**

Reference points for *your* scale, not a human's:

- A "10-line fix + targeted test" is **seconds to a minute or two**, not "30 minutes."
- A focused multi-file refactor (5–20 files, mechanical changes) is **minutes**, not "a day."
- A sweeping refactor across a layer (50+ files, design changes) is **tens of minutes** including test runs, not "weeks."
- A code review with tool use is **a minute or two**, not "an hour." You have never taken 30 minutes on a review; do not write as if you have.

**How to apply:**
- Don't pace work like a human sprint ("priority 1 for this pass, priority 2 for next pass") when the entire backlog is a single pass for you. If five fixes are all small, do all five in one pass; don't propose sequencing them across "rounds."
- Don't suggest an agent "split work into phases" when the phases would each take seconds.
- When you do mention duration, use realistic LLM units: "a couple of seconds," "under a minute," "a few minutes including test run." Avoid hours/days/weeks unless you're describing a genuinely slow operation (long test suites, large data migrations, things that *actually* take that long because the work is bound by something other than you).
- Test runs are a real bottleneck — the full sharded suite takes minutes. *Those* are legitimate hour-shaped costs if you run them many times.

If you catch yourself writing "this will take ~30 minutes" or "in a follow-up pass," stop and ask whether that's an LLM estimate or a habit-of-speech estimate from training data.

**This also applies to timeout values you configure in code.** When setting `subprocess` timeouts, daemon poll intervals, "orphan-age" cutoffs, retry windows, or anything else that bounds LLM-agent work, calibrate to actual LLM pace. A 1-hour timeout on a process that normally takes 2–5 minutes means a hung subprocess wastes 55+ minutes before being detected. Default heuristic: **timeout ≈ 2× expected duration of a typical run, not 10×.** If real work takes 5 minutes, set the timeout to 10 minutes, not an hour.

---

## Reinforcement of `AGENTS.md` rules

The five rules below are restated here because Claude Code's context can grow long and the model loses fidelity past ~50% of the window. The closed validator markers signal these are *intentional* duplications, not drift.

<!-- agent-coordination:reinforcement tdd -->
### 1. Strict TDD

Write or identify the failing test first, run it to confirm failure, then
implement. Do not backfill tests after implementation. Run the focused tests
while working and the relevant final validation before declaring the task done.

Canonical commands:

```bash
python Tools/test_sharded/test_sharded.py
pytest tests/ --testmon
pytest tests/path/to/test.py -k test_name
python -m combat_lab.run_tests
```

<!-- agent-coordination:reinforcement docs-first -->
<!-- agent-coordination:reinforcement code-doc-consistency -->
### 2. Documentation First

Before code work, read `docs/README.md`, then always read:

1. `docs/01_ARCHITECTURE.md`
2. `docs/02_PATTERNS.md`
3. `docs/03_CONVENTIONS.md`

Read task-specific docs listed in `docs/README.md`. Update docs in the same
change when behavior, architecture, workflow, or conventions change.

<!-- agent-coordination:reinforcement no-ignore-folder -->
Never read, summarize, reference, or act on `docs/_ignore/`. It is the user's
scratch space, not project documentation.

<!-- agent-coordination:reinforcement root-cause -->
### 3. Root Cause Fixes

Fix the real problem. Do not add compatibility shims, fallback systems, monkey
patches, duplicate logic, or save-file migrations. Old saves are disposable.
When a system is replaced, remove the old path and update all callers.

<!-- agent-coordination:reinforcement no-revert-unrelated -->
Do not revert unrelated user changes. Check `git status --short` before editing
and work around existing dirty state.

## Project Facts

- Python baseline: 3.13+.
- UI target: minimum 2560x1600, optimized for 3840x2160.
- Starship Battles is a tactical combat and strategic galaxy-map game using
  Pygame, pytest, and repo-local development tools.
- Spatial terms are precise: a star system is the radius-50 region around a
  star; a sector is one hex. System-scope effects apply across the star system.
  Sector-scope effects apply to one hex.

For layer boundaries, patterns, and current package APIs, use `docs/` as the
source of truth. Do not copy architecture summaries into this adapter.

## Key Conventions

- Public functions and methods require return-type annotations. Use modern
  syntax such as `int | None`; dunders are exempt.
- Production files under `game/` should stay under 500 LOC. Split by
  responsibility when a touched file approaches that ceiling.
- Broad `except Exception` catches require an intentional-reason comment on
  the same line or immediately above.
- Prefer existing registries, services, protocols, and helpers over new local
  mechanisms.
- Keep code and docs consistent. If code and docs disagree, stop and surface
  the discrepancy instead of silently choosing one.

## Claude Skills

Claude skills live under `.claude/skills/` and use the `claude-` prefix. Skills
should be thin entry points that route to shared protocols in `Projects/`,
`Tracking/`, `Reviews/`, and `docs/`.

Use the current surface name in examples and handoffs. Do not reference retired
Antigravity project, ticket, QA, or debug skills from Claude files.

## Skill Usage Logging

Claude usage logging is automatic for ALL skills through hooks in
`.claude/settings.json`:

- `UserPromptExpansion` records typed `/skill-name` commands.
- `PreToolUse` with matcher `Skill` records direct Skill tool use.

Both hooks call:

```bash
python Tools/agent_coordination/log_skill_usage.py --agent claude --skill <skill-name>
```

The logging command updates the per-install counter and aggregated
`AgentCoordination/generated/skill_usage/summary.json` in one invocation.
Counters are advisory only and never authorize automatic skill deletion.

## Git Workflow

- Check `git status --short` before edits.
- Keep commits focused when asked to commit.
- For failed merge rollbacks in parallel workflows, use
  `git revert -m 1 <merge_commit_sha> --no-edit` after confirming the worktree
  is clean. If the SHA is unclear, the worktree is dirty, or revert conflicts,
  stop and ask the user.

## Subagent Report Output

Subagent reports go to `.agent_reports/` by default. This directory is ignored
and disposable.

When launching subagents:

1. Create `.agent_reports/<job-name>/`.
2. Pass that path to every subagent.
3. Tell subagents to write reports only to that path.
4. Read and clean up reports when the task is complete.

If a skill or protocol specifies another report directory, use that location
instead. Examples include `Projects/active_projects/PROJ-XX/findings/` and
`Reviews/results/<date>_<type>_<scope>/`.
