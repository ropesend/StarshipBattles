# PROJ-408 File Manifest

## Files

| File | Type | Notes |
|------|------|-------|
| tests/unit/ui/screens/test_empire_build_queue_window.py | Test | C-01 — replace introspection-only test with real-construction. |
| tests/unit/strategy/facade/test_strategy_session_facade.py | Test | C-02 — direct unit test for `EnginePhaseError` → `TurnFailedError` conversion. (Path may differ; confirm.) |
| tests/unit/ui/screens/test_planet_selection_window.py | Test | C-04 — direct facade-threading coverage. (Path may differ; confirm.) |
| game/ui/screens/empire_build_queue_window.py | Production (read-only) | C-01 reference. |
| game/strategy/facade/strategy_session_facade.py | Production (read-only) | C-02 reference (lines 194-201). |
| game/ui/screens/planet_selection_window.py | Production (read-only) | C-04 reference. |

**No production code is modified by PROJ-408. If a coverage test reveals a real bug, raise it — don't fix here.**
