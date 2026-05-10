# Review Scope: DI Inconsistency - Strategy Layer

## Metadata
- **Date:** 2026-02-27
- **Type:** General Review (DI-focused)
- **Description:** Audit all `get_default_registry_provider()` usage to classify violations vs. legitimate entry-point usage

## Scope Definition

### Target
- **22 production files** in `game/` using `get_default_registry_provider()`
- **17 test files** in `tests/` and `simulation_tests/`
- Focus: Strategy layer primary offenders + full codebase scan

### Primary Offenders (from deep dive report)
1. `game/strategy/engine/turn_engine.py`
2. `game/strategy/data/ship_instance.py`
3. `game/strategy/data/fleet_capability_calculator.py`
4. `game/strategy/facade/strategy_session_facade.py`
5. `game/strategy/engine/empire_economy_calculator.py`

### Priorities
- DI violations: `get_default_registry_provider()` fallback patterns
- Test isolation: Whether tests properly inject or rely on global state
- Severity classification of each usage

### Exclusions
- Review/project archive files
- Documentation-only references
- `game/core/registry.py` (definition site)

## Agent Configuration
**Agent Count:** 5

### Selected Agents
| Agent | Role | Output File |
|-------|------|-------------|
| DI Strategy Analyst | Deep analysis of 5 primary strategy offenders | `findings/di_strategy_report.md` |
| DI Simulation Analyst | Analysis of simulation layer DI usage | `findings/di_simulation_report.md` |
| DI UI Layer Analyst | Analysis of UI layer DI usage (9 files) | `findings/di_ui_report.md` |
| Test Isolation Analyst | Test files relying on global state | `findings/test_isolation_report.md` |
| Architecture Reviewer | Cross-cutting DI architecture assessment | `findings/architecture_report.md` |
