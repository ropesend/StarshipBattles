# Findings: Site #3 Revert (superweapon_order_processor.py)

## FND-RVT-001 [INFO]: Revert restores pre-PROJ-377 state cleanly

`git show 9cb543f4c -- game/strategy/engine/superweapon_order_processor.py` confirms the Phase 3 commit:
1. Adds back `from game.strategy.data.pathfinding import get_system_at_hex` at line 31.
2. Changes 5 call sites from `galaxy._pathfinder.get_system_at_hex(fleet.location)` back to `get_system_at_hex(galaxy, fleet.location)`.

The 5 reverted call sites are at:
- Line 345: `_stabilizer_target_label` — `get_system_at_hex(galaxy, fleet.location)`
- Line 408: `_precheck` in `process_stellerate_star` — `get_system_at_hex(galaxy, fleet.location)`
- Line 413: `_effect` in `process_stellerate_star` — `get_system_at_hex(galaxy, fleet.location)`
- Line 453: `_precheck` in `process_open_warp_point` — `get_system_at_hex(galaxy, fleet.location)`
- Line 470: `_effect` in `process_open_warp_point` — `get_system_at_hex(galaxy, fleet.location)`

Plus additional `get_system_at_hex` calls in `process_close_warp_point` and `process_create_dyson_sphere` (which were not in the migration diff because they already used the shim import).

The diff shows clean restoration — the file is byte-for-byte identical to its pre-PROJ-377 state with one exception: the file still has a pre-existing issue format. **Verified clean reversion.**

## FND-RVT-002 [INFO]: Root cause analysis correct in decisions.md

PROJ-377 decisions.md row 2026-05-07 correctly identifies the blind spot in the original planning grep: tests patch `'game.strategy.engine.superweapon_order_processor.get_system_at_hex'` (the local module-level import name), not `'game.strategy.data.pathfinding.get_system_at_hex'`. Both patch idioms produce identical test-isolation effect when the production code does `from game.strategy.data.pathfinding import get_system_at_hex`.

Lesson for future migration sweeps: search for both `patch('pathfinding.X')` and `patch('<target_module>.X')`.

## FND-RVT-003 [INFO]: get_system_at_hex import restored and confirmed

The `grep` verification requested in instruction #7 confirms: `superweapon_order_processor.py` line 31 has `from game.strategy.data.pathfinding import get_system_at_hex` — the shim import is back. The 8 deferred Class B sites were never touched, so their patches remain intact.
