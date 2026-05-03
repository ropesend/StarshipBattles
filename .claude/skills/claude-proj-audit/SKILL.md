---
name: claude-proj-audit
description: Perform a skeptical audit of a completed project to verify quality and correctness
disable-model-invocation: true
argument-hint: <project-number>
---

# Audit Project PROJ-$0

**Protocol:** `Projects/protocols/04_audit_project.md`

Read and follow the full protocol file `Projects/protocols/04_audit_project.md`.

## Your Role

Adopt the **Skeptical Reviewer** persona. Your job is to **find problems**, not rubber-stamp completion.

## Execution

1. **LOAD** the project plan: `Projects/active_projects/PROJ-$0/plan.md`

2. **RUN** pre-audit validation (REQUIRED):
   ```bash
   python Projects/scripts/validate_audit_ready.py PROJ-$0 --run-tests
   ```
   This runs the FULL test suite (no testmon) to ensure complete verification.
   Only proceed if validation PASSES. If it FAILS, return project to implementation.

3. **EXECUTE** Comprehensive Review:
   - Go through EVERY task and subtask
   - Verify: completion, tests exist, tests pass, code matches intent
   - **Verify code changes are consistent with `docs/` (architecture, patterns, conventions)**
   - **If project changed architecture or patterns, verify `docs/` was updated**
   - Document all concerns

4. **For EACH concern:**
   - Launch investigation agent with DIFFERENT perspective
   - Evaluate: confirmed problem, false positive, or unclear

5. **COMPILE** findings and either:
   - If issues found: Extend plan with fix phase, return to implementation
   - If clean: Mark audit as passed
   - If 3 cycles with persistent issues: Escalate to user

## 03c projects: rigorous final cumulative gate

If the project has `**Execution Protocol:** 03c-phase-aware-execution` in
its `plan.md`, this audit is the **final cumulative review gate** — the
project may NOT merge to `main` until every check below passes. Mid-project
cumulative reviews already covered each phase as it landed; this gate
confirms the integrated whole.

`validate_audit_ready.py` (extended for 03c) hard-fails if ANY of:

1. A finding has status `open` or `addressed_pending_review`.
2. A `deferred_until_phase` finding's target phase is ≤ the latest clean
   coverage and has not been resolved.
3. The latest clean review's `coverage_set` does not include every
   non-skipped phase (i.e. some phase has never been in a clean review).
4. The project branch tip SHA differs from the SHA covered by the latest
   clean review (i.e. unreviewed work is sitting on the project branch).

On clean audit: merge `proj/{PROJ-ID}/main` into `main`, record
`audit.merge_to_main_sha` and `audit.merge_to_main_at_utc` in
`phase_state.json`, then hand off to `claude-proj-archive`.

**MINDSET:** Be genuinely skeptical. Your job is to find problems, not approve.
