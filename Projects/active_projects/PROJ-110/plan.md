# PROJ-110: Test Coverage - Core Systems

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-110` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-110 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Foundation - CRITICAL + MAJOR | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Simulation - CRITICAL + MAJOR | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Strategy - CRITICAL + MAJOR | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. All Layers - MINOR | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-11
**Active Phase:** 3 (Strategy - CRITICAL + MAJOR)
**Last Action:** Phase 2 complete (+222 tests: registry_loader 16, physics_constants 11, battle_config 23, component_constants 22, modifier_schema 57, modifier_effects 31, markers 16, stat_keys 22, modifiers 24)
**Next Action:** Begin Phase 3, Task 3.1 (Radiation Physics tests)
**Blockers:** None

## Overview
Address test coverage gaps in core systems: Foundation (game/core/, game/ai/, game/research/, game/engine/), Simulation (game/simulation/), and Strategy (game/strategy/). The 2026-02-10 sweep identified 54 test coverage findings across these layers, including completely untested critical modules, missing error path tests, and weak assertion patterns. Expected impact: ~542 new tests (Phase 1: ~157, Phase 2: ~151, Phase 3: ~139, Phase 4: ~95).

## Goals
- Add unit tests for all untested critical-path modules
- Cover error paths and edge cases in existing test suites
- Ensure all public APIs have explicit test coverage
- Verify serialization round-trips for data model classes
- Add boundary value tests for numerical calculations

## Scope
**In:**
- Foundation findings: TCG-FND-001 through TCG-FND-021
- Simulation findings: TCG-SIM-001 through TCG-SIM-018
- Strategy findings: TCG-STR-001 through TCG-STR-015

**Out:**
- UI test coverage (PROJ-111)
- Integration test gaps (separate effort)
- Performance testing

## Source: Sweep Findings

### Foundation - CRITICAL (3 findings)

#### TCG-FND-001: Hex Math Module - No Unit Tests [CRITICAL]
**Location:** `game/core/hex_math.py` (250 lines)
**Issue:** 8 public functions with zero unit tests. Only integration tests exist.
**Tests needed:** 15-20 test cases covering edge cases (negative coords, boundary conditions, serialization round-trip)
**Effort:** Medium

#### TCG-FND-002: AI Behaviors Module - No Unit Tests [CRITICAL]
**Location:** `game/ai/behaviors.py` (700+ lines)
**Issue:** 11 behavior classes lack dedicated unit tests.
**Tests needed:** Unit tests for each behavior: initialization, state transitions, target death handling
**Effort:** Complex

#### TCG-FND-003: Registry Loading - No Error Path Tests [CRITICAL]
**Location:** `game/core/resources.py` (143 lines)
**Issue:** Error paths (FileNotFoundError, json.JSONDecodeError, PermissionError) not tested.
**Effort:** Medium

### Foundation - MAJOR (7 findings)

#### TCG-FND-004: Core Input Mapper - Incomplete Coverage [MAJOR]
**Location:** `game/core/input_mapper.py` (300+ lines)
**Issue:** Missing conflict detection, context overlap, modifier handling tests.
**Effort:** Medium

#### TCG-FND-005: Paths Module - No Unit Tests [MAJOR]
**Location:** `game/core/paths.py` (134 lines)
**Effort:** Medium

#### TCG-FND-006: Screenshot Manager - No Unit Tests [MAJOR]
**Location:** `game/core/screenshot_manager.py` (219 lines)
**Effort:** Medium

#### TCG-FND-007: AI Controller - Incomplete Coverage [MAJOR]
**Location:** `game/ai/controller.py` (500+ lines)
**Effort:** Medium

#### TCG-FND-008: Strategy Manager - Singleton State [MAJOR]
**Location:** `game/ai/strategy_manager.py` (200+ lines)
**Effort:** Medium

#### TCG-FND-009: Target Evaluator - Rule Edge Cases [MAJOR]
**Location:** `game/ai/target_evaluator.py` (500+ lines)
**Effort:** Medium

#### TCG-FND-010: Research Service - Turn Processing Edge Cases [MAJOR]
**Location:** `game/research/systems/research_service.py` (180+ lines)
**Effort:** Medium

### Foundation - MINOR (11 findings)
- TCG-FND-011: Vector2 edge cases (Simple)
- TCG-FND-012: Logger - no unit tests (Simple)
- TCG-FND-013: Profiling coverage gaps (Simple)
- TCG-FND-014: Validation error boundary tests (Simple)
- TCG-FND-015: Error codes enum coverage (Simple)
- TCG-FND-016: JSON utils edge cases (Simple)
- TCG-FND-017: Configuration edge cases (Simple)
- TCG-FND-018: AI interfaces adapter coverage (Simple)
- TCG-FND-019: Research tracker serialization edge cases (Simple)
- TCG-FND-020: Engine physics floating point edge cases (Simple)
- TCG-FND-021: Spatial grid query edge cases (Simple)

### Simulation - CRITICAL (4 findings)

#### TCG-SIM-001: Registry Loader Service Untested [CRITICAL]
**Location:** `game/simulation/services/registry_loader.py`
**Effort:** Medium

#### TCG-SIM-002: Physics Constants Untested [CRITICAL]
**Location:** `game/simulation/physics_constants.py`
**Effort:** Simple

#### TCG-SIM-003: Battle Configuration Untested [CRITICAL]
**Location:** `game/simulation/battle_config.py`
**Effort:** Simple

#### TCG-SIM-004: Component Status/Modifier Constants Untested [CRITICAL]
**Location:** `game/simulation/components/component_constants.py`
**Effort:** Simple

### Simulation - MAJOR (5 findings)

#### TCG-SIM-005: Modifier Schema Validation Untested [MAJOR]
**Location:** `game/simulation/components/modifier_schema.py`
**Effort:** Medium

#### TCG-SIM-006: Modifier Effects Evaluation Untested [MAJOR]
**Location:** `game/simulation/components/modifier_effects.py`
**Effort:** Medium

#### TCG-SIM-007: Marker Abilities Untested [MAJOR]
**Location:** `game/simulation/components/abilities/markers.py`
**Effort:** Simple

#### TCG-SIM-008: Stat Keys and Ability Bindings Untested [MAJOR]
**Location:** `game/simulation/components/abilities/stat_keys.py`
**Effort:** Simple

#### TCG-SIM-009: Modifier Application Logic Untested [MAJOR]
**Location:** `game/simulation/components/modifiers.py`
**Effort:** Simple

### Simulation - MINOR (9 findings)
- TCG-SIM-010 through TCG-SIM-018 (Simple to Medium)

### Strategy - CRITICAL (3 findings)

#### TCG-STR-001: Core Radiation Physics Untested [CRITICAL]
**Location:** `game/strategy/data/physics.py`
**Effort:** Simple

#### TCG-STR-002: Strategy Session Facade - No Unit Tests [CRITICAL]
**Location:** `game/strategy/facade/strategy_session_facade.py` (450 LOC)
**Effort:** Complex

#### TCG-STR-003: Galaxy Generation Placement/Classification [CRITICAL]
**Location:** `game/strategy/generation/placement_strategies.py`, `game/strategy/generation/region_classifier.py`
**Effort:** Complex

### Strategy - MAJOR (5 findings)

#### TCG-STR-004: Stars Module - No Dedicated Unit Tests [MAJOR]
**Location:** `game/strategy/data/stars.py` (560 LOC)
**Effort:** Medium

#### TCG-STR-005: Planet Naming Untested [MAJOR]
**Location:** `game/strategy/data/planet_naming.py` (86 LOC)
**Effort:** Simple

#### TCG-STR-006: Engine Interfaces - No Contract Tests [MAJOR]
**Location:** `game/strategy/interfaces/engines.py` (470 LOC)
**Effort:** Medium

#### TCG-STR-007: QuickstartBuilder - No Unit Tests [MAJOR]
**Location:** `game/strategy/quickstart_builder.py` (299 LOC)
**Effort:** Medium

#### TCG-STR-008: Configuration Classes Untested [MAJOR]
**Location:** classification_config.py, race_point_budget.py, homeworld_presets.py
**Effort:** Simple

### Strategy - MINOR (7 findings)
- TCG-STR-009 through TCG-STR-015 (Simple to Medium)

## Key Files
| Component | File Path |
|-----------|-----------|
| Hex math | `game/core/hex_math.py` |
| AI behaviors | `game/ai/behaviors.py` |
| Resources | `game/core/resources.py` |
| Physics constants | `game/simulation/physics_constants.py` |
| Battle config | `game/simulation/battle_config.py` |
| Modifier system | `game/simulation/components/modifier_*.py` |
| Strategy facade | `game/strategy/facade/strategy_session_facade.py` |
| Galaxy generation | `game/strategy/generation/placement_strategies.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [phase_1_checklist.md](phase_1_checklist.md) - Foundation CRITICAL + MAJOR (~157 tests)
- [phase_2_checklist.md](phase_2_checklist.md) - Simulation CRITICAL + MAJOR (~151 tests)
- [phase_3_checklist.md](phase_3_checklist.md) - Strategy CRITICAL + MAJOR (~139 tests)
- [phase_4_checklist.md](phase_4_checklist.md) - All Layers MINOR (~95 tests)
- **Source sweep:** `Reviews/results/2026-02-10_sweep_full-codebase-sweep/findings/test_coverage_{foundation,simulation,strategy}_report.md`

## Verification
- [ ] All phase checklists complete
- [ ] All new tests passing
- [ ] Coverage improved for all targeted modules
- [ ] Audit passed
- [ ] User verified
