# PROJ-159: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-22 | Project initialized | Starting point for Rewrite Transfer Validator Tests as Integration Tests |
| 2026-02-22 | Use real Planet/Fleet objects instead of MagicMock | `MagicMock(spec=Planet)` fails `is_planet()` protocol check because `isinstance(obj, IPlanet)` returns False for mocks. Real objects satisfy the protocol by design. |
| 2026-02-22 | Move tests from unit/ to integration/ | Tests require real object graphs (Galaxy → System → Planet); this matches existing integration test patterns in `test_colonize_logic.py` |
| 2026-02-22 | Consolidate from 30 tests to ~12 core tests | Original tests included implementation details (validation order, constant existence checks) that don't add behavioral value. Per CLAUDE.md: test behavior, not implementation. |
| 2026-02-22 | Follow MockGalaxy/MockSystem pattern | Pattern from `test_colonize_logic.py:32-43` is proven, minimal, and sufficient for transfer validation needs |
| 2026-02-22 | Create factory functions for Planet/Fleet creation | Planet has 13 mandatory physical fields; factory with Earth-like defaults keeps tests clean and focused on test-specific parameters |
| 2026-02-22 | Use CargoStorage ability for transport capacity | Fleet cargo capacity comes from ship abilities; follow existing pattern from `test_colonize_population.py:41-67` |
| 2026-02-22 | Delete old tests entirely (not keep as skip) | Per CLAUDE.md System Migration Policy: "ERADICATE the old system completely" - no fallback code paths or parallel systems |
| 2026-02-22 | Use expected_stats for cargo capacity in tests | ShipStatsCalculator looks up component definitions from registry, ignoring inline abilities. Using expected_stats bypasses registry and gives tests precise control over cargo capacity. |

## Context for Key Decisions

### Why not fix the mocks?

Three options were considered:

1. **Make `is_planet()` duck-type friendly** - Would require changing `game/core/protocols.py` to use `hasattr()` checks instead of `isinstance()`. This is invasive and changes core behavior for a test concern.

2. **Create Mock subclass implementing IPlanet** - Would require maintaining a parallel mock hierarchy that must stay in sync with the real classes. Fragile and error-prone.

3. **Use real Planet objects** (CHOSEN) - The cleanest solution. Real objects satisfy protocols by design, tests exercise real code paths, and there's no mock maintenance burden.

### Why consolidate tests?

The original 30 tests included:
- `test_validation_order_direction_before_cargo_type` - Tests internal ordering, not user-facing behavior
- `test_valid_cargo_types_constant` - Tests that a constant exists
- `test_valid_directions_constant` - Tests that a constant exists

These don't prevent regressions or verify behavior. The 12 core tests cover all validation outcomes:
- 3 load scenarios (success, no capacity, no population)
- 2 unload scenarios (success, no cargo)
- 6 general validation failures (location, ownership, null inputs, invalid params)
- 2 species-specific edge cases

This provides equivalent coverage with less maintenance burden.
