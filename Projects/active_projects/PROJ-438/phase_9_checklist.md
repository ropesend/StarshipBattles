# Phase 9: Bundled small follow-ups from Codex consult

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-438 9`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** Phase 8 doc sync committed (`fd6b456ab`); Codex consult committed (`AgentCoordination/Scratchpad/Consult/20260518T153829Z_proj-438-end-of-project/response.md`).
**Objective:** Absorb the four small verified findings from the end-of-project Codex consult: framing fix, duplicate-codec consistency ratchet, `MOVE_TO_FLEET` parity coverage, and planet ability order save/load round-trip pin. The fifth verified finding (engine-mediated dispatch behavioral coverage) is split off as Phase 10 (deferred).

---

## Tasks

### Task 9.1: Framing fix for Phase 5 persistence-seam reference
**Files:** `Projects/active_projects/PROJ-438/decisions.md` (already updated with explanation)

- [x] The Phase 5 typed planet intents preserve the marker-dict target shape on the **`'dict'` codec branch** of `Order.to_dict()` (`order_types.py:118`), which `planet_serde._deserialize_planet_orders → Order.from_dict()` (`planet_serde.py:188`) consumes. The consult request mis-named `OrderSerializer._deserialize_target`; that's the fleet-order marker-rebinding path, not the planet-order path. Migration is correct; framing is now accurate in `decisions.md`.

### Task 9.2: Duplicate-codec consistency ratchet
**Files:** `tests/unit/strategy/engine/test_order_persistence_from_metadata.py`
**Tests:** `pytest tests/unit/strategy/engine/test_order_persistence_from_metadata.py::TestCodecVocabularyConsistency`

- [x] Added `test_specs_sharing_order_type_declare_same_codec` — pins that when multiple `CommandSpec` entries share an `OrderType`, they all declare the same `serializer_codec`. Today no production specs share an OrderType, so this passes trivially; the gate fires the moment a future change introduces an OrderType-sharing spec pair with inconsistent codecs.
- [x] This is the authority-strength gate that must pass before any future flip of `Order.to_dict()` to dispatch via `serializer_codec_for(...)`.

### Task 9.3: MOVE_TO_FLEET parity coverage
**Files:** `tests/unit/strategy/engine/test_restore_path_parity.py`
**Tests:** `pytest tests/unit/strategy/engine/test_restore_path_parity.py::TestRestorePathParity::test_parity_pursuer_tracker_rebuild`

- [x] Extracted helper `_session_with_pursuit_order(order_type)` so the parity fixture can build either `JOIN_FLEET` or `MOVE_TO_FLEET` source orders.
- [x] Parametrized `test_parity_pursuer_tracker_rebuild` over `[JOIN_FLEET, MOVE_TO_FLEET]` — both branches now exercised against both restore paths.

### Task 9.4: Planet ability order save/load round-trip
**Files:** `tests/unit/strategy/engine/test_typed_planet_intents.py`
**Tests:** `pytest tests/unit/strategy/engine/test_typed_planet_intents.py::TestPlanetAbilityOrderRoundtrip`

- [x] Added `TestPlanetAbilityOrderRoundtrip` with two tests (`test_activate_*` + `test_deactivate_*`) that exercise the `Order.to_dict() → Order.from_dict()` path — the same path `planet_serde._deserialize_planet_orders` invokes during save/load. Pins that `facility_instance_id` / `ability_name` / `component_key` keys all survive.

### Task 9.5: Sweep + sharded suite
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] 27 affected tests green (parity, typed intents, metadata convergence).
- [x] Run the canonical sharded suite green.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `python Tools/test_sharded/test_sharded.py` green (no NEW failures vs. Phase 0 baseline)
- [x] Game still runnable / savable / loadable (no behavior change — Phase 9 is test additions + decisions doc update)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to project completion + Phase 10 deferral
- [x] `python Projects/scripts/validate_phase.py PROJ-438 9` passes
