# Phase 3: Migrate `planet_energy_engine` (delete dead `_ACTIVATABLE_ABILITIES`)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-429 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** phase_2
**Review Mode:** lightweight

**Files (planned):**
- `game/strategy/engine/planet_energy_engine.py` (modify — delete `_ACTIVATABLE_ABILITIES`, swap `"PlanetaryShield"` literal)
- `tests/unit/strategy/engine/test_planet_energy_engine.py` (modify — assert constant gone)
- `tests/unit/strategy/services/test_planet_query_service.py` (read-only — characterization at lines 59-65 must stay green)

**Objective:** Delete the dead `_ACTIVATABLE_ABILITIES` constant (verified inert per TD-07 Verification Findings) and replace the literal `"PlanetaryShield"` at line 48 with a tag-driven query. Preserve the public surface (`_is_ability_active`, `get_activatable_ability_info`, `get_shield_info`) which is imported by `test_planet_energy_engine.py:5`.

---

## Reading

- [ ] Re-read `design.md` "Per-Consumer Migration Order" Phase 3 row and "Risks" `_ACTIVATABLE_ABILITIES` deletion row.
- [ ] Read `game/strategy/engine/planet_energy_engine.py` lines 1-100 (imports, constant, `get_shield_info`) and 270-282 (`_compute_activation_drain` — the live path that already uses `ComponentActivationState.is_draining_energy`).
- [ ] Read `tests/unit/strategy/engine/test_planet_energy_engine.py:1-15` to confirm imported symbols.

---

## Tasks

### Task 3.1: Pre-deletion safety grep [Simple]

- [ ] Run `rg -n "_ACTIVATABLE_ABILITIES"` across the entire repo.
- [ ] Confirm the only hits are the definition at `planet_energy_engine.py:80-89`, the doc reference at `docs/guides/adding_abilities.md:416`, and no in-code reads.
- [ ] If any unexpected reader is discovered, **stop** and switch to the `abilities_with_kind_tag(StrategicKind.ENERGY_DRAINING)` replacement path (per Risks table in design.md).

**Notes:** [Filled during implementation]

### Task 3.2: Add the failing "no exported constant" test (TDD red) [Simple]

**File:** `tests/unit/strategy/engine/test_planet_energy_engine.py`

- [ ] Add `test_module_does_not_export_activatable_abilities_constant`:
      `from game.strategy.engine import planet_energy_engine`
      `assert not hasattr(planet_energy_engine, '_ACTIVATABLE_ABILITIES')`
- [ ] Confirm failure: the constant still exists → test fails.

**Notes:** [Filled during implementation]

### Task 3.3: Delete `_ACTIVATABLE_ABILITIES` and swap `"PlanetaryShield"` literal (TDD green) [Medium]

**File:** `game/strategy/engine/planet_energy_engine.py`

- [ ] Delete `_ACTIVATABLE_ABILITIES` (lines 80-89).
- [ ] Replace literal `"PlanetaryShield"` at line 48 with a query: either `abilities_with_kind_tag(StrategicKind.PLANETARY_SHIELD)` membership, or keep the literal and ensure the metadata entry carries the `PLANETARY_SHIELD` tag for symmetry. Match `design.md` Phase 3 row.
- [ ] **Preserve `_is_ability_active`, `get_activatable_ability_info`, `get_shield_info`** signatures — they are imported in tests at `test_planet_energy_engine.py:5`. If they internally referenced the deleted constant, back them with `abilities_with_kind_tag(...)` queries.
- [ ] Verify: `pytest tests/unit/strategy/engine/test_planet_energy_engine.py tests/unit/strategy/services/test_planet_query_service.py -q` is green.

**Notes:** [Filled during implementation]

### Task 3.4: Confirm doc reference is acceptable [Simple]

- [ ] The reference at `docs/guides/adding_abilities.md:416` advises "do not treat `_ACTIVATABLE_ABILITIES` as the discovery surface." This becomes redundant after deletion. **Do not edit this doc here** — Phase 7 handles documentation updates and may delete/rewrite the guide entirely.

**Notes:** Defer doc edits to Phase 7.

---

## Phase Completion Checklist

When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `_ACTIVATABLE_ABILITIES` no longer exists in `planet_energy_engine.py`
- [ ] Literal `"PlanetaryShield"` at line 48 replaced (or symmetrically backed by metadata)
- [ ] Public helpers `_is_ability_active`, `get_activatable_ability_info`, `get_shield_info` still importable
- [ ] `pytest tests/unit/strategy/engine/test_planet_energy_engine.py tests/unit/strategy/services/test_planet_query_service.py` is fully green
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
