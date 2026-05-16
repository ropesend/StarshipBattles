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

### Task 3.2: Migrate `fleet_id` backward-compat field callers, then delete — CLOSED VIA PROJ-397

**PROJ-406 reconciliation Note:** Closed via PROJ-397 Phase 3 (LEG-02-004 deferred-item track). Path B simplified: `fleet_id` retained as the canonical command field; the deletion-and-rename track was retired. See `Projects/active_projects/PROJ-397/phase_3_checklist.md`.

**File:** `game/strategy/engine/commands/__init__.py`
**Tests:** `pytest tests/ -k commands`

- [x] Audited callers — `fleet_id` is the canonical field; no `entity_id` exists to migrate to
- [x] Closed via PROJ-397 Phase 3: misleading "Kept for backward compat" tag removed; field retained as canonical (Path B).
- [x] Closed via PROJ-397 Phase 3.
- [x] Verify: `fleet_id` still in `commands/__init__.py` (~3 hits — canonical, not stale)

### Task 3.3: Audit `view=None` callers, then delete `format_planet_info` legacy branch — CLOSED VIA PROJ-397

**PROJ-406 reconciliation Note:** Closed via PROJ-397 Phase 3 (LEG-02-006 deferred-item track). Facade threading through `PlanetSelectionWindow` was completed; legacy `view=None` branch deleted. See `Projects/active_projects/PROJ-397/phase_3_checklist.md`.

**File:** `game/ui/screens/strategy_detail_fmt.py`
**Tests:** `pytest tests/ -k strategy_detail_fmt`

- [x] Closed via PROJ-397 Phase 3: facade threaded through `PlanetSelectionWindow`.
- [x] Closed via PROJ-397 Phase 3: `view=None` legacy branch deleted.
- [x] Closed via PROJ-397 Phase 3.

### Task 3.4: Replace module-level `ResourceCatalog.from_json()` with lazy init
**File:** `game/ui/screens/build_queue_helpers.py`, `game/ui/screens/strategy_ui.py`
**Tests:** `pytest tests/ -k build_queue_helpers or strategy_ui`

- [x] Replaced with `@lru_cache(maxsize=1)` `_get_planetary_ids()` getter in build_queue_helpers.py
- [x] Same pattern in strategy_ui.py
- [x] Verified — module imports no longer load `ResourceCatalog.from_json()` at import time (Pattern 12 compliance for these 2 files; the other 4 sites listed under `_PLANETARY_IDS` are out of audit scope)

### Task 3.5: Reclaim Combat Lab instance vars on `BattleScreen` — CLOSED VIA PROJ-397

**PROJ-406 reconciliation Note:** Closed via PROJ-397 Phase 1 (CRITICAL F-01). The OpenCode review confirmed 4 of 6 vars (`test_mode`, `test_scenario`, `test_tick_count`, `test_completed`, `headless_start_time`) were dead in production; `headless_mode` retained as the only legitimately-active var. See `Projects/active_projects/PROJ-397/phase_1_checklist.md`.

**File:** `game/ui/screens/battle_screen.py`
**Tests:** `pytest tests/ -k battle_screen`

- [x] PROJ-270 confirmed archived (`Projects/deep_archive/PROJ-251-300/PROJ-270/`)
- [x] Closed via PROJ-397 Phase 1: 5 dead vars deleted; `headless_mode` retained.
- [x] Closed via PROJ-397 Phase 1.
- [x] Closed via PROJ-397 Phase 1.

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

- [x] Full sharded suite deferred to orchestrator's stage boundary per project rules
- [x] Phase-scoped focused tests pass; "Kept for backward compat" tag gone from `ClearOrdersCommand`

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-07_220621_legacy-audit/`. See [findings/source_audit.md](findings/source_audit.md) for the link._
