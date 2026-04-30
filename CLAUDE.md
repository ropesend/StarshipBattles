# Claude Code — Project Adapter

@AGENTS.md

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

## Reinforcement of `AGENTS.md` rules

The five rules below are restated here because Claude Code's context can grow long and the model loses fidelity past ~50% of the window. The closed validator markers signal these are *intentional* duplications, not drift.

<!-- agent-coordination:reinforcement tdd -->
**TDD always.** Write or identify the failing test first, run it to confirm failure, then implement. No exceptions. If you catch yourself writing implementation code without a failing test, **stop**. Delete or stash, write the test first, reimplement.

<!-- agent-coordination:reinforcement docs-first -->
<!-- agent-coordination:reinforcement code-doc-consistency -->
**Read docs before coding; update docs in the same commit.** Start at `docs/README.md`. Always read `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`, `docs/03_CONVENTIONS.md`, plus any task-specific docs the README points at. When you change behavior or architecture, update the relevant docs in the same commit. Bump the `Last verified:` date when you've actually re-read a doc against current code.

<!-- agent-coordination:reinforcement root-cause -->
**Root cause fixes only.** No bandaids, no workarounds, no "good enough for now." If you catch yourself writing a workaround, ask: *what is the real problem here?* and fix that. Refactor surrounding code if the clean fix requires it; propose a larger refactor and let the user decide scope rather than ship a hack.

<!-- agent-coordination:reinforcement no-ignore-folder -->
**Never read `docs/_ignore/`.** It is the user's personal scratch pad. Not documentation; not relevant to any task.

---

## Skill Usage Logging

Claude usage logging is **automatic** for `claude-*` skills via two hooks in `.claude/settings.json`:

- `UserPromptExpansion` (matcher `*`) fires when the user types `/claude-<name>` and exposes `command_name`.
- `PreToolUse` (matcher `Skill`) fires when Claude calls the Skill tool itself.

Both events run `Tools/agent_coordination/claude_skill_usage_hook.py`, which filters to the `claude-` prefix and calls `log_skill_usage.py --agent claude --skill <name>`. No manual invocation needed.

Manual call (testing or override):

```bash
python Tools/agent_coordination/log_skill_usage.py --agent claude --skill claude-proj-start
```

Counters are **advisory only** — they identify cleanup candidates and never authorize automatic deletion. Full context: `AGENTS.md §"Skill Usage Logging"` and `Tools/agent_coordination/README.md`.

---

## Subagent Report Output

Subagent reports go to `.agent_reports/` by default. The directory is gitignored and disposable.

**Default workflow:**

1. Main agent creates `.agent_reports/<descriptive-job-name>/` before spawning subagents.
2. Main agent passes the full path to each subagent in its prompt.
3. Subagents write reports to that directory only, using the Write tool (not Bash).
4. Main agent reads the reports, then deletes the job folder when the task is complete.

**Skill / protocol overrides:** when a skill or protocol specifies its own report location, use it. The skill is authoritative. Examples:

- Project reviews → `Projects/active_projects/PROJ-XX/findings/` (protocols 01, 04, 09).
- Codebase analysis sweeps → `Reviews/results/{DATE}_{TYPE}_{SCOPE}/`.

The main agent passes the override path to subagents the same way; subagents always write to whatever path they are given.

---

## Testing Configuration

- **CLI parallel workers:** 12 (`-n 12`).
- **VS Code Test Explorer:** use 4 workers; higher breaks the integrated panel.
- **Test monitor:** `--testmon` for incremental runs.
- Repo-wide baseline at `AgentCoordination/generated/test_baseline.json` (auto-updated on green whole-suite runs). One known flake: `test_colony_owner_id_matches_empire` passes when run alone (test-isolation).

---

## Help and Feedback

If a user asks for help or feedback:

- `/help` for Claude Code help.
- File feedback at https://github.com/anthropics/claude-code/issues.
