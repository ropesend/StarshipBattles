# PROJ-108: Duplication Elimination

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-108` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-108 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. SingletonMeta Foundation | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Convert Singletons | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. ComponentInspector + AI Utils | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Migrate Strategy + AI Callers | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Simulation Deduplication | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. UI Deduplication | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-02-11
**Active Phase:** Phase 1 Complete
**Last Action:** Created SingletonMeta metaclass with thread-safe double-checked locking, 14 comprehensive tests
**Next Action:** Start Phase 2 (Convert Singletons to use SingletonMeta)
**Blockers:** None

## Overview
Eliminate code duplication identified during the 2026-02-10 full-codebase sweep. After deep-dive analysis, 16 of 40 findings are in scope (10 CRITICAL, 6 MAJOR). The remaining 24 were triaged as low-ROI, false positives, or deferred to other projects. See [design.md](design.md) for full triage.

## Goals
- Extract shared SingletonMeta metaclass for 7 singleton implementations (~175 lines)
- Create ComponentInspector utility consolidating 8 duplicate layer-iteration patterns (~90 lines)
- Merge duplicated ability aggregation logic into single function (~60 lines)
- Consolidate modifier validation to eliminate drift risk
- Extract BaseGallery and BaseColumnManager for UI (~210 lines)
- Extract shared AI combat utility functions (~64 lines)
- **Total estimated deduplication: ~600+ lines**

## Scope
**In (16 findings):**
- DUP-FND-001: Singleton pattern (7 classes) -> SingletonMeta metaclass
- DUP-FND-002: Position/rotation helpers -> AI combat utils
- DUP-FND-004: HP/PDC utilities -> AI combat utils
- DUP-SIM-001: Ability aggregation duplication -> merge functions
- DUP-SIM-002: Resource consumption extraction -> utility function
- DUP-SIM-003: Modifier validation duplication -> delegation
- DUP-STR-001: Component ability extraction (3 validators) -> ComponentInspector
- DUP-STR-002: Component layer iteration (6 files) -> ComponentInspector
- DUP-STR-003: Find ship with ability (2 validators) -> ComponentInspector
- DUP-STR-006: Ship component inspection -> ComponentInspector
- DUP-UI1-001: ColumnManager duplication -> BaseColumnManager
- DUP-UI1-002: Value formatting -> shared utility
- DUP-UI1-003: Resource formatting -> verify and consolidate
- DUP-UI1-005: Gallery duplication -> BaseGallery
- DUP-UI2-004: UI singletons -> SingletonMeta (handled in Phase 2)
- DUP-SIM-005: Component status checking -> utility (deferred to Phase 5)

**Out (24 findings - see design.md for full rationale):**
- DUP-FND-003: JSON loading (15 files, high blast radius, low per-file ROI)
- DUP-FND-005/006: Minor findings
- DUP-SIM-004: Ability retrieval fallback (complex, test infrastructure)
- DUP-SIM-006-010: Intentional variation or low ROI
- DUP-STR-004/005/007-009: Low ROI or intentional patterns
- DUP-UI2-001: UI service init (only ~6 lines per class)
- DUP-UI2-002/003/005: Low ROI or deferred to god-class projects
- DUP-UI1-004/006-010: False positives or low ROI
- God class decomposition (PROJ-86/87/88/89)
- Architecture violations (PROJ-106)

## Key Files
| Component | File Path |
|-----------|-----------|
| SingletonMeta | `game/core/singleton.py` (NEW) |
| ComponentInspector | `game/strategy/services/component_inspector.py` (NEW) |
| AI combat utils | `game/ai/combat_utils.py` (NEW) |
| Ability aggregator | `game/simulation/entities/ability_aggregator.py` |
| Modifier schema | `game/simulation/components/modifier_schema.py` |
| Modifier effects | `game/simulation/components/modifier_effects.py` |
| Base gallery | `game/ui/panels/base_gallery.py` (NEW) |
| Base column mgr | `game/ui/screens/base_column_manager.py` (NEW) |
| Value formatting | `game/ui/screens/test_lab/formatting_utils.py` (NEW) |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- **Source sweep:** `Reviews/results/2026-02-10_sweep_full-codebase-sweep/findings/duplication_*.md`

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (8164+ baseline)
- [ ] No duplicate patterns remain in targeted areas
- [ ] Audit passed
- [ ] User verified
