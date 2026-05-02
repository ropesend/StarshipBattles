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

Claude usage logging is **automatic** for ALL skills via two hooks in `.claude/settings.json`:

- `UserPromptExpansion` (matcher `*`) fires when the user types `/skill-name` and exposes `command_name`.
- `PreToolUse` (matcher `Skill`) fires when Claude calls the Skill tool itself.

Both events run `Tools/agent_coordination/claude_skill_usage_hook.py`, which calls `log_skill_usage.py --agent claude --skill <name>` for all skill names (prefixed `claude-*` and builtins like `loop`, `simplify`, `review`, etc.). No manual invocation needed.

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
