# Dead Code Hunter Report: Small Modules (core, ai, engine, research, assets)

### Summary
- Total dead code items found: 5
- Estimated removable lines: 50-80
- Critical: 0, Major: 0, Minor: 3, Info: 2

### Findings

#### Minor: Profiler.save_history() never called
**ID:** DC-SM-01
**Location:** `game/core/profiling.py:81-104`
**Issue:** The `save_history()` method is implemented (24 lines) but never called anywhere in the codebase. Profiling records are collected but never persisted to disk.
**Evidence:** Grep shows no calls to `save_history()` in game/ or tests/.
**Removable Lines:** 24
**Effort:** Simple

#### Minor: Profiler.toggle() never called
**ID:** DC-SM-02
**Location:** `game/core/profiling.py:57-62`
**Issue:** The `toggle()` method is defined but never called. Profiler is started and stopped directly.
**Evidence:** No calls to `.toggle()` exist anywhere in the codebase.
**Removable Lines:** 6
**Effort:** Simple

#### Minor: Profiler.clear() unclear purpose
**ID:** DC-SM-03
**Location:** `game/core/profiling.py:41-44`
**Issue:** `clear()` method exists to reset records and regenerate session_id. Docstring claims "used for test isolation" but tests use `Profiler.reset()` via SingletonMeta instead.
**Evidence:** Tests don't call `clear()`, they use `reset()`.
**Removable Lines:** 4
**Effort:** Simple (verify first)

#### Info: hex_lerp() internal-only usage
**ID:** DC-SM-04
**Location:** `game/core/hex_math.py:254-267`
**Issue:** `hex_lerp()` is only used internally by `hex_linedraw()`. Exported in `__all__` and has tests but not used by gameplay code.
**Evidence:** Only references: hex_linedraw (uses it), tests (test it directly).
**Removable Lines:** 14 (but probably worth keeping for public hex_math API)
**Effort:** Simple

#### Info: get_random_from_group() seed parameter
**ID:** DC-SM-05
**Location:** `game/assets/asset_manager.py:108-117`
**Issue:** Uses `seed_id` parameter for deterministic selection but design intent is unclear. Only used for planet texture selection.
**Evidence:** Only called in strategy_renderer.py and strategy_screen.py.
**Removable Lines:** 0 (refactor target, not dead code)
**Effort:** Simple

### Top 5 Priority Items
1. **DC-SM-01**: Remove unused `Profiler.save_history()` (24 lines)
2. **DC-SM-02**: Remove unused `Profiler.toggle()` (6 lines)
3. **DC-SM-03**: Clarify or remove `Profiler.clear()` (4 lines)
4. **DC-SM-04**: Consider making `hex_lerp()` private
5. **DC-SM-05**: Refactor `get_random_from_group()` for clarity
