# PROJ-337 — Design Notes

## Architecture context

- **Layer:** `game/ui/` (post-PROJ-147 move; previously
  `game/research/ui/`).
- **Plug-in point:** `game/screen_router.py:start_research_tree()`
  constructs `ResearchTreeScene(width, height, on_close_callback=on_research_tree_return)`
  and switches to `GameState.RESEARCH_TREE` via `_switch_scene`.

## Dependency graph

### `ResearchTreeScene`

- `TechTree.load_from_json` (module-level loader; patched in tests).
- `ResearchTracker` (built in `__init__`; resolves fuzzy requirements
  with its seed).
- `ResearchService.process_turn` (called from `_on_next_turn`).
- `Camera` (DI-optional; built with min/max/zoom defaults if not
  injected; PROJ-132 added the seam).
- `pygame_gui.UIManager((w, h))` (built in `__init__`; rebuilt on
  `handle_resize`).
- `ResearchRenderer` (composed; injected via patch in tests).
- `ResearchControlPanel` (composed; injected via patch in tests).

### `ResearchRenderer`

- `tech_tree.nodes` (read-only iteration).
- `tracker.get_state(node_id)` and `tracker.get_all_tech_levels()`.
- `camera.world_to_screen()`, `camera.zoom`, `camera.width`,
  `camera.height`.
- `pygame.draw.line`, `pygame.draw.rect` (module-level — must be
  monkeypatched in tests).
- `get_font(size)` (delegated; rounded to nearest 2 px, min 8).
- `game.ui.colors` constants (RESEARCH_COMPLETED, RESEARCH_AVAILABLE,
  RESEARCH_SELECTED, etc.).

### `ResearchControlPanel`

- `pygame_gui.elements.*` widgets (UIButton, UILabel, UIHorizontalSlider,
  UITextBox, UIPanel) — 20+ widgets built by `_create_ui` in `__init__`.
- `tracker` (mutable: `set_rp_budget`, `set_allocation`,
  `spread_rp_evenly`, `auto_spread_enabled`, `rp_budget`).
- `tech_tree` (read for spread + node lookups).

## Lifecycle

- Scene constructed once per "open Research Tree" click.
- `handle_resize` triggers full `UIManager` + `ResearchControlPanel`
  rebuild. This is the observed behavior; PROJ-147's file move did not
  change it. New tests pin this behavior; they do not propose to change it.

## Test-isolation hazards

- **`pygame_gui` module-state corruption under pytest-xdist.** Documented
  in both `tests/unit/research/research_scene/conftest.py` and
  `tests/unit/research/research_controls/conftest.py`. Mitigations:
  - Scene tests use the `_patched_research_scene` contextmanager that
    patches all six construction-time dependencies.
  - Controls tests use `mock_pygame_gui` autouse fixture (sys.modules
    swap + reload) and the `MagicMock(spec=ResearchControlPanel) + lambda`
    binding pattern to invoke real methods on a mock instance without
    running `_create_ui`.
  - Renderer tests use the `renderer_module` autouse fixture
    (importlib-isolated module loading).
- **`pygame.draw.*` is module-level.** Renderer tests must monkeypatch
  per-test rather than relying on a clean dependency seam. Existing
  `_is_visible` tests already pass `MagicMock(spec=pygame.Surface)`; new
  draw-orchestration tests extend this with monkeypatched
  `pygame.draw.line` / `pygame.draw.rect`.

## DI seam

- `Camera` is already injectable into `ResearchTreeScene` (PROJ-132). No
  additional DI seams are introduced in PROJ-337. Refactoring
  `ResearchControlPanel` to a builder seam is deferred (D-009).

## Construction-time side effects (testability blockers)

| Class | Side effects | Mitigation |
|---|---|---|
| `ResearchTreeScene.__init__` | Loads tech tree JSON, builds tracker, validates requirements, detects cycles, builds UIManager, builds renderer + controls, builds camera if not injected. | `_patched_research_scene` patches all six. |
| `ResearchControlPanel.__init__` | `_create_ui` builds 20+ pygame_gui widgets. | `MagicMock(spec=...) + lambda` binding to call real methods without running `_create_ui`. |
| `ResearchRenderer.__init__` | None (pure attribute store). | No mitigation needed. |
