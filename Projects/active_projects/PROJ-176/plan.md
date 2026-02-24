# PROJ-176: Missing Abstractions & Duplication Elimination

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-176` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-176 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Quick Wins (ValidationResult + CrewRequired + Validator Primitives) | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Foundation (BaseCommandHandler + UITheme) | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Simulation (SimpleMultiplierAbility + SuperweaponMarker) | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-02-23 20:10
**Active Phase:** Planning Complete — Ready for Implementation
**Last Action:** Project created from review findings, plan refined to 3 logical phases
**Next Action:** Run baseline test suite, then begin Phase 1 Task 1.1
**Blockers:** None
**Context for Next Agent:** This project extracts missing abstractions and eliminates duplication across 11 identified clusters. The review identified 3,564 total pattern instances. Phases are ordered by dependency (Cluster 5 first because Clusters 6 and 10 depend on its factory methods). All agent reports are in the review findings/ directory with complete API designs, exact call sites, and before/after examples.

## Overview
Systematic extraction of missing abstractions and elimination of code duplication across 6 clusters (of 11 investigated). Based on deep analysis by 7 review agents that produced concrete API designs with exact call site counts, type signatures, and before/after code examples.

**Source Review:** [2026-02-23_194404_tech-debt_missing-abstractions-duplication-elimination](../../Reviews/results/2026-02-23_194404_tech-debt_missing-abstractions-duplication-elimination/report.md)

**Estimated Total Impact:**
- ~296 lines eliminated, ~90 lines added = **net -206 lines**
- ~120+ call sites improved across ~25 files
- 3 new abstractions created (factory methods, base class, utility functions)

## Goals
- Add `ValidationResult.success()`, `.error()`, `.errors()` factory methods and migrate all 83 call sites
- Fix last legacy value extraction in CrewRequired (1 line)
- Create composable validator primitive functions for strategy validators
- Create `BaseCommandHandler` mixin with fleet/planet resolution helpers for 19 handlers
- Create `SimpleMultiplierAbility` base class for 7 ability classes
- Create `SuperweaponMarker` base class for 6 identical superweapon classes

## Scope
**In Scope:**
- Cluster 5: ValidationResult factory methods (`game/core/validation.py` + 10 consumer files)
- Cluster 3: CrewRequired legacy fix (`game/simulation/components/abilities/crew.py`)
- Cluster 10: Validator primitives (`game/strategy/validation/`)
- Cluster 6: BaseCommandHandler (`game/strategy/engine/command_handlers.py`, `superweapon_command_handlers.py`)
- Cluster 4: SimpleMultiplierAbility (`game/simulation/components/abilities/base.py` + 6 ability files)
- Cluster 4 bonus: SuperweaponMarker (`game/simulation/components/abilities/superweapons.py`)

**Out of Scope:**
- Cluster 1/2: UITheme + DrawingUtils (partially resolved, defer to separate project)
- Cluster 7: JSON Loader Template (working correctly, structural not logical duplication)
- Cluster 8: DTO Serialization (high risk, saves are disposable)
- Cluster 9: Event Handling (inherently screen-specific, abstraction not warranted)
- Cluster 11: Test Fixtures (intentional locality for readability)

## Key Files Reference
| Component | File Path | Class/Function |
|-----------|-----------|----------------|
| ValidationResult | `game/core/validation.py` | `ValidationResult` dataclass |
| CrewRequired | `game/simulation/components/abilities/crew.py:73` | `CrewRequired.__init__` |
| Ability base | `game/simulation/components/abilities/base.py` | `Ability`, `_parse_primary_value()` |
| Command handlers | `game/strategy/engine/command_handlers.py` | `ICommandHandler`, 8 handler classes |
| Superweapon handlers | `game/strategy/engine/superweapon_command_handlers.py` | 11 handler classes |
| Colonize validator | `game/strategy/validation/colonize_validator.py` | `ColonizeValidator` |
| Superweapon validator | `game/strategy/validation/superweapon_validator.py` | `SuperweaponValidator` |
| Transfer validator | `game/strategy/validation/transfer_validator.py` | `TransferValidator` |
| Superweapons | `game/simulation/components/abilities/superweapons.py` | 6 superweapon classes |
| Defense abilities | `game/simulation/components/abilities/defense.py` | `ShieldProjection`, `ShieldRegeneration` |
| Propulsion abilities | `game/simulation/components/abilities/propulsion.py` | `CombatPropulsion`, `ManeuveringThruster`, `StrategicMovement` |
| Crew abilities | `game/simulation/components/abilities/crew.py` | `CrewCapacity`, `LifeSupportCapacity` |

## Decisions Log
See [decisions.md](decisions.md) for full log with rationale.

## Initial Analysis
From 7-agent review swarm (ABS-SIM, ABS-VAL, ABS-UI, ABS-LOAD, CENSUS, DESIGN, PRIORITY):
- **3,564 total pattern instances** counted across 11 duplication clusters
- **Key corrections to prior art:** Cluster 3 is 93% done (1 class remaining), ValidationResult count was underestimated by 2.3x (83 not 36), section headers already consolidated
- **DESIGN agent** assigned mechanisms: factory methods for Cluster 5, composable functions for Cluster 10, mixin for Cluster 6, ABC subclass for Cluster 4
- **PRIORITY agent** verified all counts independently and produced dependency-ordered roadmap

## Swarm Findings Summary
### Architecture
- All proposed abstractions respect layer boundaries (core -> simulation -> strategy)
- ValidationResult is in `game/core/` — factory methods are purely additive
- SimpleMultiplierAbility extends existing `Ability` base in `game/simulation/components/abilities/base.py`
- Validator primitives are pure functions in a new `game/strategy/validation/primitives.py`
- BaseCommandHandler is a mixin in the same module as existing handlers

### Key Patterns to Reuse
- **`_parse_primary_value()`**: `game/simulation/components/abilities/base.py:127-140` — already exists, 10/11 classes migrated
- **`AbilityStatBinding`**: `game/simulation/components/abilities/base.py` — class-attribute-driven stat binding
- **`ICommandHandler` Protocol**: `game/strategy/engine/command_handlers.py:25` — existing protocol all handlers implement
- **`CommandHandlerRegistry`**: `game/strategy/engine/command_handlers.py:41` — existing registry pattern

### Risks Identified
1. **SimpleMultiplierAbility uses setattr/getattr** — typos in class attribute strings fail silently. Mitigation: `__init_subclass__` validation that all required class attributes are set and non-empty.
2. **943 ability-related tests** — simulation-core changes need extra care. Mitigation: migrate one class at a time, full test suite after each.
3. **CrewRequired may use 'amount' key** — need to grep JSON data before dropping alias. Mitigation: verify component JSON first.

---

## Phases

### Phase 1: Quick Wins [Simple]
**Objective:** Add ValidationResult factory methods + migrate all 83 call sites, fix CrewRequired, create validator primitives
**Status:** Not Started
**Estimated Time:** ~4-6 hours
**Net Lines Saved:** ~71
**See:** [phase_1_checklist.md](phase_1_checklist.md)

### Phase 2: Foundation Abstractions [Medium]
**Objective:** Create BaseCommandHandler mixin with resolution helpers, migrate 19 handlers
**Status:** Not Started
**Estimated Time:** ~1 day
**Net Lines Saved:** ~53
**Dependencies:** Phase 1 complete (uses `ValidationResult.error()` in helpers)
**See:** [phase_2_checklist.md](phase_2_checklist.md)

### Phase 3: Simulation Abstractions [Medium]
**Objective:** Create SimpleMultiplierAbility base class + migrate 7 classes, create SuperweaponMarker + migrate 6 classes
**Status:** Not Started
**Estimated Time:** ~2-3 days
**Net Lines Saved:** ~82
**Dependencies:** None (independent of Phases 1-2, but ordered last due to higher risk)
**See:** [phase_3_checklist.md](phase_3_checklist.md)

---

## Verification Checklist

### Project Start (REQUIRED)
- [ ] Run full test suite: `pytest tests/ -n 12` — all tests pass (establishes baseline)
- [ ] Record test count baseline

### After Each Phase
- [ ] Run `pytest tests/ -n 12` — all tests pass
- [ ] Verify no new warnings introduced

### Final Verification
- [ ] Run full test suite: `pytest tests/ -n 12` — all tests pass
- [ ] Run simulation tests: `pytest simulation_tests/ -n 4` — all pass
- [ ] Verify test count has not decreased
- [ ] Spot-check: ValidationResult.success() used consistently (no bare `ValidationResult()`)
- [ ] Spot-check: No handler classes still have inline fleet resolution
- [ ] Spot-check: All 7 migrated abilities inherit from SimpleMultiplierAbility

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] All Phase 1 tasks checked off
- [ ] All Phase 2 tasks checked off
- [ ] All Phase 3 tasks checked off
- [ ] All tests passing (`pytest tests/ -n 12`)
- [ ] Simulation tests passing (`pytest simulation_tests/ -n 4`)
- [ ] Audit passed (no significant issues)
- [ ] User verified

## Related Documents
- [design.md](design.md) — Architecture analysis and API designs from review agents
- [decisions.md](decisions.md) — Full decisions log
- [Source Review Report](../../Reviews/results/2026-02-23_194404_tech-debt_missing-abstractions-duplication-elimination/report.md)
- [ABS-SIM Report](../../Reviews/results/2026-02-23_194404_tech-debt_missing-abstractions-duplication-elimination/findings/ABS-SIM_report.md) — SimpleMultiplierAbility design, full migration table
- [ABS-VAL Report](../../Reviews/results/2026-02-23_194404_tech-debt_missing-abstractions-duplication-elimination/findings/ABS-VAL_report.md) — ValidationResult + BaseCommandHandler + Validator primitives
- [PRIORITY Report](../../Reviews/results/2026-02-23_194404_tech-debt_missing-abstractions-duplication-elimination/findings/PRIORITY_report.md) — Dependency graph, risk matrix, phased roadmap
