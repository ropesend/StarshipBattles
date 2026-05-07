# Findings: AST Shim-Scope Guard

## FND-AST-001 [INFO]: EXPECTED_SHIM_FUNCTIONS exactly matches pathfinding.py

Per instruction #5: verified all 10 names in `EXPECTED_SHIM_FUNCTIONS` against `pathfinding.py` top-level functions by AST parse:

| Expected Name | pathfinding.py Line | Matches? |
|---------------|---------------------|----------|
| `strip_start_hex` | 33 | Yes |
| `find_path_deep_space` | 40 | Yes |
| `_pathfinder_for` | 47 | Yes |
| `_intercept_for` | 64 | Yes |
| `find_path_interstellar` | 74 | Yes |
| `get_system_at_hex` | 80 | Yes |
| `find_nearest_system` | 86 | Yes |
| `find_hybrid_path` | 90 | Yes |
| `project_fleet_path` | 96 | Yes |
| `calculate_intercept_point` | 101 | Yes |

**Result: 10 of 10 match. No missing functions, no extras.** The guard correctly pins the post-PROJ-377 shim surface.

## FND-AST-002 [INFO]: Guard design follows convention

- Uses `frozenset` for the expected set (immutable, hashable).
- AST-based parsing (not just `dir()` or `module.__dict__`) — correctly handles `TYPE_CHECKING`, `TypeVar`, and `from __future__` imports.
- Custom error message with added/removed diffs is helpful for debugging.
- The `test_shim_helpers_present` parametrized test is a secondary guard that will fail with a clear message if either helper is removed.
