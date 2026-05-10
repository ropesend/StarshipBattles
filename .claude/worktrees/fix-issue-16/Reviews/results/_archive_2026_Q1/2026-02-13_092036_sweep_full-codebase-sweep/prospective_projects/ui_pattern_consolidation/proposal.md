# Prospective Project: UI Pattern Consolidation

## Overview
This project addresses code duplication in the UI layer by extracting common patterns into reusable components. Multiple windows implement similar virtual scrolling, filter toggles, sidebar building, and formatting utilities. Consolidating these patterns will reduce maintenance burden and ensure consistent behavior across the UI.

## Grouping Rationale
These findings all relate to duplicated code patterns in the UI layer:
1. **Same layer** - All findings affect game/ui/ components
2. **Shared fix strategy** - Extract common patterns into shared utilities or base classes
3. **Related patterns** - Virtual scrolling, filter toggles, and sidebar building often appear together
4. **Consistency impact** - Consolidation ensures consistent UI behavior (e.g., number formatting)

## Source
- **Sweep:** 2026-02-13_092036_sweep_full-codebase-sweep
- **Findings:** 19 total (1 Critical, 9 Major, 7 Minor, 2 Info)

## Suggested Execution Order
**Should be done FOURTH** - After test coverage work establishes a safety net. Pattern extraction is a refactoring task that benefits from comprehensive tests.

## Findings

### Critical (1)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| DUP-UI1-001 | Number Formatting with K/M Suffixes Duplicated | `game/ui/panels/planet_report_panel.py`, `game/ui/screens/strategy_detail_fmt.py` | Simple |

### Major (9)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| DUP-UI2-001 | Tkinter Root Initialization Duplicated | `game/ui/services/ship_io.py:20` | Medium |
| DUP-UI2-003 | Image Bounding Box + Scale Logic Duplicated | `game/ui/utils.py:116-162` | Simple |
| DUP-UI1-002 | Virtual Scrolling List Pattern Repeated | `game/ui/screens/planet_list_window.py`, `fleet_report_window.py`, `empire_build_queue_window.py`, `event_log_window.py` | Medium |
| DUP-UI1-003 | Filter Toggle Button Pattern Duplicated | `game/ui/screens/fleet_report_window.py`, `planet_list_window.py`, `empire_build_queue_window.py` | Medium |
| DUP-UI1-005 | Sidebar Filter Section Building Pattern | `game/ui/screens/empire_build_queue_window.py`, `fleet_report_window.py`, `planet_list_sidebar.py` | Medium |
| DUP-FND-003 | Distance Calculation Pattern Repetition | `game/ai/controller.py:197-201` | Medium |
| CON-UI1-010 | Duplicate ColumnManager Classes | `game/ui/screens/column_manager.py` | Medium |
| DUP-STR-001 | Duplicated Facility Component Iteration | Strategy layer | Medium |
| DUP-STR-002 | Duplicated Command Handler Pattern | Strategy layer | Medium |

### Minor (7)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| DUP-FND-001 | IControllable Protocol Duplicates IShip | `game/ai/interfaces/controllable.py` | Medium |
| DUP-FND-002 | ResearchTracker and ResearchControlPanel Duplication | `game/research/data/research_tracker.py` | Simple |
| DUP-UI2-002 | Registry Provider Lazy Resolution Pattern | `game/ui/services/component_service.py` | Medium |
| DUP-UI1-004 | Placeholder Surface Creation | `game/ui/panels/build_queue_portraits.py`, `fleet_report_window.py`, `race_asset_loader.py` | Simple |
| DUP-UI1-007 | Column Visibility Toggle Handling | `game/ui/screens/planet_list_window.py`, `empire_build_queue_window.py` | Simple |
| DUP-FND-006 | Flee Direction Calculation | `game/ai/behaviors.py:70-85` | Simple |
| DUP-STR-003 | Duplicated Resource Cost Calculation | Strategy layer | Simple |

### Info (2)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| DUP-UI2-004 | Singleton Manager Boilerplate | `game/ui/assets/ship_theme_manager.py` | Simple |
| DUP-UI2-006 | Clipboard Copy Implementation | `game/ui/services/screenshot_manager.py` | Simple |

## Affected Files

### UI Utilities (new/modified)
- `game/ui/utils.py` - Add format_compact_number(), scale_image(), create_placeholder()

### UI Screens - Windows with Scrolling
- `game/ui/screens/planet_list_window.py`
- `game/ui/screens/fleet_report_window.py`
- `game/ui/screens/empire_build_queue_window.py`
- `game/ui/screens/event_log_window.py`

### UI Screens - Windows with Filters
- `game/ui/screens/planet_list_sidebar.py`
- `game/ui/screens/column_manager.py`

### UI Services
- `game/ui/services/ship_io.py`
- `game/ui/services/component_service.py`
- `game/ui/services/screenshot_manager.py`

### UI Panels
- `game/ui/panels/planet_report_panel.py`
- `game/ui/panels/build_queue_portraits.py`
- `game/ui/assets/ship_theme_manager.py`

### Strategy Formatting
- `game/ui/screens/strategy_detail_fmt.py`

### AI/Foundation
- `game/ai/controller.py`
- `game/ai/behaviors.py`
- `game/ai/interfaces/controllable.py`
- `game/research/data/research_tracker.py`

## Effort Estimate
- **Simple tasks:** 9
- **Medium tasks:** 10
- **Complex tasks:** 0
- **Overall scope:** Medium

## Overlap with Existing Projects
- **PROJ-127 (code-duplication-reduction)** - Direct overlap with duplication findings
- **PROJ-128 (codebase-consistency)** - Related to consistency findings

## Suggested Phases

### Phase 1: Utility Functions (2-3 days)
Extract shared utility functions:
1. DUP-UI1-001: Create format_compact_number() in game/ui/utils.py
2. DUP-UI1-004: Create create_placeholder_surface() in game/ui/utils.py
3. DUP-UI2-003: Extract image scaling utility
4. DUP-FND-006: Extract flee direction calculation utility

### Phase 2: Virtual Scrolling Component (3-4 days)
Create VirtualScrollableList base class or mixin:
1. DUP-UI1-002: Design VirtualScrollableList interface
2. Extract scrollbar setup and management
3. Extract mouse wheel handling
4. Refactor planet_list_window to use new component
5. Refactor fleet_report_window, build_queue_window, event_log_window

### Phase 3: Filter Components (3-4 days)
Create filter toggle and sidebar builder utilities:
1. DUP-UI1-003: Create ToggleFilterButton widget class
2. DUP-UI1-005: Create FilterSidebarBuilder helper
3. DUP-UI1-007: Move column toggle handling into ColumnManager
4. CON-UI1-010: Consolidate duplicate ColumnManager classes

### Phase 4: Service Layer Cleanup (2-3 days)
Consolidate service patterns:
1. DUP-UI2-001: Extract Tkinter root initialization
2. DUP-UI2-002: Standardize registry provider pattern
3. DUP-UI2-006: Consolidate clipboard utilities

### Phase 5: Foundation and Strategy Patterns (2-3 days)
Address cross-layer duplication:
1. DUP-FND-001: Evaluate IControllable/IShip consolidation
2. DUP-FND-002: Consolidate research tracker duplication
3. DUP-FND-003: Extract distance calculation utility
4. DUP-STR-001, DUP-STR-002, DUP-STR-003: Strategy layer patterns
