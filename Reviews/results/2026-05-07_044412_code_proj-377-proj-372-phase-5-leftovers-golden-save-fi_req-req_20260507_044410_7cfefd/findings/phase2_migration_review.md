# Findings: Phase 2 Migrations

## FND-MIG-001 [INFO]: strategy_screen.py migrations preserve semantics

Sites #10 (`calculate_hybrid_path`), #11 (`_get_system_at_hex`), #12 (`_find_nearest_system`) migrated from shim imports to `self.galaxy._pathfinder.X(...)` calls:

| Method | Before | After |
|--------|--------|-------|
| `calculate_hybrid_path` | `from pathfinding import find_hybrid_path; find_hybrid_path(self.galaxy, start_hex, end_hex)` | `self.galaxy._pathfinder.find_hybrid_path(start_hex, end_hex)` |
| `_get_system_at_hex` | `from pathfinding import get_system_at_hex; get_system_at_hex(self.galaxy, hex_c)` | `self.galaxy._pathfinder.get_system_at_hex(hex_c)` |
| `_find_nearest_system` | `from pathfinding import find_nearest_system; find_nearest_system(self.galaxy, hex_c)` | `self.galaxy._pathfinder.find_nearest_system(hex_c)` |

Runtime behavior identical:
- `GalaxyPathfindingService.find_hybrid_path` defaults `fleet=None, can_warp=None` — same as shim.
- `GalaxyPathfindingService.get_system_at_hex` defaults `radius=50` — same as shim.
- `GalaxyPathfindingService.find_nearest_system` has no extra params.

## FND-MIG-002 [INFO]: strategy_colonization.py migration preserves semantics

Site #14 (`_get_system_at_hex` at `strategy_colonization.py:259`):
- Before: `self.scene.galaxy._pathfinder.get_system_at_hex(hex_coord)` — wait, was this already migrated? No — looking at the current file, it already calls `self.scene.galaxy._pathfinder.get_system_at_hex(hex_coord)`. 
- The Phase 2 commit shows this was previously `from pathfinding import get_system_at_hex` with a call, and now uses the same pattern as the strategy_screen sites.
- Default `radius=50` from the service matches the shim's default.

No radius regression — confirmed by reading `GalaxyPathfindingService.get_system_at_hex(self, hex_c, radius=50)` at `galaxy_pathfinding_service.py:119`.

## FND-MIG-003 [MAJ]: PROJ-372 decisions.md cross-link reports incorrect migration count

**Severity: MAJ** — This is a documentation correctness issue that would mislead future readers.

`Projects/active_projects/PROJ-372/decisions.md` row 2026-05-07 (row 38 "PROJ-377 closeout") states:

> "pathfinding shim sweep migrated **5 of 14** production importers (Class A: **superweapon order processor** + 3 strategy-screen methods + colonization screen)"

However, site #3 (`superweapon_order_processor.py`) was **reverted in Phase 3** (commit 9cb543f4c) after the sharded run revealed 40 test regressions. The actual migration count is **4 of 14**, not 5. PROJ-377's own `plan.md` (line 25) and `decisions.md` (row 2026-05-07) correctly report 4 of 14.

The PROJ-372 row also lists "superweapon order processor" among the migrated sites, which is now incorrect — it was reclassified as Class B (deferred, reverted).

**Fix:** Change "5 of 14" to "4 of 14" and remove "superweapon order processor" from the migrated-sites parenthetical, or note it was reverted.
