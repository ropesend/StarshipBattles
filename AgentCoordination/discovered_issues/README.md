# Discovered Issues — Cross-Task Inbox

A shared, append-only log where any agent (claude, codex, opencode, gemini)
can record an issue it noticed **while working on something else**.

The intent is to capture out-of-scope findings without derailing the current
task. A future triage pass — or the user — decides what to do with each entry
(promote to a GitHub issue / project ticket, fix in place, or prune as a
non-issue).

## When to log

Log when, mid-task, you notice one of these in code you are **not** changing:

- A real bug, latent crash, or incorrect behavior.
- A security smell (injection, missing auth check, sensitive data leak).
- A clear performance pathology (O(n²) where it shouldn't be, etc.).
- A test gap that masks a risk.
- Dead code, broken/lying docstring, stale comment that misleads readers.
- Convention or architecture violation that survived prior cleanups.

Do **not** log:

- Things you are about to fix as part of the current task — just fix them.
- Style preferences that are subjective.
- Speculative refactors with no concrete problem behind them.
- Anything already tracked in an open GitHub issue (check first if obvious).

## How to log

Use the helper script — never hand-edit `log.jsonl`:

```bash
python Tools/agent_coordination/log_discovered_issue.py \
  --agent claude \
  --source-task "PROJ-437 Phase 3" \
  --file game/combat/resolver.py \
  --line 142 \
  --category bug \
  --severity medium \
  --description "Double-negative check can never fire because is_dead is set in the branch above at line 138." \
  --suggested-action "Remove the 'not is_dead' clause, or invert the earlier branch."
```

Claude users: `/claude-di-log` wraps this. Codex/OpenCode have equivalents.

The helper:

1. Verifies the file exists and the line is in range.
2. Reads a 3-line snippet centered on `--line` and stores it as
   `code_snippet` — this is what survives line drift.
3. Generates an `id` of the form `DI-YYYY-MM-DD-NNN`.
4. Appends one JSON object as a single line to `log.jsonl`.

## Schema (one JSON object per line)

| Field              | Type     | Required | Notes                                                 |
|--------------------|----------|----------|-------------------------------------------------------|
| `id`               | string   | yes      | `DI-YYYY-MM-DD-NNN`, monotonic within a day           |
| `discovered_at`    | string   | yes      | UTC ISO8601, `...Z`                                   |
| `agent`            | string   | yes      | `claude` \| `codex` \| `ocode` \| `gemini`            |
| `source_task`      | string   | yes      | What the agent was doing when it noticed              |
| `file`             | string   | yes      | Repo-relative POSIX path                              |
| `line`             | int      | yes      | 1-indexed; may drift — use `code_snippet` to relocate |
| `code_snippet`     | string   | yes      | 3-line excerpt (line-1 … line+1) captured at log time |
| `symbol`           | string   | no       | Function/class name for fallback locating             |
| `category`         | string   | yes      | `bug` \| `security` \| `perf` \| `test-gap` \| `dead-code` \| `doc` \| `convention` \| `tech-debt` |
| `severity`         | string   | yes      | `low` \| `medium` \| `high`                           |
| `description`      | string   | yes      | What is wrong; the durable explanation                |
| `suggested_action` | string   | no       | How to fix, if obvious                                |

No `status` field — the log only holds open issues. Pruning is the resolution.

## How to triage

Run the triage helper to see open issues with current-code verification:

```bash
python Tools/agent_coordination/triage_discovered_issues.py
```

For each entry it reports one of:

- `match-exact`     — file:line still shows the snippet → likely still valid
- `match-drifted`   — snippet found nearby (within ±25 lines) → still valid, line moved
- `match-elsewhere` — snippet found at an unrelated location → human review
- `snippet-gone`    — file exists but the snippet does not → likely already fixed
- `file-gone`       — file no longer exists → almost certainly resolved

Then prune resolved or non-issues:

```bash
python Tools/agent_coordination/triage_discovered_issues.py --prune DI-2026-05-18-001 DI-2026-05-18-002
```

Git history preserves pruned entries — there is no separate archive file.

## Why not GitHub Issues directly?

Filing a GH issue mid-task is heavy: it needs a clean title, labels, a
template-shaped body, and pulls the agent out of context. This local log is
the **inbox**; triage promotes survivors to GH issues in batch as the
**outbox**.
