---
protocol: consult/v1
from: codex
to: claude
mode: planning
created_at_utc: 2026-05-19T04:56:13.9124717Z
complete: true
exit_status: ok
---

# PROJ-453 audit response

## Verdict table
| Finding | Status | Evidence |
|---|---|---|
| F-B-006 | closed | `game/strategy/engine/superweapon_order_processor.py:347-356`; signature now matches `game/strategy/services/galaxy_pathfinding_service.py:113-116`. |
| F-B-007 | closed | `game/strategy/engine/order_processor.py:64-68`. |
| F-B-008 | closed | `game/strategy/engine/superweapon_order_processor.py:58-63`. |
| F-B-009 | closed | `game/strategy/engine/handlers/fms_shared.py:94-106`. |
| F-B-010 | closed | `game/strategy/engine/turn_engine.py:521-529`. |
| F-B-011 | closed | `game/strategy/engine/harvesting_engine.py:196-210`; `game/strategy/engine/atmosphere_engine.py:30-34`; `game/strategy/engine/planet_modifier_effect_engine.py:34-38`; `game/strategy/engine/production_spawner.py:101-105`; `game/strategy/engine/environmental_hazard_engine.py:65-71`; `game/strategy/engine/superweapon_order_processor.py:77-83`. |
| F-B-012 | closed | `tests/unit/strategy/services/test_superweapon_registry_contract.py:147-175`; same direct import/seeding pattern already exists at `tests/unit/strategy/engine/test_command_specs_contract.py:21-31`, `game/strategy/facade/strategy_session_facade.py:104-110`, and `game/strategy/engine/handlers/registry_factory.py:33-39`. |
| F-B-015 | closed | `game/strategy/engine/production_engine.py:79-88`; the public cargo-write seam is `ShipCargoManager` per `game/strategy/data/ship_instance.py:72-77,94-98` and fleet production delegates at `game/strategy/data/fleet.py:294-313`. |
| F-B-016 | closed | `game/strategy/engine/conflict_modifier_collection.py:25-30`; `game/strategy/engine/conflict_resolution_engine.py:558-562`; `game/strategy/services/fleet_speed_calculator.py:168-176`. `rg -n "EnvironmentalEffects" game tests` found no live caller using that legacy object name. |
| F-B-021 | closed | `game/strategy/services/replay_store.py:435-445`. |

## Side-effects / regressions
- No material behavioral regression is obvious by inspection. The new annotations are either permissive (`Optional[Any]`, `Any`) or matched to existing current signatures (`game/strategy/services/galaxy_pathfinding_service.py:113-116`).
- `game/strategy/engine/production_engine.py:80` gained a small docstring typo: ``ShipCargoManager`` is followed by an extra `)` (`... (``ShipCargoManager``)) MAY round ...`). Documentation-only residue.
- F-B-015 is still correctly closed even though `_cargo_contents` remains as private backing storage on `ShipInstance` (`game/strategy/data/ship_instance.py:72-77,163-164`); the manager name is accurate as the current public/canonical write surface, and the live manager module is `game/strategy/data/ship_cargo_manager.py:69-136`.

## Out-of-scope observations
- `game/strategy/engine/superweapon_order_processor.py:85` still has an untyped lazy accessor `_get_nav_service()`, adjacent to the F-B-011 accessor family.
- `game/strategy/engine/atmosphere_engine.py:26`, `game/strategy/engine/planet_modifier_effect_engine.py:30`, and `game/strategy/engine/environmental_hazard_engine.py:57` still have untyped constructor kwargs in files this sweep touched.

## Summary
- Overall: all 10 PROJ-453 findings are closed by inspection; I did not find a functional regression in the touched code, but I would log the extra `)` at `game/strategy/engine/production_engine.py:80` plus the remaining adjacent typing gaps as follow-up polish.

## Open questions
- None.
