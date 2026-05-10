# DUP-X-08: `Camera.hex_at_screen` Consolidation Review

**Review date:** 2026-05-09
**Reviewer:** OpenCode (review agent)
**Scope:** Coordinate semantics, caller state, test coverage, migration completeness

---

## Answer Summary

| Question | Verdict | Severity |
|----------|---------|----------|
| 1. Coordinate semantics match? | **Yes** — identical 2-step chain | INFO |
| 2. Unreconstructible camera state? | **No** — all callers pass screen coords only | INFO |
| 3. Test mock coverage parity? | **Gap** — no test validates the real transform chain | MAJOR |
| 4. Remaining `pixel_to_hex` to migrate? | **No** — all click-path sites migrated | INFO |
| 5. Grid renderer exception correct? | **Yes** — grid operates on world coords | INFO |

---

## Detailed Findings

### FND-010 — [MINOR] Stale docstring references to `pixel_to_hex`

Three migrated modules still claim to import/use `pixel_to_hex` in their module
docstrings, but the consolidation replaced all direct calls with
`camera.hex_at_screen`:

| File | Line | Stale text |
|------|------|-----------|
| `game/ui/screens/strategy_superweapons.py` | 8 | `pixel_to_hex: Runtime - coordinate conversion for command targeting` |
| `game/ui/screens/strategy_fleet_ops.py` | 8 | (same) |
| `game/ui/screens/strategy_colonization.py` | 8 | (same) |

None of these files import `pixel_to_hex` or call it directly after the
consolidation. The docstrings should reference `Camera.hex_at_screen` instead.

**Recommendation:** Update the three module docstrings.

---

### FND-011 — [MINOR] Superweapons test mock returns `tuple` instead of `HexCoord`

`tests/unit/ui/screens/test_strategy_superweapons.py:27`
```python
scene.camera.hex_at_screen = Mock(return_value=(5, 5))
```

The real `hex_at_screen` returns `HexCoord`. The mock returns a plain tuple
`(5, 5)`. This works in practice because the downstream `get_planets_at_global_hex`
and command constructors accept tuple-like inputs, but it means the test
suite would **not catch** a regression where `hex_at_screen` changes its
return type.

**Recommendation:** Change to `return_value=HexCoord(5, 5)`.

---

### FND-012 — [MAJOR] No test validates the `screen_to_world` → `pixel_to_hex` chain

Every test that exercises a code path through `hex_at_screen` mocks or stubs
the method entirely. No test verifies that the real chain produces correct
outputs:

| Test file | Mock approach |
|-----------|--------------|
| `test_strategy_superweapons.py:27` | `Mock(return_value=(5, 5))` |
| `test_strategy_fleet_ops.py:77,94,159,172` | `Mock(return_value=target_hex)` |
| `test_strategy_click_dispatcher.py:13-27` | `_IdentityCamera.hex_at_screen` stub ignores inputs |
| `test_strategy_input_handler_core.py:693` | `MagicMock(return_value=HexCoord(0,0))` |

If `screen_to_world` behaviour changes (e.g., a viewport offset bug), all
tests still pass because `hex_at_screen` is mocked out.

**Recommendation:** Add a dedicated unit test for `Camera.hex_at_screen` in
`tests/unit/ui/renderer/` that validates the full transform end-to-end (e.g.,
set camera position + zoom, call `hex_at_screen` with a known screen point,
assert the returned `HexCoord` is correct given `pixel_to_hex` semantics).

---

### FND-013 — [MINOR] Misleading test assertion on `screen_to_world` not called

`tests/unit/ui/screens/test_strategy_fleet_ops.py:66`
```python
scene.camera.screen_to_world.assert_not_called()
```

The intent of this assertion (test `test_handle_move_designation_blocks_building_fleet_before_hit_testing`)
is to verify that no coordinate conversion happens when a fleet is building.
With the old inline pattern, this assertion directly validated that
`screen_to_world` was skipped. With the consolidated pattern, the assertion
still "passes" only because `hex_at_screen` is Mock'ed (so `screen_to_world`
is never reached). The assertion should be updated to:

```python
scene.camera.hex_at_screen.assert_not_called()
```

**Recommendation:** Update the assertion to match the new consolidation
pattern for clarity and resilience against future test refactors.

---

### FND-014 — [INFO] Grid renderer exception `pixel_to_hex` import confirmed correct

`game/ui/screens/strategy_render/grid.py:14,41`

```python
from game.core.hex_math import pixel_to_hex
# ...
h = pixel_to_hex(p.x, p.y, r.hex_size)
```

The grid renderer uses `pixel_to_hex` for **viewport culling** — determining
which hex grid lines are visible on screen. Its inputs are world-space
coordinates produced by `camera.screen_to_world`. This is a rendering
concern, not a "click-to-hex targeting" concern. The direct import is
semantically correct and should not be migrated to `hex_at_screen`.

The other `pixel_to_hex` user outside the screen layer,
`game/strategy/data/galaxy_warp_generator.py:114,120`, operates on
generation-time local pixel coords (not screen clicks) — also correctly
retained.

