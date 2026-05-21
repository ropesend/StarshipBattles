# Phase 3: Minor (stale-bridge / dead-code / test-seam cleanup)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-471 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Partial — Task 3.4 DONE; 3.1 DROPPED (not dead); 3.2, 3.3 NOT DONE
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

- [ ] The audit flagged `set_default_profiler` (`profiling.py:25`) as a removable bridge (0 `get_default_profiler()` consumers; all access is via `ctx.profiler`). **Verification correction (Codex consult):** `set_default_profiler()` is still called in `create_production()` (`game/context.py:165-176`), and `profile_action` / `profile_block` (`profiling.py:116-149`) still depend on `_default_profiler` as their live module-level hook. This is a design cleanup, not dead-code deletion. Decide whether to (a) migrate `profile_action`/`profile_block` to require ctx, then remove the bridge, or (b) keep the bridge as the intentional module-level profiling hook. Record the decision in `decisions.md`.
- [ ] If removing: ensure `profile_action` / `profile_block` callers have a ctx-based path before deleting `_default_profiler` / `set_default_profiler`.
- [ ] Verify: pytest passes; profiling decorators still function; no broken `profile_action`/`profile_block` callers.

### Task 3.3: Remove `_default_llm_provider` bridge (if Phase 2.7 done) [Simple]
**File:** `game/services/llm/defaults.py`
**Tests:** `pytest tests/ -k llm`; then `pytest tests/ --testmon`

- [ ] Once Task 2.7 has migrated `panel_factory.py:167` to `ctx.llm_provider`, remove the now-stale `set_default_llm_provider()` (`defaults.py:31`) and drop its `create_production()` call (`game/context.py:183`), leaving `ctx.llm_provider` as the single path. Skip if Task 2.7 was not completed.
- [ ] Verify: pytest passes; no `get_default_llm_provider()` production consumers remain.

### Task 3.4: Add `reset_crew_priority_registry()` test seam [Simple]
**File:** `game/simulation/entities/stat_contributors/registry.py`
**Tests:** `pytest tests/ -k crew_priority`; then `pytest tests/ --testmon`

- [x] Added `reset_crew_priority_registry()` to `game/simulation/entities/stat_contributors/registry.py` that restores the 4 canonical default entries in place (mirrors `reset_stat_contributor_registry()`); wired into both the pre-test and teardown reset points of conftest's `reset_game_state` fixture.
- [x] Verify: pytest passes; a reset seam exists matching the sibling registry's pattern.

**Notes:** TDD via `tests/unit/simulation/entities/stat_contributors/test_crew_priority_reset_seam.py`.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-20_082533_state-audit/`. See `findings/source_audit.md` for the link._
