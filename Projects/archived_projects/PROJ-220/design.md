# PROJ-220: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Test Baseline
- **13,178 passed**, 2 skipped (2026-03-14)
- Test command: `pytest tests/ -n 12`

### Current State: Three Divergent Filter Implementations

| Window | State Pattern | State Location | Filter Logic | Binary Filters |
|--------|--------------|----------------|-------------|----------------|
| Fleet Report | 20 individual `bool` attributes | `FleetListViewModel` | `fleet_report_filters.py` (5 `_should_exclude_by_*()` fns) | 8 (warp, spaceyard, cargo, 5 special caps) |
| Planet List | `Dict[str, bool]` dicts | `PlanetListWindow` (on window directly) | `planet_list_filters.py` (`filter_planets()` with 11 args) | 0 (all multi-select or ranges) |
| Build Queue | `Dict[str, bool]` dicts | `BuildQueueFilterManager` (dedicated class) | `BuildQueueFilterManager.filter_sources()` | 3 (location type, queue status, capabilities) |

### Key Files

**Fleet Report:**
- `game/ui/screens/fleet_report_sidebar.py` — UI buttons (554 lines)
- `game/ui/screens/fleet_report_filters.py` — filter logic (325 lines)
- `game/ui/screens/fleet_report_view_model.py` — state management (280 lines)
- `game/ui/screens/fleet_report_window.py` — orchestrator (367 lines)
- `game/ui/screens/fleet_data_source.py` — `SPECIAL_CAPABILITY_COLUMNS` constant

**Planet List:**
- `game/ui/screens/planet_list_sidebar.py` — UI factory function (255 lines)
- `game/ui/screens/planet_list_filters.py` — filter logic (310 lines)
- `game/ui/screens/planet_list_window.py` — state + orchestrator (512 lines)
- `game/ui/screens/planet_list_presets.py` — preset serialization (185 lines)

**Build Queue:**
- `game/ui/screens/empire_build_queue_sidebar.py` — UI component (261 lines)
- `game/ui/screens/empire_build_queue_filter_manager.py` — state + filter logic (222 lines)
- `game/ui/screens/empire_build_queue_viewmodel.py` — ViewModel (337 lines)
- `game/ui/screens/empire_build_queue_window.py` — orchestrator (603 lines)

### Test Coverage (321 tests across 8 files)

| Module | Test File | Tests |
|--------|-----------|-------|
| Fleet Report filters | `test_fleet_report_filters.py` | 59 |
| Fleet Report window | `test_fleet_report_window.py` | 37 |
| Fleet Report multi-select | `test_fleet_report_window_multi_select.py` | 19 |
| Planet List filters | `test_planet_list_filters.py` | 2 |
| Planet List window | `test_planet_list_window.py` (integration) | 2 |
| Build Queue filter manager | `test_empire_build_queue_filter_manager.py` | 32 |
| Build Queue viewmodel | `test_empire_build_queue_viewmodel.py` | 51 |
| Build Queue window | `test_empire_build_queue_window.py` | 119 |

## Swarm Findings Summary

### Architecture

**Recommended new package structure:**
```
game/ui/filters/                          # Non-pygame filter infrastructure
├── __init__.py                           # Exports: FilterState, FilterStateManager
├── filter_state.py                       # FilterState enum (YES/NO/IGNORE)
└── filter_state_manager.py               # FilterStateManager base class

game/ui/components/filters/               # Pygame widget
├── __init__.py                           # Exports: TriStateFilterWidget
└── tri_state_widget.py                   # 3 radio buttons per attribute
```

**Three-layer separation:**
```
UI Layer:   TriStateFilterWidget (pygame component, 3 radio buttons)
State:      FilterStateManager (pure Python, no pygame, testable)
Logic:      Per-window filter functions (existing, refactored signatures)
```

### Key Patterns to Reuse

- **Button toggle API**: `UIButton.select()` / `unselect()` for visual state (used in all 3 sidebars)
- **Object ID theming**: `object_id='@filter_toggle_on'` for theme styling (planet_list_sidebar.py:89)
- **Enum pattern**: `game/core/constants.py` — string-valued Enum for serialization
- **Widget composition**: `game/ui/components/table/virtual_table.py` — class wrapping pygame_gui elements
- **EventBus**: `game/ui/screens/builder/event_bus.py` — pub/sub for state change notification
- **MVVM**: Build Queue pattern — ViewModel owns FilterManager, Sidebar communicates via ViewModel

### Dependencies & Risks

1. **Fleet Report special capability filters use fragile dynamic key mapping** — `col_id.replace('can_', 'no_', 1)` to derive filter keys. Must refactor to structured state before UI swap. Severity: MEDIUM.

2. **Planet List preset serialization** — `ui_presets.json` stores `Dict[str, bool]`. Changing to tri-state requires migration function. Severity: MEDIUM.

3. **Fleet Report's `filter_ships()` takes `Dict[str, bool]`** — Must change to `Dict[str, FilterState]` and update all 5 `_should_exclude_by_*()` functions. 59 tests directly test this. Severity: HIGH.

4. **Planet List's `filter_planets()` takes 11 positional args** — Signature is already unwieldy. Should NOT change in this project (Planet List has no tri-state filters to convert). Severity: LOW.

### Opportunities Discovered

- Planet List owner filter preset restore is broken (`apply_planet_list_state()` missing `filter_owner` parameter) — can fix as a byproduct
- Build Queue already has cleanest architecture — minimal refactoring needed
- Shared `FilterStateManager` enables future filter presets for Fleet Report and Build Queue (currently only Planet List has presets)

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.

### Tri-State Semantics

| State | Meaning | Filter Behavior |
|-------|---------|-----------------|
| `IGNORE` | Don't filter on this attribute | Pass all items through (no exclusion) |
| `YES` | Show only matching items | Exclude items where attribute is False |
| `NO` | Show only non-matching items | Exclude items where attribute is True |

### Mapping from Current Binary Pairs

| Current State | Tri-State Equivalent |
|---------------|---------------------|
| Both On (show all) | `IGNORE` |
| Only Yes On | `YES` |
| Only No On | `NO` |
| Both Off (show none) | Not representable — eliminated by design |

### Scope Boundaries

**IN SCOPE (tri-state conversion):**
- Fleet Report: Warp Capable, Spaceyard, Cargo, 5× Special Capabilities (8 binary filters)
- Build Queue: Location Type, Queue Status, Capabilities (3 binary filters)
- Shared infrastructure: FilterState enum, FilterStateManager, TriStateFilterWidget

**IN SCOPE (state unification only, no tri-state conversion):**
- Planet List: Adopt FilterStateManager for state management; existing multi-select/range filters unchanged

**OUT OF SCOPE:**
- Fleet Report Status filter (4-state, not binary)
- Planet List type/owner/range filters (multi-select and numeric, not binary)
