# PROJ-319 Handoff — After Phase 1+2+4.1

You're picking up `PROJ-319: Audit-shrink cleanup 2026-05-02`, a project that
removes verified dead code and consolidates verified duplications from the
audit at `Reviews/results/2026-05-02_184210_audit_shrink/`.

## Status

| Phase | Status | What was done |
|-------|--------|---------------|
| 1 | Complete | 14 dead imports / params / unreachable lines removed (~19 LOC). |
| 2 | Complete | `_extract_weapon_summaries` (battle_runner) and `_planet_has_shield_facility` (strategy_detail_fmt) deleted (~57 LOC). |
| 4 Task 4.1 | Complete | `resolve_race_config` extracted to new `game/strategy/services/race_resolver.py`; both engine wrappers route to it (DUP-X-01 CRITICAL, ~29 LOC). |
| 4 Tasks 4.2–4.14 | Not Started | 13 duplication consolidations remain; mix of Simple, Medium, Complex. |

**Total reclaimed so far: ~105 LOC. Remaining: ~628 LOC across 13 tasks.**

Three full sharded test runs passed cleanly except for one pre-existing flaky
timing test in `tests/unit/services/llm/test_background.py::test_elapsed_seconds_is_monotonic_then_frozen`
— that test fails intermittently on Windows due to `time.sleep(0.01)` vs
~15.6 ms scheduler resolution, NOT due to any PROJ-319 change. See
[decisions.md](decisions.md) and the project-memory file
`project_flaky_llm_background_test.md` for the analysis.

## Important: read these BEFORE the project plan

This session starts cold. Read in this order:

1. `docs/README.md`, then `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`,
   `docs/03_CONVENTIONS.md` (foundation).
2. `CLAUDE.md` at repo root (non-negotiable rules — strict TDD,
   documentation first, root cause fixes).
3. **`Projects/active_projects/PROJ-319/findings/verification_report.md`** —
   in particular the **Round 3 — Live Discovery During Phase 4 Task 4.1**
   section. It documents a real verifier failure mode that nearly bit the
   project: a "dead import" can still be reachable as a re-export through
   the file's `from X import Y` line. **Mitigation:** when extracting a new
   function or removing a Phase 1-style import, also grep
   `from <module_path> import <symbol>` across `tests/` to catch consumers
   treating the old module as a re-export hub.
4. `Projects/active_projects/PROJ-319/design.md` — architectural rationale
   and per-Phase risk notes.
5. `Projects/active_projects/PROJ-319/decisions.md` — decisions log
   including the 3 Round-2-and-3 verifier post-mortems.
6. `Projects/active_projects/PROJ-319/plan.md` § Current State — last action
   and next action.
7. `Projects/active_projects/PROJ-319/phase_4_checklist.md` — the active
   phase, with task-level instructions and audit IDs.
8. `Projects/active_projects/PROJ-319/manifest.md` — file-by-file action
   manifest including the test-fix file added in Round 3.

## Where to start

Begin Phase 4 at **Task 4.2 (DUP-X-09: superweapon validator pair)**. It is
[Simple] and well-bounded:

- File: `game/strategy/validation/superweapon_validator.py`
- Extract `_validate_star_targeted_superweapon(galaxy, fleet, ability_name, component_registry) -> ValidationResult`
- Both `validate_stellerate_star` (lines 99-125) and `validate_create_dyson_sphere` (lines 213-239) become thin wrappers passing `"DestroyStar"` and `"CreateDysonSphere"` respectively.
- Test path: `pytest tests/strategy/validation/`

After that, Tasks 4.3 through 4.9 are all Simple — knock them out in
sequence, running targeted pytests and checking the sharded suite at
phase end.

## Working budget guidance

- Tasks 4.2–4.9 (8 Simple tasks, ~218 LOC) can plausibly fit in one
  session if you're efficient with file reads.
- Tasks 4.10, 4.11, 4.13 (Medium, ~165 LOC) need ~1 session each — they
  involve adding a new mixin/base class and migrating 3–5 caller files.
- Tasks 4.12 (superweapon 3-file pipeline, Complex) and 4.14 (planet/star
  list window unification, Complex, ~150 LOC) **each warrant their own
  session**. Both touch many files and require manual smoke-testing of
  end-user flows (every superweapon for 4.12; both list windows + filters
  + presets for 4.14).

## Hard rules

- **Strict TDD:** for each duplication extraction, run the focused pytest
  path BEFORE the change to confirm green, then run again AFTER the change.
- **Re-export check:** before removing a function from its original file,
  grep `from <original_module> import <symbol>` across `tests/` and `game/`.
  Round 3 caught one of these the verifier missed.
- **Do not skip the LLM-flaky-test post-mortem step:** if the sharded run
  shows `tests/unit/services/llm/test_background.py::test_elapsed_seconds_is_monotonic_then_frozen`
  as the only failure, it is the known Windows timing flake; do NOT treat
  it as a regression. Cross-check `decisions.md` and project memory.
- **No premature work:** stick to the audit-verified items. Do NOT extract
  duplications the audit downrated to MINOR/INFO (e.g. DUP-X-15 onward,
  the LLM/Image background services DUP-X-23/24, etc.).

## Strict-TDD commands

```bash
# Targeted (preferred during a task)
pytest tests/strategy/validation/ --testmon
pytest tests/strategy/engine/ --testmon

# Full sharded (at phase end)
python Tools/test_sharded/test_sharded.py

# Phase validation
python Projects/scripts/validate_phase.py PROJ-319 4
```

## When you stop

- Run `python Projects/scripts/validate_phase.py PROJ-319 4` (FAIL is
  expected mid-phase; check it's a mid-phase fail not a structural fail).
- Update `plan.md` Current State (Last Updated, Active Phase, Last Action,
  Next Action, Blockers, Context for Next Agent).
- Update `manifest.md` if you touched files not yet listed.
- Update or replace this `handoff_prompt.md`.
