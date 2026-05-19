# PROJ-453 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Phase 1 — Mechanical polish sweep

### Production files

| File | Type | Notes |
|------|------|-------|
| `game/strategy/engine/superweapon_order_processor.py` | Production | F-B-006 (annotate `_get_system_at_hex`, drop `# type: ignore`); F-B-008 (annotate `__init__` params + return) |
| `game/strategy/engine/order_processor.py` | Production | F-B-007 (annotate `__init__(event_bus, ...) -> None`) |
| `game/strategy/engine/handlers/fms_shared.py` | Production | F-B-009 (annotate `resolve_requested` return as `int | ValidationResult`; type `count` param) |
| `game/strategy/engine/turn_engine.py` | Production | F-B-010 (annotate `planet_modifier_effect_engine` property) |
| `game/strategy/engine/harvesting_engine.py` | Production | F-B-011 (annotate `_get_planet_mutator` / `_get_empire_mutator` return type) |
| `game/strategy/engine/atmosphere_engine.py` | Production | F-B-011 (annotate `_get_planet_mutator` return type) |
| `game/strategy/engine/planet_modifier_effect_engine.py` | Production | F-B-011 (annotate `_get_planet_mutator` return type) |
| `game/strategy/engine/production_spawner.py` | Production | F-B-011 (annotate `_get_planet_mutator` return type — live signature at :101 is `_get_planet_mutator`, not `_get_ship_mutator`) |
| `game/strategy/engine/environmental_hazard_engine.py` | Production | F-B-011 (annotate `_get_ship_mutator` return type — added by codex audit 2026-05-19) |
| `game/strategy/engine/superweapon_order_processor.py` | Production | F-B-011 (annotate `_get_empire_mutator` return type at :70 — added by codex audit 2026-05-19; this is in addition to the F-B-006 / F-B-008 touches on the same file) |
| `game/strategy/engine/production_engine.py` | Production | F-B-015 (`_cargo_contents` → `ShipCargoManager` in `IProductionResourceSource` docstring) |
| `game/strategy/engine/conflict_modifier_collection.py` | Production | F-B-016 (drop "Phase 7 deletes the legacy path" stale promise) |
| `game/strategy/services/fleet_speed_calculator.py` | Production | F-B-016 (parallel stale `EnvironmentalEffects` reference at :175 — companion to the conflict_modifier_collection.py touch) |
| `game/strategy/services/replay_store.py` | Production | F-B-021 (annotate `_iter_replay_files(rd: Path) -> Iterator[Path]`) |

### Test files

| File | Type | Notes |
|------|------|-------|
| `tests/unit/strategy/services/test_superweapon_registry_contract.py` | Test (modified) | F-B-012 (delete two `try / except ImportError → pytest.skip` guards at lines 148-154 and 172-178) |

### New test files

| File | Type | Notes |
|------|------|-------|
| (none) | | Annotation polish + docstring fixes don't require new tests; existing engine/services suites verify no behaviour drift. |

## Cross-bucket conflicts to watch

| File | Other projects touching | Resolution |
|------|------------------------|------------|
| `game/strategy/engine/order_processor.py` | PROJ-454 Phase 3 (F-B-017 facade unwinding will delete `process_join_fleet` / `process_colonize` / `process_transfer`) | PROJ-453 touches only the `__init__` signature; PROJ-454 touches the three legacy facade methods + the legacy result dataclasses. Disjoint within the file. If PROJ-454 runs first, PROJ-453 may rebase trivially (the `__init__` is on a different line range). |
| `game/strategy/engine/production_engine.py` | PROJ-455 (read-only — uses `production_engine` only as fixture context for planet-FMS tick) | No write conflict. |
| `game/strategy/services/fleet_speed_calculator.py` | None — `data/` layer touch is docstring-only, on a single line | No conflict. |

## File count summary

- **12 production files touched** (annotation / docstring only — no behaviour changes)
- **1 test file modified** (skip-guard deletion)
- **0 new test files**
- **Total LOC delta:** ≈30-40 lines (most are annotation additions; -2/+2 per signature)
