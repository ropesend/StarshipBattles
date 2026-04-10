# Phase 2 Checklist: DamageCalculator Event Emissions

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-265 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Test all combat event emission paths in `DamageCalculator.apply_damage()`. Currently no test passes an `event_bus`, leaving lines 94, 112, 131, 165, 212-213, and 222 uncovered.

**Test File:** `tests/unit/simulation/combat/test_damage_calculator_events.py` (new)
**Source File:** `game/simulation/combat/damage_calculator.py`

---

## Task 2.1: Test Fixtures and Helpers [Simple]
**Tests:** N/A (setup only)

- [ ] Create test file with imports: `DamageCalculator`, `CombatEventType`, `CombatEvent`, `DamageContext`, `LayerType`, `LayerData`
- [ ] Create fixture: `mock_event_bus` -- MagicMock with `.emit()` method
- [ ] Create fixture: `damage_context` -- `DamageContext(attacker=Mock(), damage_type="beam")`
- [ ] Create helper: `_make_ship(shields, emissive, sra, max_shields, layers)` -- returns a MagicMock ship with correct attributes
- [ ] Create helper: `_make_component(hp)` -- returns a MagicMock with `current_hp`, `take_damage` that decrements HP

**Notes:** [Filled during implementation]

---

## Task 2.2: SHIELD_HIT Event [Simple]
**Tests:** `pytest tests/unit/simulation/combat/test_damage_calculator_events.py -v -k "shield_hit"`

- [ ] Write test: shields absorb partial damage -- `event_bus.emit()` called with `CombatEventType.SHIELD_HIT`, correct `damage_amount` (absorbed amount), correct `shield_remaining` (line 94)
- [ ] Write test: shields absorb ALL damage -- SHIELD_HIT emitted, no further events (early return after shields)
- [ ] Write test: no shields (current_shields=0) -- SHIELD_HIT NOT emitted
- [ ] Run tests -- confirm they pass

**Verification:** Check `event_bus.emit.call_args_list` for event type, damage_amount, shield_remaining, and target_ship fields.

**Notes:** [Filled during implementation]

---

## Task 2.3: ARMOR_ABSORBED Event -- Emissive Armor [Simple]
**Tests:** `pytest tests/unit/simulation/combat/test_damage_calculator_events.py -v -k "emissive"`

- [ ] Write test: emissive armor reduces overflow damage -- `ARMOR_ABSORBED` event emitted with correct `damage_amount` (the absorbed portion) (line 112)
- [ ] Write test: emissive armor blocks ALL remaining damage -- `ARMOR_ABSORBED` emitted, no further events
- [ ] Write test: no emissive armor (emissive_armor=0) -- `ARMOR_ABSORBED` NOT emitted from this stage
- [ ] Run tests -- confirm they pass

**Notes:** [Filled during implementation]

---

## Task 2.4: ARMOR_ABSORBED Event -- SRA [Simple]
**Tests:** `pytest tests/unit/simulation/combat/test_damage_calculator_events.py -v -k "sra"`

- [ ] Write test: SRA absorbs overflow and recharges shields -- `ARMOR_ABSORBED` event emitted with correct `damage_amount` (line 131)
- [ ] Write test: SRA absorbs ALL remaining damage -- event emitted, no hull damage events follow
- [ ] Write test: no SRA (shield_regenerating_armor=0) -- no `ARMOR_ABSORBED` from this stage
- [ ] Run tests -- confirm they pass

**Notes:** [Filled during implementation]

---

## Task 2.5: COMPONENT_HIT and COMPONENT_DESTROYED Events [Medium]
**Tests:** `pytest tests/unit/simulation/combat/test_damage_calculator_events.py -v -k "component"`

- [ ] Write test: damage hits component but does not destroy it (HP > 0 after hit) -- `COMPONENT_HIT` event emitted with correct component, layer_type, damage_amount (line 222)
- [ ] Write test: damage destroys component (HP reaches 0) -- `COMPONENT_DESTROYED` event emitted with correct component, layer_type, damage_amount (lines 212-213)
- [ ] Write test: damage destroys first component and hits second -- both `COMPONENT_DESTROYED` (for first) and `COMPONENT_HIT` (for second) emitted
- [ ] Write test: event contains correct `layer_type` field matching the hull layer
- [ ] Run tests -- confirm they pass

**Approach:** Create mock ship with no shields/emissive/SRA so all damage reaches hull. Use components with known HP values. Use a deterministic RNG seed so weighted selection is predictable.

**Notes:** [Filled during implementation]

---

## Task 2.6: SHIP_DERELICT Event [Medium]
**Tests:** `pytest tests/unit/simulation/combat/test_damage_calculator_events.py -v -k "derelict"`

- [ ] Write test: ship becomes derelict after damage (was_derelict=False, is_derelict=True after) -- `SHIP_DERELICT` event emitted (line 165)
- [ ] Write test: ship was already derelict before damage -- `SHIP_DERELICT` NOT emitted (no duplicate event)
- [ ] Write test: ship takes damage but does NOT become derelict -- `SHIP_DERELICT` NOT emitted
- [ ] Run tests -- confirm they pass

**Approach:** Mock `ship.is_derelict` as a property that returns different values before/after damage. Or use `side_effect` on `update_derelict_status` to flip the flag. The key is that `was_derelict` is captured at the start of `apply_damage()` and compared after `_finalize_damage()`.

**Notes:** [Filled during implementation]

---

## Task 2.7: Full Pipeline Event Sequence [Medium]
**Tests:** `pytest tests/unit/simulation/combat/test_damage_calculator_events.py -v -k "pipeline"`

- [ ] Write test: full pipeline (shields + emissive + hull) -- events emitted in correct order: SHIELD_HIT, ARMOR_ABSORBED (emissive), COMPONENT_HIT/DESTROYED
- [ ] Write test: context (DamageContext) is passed through to all emitted events
- [ ] Write test: event_bus=None (default) -- no errors, no events (existing behavior preserved)
- [ ] Run tests -- confirm they pass

**Notes:** [Filled during implementation]

---

## Task 2.8: Full Phase Verification [Simple]
**Tests:** `pytest tests/unit/simulation/combat/test_damage_calculator_events.py -v`

- [ ] Run full new test file -- all tests pass
- [ ] Run existing damage calculator tests: `pytest tests/unit/simulation/combat/test_damage_calculator.py -v` -- no regressions
- [ ] Run existing simulation tests: `pytest tests/unit/simulation/ -v` -- no regressions
- [ ] Measure coverage: `pytest tests/unit/simulation/combat/test_damage_calculator_events.py tests/unit/simulation/combat/test_damage_calculator.py --cov=game/simulation/combat/damage_calculator --cov-report=term-missing`
- [ ] Verify lines 94, 112, 131, 165, 212-213, 222 are now covered

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
