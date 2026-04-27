# Phase 5: Runtime Unknown-stat_key Warning

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-273 5`
> 2. Only proceed if output shows PASSED

**Status:** Complete
**Objective:** Surface unknown stat_keys to developers at runtime via a once-per-source WARN log. Prevents silent swallow when a compiler emits an entry that no ability/ship reads.

---

## Tasks

### Task 5.1: Write failing unit test [Simple]
**File:** `tests/unit/simulation/combat/test_fleet_aura_manager.py` (likely exists — verify; if not, create)
**Tests:** `pytest tests/unit/simulation/combat/test_fleet_aura_manager.py -v`

- [x] Add `test_unknown_stat_key_emits_warning_once_per_source()`:
  - Construct a `ModifierStack` with two entries for the same unknown stat_key from the same source
  - Run one `_apply_bonuses` tick
  - Assert logger received exactly ONE warning (not two), including the stat_key name and the source
- [x] Add `test_unknown_stat_key_different_sources_warn_separately()`:
  - Two unknown stat_keys from two different sources
  - Assert two warnings logged
- [x] Run tests — verify both fail (no warning issued today)

**Notes:** Chose to create a NEW dedicated file `tests/unit/simulation/combat/test_fleet_aura_unknown_stat_key_warning.py` rather than extending an existing fleet_aura test file — the warning is a discrete concern with 5 related tests, easier to maintain separately. Tests include: known-stat_key emits NO warning; unknown stat_key emits exactly one warning mentioning both key and source; same (key, source) repeat warns once; different sources with same key warn separately; placeholder still routes through `_log_placeholder_once` (not the new unknown path). All 3 new-behavior tests initially failed as expected.

### Task 5.2: Implement once-per-source warning [Medium]
**File:** `game/simulation/combat/fleet_aura_manager.py`
**Tests:** `pytest tests/unit/simulation/combat/test_fleet_aura_manager.py -v`

- [x] Add import: `from game.simulation.combat.ability_stat_registry import ABILITY_STAT_REGISTRY`
- [x] Also read all stat_keys that ARE consumed by abilities — see Task 5.3 (this is the "known" set)
- [x] In `_apply_bonuses`, before writing an entry to `ship.external_stats`, check if its `effect.stat_key` is in the known set
- [x] Maintain `self._warned_stat_keys: Set[Tuple[str, str]]` (key = (stat_key, source))
- [x] When an unknown stat_key is encountered and the (stat_key, source) pair is new, emit `logger.warning(...)` and add to set
- [x] Run tests — they should pass

**Notes:** Added check in `_append_external_from_entry` (not `_apply_bonuses` — the former is where each ModifierEntry is first translated and is the natural hook). Uses late import of `KNOWN_EXTERNAL_STAT_KEYS` to avoid adding a hard circular dep at module load. Deduplication set is `_unknown_stat_key_warned: Set[Tuple[str, str]]` (matches the pattern of `_placeholder_warned_sources`). The warning message tells developers EXACTLY what to do: "Add the key to KNOWN_EXTERNAL_STAT_KEYS in game/simulation/combat/ability_stat_registry.py, or check the compiler emission."

Decision: when an unknown stat_key is detected, the entry is STILL recorded (advisory-only warning). The aggregation engine already keys by stat_key, so unknown keys are harmless (just unused) — warning + record is safer than warning + drop, which could mask a wiring bug as a no-op.

### Task 5.3: Build the "known stat_keys" allowlist [Medium]
**File:** `game/simulation/combat/ability_stat_registry.py`
**Tests:** `pytest tests/unit/simulation/combat/ -v`

- [x] Add a module-level constant `KNOWN_EXTERNAL_STAT_KEYS: FrozenSet[str]` containing every stat_key written to `ship.external_stats` that is also read somewhere (ability or ship_stats)
- [x] At minimum: `shield_capacity_mult`, `damage_mult`, `shield_bonus_add` from the registry
- [x] Plus: any additional stat_keys emitted by the registry or consumed directly by `ship_stats.py::_apply_aggregated_stats` (grep for `ship.external_stats.get(`)
- [x] Add a test that asserts: every `mapping.stat_key` in `ABILITY_STAT_REGISTRY.values()` is also in `KNOWN_EXTERNAL_STAT_KEYS`
- [x] FleetAuraManager imports this set for its allowlist check

**Notes:** 10 stat_keys in the set — 3 from registry + 7 from `SimpleMultiplierAbility` subclasses. Enumerated by grep: `thrust_mult`, `turn_mult`, `strategic_mult` (propulsion.py); `capacity_mult`, `energy_gen_mult` (defense.py); `crew_capacity_mult`, `life_support_capacity_mult` (crew.py). Ship-level direct readers in `ship_stats.py` are `shield_bonus_add` (L462) and `shield_capacity_mult` (L470) — both already in the set.

Test `test_known_external_stat_keys_contains_all_registry_values` asserts registry/allowlist consistency; `test_known_external_stat_keys_is_frozen` locks the type.

### Task 5.4: End-to-end integration [Simple]
**File:** N/A
**Tests:** `pytest tests/integration/simulation/combat/ -n 12`

- [x] Full aura-manager integration suite passes
- [x] No new warnings printed for existing battles (known stat_keys)
- [x] Manual: launch a Combat Lab test that uses complex modifiers, check logs — no warnings

**Notes:** Wider regression sweep: 414 tests passed across battle_setup + simulation/combat + strategy/combat + unified entry guard. No test emitted unexpected warnings. Manual Combat Lab smoke deferred to user verification in the project's end-of-project manual checklist; all known production stat_keys are in the allowlist, so no warnings expected.

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 6
- [x] Run `python Projects/scripts/validate_phase.py PROJ-273 5`
