# PROJ-166: Make RaceThemeGallery Extend BaseGallery

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-166` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-166 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Normalize BaseGallery to 2-tuples | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Refactor RaceThemeGallery to extend BaseGallery | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Update tests and verify | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-02-23
**Active Phase:** Phase 2 — Refactor RaceThemeGallery
**Last Action:** Phase 1 complete — BaseGallery normalized to 2-tuples
**Next Action:** Begin Phase 2 — Refactor RaceThemeGallery to extend BaseGallery
**Blockers:** None
**Context for Next Agent:** BaseGallery.asset_buttons now stores 2-tuples (btn, asset_id) instead of 3-tuples. UIImage still created for visual rendering but not stored. All 30 gallery tests passing. Ready for Phase 2.

## Overview
RaceThemeGallery was missed during PROJ-108 Phase 6 when RacePortraitGallery and RaceFlagGallery were refactored to extend BaseGallery. This project completes that work by normalizing BaseGallery's data model from 3-tuples `(btn, img, id)` to 2-tuples `(btn, id)`, making `_create_content()` hookable for layout variants, and then making RaceThemeGallery extend BaseGallery.

This resolves 4 verified duplication findings from the DRY review (UI CQ-101, CQ-107, CQ-108, CQ-110) in a single refactoring.

## Goals
- Make RaceThemeGallery extend BaseGallery, eliminating 4 duplicated methods
- Normalize BaseGallery's `asset_buttons` to 2-tuples (the UIImage element is write-only)
- Make BaseGallery's `_create_content()` overridable for different layouts (list vs grid)
- Maintain backward compatibility for RaceSetupScreen (no caller changes)
- All 11994 tests continue to pass

## Scope
**In:**
- `game/ui/panels/base_gallery.py` — normalize to 2-tuples, make _create_content hookable
- `game/ui/panels/race_theme_gallery.py` — refactor to extend BaseGallery
- `tests/unit/ui/test_race_theme_gallery.py` — update all 12 tests for new API
- `tests/unit/ui/test_race_portrait_gallery.py` — update 3-tuples → 2-tuples in test data
- `tests/unit/ui/test_race_flag_gallery.py` — update 3-tuples → 2-tuples in test data

**Out:**
- RaceSetupScreen changes (public API is preserved)
- New features or capabilities for galleries
- Other UI panel refactoring

## Key Files
| Component | File Path |
|-----------|-----------|
| Base gallery class | `game/ui/panels/base_gallery.py` |
| Theme gallery (refactor target) | `game/ui/panels/race_theme_gallery.py` |
| Portrait gallery (update tuples) | `game/ui/panels/race_portrait_gallery.py` |
| Flag gallery (update tuples) | `game/ui/panels/race_flag_gallery.py` |
| Theme gallery tests | `tests/unit/ui/test_race_theme_gallery.py` |
| Portrait gallery tests | `tests/unit/ui/test_race_portrait_gallery.py` |
| Flag gallery tests | `tests/unit/ui/test_race_flag_gallery.py` |
| Caller (no changes expected) | `game/ui/screens/race_setup_screen.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- Review source: `Reviews/results/2026-02-23_160413_general_duplication-consolidation-analysis/verification_report.md`

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-23 | Option B: Normalize to 2-tuples | Clean-sheet approach. The UIImage in the 3-tuple is write-only (created during _populate_gallery, never read). Storing it in the shared data structure couples layout concerns to the selection contract. |
| 2026-02-23 | Make _create_content overridable via hooks | RaceThemeGallery doesn't want a label or preview panel. Rather than conditional flags, let subclasses override _create_content entirely (it's already non-abstract). |
| 2026-02-23 | Keep asset_loader as optional param | RaceThemeGallery uses ShipThemeManager directly and doesn't need RaceAssetLoader. Making asset_loader optional preserves this flexibility. |

---

## Phases

### Phase 1: Normalize BaseGallery to 2-Tuples [Simple]
**Objective:** Change `asset_buttons` from 3-tuple `(btn, img, id)` to 2-tuple `(btn, id)` in BaseGallery and update all existing consumers.
**Status:** Not Started

See [phase_1_checklist.md](phase_1_checklist.md) for detailed tasks.

### Phase 2: Refactor RaceThemeGallery to Extend BaseGallery [Medium]
**Objective:** Rewrite RaceThemeGallery to inherit from BaseGallery, implementing abstract methods and overriding `_create_content`/`_populate_gallery` for list layout.
**Status:** Not Started

See [phase_2_checklist.md](phase_2_checklist.md) for detailed tasks.

### Phase 3: Update Tests and Final Verification [Simple]
**Objective:** Update all theme gallery tests for the new BaseGallery API, update portrait/flag test tuples, run full suite.
**Status:** Not Started

See [phase_3_checklist.md](phase_3_checklist.md) for detailed tasks.

---

## Verification Checklist

### Project Start (REQUIRED)
- [x] Run full test suite: `pytest tests/ -n 12` — 11994 passed, 1 skipped (baseline established)

### After Each Phase
- [ ] Run `pytest tests/unit/ui/test_race_portrait_gallery.py tests/unit/ui/test_race_flag_gallery.py tests/unit/ui/test_race_theme_gallery.py -v`
- [ ] All gallery tests pass

### Final Verification
- [ ] Run full test suite: `pytest tests/ -n 12` — all tests pass
- [ ] Verify RaceThemeGallery no longer has duplicate methods (_sanitize_object_id, handle_button_click, set_from_config)
- [ ] Verify RaceThemeGallery extends BaseGallery
- [ ] Verify public API unchanged (RaceSetupScreen still works without modification)

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] All Phase 1 tasks checked off
- [ ] All Phase 2 tasks checked off
- [ ] All Phase 3 tasks checked off
- [ ] All tests passing (11994+)
- [ ] Audit passed (no significant issues)
- [ ] User verified
