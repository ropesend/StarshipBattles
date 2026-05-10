# Review Scope: God Class Decomposition Planning

## Metadata
- **Date:** 2026-02-23
- **Type:** Technical Debt Review (Focused)
- **Scope:** 16 specific files identified as god classes
- **Prior Art:** PROJ-86/87/88/89, Deliberate Design Debt Audit (2026-02-23)

## Focus
Produce actionable decomposition plans for the 16 largest classes in the codebase. Each plan should include responsibility inventory, extraction candidates, dependency analysis, pattern recommendation, target line count, test impact, and an accept/decompose verdict.

## Target Files

### Tier 1: Critical (>1,000 lines) — 5 files
1. `game/ui/screens/test_lab/screen.py` (1,906 lines) — Re-offender
2. `game/ui/screens/fleet_report_window.py` (1,108 lines) — New
3. `game/ui/screens/build_queue_screen.py` (1,084 lines) — Re-offender
4. `game/ui/screens/builder/weapons_panel.py` (1,037 lines) — New
5. `game/ui/screens/formation_editor.py` (941 lines) — New

### Tier 2: Major (800-999 lines) — 5 files
6. `game/ui/screens/race_setup_screen.py` (946 lines) — New
7. `game/strategy/data/galaxy.py` (928 lines) — New
8. `game/ui/screens/strategy_input_handler.py` (898 lines) — New
9. `game/ui/screens/empire_build_queue_window.py` (863 lines) — Re-offender
10. `game/ui/screens/strategy_screen.py` (823 lines) — Partially covered

### Tier 3: Borderline (600-799 lines) — 6 files
11. `game/simulation/entities/ship.py` (810 lines) — Stable
12. `game/ui/screens/strategy_renderer.py` (764 lines) — Accept candidate
13. `game/simulation/components/component.py` (723 lines) — Stable
14. `game/app.py` (705 lines) — Accept candidate
15. `game/ui/screens/battle_state_viewer.py` (687 lines) — New
16. `game/simulation/battle_controller.py` (659 lines) — New

## Special Investigations
- Re-offender root cause analysis (files 1, 3, 9)
- Growth prevention guardrails (CI checks, complexity metrics, architectural rules)

## Agent Configuration
**Recommended Agents:** 7
**Confirmed Agent Count:** TBD (awaiting user confirmation)

### Selected Agents
| # | Agent | Role | Files Assigned | Status |
|---|-------|------|----------------|--------|
| 1 | Tier 1 Decomposition Analyst | Deep analysis of 5 critical files (>1000 lines) | Files 1-5 | Pending |
| 2 | Tier 2 Decomposition Analyst | Deep analysis of 5 major files (800-999 lines) | Files 6-10 | Pending |
| 3 | Tier 3 Decomposition Analyst | Deep analysis of 6 borderline files + accept/decompose verdicts | Files 11-16 | Pending |
| 4 | Re-Offender Analyst | Root cause analysis of 3 re-offender files, growth pattern investigation | Files 1, 3, 9 | Pending |
| 5 | Dependency & Test Impact Analyst | Cross-cutting dependency analysis, test impact assessment for all 16 files | All 16 files | Pending |
| 6 | Extraction Pattern Analyst | Pattern matching, prior art evaluation, phasing recommendations | All 16 files | Pending |
| 7 | Growth Prevention Strategist | CI guardrails, complexity metrics, architectural rules | Codebase-wide | Pending |

## Notes
- All agents should produce findings structured for conversion to a project via `review_to_project.py`
- Re-offender analysis is highest priority alongside Tier 1 decomposition
- Agents share the same prior art context from PROJ-86/87/88/89 and the Deliberate Design Debt Audit
