# Duplication & Fragmentation Sweep: UI-Screens

## Summary
- **Shard:** UI-Screens
- **Files Scanned:** 132
- **Total Issues Found:** 10
- **Critical:** 3 | **Major:** 5 | **Minor:** 2 | **Info:** 0

## Findings

#### CRITICAL: Duplicate ColumnManager Implementations
**ID:** DUP-UI1-001
**Location:** `game/ui/screens/column_manager.py` AND `game/ui/screens/planet_list_columns.py`
**Issue:** Two completely separate implementations of ColumnManager exist with identical concepts but different data models (column_manager.py for fleet reports vs planet_list_columns.py for planet list). ~100+ lines of overlapping logic.
**Impact:** Maintenance nightmare - changes to column logic must be made in two places. High risk of divergence.
**Recommendation:** Extract shared `BaseColumnManager` class with template method for data-model-specific behavior.
**Effort:** Complex

#### CRITICAL: Duplicate Value Formatting Logic
**ID:** DUP-UI1-002
**Location:** `game/ui/screens/test_lab/test_run_details.py:_format_value()` AND `game/ui/screens/test_lab/test_run_card.py:_format_value_short()`
**Issue:** Both implement probability detection (0 < value < 1) and scientific notation formatting with nearly identical logic but slightly different precision. ~15 lines each duplicated across 2 locations.
**Impact:** Bug divergence risk - if one is fixed, the other may remain broken.
**Recommendation:** Extract to shared utility module.
**Effort:** Simple

#### CRITICAL: Duplicate Empire Resource Formatting
**ID:** DUP-UI1-003
**Location:** `game/ui/screens/build_queue_helpers.py:format_empire_resources()` AND `game/ui/screens/strategy_ui.py:_format_spectrum()`
**Issue:** Resource abbreviation logic (Met/Org/Vap/Rad/Exo) duplicated with identical conversion patterns. ~12 lines duplicated.
**Impact:** Resource display inconsistencies if formats diverge.
**Recommendation:** Consolidate into single resource formatting utility.
**Effort:** Simple

#### MAJOR: Three Similar Format Functions for Star/System/Planet Info
**ID:** DUP-UI1-004
**Location:** `game/ui/screens/strategy_detail_fmt.py` AND `game/ui/screens/strategy_detail_formatter.py` AND `game/ui/screens/galaxy_test/system_mode.py`
**Issue:** format_planet_info, format_star_info, format_star_system_info exist in multiple files with similar structure. ~30 lines per function x 3 locations.
**Impact:** Maintenance burden, unclear which version is canonical.
**Recommendation:** Extract to strategy_detail_fmt, update callers.
**Effort:** Medium

#### MAJOR: Gallery Pattern Duplication (RacePortraitGallery, RaceFlagGallery)
**ID:** DUP-UI1-005
**Location:** `game/ui/panels/race_portrait_gallery.py` AND `game/ui/panels/race_flag_gallery.py`
**Issue:** ~70% identical class structure and methods (_create_content, _get_asset, etc.) with only asset type differences. ~150 lines each with ~110 lines duplicated.
**Impact:** Changes to gallery UI behavior must be applied to both classes.
**Recommendation:** Extract base GalleryWidget class with template method pattern.
**Effort:** Complex

#### MAJOR: Draw Utilities Duplication
**ID:** DUP-UI1-006
**Location:** `game/ui/screens/battle_panels.py:draw_stat_bar()` AND `game/ui/screens/ship_stats_renderer.py:draw_stat_bar()`
**Issue:** Similar draw utility functions exist in both modules. While battle_panels delegates correctly, there's no centralized location for other draw utilities.
**Impact:** Inconsistency in architecture for draw utilities.
**Recommendation:** Centralize draw utilities.
**Effort:** Simple

#### MAJOR: Filter Manager Pattern Duplication
**ID:** DUP-UI1-007
**Location:** `game/ui/screens/empire_build_queue_filter_manager.py` AND `game/ui/screens/planet_list_filters.py`
**Issue:** Similar filter, sort, and visibility management patterns but different implementations. ~50 lines of similar filter logic patterns.
**Impact:** Inconsistent filtering behavior across UI surfaces.
**Recommendation:** Extract abstract FilterManager base class.
**Effort:** Medium

#### MAJOR: Build Queue Formatting Fragmentation
**ID:** DUP-UI1-008
**Location:** `game/ui/screens/build_queue_helpers.py` AND `game/ui/screens/build_queue_screen.py` AND `game/ui/screens/empire_build_queue_formatter.py`
**Issue:** Three separate modules handling build queue formatting with overlapping responsibilities.
**Impact:** Unclear which module owns which formatting logic.
**Recommendation:** Consolidate to empire_build_queue_formatter.py.
**Effort:** Medium

#### MINOR: Similar K/M Number Formatting
**ID:** DUP-UI1-009
**Location:** Multiple locations use `amount >= 1000000: f"{amount / 1000000:.1f}M"` pattern
**Issue:** Number formatting with K/M suffixes implemented inline in multiple places.
**Impact:** Low risk, but code readability improvement possible.
**Recommendation:** Extract format_with_suffix() utility.
**Effort:** Simple

#### MINOR: Team 1/Team 2 Display Loop Duplication
**ID:** DUP-UI1-010
**Location:** `game/ui/screens/battle_panels.py:ShipStatsPanel.draw()` lines 110-131
**Issue:** Nearly identical loop structure for rendering team 1 and team 2. ~20 lines duplicated with only team ID and colors different.
**Impact:** Low (UI rendering code), but reduces readability.
**Recommendation:** Extract _draw_team_section method.
**Effort:** Simple

## Top 5 Priority Issues
1. **DUP-UI1-001: ColumnManager Duplication** - Two incompatible implementations managing same concept
2. **DUP-UI1-002: Value Formatting Functions** - Test lab formatting inconsistencies risk divergence
3. **DUP-UI1-005: Gallery Widget Pattern** - RacePortraitGallery and RaceFlagGallery share 70%+ code
4. **DUP-UI1-004: Info Formatting Fragmentation** - Star/planet/system formatting spread across 3+ locations
5. **DUP-UI1-008: Build Queue Formatting** - Three modules with overlapping responsibilities
