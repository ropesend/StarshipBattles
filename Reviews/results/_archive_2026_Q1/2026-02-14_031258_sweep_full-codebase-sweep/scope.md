# Sweep Review Scope

## Review Type
Sweep Review (Continuous Improvement Loop - Cycle 6)

## Scope
`game/` (entire production codebase)

## Exclusions
- tests/
- __pycache__/
- .git/
- assets/
- refactor_loop/
- Reviews/
- Projects/

## Agent Configuration
- **Total Agents:** 25 (5 sweep types x 5 shards)
- **Validation Agents:** 5 (1 per shard)
- **Execution Model:** 5 waves of 5 parallel agents, then 1 wave of 5 validators

## Agent Matrix

| Wave | Sweep Type | Prefix | Shard | Output File | Finding ID Pattern |
|------|-----------|--------|-------|-------------|-------------------|
| 1 | Duplication | DUP | UI-Screens (UI1) | `duplication_ui_screens_report.md` | DUP-UI1-XXX |
| 1 | Duplication | DUP | UI-Framework (UI2) | `duplication_ui_framework_report.md` | DUP-UI2-XXX |
| 1 | Duplication | DUP | Simulation (SIM) | `duplication_simulation_report.md` | DUP-SIM-XXX |
| 1 | Duplication | DUP | Strategy (STR) | `duplication_strategy_report.md` | DUP-STR-XXX |
| 1 | Duplication | DUP | Foundation (FND) | `duplication_foundation_report.md` | DUP-FND-XXX |
| 2 | Legacy Holdovers | LEG | UI-Screens (UI1) | `legacy_ui_screens_report.md` | LEG-UI1-XXX |
| 2 | Legacy Holdovers | LEG | UI-Framework (UI2) | `legacy_ui_framework_report.md` | LEG-UI2-XXX |
| 2 | Legacy Holdovers | LEG | Simulation (SIM) | `legacy_simulation_report.md` | LEG-SIM-XXX |
| 2 | Legacy Holdovers | LEG | Strategy (STR) | `legacy_strategy_report.md` | LEG-STR-XXX |
| 2 | Legacy Holdovers | LEG | Foundation (FND) | `legacy_foundation_report.md` | LEG-FND-XXX |
| 3 | Consistency | CON | UI-Screens (UI1) | `consistency_ui_screens_report.md` | CON-UI1-XXX |
| 3 | Consistency | CON | UI-Framework (UI2) | `consistency_ui_framework_report.md` | CON-UI2-XXX |
| 3 | Consistency | CON | Simulation (SIM) | `consistency_simulation_report.md` | CON-SIM-XXX |
| 3 | Consistency | CON | Strategy (STR) | `consistency_strategy_report.md` | CON-STR-XXX |
| 3 | Consistency | CON | Foundation (FND) | `consistency_foundation_report.md` | CON-FND-XXX |
| 4 | Architecture Drift | ADR | UI-Screens (UI1) | `architecture_ui_screens_report.md` | ADR-UI1-XXX |
| 4 | Architecture Drift | ADR | UI-Framework (UI2) | `architecture_ui_framework_report.md` | ADR-UI2-XXX |
| 4 | Architecture Drift | ADR | Simulation (SIM) | `architecture_simulation_report.md` | ADR-SIM-XXX |
| 4 | Architecture Drift | ADR | Strategy (STR) | `architecture_strategy_report.md` | ADR-STR-XXX |
| 4 | Architecture Drift | ADR | Foundation (FND) | `architecture_foundation_report.md` | ADR-FND-XXX |
| 5 | Test Coverage | TCG | UI-Screens (UI1) | `test_coverage_ui_screens_report.md` | TCG-UI1-XXX |
| 5 | Test Coverage | TCG | UI-Framework (UI2) | `test_coverage_ui_framework_report.md` | TCG-UI2-XXX |
| 5 | Test Coverage | TCG | Simulation (SIM) | `test_coverage_simulation_report.md` | TCG-SIM-XXX |
| 5 | Test Coverage | TCG | Strategy (STR) | `test_coverage_strategy_report.md` | TCG-STR-XXX |
| 5 | Test Coverage | TCG | Foundation (FND) | `test_coverage_foundation_report.md` | TCG-FND-XXX |

## Shard Definitions

| Shard Name | ID | Directories |
|------------|-----|-------------|
| UI-Screens | UI1 | `game/ui/screens/`, `game/ui/panels/` |
| UI-Framework | UI2 | `game/ui/` (root files, services/, renderer/, interfaces/, orchestration/, assets/, components/, utils/) |
| Simulation | SIM | `game/simulation/` (all subdirectories) |
| Strategy | STR | `game/strategy/` (all subdirectories) |
| Foundation | FND | `game/core/`, `game/ai/`, `game/research/`, `game/engine/` |
