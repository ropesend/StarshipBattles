# Phase 3: Minor (stale-bridge / dead-code / test-seam cleanup)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-471 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete — Task 3.4 DONE; 3.1 DROPPED (not dead); 3.2 RESOLVED (keep bridge as intentional hook); 3.3 DROPPED (gated on 2.7, which was dropped)
**Objective:** Remove the two truly-dead bridge singletons, evaluate (do not blindly delete) the profiler bridge, and add the missing crew-priority test-isolation seam. Do this last, after the singleton-divergence and collection work in Phases 1–2.

---

## Tasks

### Task 3.1: ~~Remove dead `_default_game_settings` and `_default_image_provider` bridges~~ — DROPPED (not dead)
**Status:** DROPPED per scope revision 2026-05-20 (see decisions.md).

Codex re-verification found both are still tested and injectable:
`get_default_game_settings()`/`set_default_game_settings()` are exercised by
`tests/unit/ui/services/test_game_settings.py:88-93`; the image-provider defaults are part
of the application-context contract (`tests/unit/ui/services/image/test_defaults.py`,
`tests/unit/core/test_application_context.py:192-195`). They are not dead code. No change.

### Task 3.2: Evaluate/remove the `_default_profiler` bridge (design cleanup, NOT blind deletion) [Medium]
**File:** `game/core/profiling.py`
**Tests:** `pytest tests/ -k profil`; then `pytest tests/ --testmon`

- [x] RESOLVED — decision (b): keep the bridge as the intentional module-level profiling hook. Re-verified `profile_action`/`profile_block` (`profiling.py:116-149`) read `_default_profiler` directly and are applied at import/definition time across the codebase with no `ctx` at their call sites; `set_default_profiler()` is the single startup wiring (`context.py:176`). Migrating the decorators/context-managers to require ctx would mean threading ctx into every decorated function — large change, zero divergence benefit (single startup setter). Decision in `decisions.md` (2026-05-21).
- [x] Not removing — bridge retained; `profile_action`/`profile_block` unchanged.
- [x] Verify: existing `tests/ -k profil` stays green; decorators still function.

### Task 3.3: Remove `_default_llm_provider` bridge (if Phase 2.7 done) [Simple]
**File:** `game/services/llm/defaults.py`
**Tests:** `pytest tests/ -k llm`; then `pytest tests/ --testmon`

- [x] DROPPED — gated on Task 2.7, which was dropped (see Phase 2 + decisions.md 2026-05-21). The sole consumer was not migrated (ctx-less UI chain), so the `set_default_llm_provider()` bridge + its `create_production()` call remain as the intentional module-level hook. No change.
- [x] Verify: n/a — bridge intentionally retained.

### Task 3.4: Add `reset_crew_priority_registry()` test seam [Simple]
**File:** `game/simulation/entities/stat_contributors/registry.py`
**Tests:** `pytest tests/ -k crew_priority`; then `pytest tests/ --testmon`

- [x] Added `reset_crew_priority_registry()` to `game/simulation/entities/stat_contributors/registry.py` that restores the 4 canonical default entries in place (mirrors `reset_stat_contributor_registry()`); wired into both the pre-test and teardown reset points of conftest's `reset_game_state` fixture.
- [x] Verify: pytest passes; a reset seam exists matching the sibling registry's pattern.

**Notes:** TDD via `tests/unit/simulation/entities/stat_contributors/test_crew_priority_reset_seam.py`.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked (done / resolved / dropped-with-reason)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-20_082533_state-audit/`. See `findings/source_audit.md` for the link._
