# Dead Code Validation Report

## Summary
- Total Candidates Reviewed: 8 (3 variables + 5 imports)
- Confirmed Dead: 1
- Product Decision Required: 0
- False Positives: 7
- Documentation Discrepancies: 0

## Confirmed Dead Code (no tests, docs, or production references)

### Tier 4: Dead Imports
| Import | File:Line | Source | Test refs? | Doc refs? | Verified? |
|--------|-----------|--------|------------|-----------|-----------|
| `IControllableShip` | `game/ai/controller.py:56` | Vulture 90% | 0 (symbol doesn't exist anywhere) | 0 | **CONFIRMED** |

**Detail on `IControllableShip` (controller.py:56):**

The TYPE_CHECKING import `from game.simulation.interfaces.ai_controller import IControllableShip` references a symbol that **no longer exists**. The module `game/simulation/interfaces/ai_controller.py` defines `IAIController` and `IAIControllerFactory` — not `IControllableShip`. The annotation at line 86 (`ship: 'IControllableShip'`) is a stale forward reference. The runtime class actually received by `AIController.__init__` is `ShipControllableAdapter` (imported at line 69, implements `IControllable`).

MyPy corroborates: `game/ai/controller.py:56: error: Module "game.simulation.interfaces.ai_controller" has no attribute "IControllableShip" [attr-defined]`

**Recommended fix:** Remove the dead import line. Update the annotation at line 86 from `ship: 'IControllableShip'` to `ship: 'ShipControllableAdapter'` (already imported at line 69).

## False Positives (Not Dead)

| Item | Reason It's Actually Used |
|------|--------------------------|
| `exc_type`, `exc_val`, `exc_tb` at `battle_engine.py:98` | `__exit__` context manager protocol parameters. Required by Python's context manager protocol; the body `self.close(); return False` intentionally doesn't use them. Standard pattern — not dead. |
| `RegionClassifier` at `galaxy.py:29` | TYPE_CHECKING-guarded import used as string annotation at line 265. At runtime, `RegionClassifier` objects ARE passed as arguments through `Galaxy.generate_warp_lanes()` -> `GalaxyWarpGenerator`. The class is actively used in production code. |
| `RegionClassifier` at `galaxy_warp_generator.py:15` | TYPE_CHECKING-guarded import used in string annotations at lines 192, 278, 316. At runtime, `RegionClassifier` objects flow through method parameters (`region_classifier.get_region(system)` at runtime). Class is tested (43 test refs in `test_region_classifier.py`). |
| `BuildContext` at `build_queue_controller.py:19` | TYPE_CHECKING-guarded import under `from __future__ import annotations` (all annotations are strings at runtime). Used at line 60: `Union['Planet', 'Fleet', 'BuildContext']`. Protocol class is tested in dedicated test file (`test_build_context.py`, 15+ test refs, 1 doc ref). At runtime, Planet/Fleet satisfy the protocol via structural conformance. |

## Product Decision Required
*None.* All false positive candidates are standard TYPE_CHECKING patterns or context-manager protocol parameters.

## Documentation Discrepancies
*None.* No docs reference `IControllableShip` (the single dead symbol).

## Prioritized Cleanup Order

| Priority | Item | LOC saved | Risk | Effort |
|----------|------|-----------|------|--------|
| 1 | Remove `IControllableShip` import + fix annotation | 1 line removed, 1 fixed | Very Low | Trivial |
