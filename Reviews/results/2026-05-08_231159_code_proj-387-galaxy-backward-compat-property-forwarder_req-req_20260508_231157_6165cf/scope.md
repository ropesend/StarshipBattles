# Review Scope: PROJ-387 Galaxy backward-compat property forwarder removal
**Type:** code (delegated by Claude Code)
**Request ID:** req_20260508_231157_6165cf
**Review Mode:** normal
**Branch:** feat/03c-phase-aware-execution
**Scope:** 4 production files, 8 test files, 5 project docs

### Production
- `game/strategy/data/galaxy.py` — deleted 5 forwarders + docstring
- `game/strategy/engine/handlers/movement.py` — 1 line `_global_hex_warp_points` -> `_state.global_hex_warp_points`
- `game/strategy/services/fleet_navigation_service.py` — 1 line same
- `game/ui/screens/strategy_render/hex_outlines.py` — 3 lines planets/zones/warp_points iterations

### Tests (migrated)
- `tests/unit/strategy/engine/handlers/test_movement_handlers.py` — added `_FakeGalaxyState`
- `tests/unit/strategy/fleet_navigation/test_navigation_pure.py`
- `tests/unit/strategy/services/test_fleet_navigation_gaps.py`
- `tests/unit/strategy/services/test_fleet_navigation_action_timing.py`
- `tests/unit/ui/screens/strategy_render/test_hex_outlines.py` — fake galaxy fixture rewrite
- `tests/unit/ui/screens/test_strategy_renderer.py`
- `tests/integration/strategy/test_warp_orders.py`
- `tests/unit/strategy/data/test_galaxy_cleanup.py`

### Project docs
- `Projects/active_projects/PROJ-387/plan.md`
- `Projects/active_projects/PROJ-387/phase_1_checklist.md`
- `Projects/active_projects/PROJ-387/manifest.md`
- `Projects/active_projects/PROJ-387/decisions.md`
- `Projects/active_projects/PROJ-387/findings/verification_report.md`

### Instructions (abbreviated)
1. Completeness of removal (grep for remaining forwarder usage)
2. Migration target — is `_state.<field>` the right destination?
3. Behavior preservation — mutation semantics
4. Test fake equivalence — `_FakeGalaxyState`
5. Plan path correction — `data/movement.py` vs `engine/handlers/movement.py`
6. Other forwarders in scope — `_next_planet_id`/`_next_fleet_id` preserved
7. Compat-shim hygiene — no new wrappers
8. Scope discipline — GalaxyState public API unchanged
9. PROJ-385/388 changes preserved
10. Pre-existing failures — no new failures introduced
11. Coverage — migrated branches are exercised

### Limitations
- Review restricted to the scope files listed above. Peripheral test files (`test_galaxy_state_encapsulation.py`, `test_galaxy_entity_registry.py`, etc.) were read in passing to check for stale references but were not exhaustively reviewed.
- Broader call-site audit used automated grep/AST scanning, not manual inspection of every file in the repo.
