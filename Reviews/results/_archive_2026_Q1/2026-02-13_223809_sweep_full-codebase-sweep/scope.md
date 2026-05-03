# Sweep Review Scope

**Review Type:** Sweep Review (Continuous Improvement Loop - Cycle 5)
**Created:** 2026-02-13
**Scope:** `game/` (entire production codebase)
**Agent Count:** 25 (5 sweep types x 5 shards)
**Execution Model:** 5 waves of 5 parallel agents

## Shard Definitions

| Shard Name | ID Suffix | Directories |
|------------|-----------|-------------|
| UI-Screens | UI1 | `game/ui/screens/`, `game/ui/panels/` |
| UI-Framework | UI2 | `game/ui/` (root files, services/, renderer/, interfaces/, orchestration/, assets/, components/, utils/) |
| Simulation | SIM | `game/simulation/` (all subdirectories) |
| Strategy | STR | `game/strategy/` (all subdirectories) |
| Foundation | FND | `game/core/`, `game/ai/`, `game/research/`, `game/engine/` |

## Exclusions

- `tests/`
- `__pycache__/`
- `.git/`
- `assets/`
- `refactor_loop/`
- `Reviews/`
- `Projects/`

## Agent Matrix (25 Agents)

| Wave | Sweep Type | Shard | Output File | Finding ID Prefix |
|------|-----------|-------|-------------|-------------------|
| 1 | Duplication | UI-Screens | `duplication_ui_screens_report.md` | DUP-UI1 |
| 1 | Duplication | UI-Framework | `duplication_ui_framework_report.md` | DUP-UI2 |
| 1 | Duplication | Simulation | `duplication_simulation_report.md` | DUP-SIM |
| 1 | Duplication | Strategy | `duplication_strategy_report.md` | DUP-STR |
| 1 | Duplication | Foundation | `duplication_foundation_report.md` | DUP-FND |
| 2 | Legacy Holdovers | UI-Screens | `legacy_ui_screens_report.md` | LEG-UI1 |
| 2 | Legacy Holdovers | UI-Framework | `legacy_ui_framework_report.md` | LEG-UI2 |
| 2 | Legacy Holdovers | Simulation | `legacy_simulation_report.md` | LEG-SIM |
| 2 | Legacy Holdovers | Strategy | `legacy_strategy_report.md` | LEG-STR |
| 2 | Legacy Holdovers | Foundation | `legacy_foundation_report.md` | LEG-FND |
| 3 | Consistency | UI-Screens | `consistency_ui_screens_report.md` | CON-UI1 |
| 3 | Consistency | UI-Framework | `consistency_ui_framework_report.md` | CON-UI2 |
| 3 | Consistency | Simulation | `consistency_simulation_report.md` | CON-SIM |
| 3 | Consistency | Strategy | `consistency_strategy_report.md` | CON-STR |
| 3 | Consistency | Foundation | `consistency_foundation_report.md` | CON-FND |
| 4 | Architecture Drift | UI-Screens | `architecture_ui_screens_report.md` | ADR-UI1 |
| 4 | Architecture Drift | UI-Framework | `architecture_ui_framework_report.md` | ADR-UI2 |
| 4 | Architecture Drift | Simulation | `architecture_simulation_report.md` | ADR-SIM |
| 4 | Architecture Drift | Strategy | `architecture_strategy_report.md` | ADR-STR |
| 4 | Architecture Drift | Foundation | `architecture_foundation_report.md` | ADR-FND |
| 5 | Test Coverage | UI-Screens | `test_coverage_ui_screens_report.md` | TCG-UI1 |
| 5 | Test Coverage | UI-Framework | `test_coverage_ui_framework_report.md` | TCG-UI2 |
| 5 | Test Coverage | Simulation | `test_coverage_simulation_report.md` | TCG-SIM |
| 5 | Test Coverage | Strategy | `test_coverage_strategy_report.md` | TCG-STR |
| 5 | Test Coverage | Foundation | `test_coverage_foundation_report.md` | TCG-FND |
