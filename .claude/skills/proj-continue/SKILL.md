---
name: proj-continue
description: Continue working on an active project using the autonomous TDD work loop
disable-model-invocation: true
argument-hint: <project-number>
---

# Continue Project PROJ-$0

**Protocols:**
- `Projects/protocols/02_plan_protocol.md` (how to use the plan)
- `Projects/protocols/03a_continue_working.md` (autonomous work loop)
- `Projects/protocols/context_config.md` (threshold + handoff template)

Read and follow all three protocol files.

## Principle

Prefer loading extra context over making a short-sighted decision. This
session starts cold — the project plan's author took surrounding
architecture and patterns for granted. A few thousand extra tokens spent
on orientation is cheap compared to a bad architectural choice.

Do NOT open `plan.md` first. Orient yourself in the codebase FIRST.

## Execution

### 1. ORIENT yourself in the codebase (before touching the project plan)

Read in this order:

**1a. Foundation docs (always):**
- `docs/README.md` — doc index + task-driven reading order
- `docs/01_ARCHITECTURE.md` — layers, package APIs, dependency rules
- `docs/02_PATTERNS.md` — design patterns in use
- `docs/03_CONVENTIONS.md` — naming, file org, test + doc conventions

**1b. `CLAUDE.md`** at the project root (non-negotiable instructions)
and any auto-memory files referenced.

**1c. Task-specific docs** for the area this project works in — consult
the project's `design.md` (in Step 2) for which docs are relevant; or
scan `docs/systems/` and `docs/guides/` for subsystem docs that the
project's files mention.

**1d. Related code** — read the files that Phase <N> touches AND their
upstream/downstream neighbours. Read helpers and fixtures introduced by
earlier phases of the same project; their docstrings encode the contract.

**1e. Related tests** — read the tests that Phase <N> will modify PLUS
neighbouring tests that exercise the same subsystem.

If you're unsure whether a file is relevant, read it. Short-sighted
decisions cost more than extra tokens.

### 2. LOAD the project files (only after Step 1)

Read in this order:

1. `Projects/active_projects/PROJ-$0/design.md` — architectural rationale
2. `Projects/active_projects/PROJ-$0/decisions.md` — full decision log
3. `Projects/active_projects/PROJ-$0/plan.md` § Current State — authoritative handoff
4. `Projects/active_projects/PROJ-$0/phase_<N>_checklist.md` — task list for the active phase
5. `Projects/active_projects/PROJ-$0/manifest.md` — file manifest for parallel-work safety
6. `Projects/active_projects/PROJ-$0/handoff_prompt.md` IF it exists — expanded context from the previous session
7. Any `.agent_reports/PROJ-$0-*` directories — audit outputs from prior sessions

### 3. RUN status scripts

```bash
python Projects/scripts/project_status.py PROJ-$0
python Projects/scripts/current_task.py PROJ-$0
```

**FIRST TIME on a new project:** also run `pytest tests/` (full, no
--testmon) to establish baseline and initialize testmon.

### 4. EXECUTE the autonomous work loop

- Work through tasks using **Strict TDD** (tests BEFORE implementation)
- Use `pytest tests/ --testmon` for incremental testing
- Check off completed subtasks AS you finish them (not in batches)
- Add implementation notes to each task
- **Update `manifest.md` DURING the task** if you touch a file not yet listed
- **Update `docs/` DURING the task** if you change architecture/patterns/conventions
- **Continue until `check_context.py` returns STOP (at the 80% threshold),
  all project tasks are complete, or a genuine blocker is hit.**
  **Phase completion is a checkpoint, not an exit condition.** If the next
  phase looks too big to fit under 80%, split it (add sub-phases in the
  checklist file), don't hand off early. A cold restart burns 40-70k on
  re-orientation — splitting is cheaper. See
  `Projects/protocols/context_config.md` § Natural Stopping Points.

### 5. BEFORE STOPPING

1. Run phase validation:
   ```bash
   python Projects/scripts/validate_phase.py PROJ-$0 [current_phase]
   ```
   FAIL is EXPECTED at mid-phase stops (later tasks in the same phase are
   not yet done). Read the output carefully:
   - Structural FAIL (you claimed something complete that isn't) → fix it
   - Mid-phase FAIL (finished tasks all checked, later tasks pending) → legitimate stop
   See `Projects/protocols/03a_continue_working.md` § "Interpreting the result".

2. Update `## Current State` in plan.md with all 5 fields (Last Updated,
   Last Agent Action, Next Action, Blockers, Context for Next Agent).

3. Verify `manifest.md` lists every file touched this session.

4. Write `Projects/active_projects/PROJ-$0/handoff_prompt.md` using the
   template in `Projects/protocols/context_config.md` § Handoff prompt
   template. The prompt MUST instruct the next agent to read all
   project-related docs + related code BEFORE reading the project plan.
   Bias toward extra context, not minimal.

5. Print the handoff prompt to chat so the user can copy-paste into a new session.

6. Provide a session summary (Tasks Completed, Tasks In Progress, Tests,
   Files Modified, Exit Reason, Next Agent Should).

## Constraints

- Tests MUST be written BEFORE implementation (Strict TDD).
- Code MUST be consistent with `docs/`. Flag discrepancies; don't silently diverge.
- If a file is relevant to Phase <N> but unfamiliar to you, READ IT before modifying.
- Prefer extra context over short-sighted decisions.
