# Context Window Configuration

Single source of truth for context-window settings across all Projects protocols
(03a, 03b, 08). Tune the numbers here — do not hardcode them in the protocols.

---

## Settings

- **CONTEXT_WINDOW_TOKENS:** 1000000
- **STOP_THRESHOLD_PERCENT:** 80

At the threshold Claude should finish the current task, complete a **natural
handoff point** (end of phase preferred, end of task acceptable), write the
handoff prompt (§3), and exit. See [Natural Stopping Points](#natural-stopping-points).

> `check_context.py` parses the two numbers above with a forgiving regex
> (`CONTEXT_WINDOW_TOKENS[^\d]*(\d+)` and `STOP_THRESHOLD_PERCENT[^\d]*(\d+(?:\.\d+)?)`),
> so markdown bold is fine — just keep each setting on its own line with a single
> number.

---

## How to check context usage

Run the check script at natural handoff points — **not after every task**:

```bash
python Projects/scripts/check_context.py
```

The script finds the current session's JSONL transcript, estimates tokens used,
and prints a verdict.

**Output format:**

```
Session: <sessionId>
Tokens used (est): 612,400 / 1,000,000 (61.2%)
Threshold: 80.0%
Verdict: CONTINUE
```

**Exit codes:**

- `0` — CONTINUE (below threshold)
- `1` — STOP (at or above threshold)
- `2` — UNKNOWN (transcript not found; fall back to cautious self-estimate)

---

## When to check

Check **only at natural handoff points**, never mid-task:

1. **Phase complete** — best place to stop.
2. **Task complete with no in-progress work** — acceptable.
3. **Before starting a large task** (estimated to require many file reads) — decide up front whether to start or hand off.

Do not check every iteration of the work loop. The token count does not change
mid-tool-call, and checking too often wastes output tokens.

---

## Natural Stopping Points

Prefer stopping at:

1. End of a phase (best)
2. End of a task (good)
3. After a subtask with a clear handoff (acceptable)

Avoid stopping:

- Mid-implementation with failing tests
- Without updating `## Current State` in the project plan
- With uncommitted mental context

---

## Handoff prompt template

When `check_context.py` returns STOP at a natural handoff point, write a handoff
prompt to `Projects/active_projects/PROJ-XX/handoff_prompt.md` using the template
below, then print it to the chat so the user can copy-paste it into a new session.

```markdown
# Handoff: PROJ-XX — <phase/task name>

Resume **PROJ-XX** at **Phase <N>**. The previous session ended at <threshold>%
context after completing <what was completed>.

## Read first (docs)
- docs/README.md (reading order)
- docs/01_ARCHITECTURE.md
- docs/02_PATTERNS.md
- docs/03_CONVENTIONS.md
- <task-specific docs with line ranges if narrow>

## Read first (code)
- <file:line-range> — <why it matters>
- <file:line-range> — <why it matters>

## Current State
Open `Projects/active_projects/PROJ-XX/plan.md` and read the `## Current State`
section in full. It contains the authoritative handoff notes from the previous
session — do not rely on this prompt as a substitute.

## First action
<literal next checklist item, copied verbatim from phase_N_checklist.md>

## Protocol
Follow Projects/protocols/03a_continue_working.md. Check context at natural
handoff points via `python Projects/scripts/check_context.py`.
```

Rules for filling it in:

- **Docs section**: list only files relevant to the next phase. Always include
  01–03 as the foundation. If a doc section is narrow, add `:L<start>-<end>`.
- **Code section**: list files the next agent *must* read before touching
  anything — not a full file tour. Include line ranges where helpful.
- **Current State**: do **not** duplicate the content. Point at `plan.md` and
  let that be the source of truth. Duplication creates drift.
- **First action**: copy the literal next `- [ ]` item from the active phase
  checklist. No paraphrasing.
