# Phase 5: Runtime Unknown-stat_key Warning

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-273 5`
> 2. Only proceed if output shows PASSED

**Status:** Not Started
**Objective:** Surface unknown stat_keys to developers at runtime via a once-per-source WARN log. Prevents silent swallow when a compiler emits an entry that no ability/ship reads.

---

## Tasks

### Task 5.1: Write failing unit test [Simple]
**File:** `tests/unit/simulation/combat/test_fleet_aura_manager.py` (likely exists — verify; if not, create)
**Tests:** `pytest tests/unit/simulation/combat/test_fleet_aura_manager.py -v`

- [ ] Add `test_unknown_stat_key_emits_warning_once_per_source()`:
  - Construct a `ModifierStack` with two entries for the same unknown stat_key from the same source
  - Run one `_apply_bonuses` tick
  - Assert logger received exactly ONE warning (not two), including the stat_key name and the source
- [ ] Add `test_unknown_stat_key_different_sources_warn_separately()`:
  - Two unknown stat_keys from two different sources
  - Assert two warnings logged
- [ ] Run tests — verify both fail (no warning issued today)

**Notes:**

### Task 5.2: Implement once-per-source warning [Medium]
**File:** `game/simulation/combat/fleet_aura_manager.py`
**Tests:** `pytest tests/unit/simulation/combat/test_fleet_aura_manager.py -v`

- [ ] Add import: `from game.simulation.combat.ability_stat_registry import ABILITY_STAT_REGISTRY`
- [ ] Also read all stat_keys that ARE consumed by abilities — see Task 5.3 (this is the "known" set)
- [ ] In `_apply_bonuses`, before writing an entry to `ship.external_stats`, check if its `effect.stat_key` is in the known set
- [ ] Maintain `self._warned_stat_keys: Set[Tuple[str, str]]` (key = (stat_key, source))
- [ ] When an unknown stat_key is encountered and the (stat_key, source) pair is new, emit `logger.warning(...)` and add to set
- [ ] Run tests — they should pass

**Notes:**

### Task 5.3: Build the "known stat_keys" allowlist [Medium]
**File:** `game/simulation/combat/ability_stat_registry.py`
**Tests:** `pytest tests/unit/simulation/combat/ -v`

- [ ] Add a module-level constant `KNOWN_EXTERNAL_STAT_KEYS: FrozenSet[str]` containing every stat_key written to `ship.external_stats` that is also read somewhere (ability or ship_stats)
- [ ] At minimum: `shield_capacity_mult`, `damage_mult`, `shield_bonus_add` from the registry
- [ ] Plus: any additional stat_keys emitted by the registry or consumed directly by `ship_stats.py::_apply_aggregated_stats` (grep for `ship.external_stats.get(`)
- [ ] Add a test that asserts: every `mapping.stat_key` in `ABILITY_STAT_REGISTRY.values()` is also in `KNOWN_EXTERNAL_STAT_KEYS`
- [ ] FleetAuraManager imports this set for its allowlist check

**Notes:**

### Task 5.4: End-to-end integration [Simple]
**File:** N/A
**Tests:** `pytest tests/integration/simulation/combat/ -n 12`

- [ ] Full aura-manager integration suite passes
- [ ] No new warnings printed for existing battles (known stat_keys)
- [ ] Manual: launch a Combat Lab test that uses complex modifiers, check logs — no warnings

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 6
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-273 5`
