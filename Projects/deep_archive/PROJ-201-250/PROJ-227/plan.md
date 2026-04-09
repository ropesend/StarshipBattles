# PROJ-227: UI Formatting, Portraits & Shared Components (Dedup Campaign 4/5)

## Overview
Consolidate duplicated UI formatting utilities (compact numbers, damage colors) and portrait loading/placeholder generation into shared modules. Fourth project in the 5-project duplication elimination campaign (PROJ-224 through PROJ-228).

**Source Review:** `Reviews/results/2026-03-24_200858_general_duplication-consolidation-full-codebase/`

## Goals
1. Create shared `format_compact_number()` utility eliminating 4+ duplicate implementations
2. Consolidate HP/damage color functions into single parameterized utility
3. Create shared portrait resolution and placeholder portrait generation utilities
4. Clean up `COLORS` dict vs module-level constant inconsistency in `colors.py`

## Scope
- `game/ui/utils/formatters.py` (NEW) — compact number formatting, damage color
- `game/ui/utils/portraits.py` (NEW) — portrait resolution, placeholder generation
- `game/ui/panels/planet_report_panel.py` — remove `_format_compact_number`
- `game/ui/panels/ship_stats_renderer.py` — delegate `get_hp_bar_color` to shared
- `game/ui/panels/ship_detail_panel.py` — remove `get_damage_color`, import shared
- `game/ui/panels/design_report_panel.py` — delegate portrait to shared utility
- `game/ui/panels/build_queue_portraits.py` — delegate portrait to shared utility
- `game/ui/screens/empire_build_queue_formatter.py` — use shared formatting
- `game/ui/screens/planet_list_filters.py` — use shared formatting
- `game/ui/screens/strategy_detail_fmt.py` — use shared formatting

## Findings Addressed
| ID | Severity | Description |
|----|----------|-------------|
| DUP-XL-002 | MAJOR | Compact number formatting (K/M suffixes) in 4+ UI files |
| DUP-UIW-003 | MAJOR | HP/Damage color threshold functions in 2 files |
| DUP-XL-005 | MINOR | HP-to-color mapping in two UI panels |
| DUP-UIW-001 | MAJOR | Portrait loading + ship class parsing in 2 files |
| DUP-UIW-005 | MAJOR | Placeholder portrait generation in 2 files |
| DUP-SCR-014 | MINOR | Population formatting with K/M suffixes |

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Shared Formatting Utilities | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Consolidate Compact Number Call Sites | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Consolidate Damage Color Call Sites | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Shared Portrait Utilities | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Consolidate Portrait Call Sites & Cleanup | Complete | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-03-24
**Last Agent Action:** Completed all 5 phases. Project is complete.
**Next Action:** None — project complete.
**Blockers:** None
**Context for Next Agent:** All phases complete. 13513 tests pass (43 new tests added from 13470 baseline). Key changes:
- Phase 1: Created `game/ui/utils/formatters.py` with `format_compact_number()` and `get_damage_color()` (23 tests)
- Phase 2: Consolidated 4 call sites for compact number formatting (planet_report_panel, empire_build_queue_formatter, planet_list_filters, strategy_detail_fmt)
- Phase 3: Consolidated damage color into single function with unified thresholds (>=50% HEALTHY, 25-49% DAMAGED, <25% CRITICAL, <=0 DESTROYED). `get_hp_bar_color` kept as thin wrapper for COMPONENT_INACTIVE_BG case.
- Phase 4: Created `game/ui/utils/portraits.py` with `parse_ship_class_name`, `get_ship_class_color`, `get_portrait_filename`, `get_portrait_search_paths`, `create_placeholder_portrait` (20 tests)
- Phase 5: Consolidated design_report_panel and build_queue_portraits to use shared portrait utilities

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-03-24 | Put formatters in game/ui/utils/formatters.py | UI-specific formatting belongs in UI layer, not core |
| 2026-03-24 | Consolidate get_hp_bar_color and get_damage_color into single function | Both map HP percentage to color with same semantic meaning |
| 2026-03-24 | Use colors.py HP_* constants as canonical damage colors | Already defined there, just need consistent thresholds |
| 2026-03-24 | Unified thresholds: >=50% HEALTHY, 25-49% DAMAGED, <25% CRITICAL | Compromise between old ship_stats (20/50) and ship_detail (50/75) thresholds |
| 2026-03-24 | Keep get_hp_bar_color as thin wrapper | Returns COMPONENT_INACTIVE_BG for inactive components, specific to combat rendering |
| 2026-03-24 | Lowercase 'k' for thousands suffix | 3 of 4 existing implementations used lowercase, standardized on it |

## Execution Order
**4th of 5 projects** — depends on PROJ-224 utilities (display_name, EARTH_MASS). No overlap with PROJ-225 (simulation layer).

## Success Criteria
- [x] All 13470+ tests pass (13513 passed, 2 skipped)
- [x] `format_compact_number()` utility exists and is used by all 4+ call sites
- [x] Single `get_damage_color()` function with consistent thresholds
- [x] Portrait resolution utility eliminates 50+ lines of duplication
- [x] No inline K/M formatting patterns remain in consolidated call sites
