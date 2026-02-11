# Phase 5: Fix Research/UI Camera Dependency

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-106 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
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

- [x] Check if `game/core/protocols.py` already exists and has patterns we should follow
- [x] Add `ICamera` Protocol class with the methods research_scene/research_renderer use:
  - `world_to_screen(self, world_pos) -> Vector2`
  - `screen_to_world(self, screen_pos) -> Vector2`
  - `width: int` property
  - `height: int` property
  - `zoom: float` property
  - `position` property (camera world position)
- [x] Use `typing.Protocol` with `runtime_checkable=True`
- [x] Write unit test that verifies the existing Camera class satisfies the ICamera protocol
- [x] Run tests: `pytest tests/unit/core/test_protocols.py::TestICameraProtocol -v` -- 5 passed

**Notes:**
- Added ICamera protocol to existing `game/core/protocols.py` (follows existing patterns)
- Added `is_camera()` TypeGuard function
- Includes: width, height, zoom, position, world_to_screen, screen_to_world, update, update_input
- 5 new tests verify Camera satisfies ICamera protocol

---

### Task 5.2: Update research_scene.py to Use ICamera Protocol [Simple]
**File:** `game/research/ui/research_scene.py`
**Tests:** `pytest tests/ -v -k research`

- [x] Line 14: Replace `from game.ui.renderer.camera import Camera` with `from game.core.protocols import ICamera` (or wherever protocol was placed)
- [x] Update type hints in `__init__` and any methods that reference `Camera` to use `ICamera`
- [x] If ResearchTreeScene creates its own Camera instance, keep the `game.ui.renderer.camera` import for construction but use ICamera for the type hint
- [x] Check if ResearchTreeScene creates Camera internally (line 14 is direct import, suggesting it creates one)
- [x] If so: The scene needs Camera at construction time. Options:
  - Accept ICamera as constructor parameter (preferred -- DI)
  - Keep runtime import of Camera for construction only
- [x] Run tests: `pytest tests/ -v -k research` -- 252 passed

**Notes:**
- ResearchTreeScene creates its own Camera internally (line 88: `self.camera = Camera(...)`)
- Kept runtime import for Camera construction (necessary for scene to own its camera)
- Added docstring note explaining the intentional cross-layer import

---

### Task 5.3: Update research_renderer.py to Use ICamera Protocol [Simple]
**File:** `game/research/ui/research_renderer.py`
**Tests:** `pytest tests/ -v -k research`

- [x] Line 12: Replace `from game.ui.renderer.camera import Camera` with ICamera protocol import
- [x] Update type hints to use ICamera instead of Camera
- [x] ResearchRenderer receives camera as a parameter, so this is straightforward
- [x] Run tests: `pytest tests/ -v -k research` -- 252 passed

**Notes:**
- ResearchRenderer now uses `ICamera` protocol for type hint (clean separation)
- Camera is passed in as parameter, no construction needed

---

### Task 5.4: Verify Research Layer Has No UI Dependencies [Simple]

- [x] Grep for `from game.ui` in `game/research/` directory
- [x] Expected: Zero matches (all UI imports eliminated)
- [x] Run full test suite: `pytest tests/ -n 12` -- 8187 passed

**Notes:**
- research_renderer.py: Zero UI imports (uses ICamera protocol) ✓
- research_scene.py: One UI import remains (Camera construction) - **Acceptable per design.md mitigation**
  - This is intentional: ResearchTreeScene owns and creates its Camera
  - Converting to DI would require app.py to create Camera and inject it
  - Current design is acceptable trade-off per Phase 5 risk mitigation

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] ICamera protocol created in game.core
- [x] Research layer dependency reduced (renderer clean, scene retains construction import)
- [x] Full test suite passes: `pytest tests/ -n 12` (8187 tests)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
