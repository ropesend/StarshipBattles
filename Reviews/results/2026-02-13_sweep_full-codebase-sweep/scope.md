# Sweep Review Scope

## Review Type
Sweep Review (Continuous Improvement Loop - Cycle 2)

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
- **Total Agents:** 25 (5 sweep types × 5 shards)
- **Execution Model:** 5 waves of 5 parallel agents
- **Validation:** 5 skeptical validator agents (1 per shard)

## Shard Definitions

| Shard Name | ID Suffix | Directories |
|------------|-----------|-------------|
| UI-Screens | UI1 | `game/ui/screens/`, `game/ui/panels/` |
| UI-Framework | UI2 | `game/ui/` (root files, services/, renderer/, interfaces/, orchestration/, assets/, components/, utils/) |
| Simulation | SIM | `game/simulation/` (all subdirectories) |
| Strategy | STR | `game/strategy/` (all subdirectories) |
| Foundation | FND | `game/core/`, `game/ai/`, `game/research/`, `game/engine/` |

## Agent Matrix

| Wave | Sweep Type | Prefix | Shard | Output File | Finding ID Format |
|------|-----------|--------|-------|-------------|-------------------|
| 1 | Duplication & Fragmentation | DUP | UI-Screens | `duplication_ui_screens_report.md` | DUP-UI1-XXX |
| 1 | Duplication & Fragmentation | DUP | UI-Framework | `duplication_ui_framework_report.md` | DUP-UI2-XXX |
| 1 | Duplication & Fragmentation | DUP | Simulation | `duplication_simulation_report.md` | DUP-SIM-XXX |
| 1 | Duplication & Fragmentation | DUP | Strategy | `duplication_strategy_report.md` | DUP-STR-XXX |
| 1 | Duplication & Fragmentation | DUP | Foundation | `duplication_foundation_report.md` | DUP-FND-XXX |
| 2 | Legacy System Holdovers | LEG | UI-Screens | `legacy_ui_screens_report.md` | LEG-UI1-XXX |
| 2 | Legacy System Holdovers | LEG | UI-Framework | `legacy_ui_framework_report.md` | LEG-UI2-XXX |
| 2 | Legacy System Holdovers | LEG | Simulation | `legacy_simulation_report.md` | LEG-SIM-XXX |
| 2 | Legacy System Holdovers | LEG | Strategy | `legacy_strategy_report.md` | LEG-STR-XXX |
| 2 | Legacy System Holdovers | LEG | Foundation | `legacy_foundation_report.md` | LEG-FND-XXX |
| 3 | Consistency Violations | CON | UI-Screens | `consistency_ui_screens_report.md` | CON-UI1-XXX |
| 3 | Consistency Violations | CON | UI-Framework | `consistency_ui_framework_report.md` | CON-UI2-XXX |
| 3 | Consistency Violations | CON | Simulation | `consistency_simulation_report.md` | CON-SIM-XXX |
| 3 | Consistency Violations | CON | Strategy | `consistency_strategy_report.md` | CON-STR-XXX |
| 3 | Consistency Violations | CON | Foundation | `consistency_foundation_report.md` | CON-FND-XXX |
| 4 | Architecture Drift | ADR | UI-Screens | `architecture_ui_screens_report.md` | ADR-UI1-XXX |
| 4 | Architecture Drift | ADR | UI-Framework | `architecture_ui_framework_report.md` | ADR-UI2-XXX |
| 4 | Architecture Drift | ADR | Simulation | `architecture_simulation_report.md` | ADR-SIM-XXX |
| 4 | Architecture Drift | ADR | Strategy | `architecture_strategy_report.md` | ADR-STR-XXX |
| 4 | Architecture Drift | ADR | Foundation | `architecture_foundation_report.md` | ADR-FND-XXX |
| 5 | Test Coverage Gaps | TCG | UI-Screens | `test_coverage_ui_screens_report.md` | TCG-UI1-XXX |
| 5 | Test Coverage Gaps | TCG | UI-Framework | `test_coverage_ui_framework_report.md` | TCG-UI2-XXX |
| 5 | Test Coverage Gaps | TCG | Simulation | `test_coverage_simulation_report.md` | TCG-SIM-XXX |
| 5 | Test Coverage Gaps | TCG | Strategy | `test_coverage_strategy_report.md` | TCG-STR-XXX |
| 5 | Test Coverage Gaps | TCG | Foundation | `test_coverage_foundation_report.md` | TCG-FND-XXX |
