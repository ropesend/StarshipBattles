# Phase 3: Major — backward-compat fields + misc legacy paths

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-393 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove 7 legacy code paths of varying shapes — backward-compat fields, hardcoded fallbacks, module-level side-effect calls, and tracked-elsewhere instance vars whose tracker (PROJ-270) has been archived. Tasks are independent and can run in parallel.

---

## Tasks

### Task 3.1: Delete `'PlanetaryShield'` hardcoded fallback in `planet_action_engine`
**File:** `game/strategy/engine/planet_action_engine.py`
**Tests:** `pytest tests/ -k planet_action_engine`

- [ ] Either formally support the string-only target format OR require all callers to pass a full target dict (with `ability_name` and `facility_instance_id`)
- [ ] Delete the legacy fallback at line 366-369 (LEG-02-003)
- [ ] Verify: file no longer references the hardcoded `'PlanetaryShield'` literal in the legacy branch

### Task 3.2: Migrate `fleet_id` backward-compat field callers, then delete
**File:** `game/strategy/engine/commands/__init__.py`
**Tests:** `pytest tests/ -k commands`

- [ ] Audit callers across `game/`, `tests/` for `fleet_id=` keyword arg or `.fleet_id` attribute reads on `ClearOrdersCommand`, `DeleteOrderCommand`, `ReorderOrderCommand`
- [ ] Migrate each caller to use `entity_id`/`entity_type` (LEG-02-004)
- [ ] Delete the `fleet_id: int  # Kept for backward compat` field on all 3 command classes (instances at line 102, ~286, ~297)
- [ ] Verify: `grep -rn "fleet_id" game/strategy/engine/commands/__init__.py" returns zero hits

### Task 3.3: Audit `view=None` callers, then delete `format_planet_info` legacy branch
**File:** `game/ui/screens/strategy_detail_fmt.py`
**Tests:** `pytest tests/ -k strategy_detail_fmt`

- [ ] Run `grep -rn "format_planet_info" game/ tests/" — for each caller passing `view=None`, migrate to construct a `ColonyDemographicView` (LEG-02-006 UNCERTAIN-included)
- [ ] Delete the legacy `view is None` branch at lines 254-256 (15 LOC)
- [ ] Verify: function signature requires `view: ColonyDemographicView` (no Optional); all tests pass

### Task 3.4: Replace module-level `ResourceCatalog.from_json()` with lazy init
**File:** `game/ui/screens/build_queue_helpers.py`, `game/ui/screens/strategy_ui.py`
**Tests:** `pytest tests/ -k build_queue_helpers or strategy_ui`

- [ ] In `build_queue_helpers.py:8`: replace `_PLANETARY_IDS = [d.id for d in ResourceCatalog.from_json().by_display_group("planetary")]` with a `@lru_cache`-wrapped getter or a function that resolves on first access (LEG-02-013)
- [ ] In `strategy_ui.py:25`: same pattern
- [ ] Verify: module imports do not trigger `ResourceCatalog.from_json()` at import time (Pattern 12)

### Task 3.5: Reclaim Combat Lab instance vars on `BattleScreen`
**File:** `game/ui/screens/battle_screen.py`
**Tests:** `pytest tests/ -k battle_screen`

- [ ] Confirm PROJ-270 is archived and there is no live PROJ-270 Phase 10 follow-up still using these vars (LEG-03-023 UNCERTAIN-included)
- [ ] Delete the 6 instance variables `headless_mode`, `headless_start_time`, `test_mode`, `test_scenario`, `test_tick_count`, `test_completed` at lines 117-125
- [ ] Delete the `# NOQA: legacy-retained` comment block above them
- [ ] Verify: `grep -rn "headless_mode\|test_tick_count\|test_completed" game/ tests/` returns zero hits

### Task 3.6: Confirm-then-delete `_LEGACY_PATTERN` sprite regex
**File:** `game/ui/renderer/sprites.py`
**Tests:** `pytest tests/ -k sprites`

- [ ] Scan the assets directory: `grep -rln -E "Comp_[0-9]+\.[a-z]+" assets/" — check whether any current asset filename matches the legacy `Comp_N.ext` pattern (LEG-03-024 UNCERTAIN-included with asset scan)
- [ ] If zero matches, delete `_LEGACY_PATTERN = re.compile(r"Comp_(\d+)\.\w+$")` at line 14 and any code that uses it
- [ ] If matches found, surface to the user and pause this task
- [ ] Verify: `grep -rn "_LEGACY_PATTERN" game/" returns zero hits (assuming asset scan was clean)

### Task 3.7: Delete `Legacy/Default` first-species fallback in `transfer_branches`
**File:** `game/strategy/engine/order_handlers/transfer_branches.py`
**Tests:** `pytest tests/ -k transfer_branches`

- [ ] Resolve the TODO at line 116 ("If we ever track species in fleet cargo, use species_id here") OR delete the fallback to `populations[0]` and require callers to pass `species_id` (LEG-04-004)
- [ ] Delete the `# Legacy/Default: use first species` branch at lines 107-108
- [ ] Verify: file requires explicit `species_id`

### Task 3.8: Final regression
**File:** —
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run full sharded suite — confirm baseline preserved
- [ ] Verify: pytest passes; no remaining legacy/backward-compat tags in the touched files

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-07_220621_legacy-audit/`. See [findings/source_audit.md](findings/source_audit.md) for the link._
