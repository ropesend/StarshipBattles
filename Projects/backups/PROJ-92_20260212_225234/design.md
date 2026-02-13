# PROJ-92: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### From Review (2026-02-10): Circular Dependency & TYPE_CHECKING Audit

A previous audit flagged "Pervasive Circular Dependencies Managed Through TYPE_CHECKING Guards" as high severity. Investigation confirmed PROJ-90 resolved most issues, but three residual artifacts remain:

1. **6 vestigial `if TYPE_CHECKING: pass` blocks** — dead code left behind after imports were cleaned up
2. **`game/core/protocols.py` imports `HexCoord` from `game/strategy/data/hex_math`** — a core→strategy layer violation (TYPE_CHECKING-only, no runtime impact)
3. **`hex_math.py` is a pure math utility living in strategy** — it has zero strategy dependencies (only `import math`), so it belongs in `game/core/`

### Key Statistics
- **131 files** have TYPE_CHECKING blocks — healthy, standard Python pattern
- **6 files** have dead `if TYPE_CHECKING: pass` — vestigial
- **1 layer violation** in `core/protocols.py:39-40`
- **hex_math.py** is 250 lines, self-contained (only depends on stdlib `math`)
- **32 production files** + **124 test files** import from `game.strategy.data.hex_math`
- **Baseline:** 7616 tests passing, 0 failures

### What PROJ-90 Already Fixed
- `ship.py` lazy init of `ShipCombatEngine` → now module-level import
- `ship.py` no-op `if TYPE_CHECKING: pass  # GameRegistries` → eliminated
- Added `IPostBattleShip` protocol for clean strategy-simulation boundary

## Swarm Findings Summary

### Architecture
- The architecture is clean overall. All seven layers (core, engine, simulation, research, strategy, ai, ui) are properly isolated
- No runtime circular dependencies exist
- The only TYPE_CHECKING layer violation is `core/protocols.py` → `strategy/data/hex_math`
- All remaining late imports are documented in `docs/architecture/ARCHITECTURE.md`

### Key Patterns to Reuse
- **Re-export shim pattern**: Used in PROJ-58 for safe incremental migration. Create a shim at the old location that re-exports from the new location, update all callers, then delete the shim.
- **find-and-replace import migration**: Simple `sed`-style replacement across many files (used extensively in PROJ-43, PROJ-58, etc.)

### Dependencies & Risks
1. **High file count (156 files)** — mechanical but tedious. Risk: missing a file. Mitigation: `grep -r` verification after each step.
2. **Test file imports (124 files)** — conftest.py files may import hex_math indirectly. Mitigation: re-export shim ensures nothing breaks during migration.
3. **`game/strategy/__init__.py` re-exports HexCoord** — must update to import from `game.core.hex_math`. External code importing `from game.strategy import HexCoord` will continue to work.

### Opportunities Discovered
- None beyond the stated scope. The remaining late imports (ModifierService in ship.py, ShipSerializer in ship_instance.py) are well-documented and acceptable.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
