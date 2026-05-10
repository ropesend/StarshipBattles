# PROJ-337 — Decisions

| ID | Decision |
|---|---|
| D-001 | The brief was wrong about "ZERO" coverage. Four existing test files (~1320 LOC) cover ~30 behaviors across the three production files. PROJ-337 is a gap-fill project, not green-field characterization. |
| D-002 | Do NOT relocate `tests/unit/research/research_*` to `tests/unit/ui/research/`. The master plan rule explicitly forbids "Moving existing tests into a new layout." Update the master plan's tests-scope column to reflect reality (the tests already live under `tests/unit/research/`). |
| D-003 | Reuse the `_patched_research_scene` contextmanager pattern from existing scene tests for new scene gap-fills. Do not invent a new fixture. |
| D-004 | For renderer tests, continue the importlib-isolated module loading pattern (`test_research_renderer.py`) to avoid pygame_gui xdist corruption. New renderer tests use the same `renderer_module` autouse fixture. |
| D-005 | For controls tests, reuse the `mock_pygame_gui` autouse fixture that swaps `sys.modules['pygame_gui']` and reloads. Do NOT instantiate `ResearchControlPanel` directly — use the existing `MagicMock(spec=...) + lambda binding` pattern from `test_reset_state.py` to call real methods on a mock instance. |
| D-006 | Renderer draw-call assertions: pass a `MagicMock(spec=pygame.Surface)` (not a live surface) and a Mock `pygame.draw.line` / `pygame.draw.rect` via monkeypatch. Assert call counts and color args, not pixel output. No golden images. |
| D-007 | Pin observed behavior — including any apparently-buggy paths (e.g. `update_turn_log` truncates to first-5 not last-5). Characterize what the code does today; file separate tickets for any behavior that appears wrong. |
| D-008 | One characterization commit per behavior cluster (typically one commit per public method tested), not one commit per test, to keep the commit graph readable. Each new test file stays under 500 LOC. |
| D-009 | DEFER: PROJ-329-style two-stage construction or builder seam for `ResearchControlPanel`. Per user direction, PROJ-329 work is a separate effort and is not pulled into PROJ-337. |