**Verdict:** No false negative. The exception is well-reasoned.

---

### FND-015 — [INFO] Coordinate semantics preserved exactly

`game/ui/renderer/camera.py:154-172`

```python
def hex_at_screen(self, screen_x, screen_y, hex_size):
    world_pos = self.screen_to_world((screen_x, screen_y))
    return pixel_to_hex(world_pos.x, world_pos.y, hex_size)
```

The original inline pattern across all call sites was:
```python
world_pos = self.camera.screen_to_world((mx, my))
target_hex = pixel_to_hex(world_pos.x, world_pos.y, self.hex_size)
```

The consolidated method performs the identical two-step transformation:
1. `screen_to_world` — removes viewport offset, applies inverse zoom, adds camera position
2. `pixel_to_hex` — converts Cartesian world coords to axial hex coords with `size` divisor

**No semantic drift.** The `hex_size` parameter is passed through verbatim.
The camera's internal state (`self.position`, `self.zoom`, `self.offset_*`,
`self.width`, `self.height`) is accessed through `screen_to_world` as before.

---

### FND-016 — [INFO] No caller passes unreconstructible camera state

All 11 call sites pass only `(mx, my, hex_size)`:
- `mx, my`: raw screen pixel coordinates from `pygame.mouse.get_pos()` or `event.pos`
- `hex_size`: `self.hex_size` delegated from `scene`

The camera's pan offset (`self.position`), zoom (`self.zoom`), viewport
offset (`self.offset_x`, `self.offset_y`), and viewport dimensions
(`self.width`, `self.height`) are internal instance state accessed by
`screen_to_world`. No caller needs to pass these values because
`hex_at_screen` reads them from `self`.

**Verdict:** The consolidated signature is complete. No MAJOR issue.

---

### FND-017 — [MAJOR] `handle_colonize_designation` has no test coverage

`tests/unit/ui/screens/test_strategy_colonization.py` tests `on_colonize_click`
(which works from fleet location, not screen coords) but never tests
`handle_colonize_designation`, the method at `strategy_colonization.py:158`
that actually calls `hex_at_screen`. This is the single `hex_at_screen` call
in the colonization module and it has zero test coverage.

**Recommendation:** Add a test for `handle_colonize_designation` covering:
- No fleet → returns None
- No system at hex → returns None / None response
- No colonizable planets → returns None
- Valid planets → returns prompt with candidates and target_hex

---

### FND-018 — [MINOR] No dedicated `hex_at_screen` unit test on Camera

`Camera.hex_at_screen` is a public method on the Camera class but has no
dedicated unit test. While it is a thin wrapper (2 lines of real logic),
a unit test would serve as a regression guard. The existing `test_camera_hex_at_screen` test file
does not exist.

**Recommendation:** Add a test in a new or existing camera test file that:
1. Creates a Camera with known position/zoom/offset
2. Calls `hex_at_screen` with known screen coordinates
3. Asserts the returned HexCoord matches the expected value from the equivalent `screen_to_world + pixel_to_hex` computation

---

## Migration Completeness

| File | `hex_at_screen` sites | Status |
|------|----------------------|--------|
| `strategy_superweapons.py` | 5 (lines 106,160,204,258,300) | Migrated |
| `strategy_click_dispatcher.py` | 2 (lines 502,525) | Migrated |
| `strategy_fleet_ops.py` | 2 (lines 111,190) | Migrated |
| `strategy_colonization.py` | 1 (line 158) | Migrated |
| `strategy_input_handler.py` | 1 (line 211) | Migrated (hover) |
| **All remaining `pixel_to_hex` in production** | grid.py (culling), galaxy_warp_generator.py (generation), camera.py (wrapper), hex_math.py (definition) | Correctly retained |

---

## Severity Summary

| ID | Severity | Category | Description |
|----|----------|----------|-------------|
| FND-010 | MINOR | Doc staleness | Stale `pixel_to_hex` mentions in 3 module docstrings |
| FND-011 | MINOR | Test fidelity | Mock returns tuple, not HexCoord |
| FND-012 | **MAJOR** | Test coverage gap | No test validates the real `screen_to_world` → `pixel_to_hex` chain |
| FND-013 | MINOR | Test clarity | `screen_to_world.assert_not_called` should be `hex_at_screen.assert_not_called` |
| FND-014 | INFO | Exception validated | Grid renderer `pixel_to_hex` retained correctly |
| FND-015 | INFO | Semantics confirmed | Coordinate transform chain unchanged |
| FND-016 | INFO | State completeness | No unreconstructible camera state |
| FND-017 | **MAJOR** | Test coverage gap | `handle_colonize_designation` untested |
| FND-018 | MINOR | Test coverage gap | No dedicated `Camera.hex_at_screen` unit test |

**Overall assessment:** The consolidation is functionally sound — coordinate
semantics are preserved, no caller passes state the method can't reconstruct,
and all click-path `pixel_to_hex` usages are migrated. The two MAJOR findings
are test coverage gaps, not production defects.
