# Test Coverage Review Scope

## Review Metadata
- **Date:** 2026-01-23
- **Type:** Test Coverage Review
- **Review Folder:** 2026-01-23_test-coverage_full-codebase-coverage-gaps

## Scope Definition

### Target
- **Coverage:** Entire codebase
- **Exclusions:** Simulation tests (simulation_tests/ directory)

### Test Types in Scope
- Unit tests (tests/unit/)
- Integration tests (tests/integration/)
- Strategy tests (tests/strategy/)
- Repro issue tests (tests/repro_issues/)
- UI tests (tests/ui/)

### Focus Areas
1. **Missing tests (coverage gaps)** - Code without adequate test coverage
2. **Weak tests** - Tests that pass but may not effectively catch bugs

### Priority
- Equal attention to all modules
- No specific modules prioritized over others

### Known Concerns
- Tests may pass but have weak assertions
- Concern about tests that can't fail

## Codebase Analysis

### Test Suite Statistics
- **Total Test Files:** ~253 (excluding simulation tests)
- **Test Functions:** 150+
- **Framework:** pytest with parallel execution (4 workers)

### Test Directory Structure
```
tests/
├── unit/           (188 files - main test suite)
├── strategy/       (19 files)
├── integration/    (3 files)
├── repro_issues/   (27 files)
├── ui/             (8 files)
├── regression/     (1 file)
├── infrastructure/ (test utilities)
├── fixtures/       (test data)
└── performance/    (perf utilities)
```

### Source Modules to Analyze
| Module | Files | Purpose |
|--------|-------|---------|
| simulation | 49 | Core game engine |
| ui | 53 | UI rendering |
| strategy | 30 | Strategy layer |
| research | 11 | Tech trees |
| core | 10 | Global utilities |
| ai | 5 | AI behaviors |
| engine | 4 | Engine utilities |
| assets | 1 | Asset management |

## Agent Configuration

### Total Agents: 22

### Core Agents
| Agent | Role | Finding Prefix |
|-------|------|----------------|
| Test Coverage Analyst | Overall coverage gaps | TC |
| Test Behavior Analyst | Weak tests, assertion quality | TB |
| Architecture Reviewer | Test architecture patterns | AR |
| Code Quality Analyst | Test code maintainability | CQ |

### Module Specialist Agents (12)
| Agent | Focus Area | Finding Prefix |
|-------|------------|----------------|
| MOD-SIM | Simulation module (49 source files) | MOD-SIM |
| MOD-UI | UI module (53 source files) | MOD-UI |
| MOD-STR | Strategy layer (30 source files) | MOD-STR |
| MOD-RES | Research/tech trees (11 source files) | MOD-RES |
| MOD-CORE | Core utilities (10 source files) | MOD-CORE |
| MOD-AI | AI behaviors (5 source files) | MOD-AI |
| MOD-CMB | Combat systems | MOD-CMB |
| MOD-BLD | Builder/editor systems | MOD-BLD |
| MOD-SYS | Physics/collision systems | MOD-SYS |
| MOD-ENT | Entity/component tests | MOD-ENT |
| MOD-INT | Integration tests | MOD-INT |
| MOD-SVC | Services layer | MOD-SVC |

### Deep-Dive Agents (6)
| Agent | Focus Area | Finding Prefix |
|-------|------------|----------------|
| Edge Case Hunter | Untested edge cases | ECH |
| Error Path Analyst | Untested error conditions | EPA |
| Public API Mapper | Untested public interfaces | PAM |
| Mock Overuse Detector | Tests hiding bugs via mocks | MOD |
| Assertion Quality Auditor | Weak/missing assertions | AQA |
| Test Isolation Checker | Cross-test dependencies | TIC |

## Expected Outputs
- Individual agent reports in `findings/` directory
- Compiled `report.md` with prioritized coverage gaps
- Module-by-module coverage assessment
- Prioritized list of tests to add
