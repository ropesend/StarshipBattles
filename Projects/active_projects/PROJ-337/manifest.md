# PROJ-337 — Manifest

## Production files in scope

| File | LOC | Notes |
|---|---|---|
| `game/ui/research_scene.py` | 401 | `ResearchTreeScene` — moved from `game/research/ui/` by PROJ-147. |
| `game/ui/research_renderer.py` | 324 | `ResearchRenderer` — pure attribute-store ctor; no construction-time side effects. |
| `game/ui/research_controls.py` | 475 | `ResearchControlPanel` — `_create_ui` builds 20+ pygame_gui widgets in `__init__`. |

## Existing test files (reused, not modified except by addition)

| File | LOC | Coverage today |
|---|---|---|
| `tests/unit/research/test_research_renderer.py` | 259 | Font quantization + exhaustive `_is_visible` cases. |
| `tests/unit/research/research_scene/test_initialization.py` | 36 | Stores dims, canvas width, callbacks. |
| `tests/unit/research/research_scene/test_callbacks.py` | 244 | `_on_next_turn`, `_on_reset`, `_on_close`, `_on_auto_spread_changed`. |
| `tests/unit/research/research_scene/test_interaction.py` | 166 | `_get_node_at_position` cases, layout, centering. |
| `tests/unit/research/test_research_scene_di.py` | 259 | DI camera injection + viewport propagation. |
| `tests/unit/research/research_controls/test_reset_state.py` | 88 | `reset()` mechanics + 2 selected-node-id consistency invariants. |
| `tests/unit/research/research_controls/conftest.py` | 269 | `mock_pygame_gui`, `mock_tracker`, `mock_node` fixtures + `MagicMock(spec=...) + lambda` binding pattern. |

## New test files (planned)

One new test module per production file, placed in the matching existing
subdirectory:

| New file | Target production file | Estimated tests |
|---|---|---|
| `tests/unit/research/research_scene/test_event_routing_and_draw.py` | `research_scene.py` | ~12 |
| `tests/unit/research/test_research_renderer_drawing.py` | `research_renderer.py` | ~18 |
| `tests/unit/research/research_controls/test_event_routing_and_updates.py` | `research_controls.py` | ~25 |

If any new file approaches 500 LOC, split by behavior cluster (e.g.
`test_event_routing.py` + `test_draw.py`).

## Fixtures reused

- `tests/unit/research/research_scene/conftest.py::_patched_research_scene`
- `tests/unit/research/research_controls/conftest.py::mock_pygame_gui`
- `tests/unit/research/research_controls/conftest.py::mock_tracker`
- `tests/unit/research/research_controls/conftest.py::mock_node`
- `tests/unit/research/test_research_renderer.py::renderer_module`

## New fixtures

None planned. If a new gap-fill test reveals a setup that would benefit
multiple tests, promote it to the matching `conftest.py` rather than
duplicating it.

## Exit gates

- Baseline before work: `pytest tests/unit/research/ -x -q` green.
- After each behavior cluster: targeted run green.
- Before commit: `pytest tests/unit/research/ -x -q` green and
  `python Tools/lint_test_files.py` clean.
- Before PR: `python Tools/test_sharded/test_sharded.py` green.
