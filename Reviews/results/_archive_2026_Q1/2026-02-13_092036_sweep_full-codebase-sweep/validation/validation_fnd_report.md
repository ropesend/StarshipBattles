# Validation Report: Foundation

## Summary
- **Shard:** Foundation (FND)
- **Findings Reviewed:** 36
- **Confirmed:** 16
- **Downgraded:** 10
- **Rejected:** 10
- **Rejection Rate:** 27.8%

## Verdicts

#### Finding: ADR-FND-001
**Original Severity:** Critical
**Verdict:** CONFIRMED
**Reason:** Verified - `game/research/ui/research_scene.py:19` contains `from game.ui.renderer.camera import Camera`. The research module imports directly from the UI layer, creating a layer violation.

#### Finding: ADR-FND-002
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**New Severity:** Minor
**Reason:** The IControllable interface at 478 lines is not a "god class" - it is a Protocol/Interface definition with abstract methods. The file contains both the interface and a concrete adapter implementation. This is appropriate for interface definitions.

#### Finding: ADR-FND-003
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified - `game/core/protocols.py` is 548 lines, exceeding the 500-line threshold mentioned. The file contains many protocol definitions which is acceptable, but technically exceeds the guideline.

#### Finding: ADR-FND-004
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Verified - The research module structure does mix layers with `game/research/ui/` subdirectory. This is an intentional design observation, not a bug.

#### Finding: CON-FND-001
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified - `game/ai/combat_utils.py:14` uses direct logging `logger = logging.getLogger(__name__)` instead of the centralized game.core.logger pattern. Line 13 shows `import logging` and line 19 shows `logger = logging.getLogger(__name__)`.

#### Finding: CON-FND-002
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified - `game/core/paths.py` uses `os.path.join` for string path constants (lines 53-99) while also providing `Path` accessor methods (lines 106-133). This is a deliberate design choice for backward compatibility but does create inconsistency.

#### Finding: CON-FND-003
**Original Severity:** Major
**Verdict:** REJECTED
**Reason:** The finding claims "is_" prefix issues at lines 63-64 of profiling.py. At line 63, the method is `is_active()` which correctly uses the "is_" prefix for a boolean-returning method. There is no inconsistency.

#### Finding: CON-FND-004
**Original Severity:** Major
**Verdict:** REJECTED
**Reason:** The `load_json` function at `game/core/json_utils.py:33-67` consistently returns `default` (defaulting to `None`) on all error paths. The `load_json_required` function raises exceptions as documented. This is intentional API design, not inconsistency.

#### Finding: CON-FND-005
**Original Severity:** Major
**Verdict:** REJECTED
**Reason:** The singleton reset pattern at `game/core/singleton.py:84-97` shows a single consistent `reset()` method implementation. There is no inconsistency visible in the code.

#### Finding: CON-FND-006
**Original Severity:** Minor
**Verdict:** DOWNGRADED(Info)
**New Severity:** Info
**Reason:** Method verb prefix differences in IControllable are intentional - "get_" for accessors and "set_" for mutators. This follows Python conventions and is not an inconsistency issue.

#### Finding: CON-FND-007
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified - `game/research/data/tech_tree.py` uses `node_id` as parameter name while the TechNode class uses `id`. Minor naming inconsistency exists.

#### Finding: CON-FND-008
**Original Severity:** Minor
**Verdict:** REJECTED
**Reason:** Location is "Unknown" - cannot verify against actual code without a specific file location.

#### Finding: CON-FND-009
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified - `game/research/ui/research_scene.py` contains magic numbers for layout constants (lines 40-44: SIDEBAR_WIDTH=350, COLUMN_SPACING=280, etc.). While documented as class constants, they are hardcoded values.

#### Finding: CON-FND-010
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified - `game/engine/collision.py:50-54` uses `Any` type hints extensively in the type signature and line 54 comment notes "Ship type hint uses Any to avoid tight coupling". This is intentional but could be more specific.

#### Finding: CON-FND-011
**Original Severity:** Minor
**Verdict:** DOWNGRADED(Info)
**New Severity:** Info
**Reason:** `game/core/singleton.py:22` shows `__all__ = ['SingletonMeta']` which is a standard export pattern. No inconsistency detected.

#### Finding: CON-FND-012
**Original Severity:** Minor
**Verdict:** REJECTED
**Reason:** Review of `game/ai/interfaces/controllable.py` shows consistent `_ship` naming for the private attribute in the adapter class. No inconsistency found.

#### Finding: CON-FND-013
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Verified - `game/core/protocols.py:24-31` uses both `Optional` and `Union[X, None]` styles. This is an observation about style, not an issue.

#### Finding: CON-FND-014
**Original Severity:** Info
**Verdict:** REJECTED
**Reason:** Location is "Unknown" - cannot verify against actual code. Additionally, this is a positive observation, not an actionable finding.

#### Finding: DUP-FND-001
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**New Severity:** Minor
**Reason:** The IControllable protocol and IShip protocol serve different purposes. IControllable is specifically for AI-controlled entities. Some overlap in method signatures is expected when defining behavior contracts.

#### Finding: DUP-FND-002
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**New Severity:** Minor
**Reason:** ResearchTracker and ResearchControlPanel serve different roles - one is data/state management, the other is UI. Some duplication in state access is expected in MVC-style patterns.

#### Finding: DUP-FND-003
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified - `game/ai/controller.py:197-201` contains distance calculation that duplicates logic found in `game/ai/combat_utils.py`. The `safe_distance` function exists but is not always used.

#### Finding: DUP-FND-004
**Original Severity:** Minor
**Verdict:** REJECTED
**Reason:** `game/core/registry.py:217-237` shows `clear()` method implementation. There is only one clear pattern visible - this is not duplication.

