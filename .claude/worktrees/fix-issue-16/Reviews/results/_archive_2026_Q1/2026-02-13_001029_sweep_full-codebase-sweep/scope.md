# Sweep Review Scope

**Review Type:** Sweep Review (Continuous Improvement Loop - Cycle 1)
**Date:** 2026-02-13
**Scope:** `game/` (entire production codebase)
**Agent Count:** 25 (5 sweep types × 5 shards)
**Execution Model:** 5 waves of 5 parallel agents

## Excluded Directories
- `tests/`
- `__pycache__/`
- `.git/`
- `assets/`
- `refactor_loop/`
- `Reviews/`
- `Projects/`

## Shard Definitions

| Shard Name | ID Suffix | Directories |
|------------|-----------|-------------|
| UI-Screens | UI1 | `game/ui/screens/`, `game/ui/panels/` |
| UI-Framework | UI2 | `game/ui/` (root files, services/, renderer/, interfaces/, orchestration/, assets/, components/, utils/) |
| Simulation | SIM | `game/simulation/` (all subdirectories) |
| Strategy | STR | `game/strategy/` (all subdirectories) |
| Foundation | FND | `game/core/`, `game/ai/`, `game/research/`, `game/engine/` |

## Agent Matrix (25 Agents)

| Wave | Sweep Type | Prefix | Agents |
|------|-----------|--------|--------|
| 1 | Duplication & Fragmentation | DUP | DUP-UI1, DUP-UI2, DUP-SIM, DUP-STR, DUP-FND |
| 2 | Legacy System Holdovers | LEG | LEG-UI1, LEG-UI2, LEG-SIM, LEG-STR, LEG-FND |
| 3 | Consistency Violations | CON | CON-UI1, CON-UI2, CON-SIM, CON-STR, CON-FND |
| 4 | Architecture Drift | ADR | ADR-UI1, ADR-UI2, ADR-SIM, ADR-STR, ADR-FND |
| 5 | Test Coverage Gaps | TCG | TCG-UI1, TCG-UI2, TCG-SIM, TCG-STR, TCG-FND |

## Output Files

| Sweep Type | Shard | Output File |
|-----------|-------|-------------|
| Duplication | UI-Screens | `findings/duplication_ui_screens_report.md` |
| Duplication | UI-Framework | `findings/duplication_ui_framework_report.md` |
| Duplication | Simulation | `findings/duplication_simulation_report.md` |
| Duplication | Strategy | `findings/duplication_strategy_report.md` |
| Duplication | Foundation | `findings/duplication_foundation_report.md` |
| Legacy | UI-Screens | `findings/legacy_ui_screens_report.md` |
| Legacy | UI-Framework | `findings/legacy_ui_framework_report.md` |
| Legacy | Simulation | `findings/legacy_simulation_report.md` |
| Legacy | Strategy | `findings/legacy_strategy_report.md` |
| Legacy | Foundation | `findings/legacy_foundation_report.md` |
| Consistency | UI-Screens | `findings/consistency_ui_screens_report.md` |
| Consistency | UI-Framework | `findings/consistency_ui_framework_report.md` |
| Consistency | Simulation | `findings/consistency_simulation_report.md` |
| Consistency | Strategy | `findings/consistency_strategy_report.md` |
| Consistency | Foundation | `findings/consistency_foundation_report.md` |
| Architecture | UI-Screens | `findings/architecture_ui_screens_report.md` |
| Architecture | UI-Framework | `findings/architecture_ui_framework_report.md` |
| Architecture | Simulation | `findings/architecture_simulation_report.md` |
| Architecture | Strategy | `findings/architecture_strategy_report.md` |
| Architecture | Foundation | `findings/architecture_foundation_report.md` |
| Test Coverage | UI-Screens | `findings/test_coverage_ui_screens_report.md` |
| Test Coverage | UI-Framework | `findings/test_coverage_ui_framework_report.md` |
| Test Coverage | Simulation | `findings/test_coverage_simulation_report.md` |
| Test Coverage | Strategy | `findings/test_coverage_strategy_report.md` |
| Test Coverage | Foundation | `findings/test_coverage_foundation_report.md` |
