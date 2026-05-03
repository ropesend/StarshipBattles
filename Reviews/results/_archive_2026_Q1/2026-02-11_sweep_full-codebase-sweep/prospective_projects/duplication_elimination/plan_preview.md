# PROJ-XX: Duplication Elimination

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-XX` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-XX [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. UNK Finding Investigation | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Foundation and AI Deduplication | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Simulation Deduplication | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Strategy Deduplication | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. UI Deduplication | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-02-11
**Active Phase:** Planning
**Last Action:** Project created from sweep findings
**Next Action:** Begin Phase 1 -- investigate UNK findings to determine locations
**Blockers:** None

## Overview
Eliminate all code duplication found in the sweep: copy-pasted functions, near-identical class implementations, duplicated utility logic, and parallel systems doing the same thing. Includes 21 UNK findings that require investigation to locate before fixing. The fix strategy is consistent: extract shared code to a single authoritative location, delete all duplicates, and update callers.

## Goals
- Locate and verify all 21 UNK-prefixed duplication findings
- Extract shared utility functions for repeated patterns (vector math, angle calculation, system lookup)
- Consolidate parallel implementations (ability aggregation, formula evaluation, command handlers)
- Reduce copy-paste duplication in strategy engine command handlers
- Consolidate UI patterns (portrait loading, image scaling, window centering, screenshot capture)
- Ensure every piece of logic has exactly one authoritative implementation

## Scope
**In:**
- All DUP-type findings (38 items with known locations)
- All UNK-type findings (21 items requiring investigation)
- Extracting shared utilities and consolidating parallel implementations

**Out:**
- Legacy dead code removal (separate project -- though some overlap exists)
- Architecture layer violations (separate project)
- New feature development

## Key Files
| Component | File Path |
|-----------|-----------|
| Resource loading duplication | `game/core/resources.py` |
| AI behavior patterns | `game/ai/behaviors.py`, `game/ai/controller.py` |
| Strategy command handlers | `game/strategy/engine/superweapon_order_processor.py` |
| Strategy engine helpers | `game/strategy/engine/harvesting_engine.py` |
| Portrait/image loading | `game/ui/assets/ship_theme_manager.py` |
| ColumnManager duplication | `game/ui/screens/column_manager.py` |
| UI formatting duplication | `game/ui/screens/strategy_ui.py`, `game/ui/screens/strategy_detail_formatter.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All UNK findings investigated and resolved or documented as false positives
- [ ] No copy-pasted functions remain between strategy engine modules
- [ ] No duplicate ColumnManager classes
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
