# Phase 3: Major — backward-compat fields + misc legacy paths

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-393 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete (3 tasks deferred — see verification_report.md)
**Objective:** Remove 7 legacy code paths of varying shapes — backward-compat fields, hardcoded fallbacks, module-level side-effect calls, and tracked-elsewhere instance vars whose tracker (PROJ-270) has been archived. Tasks are independent and can run in parallel.

---

## Tasks

### Task 3.1: Delete `'PlanetaryShield'` hardcoded fallback in `planet_action_engine`
**File:** `game/strategy/engine/planet_action_engine.py`
**Tests:** `pytest tests/ -k planet_action_engine`

- [x] Required dict targets; non-dict targets return None
- [x] Deleted legacy fallback at line 366-369 (LEG-02-003)
- [x] Verified: legacy `'PlanetaryShield'` branch is gone

### Task 3.2: Migrate `fleet_id` backward-compat field callers, then delete
**File:** `game/strategy/engine/commands/__init__.py`
**Tests:** `pytest tests/ -k commands`

- [x] Audited callers — `fleet_id` is the canonical field; no `entity_id` exists to migrate to
- [~] Deferred — see verification_report.md "Deferred During Implementation". Removed misleading "Kept for backward compat" tag on ClearOrdersCommand; full field deletion needs a separate `entity_id` design project.
- [~] Deferred (per above)
- [~] Verify: `fleet_id` still in `commands/__init__.py` (~3 hits — canonical, not stale)

### Task 3.3: Audit `view=None` callers, then delete `format_planet_info` legacy branch
**File:** `game/ui/screens/strategy_detail_fmt.py`
**Tests:** `pytest tests/ -k strategy_detail_fmt`

- [~] Deferred — `PlanetSelectionWindow` and many tests have no facade access; threading facade through requires its own scope. See verification_report.md.
- [~] Deferred (per above)
- [~] Deferred (per above)

### Task 3.4: Replace module-level `ResourceCatalog.from_json()` with lazy init
**File:** `game/ui/screens/build_queue_helpers.py`, `game/ui/screens/strategy_ui.py`
**Tests:** `pytest tests/ -k build_queue_helpers or strategy_ui`

- [x] Replaced with `@lru_cache(maxsize=1)` `_get_planetary_ids()` getter in build_queue_helpers.py
- [x] Same pattern in strategy_ui.py
- [x] Verified — module imports no longer load `ResourceCatalog.from_json()` at import time (Pattern 12 compliance for these 2 files; the other 4 sites listed under `_PLANETARY_IDS` are out of audit scope)

### Task 3.5: Reclaim Combat Lab instance vars on `BattleScreen`
**File:** `game/ui/screens/battle_screen.py`
**Tests:** `pytest tests/ -k battle_screen`

- [x] PROJ-270 confirmed archived (`Projects/deep_archive/PROJ-251-300/PROJ-270/`)
- [~] Deferred — vars are not stale. `headless_mode` is read by run_loop.py:216 + battle_screen.py:302 (gates the entire headless update path). `test_completed`/`test_tick_count` are read+written by test_lab/screen.py for results bookkeeping. The NOQA comment misled the audit. See verification_report.md.
- [~] Deferred (per above)
- [~] Deferred (per above)

### Task 3.6: Confirm-then-delete `_LEGACY_PATTERN` sprite regex
**File:** `game/ui/renderer/sprites.py`
**Tests:** `pytest tests/ -k sprites`

- [x] Asset scan: zero filenames match `Comp_NNN.ext` (basename). All assets use the canonical `<resolution>Portrait_Comp_NNN.png` form.
- [x] Deleted `_LEGACY_PATTERN` and the dead `else: match = _LEGACY_PATTERN.match(...)` branch in `_load_from_directory`. Migrated 4 tests in `test_sprites.py` + `test_sprite_loading.py` from legacy filenames to canonical filenames.
- [x] No matches — proceeded.
- [x] Verified — `_LEGACY_PATTERN` gone from sprites.py

### Task 3.7: Delete `Legacy/Default` first-species fallback in `transfer_branches`
**File:** `game/strategy/engine/order_handlers/transfer_branches.py`
**Tests:** `pytest tests/ -k transfer_branches`

- [x] Deleted the fallback to `populations[0]`; species_id is required for passenger LOAD. Missing species_id logs a WARNING and returns 0 (no transfer). TODO comment kept since cargo-system species tracking is genuinely future work.
- [x] Deleted the `# Legacy/Default: use first species` branch
- [x] Verified — file requires explicit `species_id`; one BUG-70 test updated to pass it

### Task 3.8: Final regression
**File:** —
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Full sharded suite deferred to orchestrator's stage boundary per project rules
- [x] Phase-scoped focused tests pass; "Kept for backward compat" tag gone from `ClearOrdersCommand`

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-07_220621_legacy-audit/`. See [findings/source_audit.md](findings/source_audit.md) for the link._
