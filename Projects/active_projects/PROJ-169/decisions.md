# PROJ-169: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-23 | Project initialized from dead code review | 6-agent focused review identified ~4,288 LOC of dead code across 54 files |
| 2026-02-23 | Keep test_framework/ (NOT dead code) | Combat Lab UI actively depends on it; unique functionality (TestHistory, BattleStateCapture, 6 services) with no equivalent in simulation_tests |
| 2026-02-23 | Keep Debugging/ (NOT dead code) | Active bug tracking workflow — confirm_bugs_ui.py + archive_confirmed.py are interdependent |
| 2026-02-23 | Keep BattlePanel (correct pattern) | Active abstract base class with 3 subclasses all properly overriding draw() |
| 2026-02-23 | Keep tkinter_utils.py (well placed) | Intentional consolidation from 4 files (DUP-UI2-001), 6 active consumers |
| 2026-02-23 | Delete Tools/formation_editor.py as duplicate | game/ui/screens/formation_editor.py is the authoritative refactored version; Tools/ version is legacy standalone |
| 2026-02-23 | 4-phase approach: zero-risk first, then tools, then migration, then polish | Maximizes safety — each phase is independently verifiable with full test suite |
| 2026-02-23 | Delete (not archive) all dead scripts | All are preserved in git history; no value in keeping files that will never be used again |
| 2026-02-23 | Remove Tools from pytest.ini pythonpath after migration | Tools directory should not be on Python path — game modules belong in game/ |
