# PROJ-341 — Manifest

Read-only references and the new test files this project creates.

---

## Production files (read-only references)

| File | LOC | Role | Existing tests |
|---|---:|---|---|
| `game/strategy/engine/superweapon_order_processor.py` | 771 | Processes superweapon orders during turn execution; one method per superweapon (implode_planet, stellerate_star, open/close_warp_point, create_dyson_sphere, self_destruct). Delegates stabilizer-blocking lookup to `stabilizer_registry`. | `tests/unit/strategy/engine/test_superweapon_order_processor.py` (1232 LOC, 27 tests) |
| `game/strategy/engine/environmental_hazard_engine.py` | 219 | Per-tick environmental hazard processor; reads `EnvironmentalDamage` and `FuelDrain` ability rates from `system_effects_collector` and applies damage / fuel drain to fleets in storm hexes. | **none** |
| `game/strategy/engine/action_execution_engine.py` | 215 | Tick-based action-order driver. Routes movement orders to FleetMovementEngine, BUILD to ProductionEngine, and action orders (COLONIZE, TRANSFER, superweapons, etc.) through speed/action_time progress accumulation, then delegates to an injected order processor on completion. | `tests/unit/strategy/engine/test_action_execution_engine.py` (~520 LOC, 19 tests) |

---

## Collaborator references (touched by tests via mocks/patches)

These are not modified; they are listed so a future maintainer knows which boundaries the test files cross:

- `game/strategy/services/stabilizer_registry.py` — `find_blocking_stabilizer` (patched for stabilizer-cancel branches).
- `game/strategy/services/system_destroyer.py` — `collect_system_contents`, `destroy_system` (patched for STELLERATE_STAR tests).
- `game/strategy/services/system_effects_collector.py` — `collect_sector_effects` (patched for environmental-hazard tests).
- `game/strategy/services/action_time_resolver.py` — `ActionTimeResolver.resolve_action_time` (patched for action_time-controlled tests; matches existing pattern in `test_action_execution_engine.py`).
- `game/strategy/services/fleet_speed_calculator.py` — `get_tick_interval` (used as-is via real import; no patching).
- `game/strategy/validation/superweapon_validator.py` — `SuperweaponValidator.find_ship_with_ability` (patched for ability-resolution tests; matches existing pattern).
- `game/core/exceptions.py` — `ValidationException` (raised in `_validate_tick_inputs`; asserted via `pytest.raises`).
- `game/core/event_logging.py` — `EventBus` (real instance with a capture callback; matches existing pattern).
- `game/strategy/events/event_types.py` — `EventType`, `EventCategory` (real enums).

---

## New test files (deliverables)

| File | Phase | New tests | Purpose |
|---|---|---:|---|
| `tests/unit/strategy/engine/test_environmental_hazard_engine.py` | 1 | ~17 | Green-field characterization of `EnvironmentalHazardEngine.process_environmental_tick` and the two private helpers. |
| `tests/unit/strategy/engine/test_superweapon_order_processor_gaps.py` | 2 | ~16 | Gap-fill: stabilizer cancellation paths, OPEN/CLOSE warp-point edge cases, race_config fallback, fleet-cleanup, `_get_reference_planet`. |
| `tests/unit/strategy/engine/test_action_execution_engine_gaps.py` | 3 | ~10 | Gap-fill: `_validate_tick_inputs`, `ActionTimeResolver`-injection, processor-pops-order contract, kwarg threading in `_execute_action`. |

Total new tests: ~43.

---

## Files NOT modified

- `tests/unit/strategy/engine/test_superweapon_order_processor.py` — left as-is. New gap-fill tests live in a sibling file (decision D-002).
- `tests/unit/strategy/engine/test_action_execution_engine.py` — left as-is.
- All production files. Master plan rule (no production refactors).

---

## Test infrastructure

- `tests/unit/strategy/engine/` already exists; no new directory needed.
- `conftest.py` — none required. Fixtures are copied into each new test file (decision D-007).

---

## Verification matrix (per phase)

| Phase | Command |
|---|---|
| 1 | `pytest tests/unit/strategy/engine/test_environmental_hazard_engine.py -x -v` |
| 2 | `pytest tests/unit/strategy/engine/test_superweapon_order_processor_gaps.py -x -v` |
| 3 | `pytest tests/unit/strategy/engine/test_action_execution_engine_gaps.py -x -v` |
| All | `python Tools/test_sharded/test_sharded.py` and `python Tools/lint_test_files.py` |
