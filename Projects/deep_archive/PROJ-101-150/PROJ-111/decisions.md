# PROJ-111: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-11 | Project initialized | Starting point for Test Coverage - UI and Framework |
| 2026-02-11 | 7 phases: Framework Services -> Framework Complex -> Battle -> Strategy Core -> Strategy Support -> Workshop/Setup -> Quality | Order by dependency depth and complexity. Framework services have clean DI and no rendering deps, so they're fastest to test and establish patterns. Complex singletons next. Screens grouped by subsystem. Quality improvements last as cross-cutting. |
| 2026-02-11 | Use bypass-init pattern as primary approach for screen tests | Most screens have heavy `__init__` with pygame_gui UIManager creation, session objects, etc. The bypass-init pattern (`patch.object(Cls, '__init__', ...)` + `__new__`) is proven in `test_strategy_menu_actions.py` and avoids all initialization side effects. |
| 2026-02-11 | Prefer mock-based tests over integration-style with real pygame surfaces | Unit tests should be fast and isolated. Only use real pygame surfaces when testing actual rendering math (camera transforms, image scaling). Use MagicMock for Surface/Rect in logic tests. |
| 2026-02-11 | Create shared fixtures in conftest.py for common mock patterns | Mock scene, mock ship DTOs, mock fleet, mock galaxy etc. should be in `conftest.py` files to avoid duplication across test modules. |
| 2026-02-11 | Test file naming follows `tests/unit/ui/screens/test_{source_file_name}.py` | Consistent with existing convention. New test files mirror production file names. |
| 2026-02-11 | Exclude INFO-level findings from phase checklists | INFO findings (TCG-UI1-026 through TCG-UI1-029) are organizational issues, not test coverage gaps. Include only CRITICAL, MAJOR, and MINOR findings. |
| 2026-02-11 | Group MINOR quality findings into Phase 7 | Assertion quality (TCG-UI1-020), over-mocking (TCG-UI1-021), missing error paths (TCG-UI1-022), edge cases (TCG-UI1-023), resize handling (TCG-UI1-024) are cross-cutting quality improvements best done after primary coverage exists. |
| 2026-02-11 | Singleton tests (SpriteManager, ShipThemeManager) must use `reset()` in teardown | Both classes have `reset()` classmethod for test cleanup. Failing to call it leaves stale singleton state that breaks subsequent tests in xdist. |
| 2026-02-11 | Skip tkinter-dependent tests in headless CI if tkinter unavailable | `setup_screen.py` and `formation_editor.py` import tkinter at module level. Tests should handle `TclError` gracefully. |