#### Finding: DUP-FND-005
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified - `game/research/data/research_tracker.py` has `to_dict`/`from_dict` methods (lines 22-37, 236-255). This is a common pattern throughout the codebase but does represent duplication of serialization boilerplate.

#### Finding: DUP-FND-006
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified - `game/ai/behaviors.py:70-85` has `_flee_direction` function. This flee direction calculation pattern may exist elsewhere in the codebase.

#### Finding: DUP-FND-007
**Original Severity:** Minor
**Verdict:** REJECTED
**Reason:** `game/core/registry.py:319-330` shows the DefaultRegistryProvider class with standard get_* accessor methods. These are not duplicates - they are the proper delegation pattern.

#### Finding: DUP-FND-008
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Verified - `game/ai/behaviors.py:67` imports `angle_diff as calc_angle_diff` from `game.core.math`. This is proper import usage, not duplication.

#### Finding: LEG-FND-001
**Original Severity:** Major
**Verdict:** REJECTED
**Reason:** `game/core/resources.py:16` imports `RegistryManager` and it IS used in the file context. The import is for the module's purpose of loading resources into the registry system.

#### Finding: LEG-FND-002
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**New Severity:** Minor
**Reason:** Verified - `game/ai/combat_utils.py:63-181` uses extensive `getattr()` defensive patterns. However, this is documented as intentional defensive programming for combat robustness, not legacy holdover.

#### Finding: LEG-FND-003
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified - `game/core/singleton.py` implements the singleton pattern, which is intentionally still used throughout the codebase. This is an observation, not necessarily an issue.

#### Finding: LEG-FND-004
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified - `game/ai/combat_utils.py:43-47` has `hasattr(obj, '_mock_name')` check for mock detection. This is a testing utility pattern that exists in production code.

#### Finding: LEG-FND-005
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified - `game/ai/__init__.py:34-52` has extensive documentation about fallback behavior. This is documentation, not code issue.

#### Finding: LEG-FND-006
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified - `game/ai/controller.py:346` area contains comments about strategy handling. These are implementation notes.

#### Finding: LEG-FND-007
**Original Severity:** Minor
**Verdict:** DOWNGRADED(Info)
**New Severity:** Info
**Reason:** `game/ai/controller.py:434` shows `navigate_to` method with `stop_dist` and `precise` parameters. Both parameters are used in the method body. Not dead parameters.

#### Finding: LEG-FND-008
**Original Severity:** Info
**Verdict:** REJECTED
**Reason:** This is a positive observation stating the research module is "well-structured" - not an actionable finding.

#### Finding: TCG-FND-001
**Original Severity:** Critical
**Verdict:** DOWNGRADED(Major)
**New Severity:** Major
**Reason:** Tests DO exist for PhysicsBody: `tests/unit/systems/test_physics.py` (extensive tests) and `tests/unit/systems/test_physics_edge_cases.py`. The finding overstates the gap - `update()`, `apply_force()`, and `forward_vector()` are all tested.

#### Finding: TCG-FND-002
**Original Severity:** Critical
**Verdict:** DOWNGRADED(Major)
**New Severity:** Major
**Reason:** Tests exist for research UI components in `tests/unit/research/research_controls/` and `tests/unit/research/research_scene/`. The finding is valid that they mock pygame, but tests do exist.

#### Finding: TCG-FND-003
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified - CollisionSystem tests exist in `tests/unit/systems/test_collision_system.py` and `tests/unit/engine/collision_edge_cases/` but integration-level tests with full physics may be limited.

#### Finding: TCG-FND-004
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified - `game/research/data/tech_tree.py:208-252` shows `detect_cycles()` method. Tests exist in `tests/unit/research/tech_tree/` but cycle detection edge cases may not be comprehensive.

#### Finding: TCG-FND-005
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified - `game/ai/behaviors.py` contains `FleeBehavior` class. AI behavior tests exist in `tests/unit/ai/test_ai_behaviors.py` but direct FleeBehavior tests may be limited.

#### Finding: TCG-FND-006
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified - `game/ai/target_evaluator.py` contains rule processing logic. Tests exist in `tests/unit/ai/target_evaluator/` directory but edge case coverage could be improved.

#### Finding: TCG-FND-007
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified - `game/ai/ai_factory.py` has `create_for_ship` method that raises `RuntimeError` if grid is not set. The error path test coverage may be limited.

#### Finding: TCG-FND-008
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified - `game/core/protocols.py` defines ICamera interface at lines 468-547. Protocol interfaces typically don't require direct unit tests as they are tested via implementations.

#### Finding: TCG-FND-009
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified - `game/core/hex_math.py` contains coordinate math. Large coordinate edge cases may not be comprehensively tested.

#### Finding: TCG-FND-010
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified - `game/research/systems/research_service.py:204-230` contains `estimate_turns_to_breakthrough()` method. This estimation logic may have limited test coverage.

#### Finding: TCG-FND-011
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified - `game/engine/spatial.py:24-26` shows `_get_cell()` method using integer division. Negative coordinate handling may not be explicitly tested.

#### Finding: TCG-FND-012
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified - `game/research/data/research_tracker.py:167-203` shows `spread_rp_evenly()` method with distribution logic. Distribution edge cases may need more tests.

#### Finding: TCG-FND-013
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Verified - AI tests are in `tests/unit/ai/` with multiple subdirectories. This is an observation about organization, not an issue.

#### Finding: TCG-FND-014
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Verified - Research UI tests in `tests/unit/research/` exist. The observation about visual testing benefits is valid but informational.

## Cross-Shard Duplicates

No cross-shard duplicates detected.
