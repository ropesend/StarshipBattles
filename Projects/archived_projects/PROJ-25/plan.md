# PROJ-25: Consolidate Dual AI Implementations

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-25` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-25 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Preparation | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Migrate UI Consumers | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Migrate Test Files | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Delete Legacy Code | Complete | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-01-27
**Active Phase:** AUDIT PASSED
**Last Action:** Audit Cycle 1 passed - all code changes verified by investigation agents
**Next Action:** User verification required (launch game, verify AI strategy dropdowns, run battle)
**Blockers:** None
**Context for Next Agent:** Project is audit-complete. User needs to verify UI manually and close.

## Overview
After PROJ-24 completes the IControllable interface migration, consolidate the two parallel AI implementations into a single canonical version (`game/ai/controller.py`), eliminating code duplication in `game/ai/core/`. This is a code cleanup project - no behavior changes, only import path migrations.

## Goals
- Eliminate duplicate AI implementation in `game/ai/core/`
- Migrate all consumers to use the modern, refactored simulation layer
- Move root-level test files into proper test directory structure
- Reduce maintenance burden by having single source of truth for AI code

## Scope
**In:**
- Migrate 4 UI files to use `StrategyManager.instance().strategies`
- Update ~7 test file imports
- Move `test_formation_*.py` files to `tests/integration/`
- Delete `game/ai/core/` directory

**Out:**
- Changing AI behavior or logic (100% feature parity confirmed)
- Modifying the simulation layer implementation
- Any work until PROJ-24 is complete

## Key Files
| Component | File Path | Action |
|-----------|-----------|--------|
| Canonical AI | `game/ai/controller.py` | Keep (target) |
| Canonical Behaviors | `game/ai/behaviors.py` | Keep (target) |
| Strategy Manager | `game/ai/strategy_manager.py` | Keep (import source) |
| Legacy AI | `game/ai/core/system.py` | **DELETE** |
| Legacy Behaviors | `game/ai/core/behaviors.py` | **DELETE** |
| UI - Battle | `game/ui/screens/battle.py` | Remove unused import |
| UI - Setup | `game/ui/screens/setup.py` | Update import |
| UI - Panels | `game/ui/hud/panels.py` | Update import |
| UI - Builder | `game/ui/screens/builder/right_panel.py` | Update import |

## Decisions
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-27 | Use simulation layer as canonical | Modern, refactored, modular, documented, uses ShipControllableAdapter |
| 2026-01-27 | Delete `game/ai/core/` entirely | No compatibility shim needed; direct migration is cleaner |
| 2026-01-27 | Use `StrategyManager.instance().strategies` | No magic proxy; explicit access pattern |
| 2026-01-27 | Move root test files to tests/integration/ | Consistent test organization |

## Related Documents
- [design.md](design.md) - Architecture analysis and swarm findings
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [x] All phase checklists complete
- [ ] All UI dropdowns show correct strategy names (manual test) - **pending user**
- [ ] Battle AI functions correctly (run a battle manually) - **pending user**
- [x] All tests pass: `pytest tests/` (4594 passed, 1 skipped)
- [x] No imports from `game.ai.core` exist: `grep -r "game.ai.core" --include="*.py"`
- [x] `game/ai/core/` directory deleted
- [x] Root-level test files moved to `tests/integration/`

## Estimated Effort
- Phase 1: ~15 min (verification only)
- Phase 2: ~30 min (4 UI files)
- Phase 3: ~30 min (5+ test files + relocate 2)
- Phase 4: ~15 min (delete + verify)
- **Total: ~1.5 hours**

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | 2026-01-27 | No significant issues | PASSED |

### Audit Cycle 1 Details
- **Auditor:** Skeptical Reviewer
- **Tests:** 4594 passed, 1 skipped (matches Phase 1 baseline)
- **Investigations:** 5 parallel agents verified all claims
  - No `game.ai.core` imports in executable code
  - `game/ai/core/` directory confirmed deleted
  - Test files relocated to `tests/integration/`
  - All 5 UI files use correct imports
  - All 4 test files use correct imports
- **Manual Items:** UI verification appropriately deferred to user

## Completion Checklist
- [x] All tasks checked off
- [x] All tests passing
- [x] Regression tests passing
- [x] Audit passed (no significant issues)
- [ ] User verified
