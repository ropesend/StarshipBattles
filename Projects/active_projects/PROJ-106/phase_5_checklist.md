# Phase 5: Fix Research/UI Camera Dependency

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-106 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Eliminate the cross-layer dependency where `game/research/ui/` imports `Camera` from `game/ui/renderer/camera.py`. Research layer should only depend on core.

---

## Context

Two files in the research UI layer import Camera from the main UI layer:
- `game/research/ui/research_scene.py:14` -- `from game.ui.renderer.camera import Camera`
- `game/research/ui/research_renderer.py:12` -- `from game.ui.renderer.camera import Camera`

Camera is a pure math/viewport utility (pan, zoom, world-to-screen transforms). It depends on pygame but provides viewport math that any rendering layer could use.

### Design Options

**Option A: Move Camera to game.core** (Rejected)
Camera uses `pygame.math.Vector2` internally and `pygame` for initialization. Moving to core would require refactoring Camera to use `game.core.math.Vector2` instead. This is feasible but a larger change than needed.

**Option B: Extract CameraProtocol to game.core** (Recommended)
Create a Protocol (or ABC) in `game.core` that defines the Camera interface. Research layer depends on the protocol. The actual Camera class in `game.ui` implements it. This is the cleanest separation with minimal disruption.

**Option C: Pass camera as a constructor parameter** (Simpler alternative)
Research scene already receives camera-like configuration. Could accept a camera object via DI without type-checking it against `game.ui`. But TYPE_CHECKING import would still reference `game.ui`.

Decision: **Option B** -- create a protocol in core.

---

## Tasks

### Task 5.1: Create ICamera Protocol in game.core [Simple]
**File:** `game/core/protocols.py` (or new `game/core/camera_protocol.py`)
**Tests:** `tests/unit/core/test_camera_protocol.py` (NEW)

- [ ] Check if `game/core/protocols.py` already exists and has patterns we should follow
- [ ] Add `ICamera` Protocol class with the methods research_scene/research_renderer use:
  - `world_to_screen(self, world_pos) -> Vector2`
  - `screen_to_world(self, screen_pos) -> Vector2`
  - `width: int` property
  - `height: int` property
  - `zoom: float` property
  - `position` property (camera world position)
- [ ] Use `typing.Protocol` with `runtime_checkable=True`
- [ ] Write unit test that verifies the existing Camera class satisfies the ICamera protocol
- [ ] Run tests: `pytest tests/unit/core/test_camera_protocol.py -v`

---

### Task 5.2: Update research_scene.py to Use ICamera Protocol [Simple]
**File:** `game/research/ui/research_scene.py`
**Tests:** `pytest tests/ -v -k research`

- [ ] Line 14: Replace `from game.ui.renderer.camera import Camera` with `from game.core.protocols import ICamera` (or wherever protocol was placed)
- [ ] Update type hints in `__init__` and any methods that reference `Camera` to use `ICamera`
- [ ] If ResearchTreeScene creates its own Camera instance, keep the `game.ui.renderer.camera` import for construction but use ICamera for the type hint
- [ ] Check if ResearchTreeScene creates Camera internally (line 14 is direct import, suggesting it creates one)
- [ ] If so: The scene needs Camera at construction time. Options:
  - Accept ICamera as constructor parameter (preferred -- DI)
  - Keep runtime import of Camera for construction only
- [ ] Run tests: `pytest tests/ -v -k research`

---

### Task 5.3: Update research_renderer.py to Use ICamera Protocol [Simple]
**File:** `game/research/ui/research_renderer.py`
**Tests:** `pytest tests/ -v -k research`

- [ ] Line 12: Replace `from game.ui.renderer.camera import Camera` with ICamera protocol import
- [ ] Update type hints to use ICamera instead of Camera
- [ ] ResearchRenderer receives camera as a parameter, so this is straightforward
- [ ] Run tests: `pytest tests/ -v -k research`

---

### Task 5.4: Verify Research Layer Has No UI Dependencies [Simple]

- [ ] Grep for `from game.ui` in `game/research/` directory
- [ ] Expected: Zero matches (all UI imports eliminated)
- [ ] Run full test suite: `pytest tests/ -n 12`

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] ICamera protocol created in game.core
- [ ] Research layer has zero imports from game.ui
- [ ] Full test suite passes: `pytest tests/ -n 12` (8164+ tests)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
