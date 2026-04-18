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
python Tools/check_context/check_context.py
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

Check **at natural checkpoints, not mid-task**:

1. **Phase complete** — a checkpoint where you decide whether to continue (usually yes) or, if near 80%, wind down.
2. **Task complete with no in-progress work** — another good checkpoint.
3. **Before starting a task you estimate will use >100k tokens** — check up front. If starting it would push past 80%, SPLIT the task (don't hand off).

You're **checking** context at these points, not **stopping**. Stop only when
`check_context.py` returns STOP. Below 80%, keep working.

Do not check every iteration of the work loop. The token count does not change
mid-tool-call, and checking too often wastes output tokens.

---

## Natural Stopping Points

**The 80% threshold is the only trigger for a handoff.** Below 80%, you
keep working. The threshold reserves ~200k tokens for writing the
handoff prompt and updating plan state — roughly the full context
window the codebase operated in a month ago. That's ample buffer.

**When `check_context.py` returns STOP**, wind down at the nearest
clean boundary (in this priority order):

1. End of a phase (best)
2. End of a task (good)
3. After a subtask with a clear stopping state (acceptable)

These priorities apply to **finding** a stopping point once you're at 80% —
NOT to deciding when to stop. Below 80%, "end of phase" is a checkpoint,
not an exit.

**Don't hand off early.** Ending a session at 27% context (or 50%, or
even 70%) wastes 300-600k of budget on re-orientation next session. The
next agent starts cold, re-reads docs, re-loads project files, and
rebuilds mental state — typically 40-70k of overhead by itself.
Restarting when you could have continued is measurably expensive.

**If the next phase looks too big to finish under 80%: SPLIT IT.**
No single phase should consume more than ~200k tokens beyond the session
baseline. If a phase looks larger than that as-planned, it's too coarse —
update the phase checklist to break it into sub-phases (same numbering
scheme, e.g. `phase_6a_checklist.md` / `phase_6b_checklist.md`, or
extend `phase_6_checklist.md` with clearly-delineated task groups), then
execute the first sub-phase. **Do not hand off early just because the
next phase feels dense.** Splitting is cheaper than handing off.

**Genuine blockers are exceptions.** User-approval gates, unresolvable
test failures, missing information — those are real stops regardless
of context %. A "phase complete, awaiting user verification" gate IS a
legitimate stop.

Avoid stopping:

- Mid-implementation with failing tests
- Without updating `## Current State` in the project plan
- With uncommitted mental context
- Because the next phase feels big — split it instead
- Below 60% unless there's a genuine blocker or the project is complete

---

## Handoff prompt template

When `check_context.py` returns STOP at a natural handoff point, write a handoff
prompt to `Projects/active_projects/PROJ-XX/handoff_prompt.md` using the template
below, then print it to the chat so the user can copy-paste it into a new session.

> **Principle:** prefer loading extra context over making a short-sighted
> decision. The next agent starts with zero memory of the project and the
> full repo as a cold cache. A few thousand extra tokens spent on
> orientation is cheap compared to a bad architectural choice. Over-brief
> prompts produce confident-but-wrong work.

```markdown
# Handoff: PROJ-XX — <phase/task name>

Resume **PROJ-XX** at **Phase <N>**. The previous session ended at <threshold>%
context after completing <what was completed>.

## Orientation (read BEFORE touching the project plan)

The instinct is to open `plan.md` first. Resist it. The project plan assumes
you understand the surrounding architecture, conventions, and related code
— if you don't, you'll make short-sighted decisions that the plan's author
took for granted. Prefer loading extra context.

### 1. Foundation docs (always read these first)
- docs/README.md — doc index + task-driven reading order
- docs/01_ARCHITECTURE.md — layer structure + package APIs + dependency rules
- docs/02_PATTERNS.md — design patterns used in this codebase
- docs/03_CONVENTIONS.md — naming, file org, test conventions, line budgets

### 2. Task-specific docs (whichever apply to Phase <N>)
- <docs/systems/*.md or docs/guides/*.md with line ranges if narrow>
- <CLAUDE.md memory files if relevant>

### 3. Related code (read for context, even if you won't modify it)
- <file:line-range> — <why it matters / what pattern it demonstrates>
- <file:line-range> — <adjacent/upstream/downstream code that constrains the task>
- <test fixtures / helpers that Phase <N> will interact with>

If a previous phase introduced a helper/pattern (e.g. `make_minimal_spec`,
`_common_preconditions`), read its source + docstring before using it —
docstrings often encode constraints the plan doesn't repeat.

### 4. Related tests (read so you know what "working" looks like)
- <test files that Phase <N> will modify>
- <existing tests that exercise the same subsystem>

## Only now: read the project files
Read in this order — the plan depends on all of the above:
1. `Projects/active_projects/PROJ-XX/design.md` — architectural rationale
2. `Projects/active_projects/PROJ-XX/decisions.md` — full decision log
3. `Projects/active_projects/PROJ-XX/plan.md` § Current State — authoritative handoff
4. `Projects/active_projects/PROJ-XX/phase_<N>_checklist.md` — task list
5. `Projects/active_projects/PROJ-XX/manifest.md` — file manifest
6. `.agent_reports/PROJ-XX-*` if any exist — audit outputs from prior sessions

## First action
<literal next checklist item, copied verbatim from phase_N_checklist.md>

## Watchouts (from the previous session)
- <landmine / complication / interpretation question discovered last session>
- <non-obvious constraint the next agent might miss>
- <anything the previous session ALMOST got wrong that the next agent should not>

## Protocol
Follow Projects/protocols/03a_continue_working.md. Check context at natural
handoff points via `python Tools/check_context/check_context.py`.
```

Rules for filling it in:

- **Bias toward extra context**, not minimal: when in doubt, list the file.
  A next-agent who reads 3 extra files produces better work than one who
  missed a constraint.
- **Foundation docs**: ALWAYS include 01–03. Non-negotiable.
- **Task-specific docs**: list every doc even tangentially relevant. Add line
  ranges only when a file is large and the relevant section is narrow.
- **Related code**: list files the next agent should read for *understanding*,
  not just files they'll *modify*. Include helpers/fixtures introduced by
  prior phases — their docstrings encode the contract.
- **Related tests**: list the tests that will be changed AND neighbouring
  tests that demonstrate how the subsystem is exercised.
- **Current State**: do **not** duplicate into this prompt. Point at `plan.md`
  and let it be the source of truth. Duplication creates drift.
- **First action**: copy the literal next `- [ ]` item from the active phase
  checklist. No paraphrasing.
- **Watchouts**: document what the previous session learned the hard way so
  the next agent doesn't repeat the discovery. Decisions made under time
  pressure belong here.
