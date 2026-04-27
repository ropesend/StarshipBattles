# Phase 1: `SHIELD_BONUS_ADD` additive stat_key + ship-level plumbing

> **SCOPE REVISED 2026-04-13:** Originally scoped to follow `ACCURACY_ADD`'s
> per-ability binding pattern. User clarified that flat shield bonus is
> per-ship, not per-component — the bonus should behave exactly as if
> the ship had an extra shield component providing the ability. So the
> plumbing lives at ship-level (`Ship.recalculate_stats`), not in a
> per-ability `AbilityStatBinding`. See [decisions.md](decisions.md) 2026-04-13 entries.

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-271 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Risk:** MEDIUM (ship-level plumbing is novel; pipeline ordering is load-bearing)
**Depends On:** None
**Objective:** Add the infrastructure needed to apply additive shield bonuses to ships at the SHIP level via the `external_stats` bridge. A ship with `ship.external_stats['shield_bonus_add'] = 50` has its `max_shields` raised by 50 once (not per shield component). Pipeline order is `(base + flat) × mult` — flat adds to base, then multiplicative effects scale.

---

## Tasks

### Task 1.1: Add `SHIELD_BONUS_ADD` to `StatKey` enum [Simple]
**File:** `game/simulation/components/abilities/stat_keys.py`
**Tests:** `pytest tests/unit/modifiers/test_stat_key.py tests/unit/simulation/components/abilities/test_stat_keys.py --tb=short`

- [x] Write failing test asserting `StatKey.SHIELD_BONUS_ADD` exists with `.value == "shield_bonus_add"`, `StatKey.get_default(SHIELD_BONUS_ADD) == 0.0`
- [x] Run — fails (4/4 new tests fail with "has no attribute SHIELD_BONUS_ADD")
- [x] Add the enum entry (copy shape of `ACCURACY_ADD` at `stat_keys.py:57`)
- [x] Add it to the `additive_stats` set in `get_default` (line 72-77) so default is 0.0
- [x] Run — passes (9/9 green in test_stat_key.py)

**Notes:** Added `TestShieldBonusAddStatKey` class with 4 tests (exists, value, default_is_zero, in_default_stats_dict) to `tests/unit/modifiers/test_stat_key.py`. Added `SHIELD_BONUS_ADD = "shield_bonus_add"` to the StatKey enum and included it in `additive_stats` set in `get_default()`.

---

### Task 1.2: Ship-level `max_shields` includes `shield_bonus_add` from external_stats [Complex]
**Files:** `game/simulation/entities/ship.py` (and wherever `max_shields` is computed — grep for `max_shields` assignment)
**Tests:** `pytest tests/unit/simulation/entities/test_ship_shield_bonus_add.py --tb=short` (new file)

- [x] Grep `game/simulation/entities/` for where `Ship.max_shields` is computed/aggregated. Document current shape in Notes.
- [x] Write failing test: a ship with baseline `max_shields == 500` (shield_generator component) and `ship.external_stats = {'shield_bonus_add': 50.0}` has effective `max_shields == 550` after `ship.recalculate_stats()`.
- [x] Run — fails (3/5 fail for the right reason: 500→550 raise not happening, storm compose not happening, no-shields case returns 0 instead of 50)
- [x] Implement: in `ship_stats.py::_apply_aggregated_stats` at line 456, after setting `ship.max_shields = acc['max_shields']`, add the external flat bonus scaled by the external `shield_capacity_mult` so it composes identically to a virtual extra shield component.
- [x] Run — 5/5 passes
- [x] Pipeline-ordering test: ship with `shield_capacity_mult=0.5` AND `shield_bonus_add=50` on `external_stats`, baseline shield capacity 500 → effective `max_shields` = (500 + 50) × 0.5 = 275. Locked in `test_flat_bonus_stacks_with_storm_mult`.
- [x] Edge case test: ship with zero shield components + `shield_bonus_add=50` on external_stats → `max_shields == 50` (`test_flat_bonus_on_ship_with_no_shields` green).

**Notes:** `Ship.max_shields` is computed in `game/simulation/entities/ship_stats.py::_aggregate_defense_abilities` (line 415-417 sums `ShieldProjection.capacity` into `acc['max_shields']`) and finalized in `_apply_aggregated_stats` (line 456 `ship.max_shields = acc['max_shields']`). The per-component `capacity` has already been multiplied by external `shield_capacity_mult` via `ShieldProjection.recalculate()` → `get_effective_stat('shield_capacity_mult', 1.0)` composition at `abilities/base.py:291-292`. For the flat bonus to behave "like a virtual extra shield component", we apply the same `shield_capacity_mult` to the flat value at the same boundary. Implementation: 7-line insert immediately after `ship.max_shields = acc['max_shields']` in `_apply_aggregated_stats`. Regression gate: 1530 tests (entities + modifiers + abilities + strategy combat integration) green.

---

### Task 1.3: `FleetAuraManager` end-to-end test for SHIELD_BONUS_ADD [Medium]
**File:** `tests/unit/simulation/combat/test_fleet_aura_extended.py` (extend)
**Tests:** `pytest tests/unit/simulation/combat/test_fleet_aura_extended.py --tb=short`

- [x] Write a test that builds a `ModifierStack` with a `ModifierEntry(stat_key="shield_bonus_add", value=50.0, operation="add")` targeting team 0, materializes a ship stand-in, and asserts `ship.external_stats['shield_bonus_add'] == 50.0` after `FleetAuraManager.initialize(ships, modifier_stack=stack)`.
- [x] Test stacking from multiple ModifierStack entries: entry A (+30) + entry B (+20) on team 0 → total external_stats = 50. SimpleNamespace ships + direct external_stats inspection.
- [x] Verify `FleetAuraManager._apply_bonuses` populates `ship.external_stats['shield_bonus_add']` correctly; no placeholder warning logged (caplog assertion).
- [x] Regression check: ran `tests/unit/simulation/entities/ tests/unit/modifiers/ tests/unit/simulation/components/abilities/ tests/integration/strategy/combat/` — 1530 passed (before Task 1.3 additions).

**Notes:** Added 4 tests to `test_fleet_aura_manager_modifier_stack.py`: per_team routing, multiple entries sum, global reaches every team, no placeholder warning. The max_shields → 150 integration is proven at the ship-level unit tests in `test_ship_shield_bonus_add.py` (Task 1.2) — splitting the bridge test (FleetAuraManager → external_stats) from the composition test (external_stats → max_shields) keeps each layer's contract testable independently. Added `external_stats={}` to the `_ship()` SimpleNamespace helper so the FleetAuraManager can write to it.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Unit tests for `SHIELD_BONUS_ADD` + ship plumbing + FleetAuraManager bridge green
- [x] Pipeline-ordering test locked with assertion (base + flat) × mult
- [x] `FleetAuraManager` logs NO placeholder warning for `shield_bonus_add`
- [x] All Phase 9 Track A integration tests still green (regression ran 1530 passing before Task 1.3)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
