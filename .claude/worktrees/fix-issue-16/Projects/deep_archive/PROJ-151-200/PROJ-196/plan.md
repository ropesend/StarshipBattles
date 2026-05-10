# PROJ-196: Consolidate Duplicated Code

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-196` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-196 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Font Module + Per-Frame Fixes | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Cached Font Migration | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Color Constants + TestLabTheme | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Test Lab Theme Migration | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Non-Test-Lab Color Migration | Complete | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. ValidationResult Cleanup + Audit | Complete | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-02-25
**Active Phase:** Complete — All phases done, ready for project audit
**Last Action:** Phase 6 complete — Migrated 7 ValidationResult constructor calls to factory methods, all verifications passed
**Next Action:** Project audit (Protocol 04)
**Blockers:** None
**Context for Next Agent:** All 6 phases complete. 12,734 tests passed. Font module created, Test Lab theme created, ValidationResult cleanup done. Project ready for final audit.

## Overview
Consolidate three categories of duplicated boilerplate: font instantiations (81 instances, many per-frame performance bugs), inline color tuples (253 instances, Test Lab alone has ~80), and ValidationResult constructor calls in tests (7 instances). Creates `game/ui/fonts.py` for cached font management, `game/ui/screens/test_lab/theme.py` for Test Lab color theming, and adds 6 common color constants to `game/ui/colors.py`.

## Goals
- Eliminate per-frame font creation in 16+ files (performance fix)
- Centralize all font creation through cached `get_font()` / `get_default_font()`
- Reduce Test Lab inline color tuples from ~80 to near zero
- Add commonly-used color constants to `colors.py`
- Migrate 7 test ValidationResult constructor calls to factory methods

## Scope
**In:**
- All `pygame.font.SysFont` and `pygame.font.Font(None, ...)` calls in `game/`
- Inline color tuples in Test Lab files (`game/ui/screens/test_lab/`)
- Common inline colors in non-Test-Lab `game/ui/` files
- 7 specific `ValidationResult` constructor calls in `tests/`
- `FONT_MAIN` constant migration from `colors.py` to `fonts.py`

**Out:**
- `scripts/` font/color usage (standalone visual test scripts)
- `test_framework/scenario.py` colors (domain-specific test metadata)
- `game/strategy/data/stars.py` colors (scientific domain data)
- `simulation_tests/data/schema_validator.py` ValidationResult (different class entirely)
- `simulation_tests/scenarios/validation.py` ValidationResult (different class entirely)
- `tests/unit/core/test_validation.py` (intentionally tests all construction patterns)
- Bare `ValidationResult()` calls in tests (44 instances — semantically correct, no change needed)

## Key Files
| Component | File Path |
|-----------|-----------|
| Font module (new) | `game/ui/fonts.py` |
| Font tests (new) | `tests/unit/ui/test_fonts.py` |
| Test Lab theme (new) | `game/ui/screens/test_lab/theme.py` |
| Colors module | `game/ui/colors.py` |
| UI Config | `game/ui/config.py` |
| ValidationResult | `game/core/validation.py` |
| Duplication report | `Duplication_Report.md` |

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-24 | Drop ValidationResult production refactor | All game/ code already uses factory methods |
| 2026-02-24 | New `game/ui/fonts.py` module for font caching | Dedicated module, matches colors.py pattern |
| 2026-02-24 | Two font APIs: `get_font()` + `get_default_font()` | `SysFont` and `Font(None)` are semantically different |
| 2026-02-24 | Remove FONT_MAIN from colors.py entirely | Per project policy: eradicate old patterns, no backward compat |
| 2026-02-24 | TestLabTheme as separate module | Test Lab has ~80 colors forming a cohesive theme; too many for colors.py |
| 2026-02-24 | Only 6 new constants in colors.py | TEXT_LIGHT, TEXT_MUTED, TEXT_DIM, PANEL_BG, BORDER_LIGHT, BORDER_DARK |
| 2026-02-24 | Clean up tests/ ValidationResult too | User requested consistency even in test mock code |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [x] All phase checklists complete
- [x] All tests passing (12,734 passed, 1 skipped)
- [x] `grep -rn "pygame.font.SysFont\|pygame.font.Font(None" game/` returns only fonts.py (cache implementation)
- [x] `grep -rn "FONT_MAIN" game/ui/colors.py` returns only deprecation comment
- [x] Audit passed (Cycle 1)
- [ ] User verified
