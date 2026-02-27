# PROJ-169: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis
This project originates from a focused dead code review conducted 2026-02-23, which deployed 6 specialized agents to analyze the codebase:

1. **Trivial Delete Verifier** — Confirmed zero dependencies for Categories A, B, F, G
2. **test_framework Dependency Analyzer** — Deep analysis proving test_framework is NOT orphaned
3. **Tools & Scripts Auditor** — File-by-file disposition of 38 files in Tools/ and scripts/
4. **Unused Import Scanner** — Found 14 unused standard library imports across 10 files
5. **Misplaced File Auditor** — Found duplicate formation_editor.py, misnamed dirs, empty dirs
6. **Size & Impact Estimator** — Calculated total impact: 4,288 LOC + 22.8MB __pycache__

Full review report: `Reviews/results/2026-02-23_180329_focused_dead-code-cleanup-audit/report.md`
Individual agent reports: `Reviews/results/2026-02-23_180329_focused_dead-code-cleanup-audit/findings/`

## Swarm Findings Summary

### Architecture
- Dead code is distributed across 6 distinct areas with no cross-dependencies
- All dead code is leaf-level — nothing else depends on it
- The only non-trivial deletion is `Tools/formation_editor.py` which has an active import in `game/app.py:22`, but this is a duplicate of `game/ui/screens/formation_editor.py`
- `pytest.ini` adds `Tools` to pythonpath (line 5) — must be updated when Tools/ is deleted

### Key Patterns to Reuse
- No new code patterns needed — this is purely deletion and relocation

### Dependencies & Risks
1. **Tools/formation_editor.py import chain** — `game/app.py:22` imports `FormationEditorScreen` from Tools/. The same class exists in `game/ui/screens/formation_editor.py`. After verifying the game/ui/screens version is the authoritative one, delete Tools/ version and update the import. Risk: Low.
2. **pytest.ini pythonpath** — Currently `pythonpath = . Tools`. After Tools/ removal, change to `pythonpath = .`. Risk: Low — tests may fail if missed.
3. **test_formation_editor_logic.py** — Currently in `tests/unit/builder/` and imports via the Tools pythonpath. Must update import and relocate to `tests/unit/ui/screens/`. Risk: Low.

### Revised Assessments (Items NOT Dead)
Four items from the prior DC review were reclassified after deep investigation:

| Item | Prior Finding | Revised Status | Evidence |
|------|--------------|----------------|----------|
| `test_framework/` | DC-003: Orphaned | **ACTIVE** | 4 game/ consumers, unique Combat Lab functionality, 6 service classes with no equivalent in simulation_tests |
| `Debugging/` | DC-005: Delete | **ACTIVE** | Interdependent bug tracking workflow (Tkinter UI + auto-archiver) |
| `BattlePanel` | DC-011: Stub | **CORRECT** | Active abstract base with 3 subclasses (ShipStatsPanel, SeekerMonitorPanel, BattleControlPanel) all overriding draw() |
| `tkinter_utils.py` | DC-008: Questionable | **WELL PLACED** | Intentional consolidation from 4 files (DUP-UI2-001), 6 active consumers |

### Opportunities Discovered
- After cleanup, scripts/ drops from ~28 to 11 well-curated development tools
- Tools/ directory can be completely removed (formation_editor migrated to game/ui/screens/)
- ~22.8MB repo size reduction from __pycache__ untracking alone

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
