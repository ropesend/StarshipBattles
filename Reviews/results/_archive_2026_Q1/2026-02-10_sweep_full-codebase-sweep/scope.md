# Sweep Review: Full Codebase Sweep

## Review Type
Sweep Review (5 sweep types x 5 module shards = 25 agents)

## Scope
`game/` (entire production codebase)

**Exclusions:** tests/, __pycache__/, .git/, assets/, refactor_loop/, Reviews/, Projects/

## Execution Model
5 waves of 5 parallel agents each (25 total agents)

## Agent Matrix

| # | Sweep Type | Shard | Output File | Finding ID Prefix |
|---|-----------|-------|-------------|-------------------|
| 1 | Duplication & Fragmentation | UI-Screens | `duplication_ui_screens_report.md` | DUP-UI1 |
| 2 | Duplication & Fragmentation | UI-Framework | `duplication_ui_framework_report.md` | DUP-UI2 |
| 3 | Duplication & Fragmentation | Simulation | `duplication_simulation_report.md` | DUP-SIM |
| 4 | Duplication & Fragmentation | Strategy | `duplication_strategy_report.md` | DUP-STR |
| 5 | Duplication & Fragmentation | Foundation | `duplication_foundation_report.md` | DUP-FND |
| 6 | Legacy System Holdovers | UI-Screens | `legacy_ui_screens_report.md` | LEG-UI1 |
| 7 | Legacy System Holdovers | UI-Framework | `legacy_ui_framework_report.md` | LEG-UI2 |
| 8 | Legacy System Holdovers | Simulation | `legacy_simulation_report.md` | LEG-SIM |
| 9 | Legacy System Holdovers | Strategy | `legacy_strategy_report.md` | LEG-STR |
| 10 | Legacy System Holdovers | Foundation | `legacy_foundation_report.md` | LEG-FND |
| 11 | Consistency Violations | UI-Screens | `consistency_ui_screens_report.md` | CON-UI1 |
| 12 | Consistency Violations | UI-Framework | `consistency_ui_framework_report.md` | CON-UI2 |
| 13 | Consistency Violations | Simulation | `consistency_simulation_report.md` | CON-SIM |
| 14 | Consistency Violations | Strategy | `consistency_strategy_report.md` | CON-STR |
| 15 | Consistency Violations | Foundation | `consistency_foundation_report.md` | CON-FND |
| 16 | Architecture Drift | UI-Screens | `architecture_ui_screens_report.md` | ADR-UI1 |
| 17 | Architecture Drift | UI-Framework | `architecture_ui_framework_report.md` | ADR-UI2 |
| 18 | Architecture Drift | Simulation | `architecture_simulation_report.md` | ADR-SIM |
| 19 | Architecture Drift | Strategy | `architecture_strategy_report.md` | ADR-STR |
| 20 | Architecture Drift | Foundation | `architecture_foundation_report.md` | ADR-FND |
| 21 | Test Coverage Gaps | UI-Screens | `test_coverage_ui_screens_report.md` | TCG-UI1 |
| 22 | Test Coverage Gaps | UI-Framework | `test_coverage_ui_framework_report.md` | TCG-UI2 |
| 23 | Test Coverage Gaps | Simulation | `test_coverage_simulation_report.md` | TCG-SIM |
| 24 | Test Coverage Gaps | Strategy | `test_coverage_strategy_report.md` | TCG-STR |
| 25 | Test Coverage Gaps | Foundation | `test_coverage_foundation_report.md` | TCG-FND |

## Shard Definitions

| Shard Name | ID | Directories |
|------------|-----|-------------|
| UI-Screens | UI1 | `game/ui/screens/`, `game/ui/panels/` |
| UI-Framework | UI2 | `game/ui/` (root files, services/, renderer/, interfaces/, orchestration/, assets/, components/, utils/) |
| Simulation | SIM | `game/simulation/` (all subdirectories) |
| Strategy | STR | `game/strategy/` (all subdirectories) |
| Foundation | FND | `game/core/`, `game/ai/`, `game/research/`, `game/engine/` |

## Wave Schedule

1. **Wave 1:** Duplication & Fragmentation (5 agents)
2. **Wave 2:** Legacy System Holdovers (5 agents)
3. **Wave 3:** Consistency Violations (5 agents)
4. **Wave 4:** Architecture Drift (5 agents)
5. **Wave 5:** Test Coverage Gaps (5 agents)
