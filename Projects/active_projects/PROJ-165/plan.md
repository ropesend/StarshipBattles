# PROJ-165: Create `create_section_header()` UI Helper

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-165` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-165 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Add helper + tests | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Migrate race editor panels (19 sites) | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Migrate empire/other panels (5 sites) | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Final verification | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-23
**Active Phase:** Planning
**Last Action:** Project plan written
**Next Action:** User approval, then begin Phase 1
**Blockers:** None

## Overview
Extract the repeated `pygame_gui.elements.UILabel(..., object_id="#section_header")` pattern from 24 inline call sites across 8 UI files into a single `create_section_header()` helper function in `game/ui/utils.py`. This eliminates the most-duplicated UI widget construction pattern in the codebase.

**Origin:** Review `2026-02-23_160413_general_duplication-consolidation-analysis`, Finding UI CQ-103, verified as Tier 1 #3 with 24 instances across 8 files.

## Goals
- Eliminate 24 identical UILabel constructions for section headers across 8 files
- Provide a single source of truth for section header appearance (height, object_id, x-margin)
- Make it easy to change section header style globally in the future
- Zero behavior change — pure refactor, all existing tests must pass unchanged

## Scope
**In:**
- Add `create_section_header()` function to existing `game/ui/utils.py`
- Migrate all 24 `object_id="#section_header"` sites across 8 files
- Write unit tests for the new helper

**Out:**
- The `── Title ──` decorated headers in `ship_detail_panel.py` and `design_stats_panel.py` — these are a different visual style (decorated with dash characters, sometimes no `#section_header` object_id). `ship_detail_panel.py` already has its own `_add_section_header()` method.
- The `builder_widgets.py` / `component_modifier_grid_panel.py` / `weapons_panel.py` decorated headers — same decorated style, separate pattern.
- Any refactoring of panel base classes — that's a separate future project.

## Key Files
| Component | File Path |
|-----------|-----------|
| Helper location | `game/ui/utils.py` |
| Race identity panel | `game/ui/panels/race_identity_panel.py` (3 sites) |
| Race environment panel | `game/ui/panels/race_environment_panel.py` (6 sites) |
| Race aptitudes panel | `game/ui/panels/race_aptitudes_panel.py` (3 sites) |
| Race description panel | `game/ui/panels/race_description_panel.py` (2 sites) |
| Race summary panel | `game/ui/panels/race_summary_panel.py` (4 sites) |
| Empire panel window | `game/ui/screens/empire_panel_window.py` (5 sites) |
| Empire treasury panel | `game/ui/panels/empire_treasury_panel.py` (1 site, inside `_build_section()`) |
| Helper tests | `tests/unit/ui/test_ui_utils.py` (new or extend) |

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-23 | Module-level function, not a class method | `game/ui/utils.py` is already a module of standalone utility functions. No need for a class. |
| 2026-02-23 | Return the UILabel, don't advance y | Callers handle y-advancement differently (`y += 28` vs `y += ROW_HEIGHT + 5` vs `y += ROW_HEIGHT`). Let the caller control the spacing. |
| 2026-02-23 | Default height=25, default x_margin=10 | 23 of 24 sites use height=25 and x=10. The one variant (empire_treasury) uses `LEFT_MARGIN` and `ROW_HEIGHT` constants but same semantic. |
| 2026-02-23 | Exclude `── Title ──` decorated headers | Different visual style, different pattern. `ship_detail_panel.py` already has its own helper. |
| 2026-02-23 | Width is always a required parameter | Width varies substantially (200, 300, `col_width`, `content_width`, calculated expressions). No sensible default. |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

---

## Pattern Analysis

### The Standard Pattern (24 sites)
All use this structure (only text, width, manager attribute name, and container vary):
```python
pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect(10, y, <width>, 25),
    text="<Section Title>:",
    manager=self.ui_manager,
    container=self.panel,
    object_id="#section_header"
)
```

### Variations
| Variation | Files | Count |
|-----------|-------|-------|
| `x=10`, `height=25`, `manager=self.ui_manager`, `container=self.panel` | race_*.py panels | 18 |
| `x=10`, `height=ROW_HEIGHT`, `manager=self.ui_manager`, `container=container` | empire_panel_window.py | 5 |
| `x=LEFT_MARGIN`, `height=ROW_HEIGHT`, `manager=self.ui_manager`, `container=self._scroll_container` | empire_treasury_panel.py | 1 |

### Complete Site Inventory

**race_identity_panel.py** (3 sites):
| # | Line | Text | Width |
|---|------|------|-------|
| 1 | 101 | "Species Identity:" | 200 |
| 2 | 166 | "Government:" | 200 |
| 3 | 268 | "Faction:" | 200 |

**race_environment_panel.py** (6 sites):
| # | Line | Text | Width |
|---|------|------|-------|
| 4 | 135 | "Homeworld Type:" | 200 |
| 5 | 169 | "Gravity Preferences:" | 200 |
| 6 | 228 | "Temperature Preferences:" | 200 |
| 7 | 287 | "Radiation Tolerance:" | 200 |
| 8 | 323 | "Water Preferences:" | 200 |
| 9 | 382 | "Atmosphere Preferences (-100 toxic to +100 beneficial):" | `width` (variable) |

**race_aptitudes_panel.py** (3 sites):
| # | Line | Text | Width |
|---|------|------|-------|
| 10 | 108 | "Point Budget:" | 200 |
| 11 | 132 | "Aptitudes (1-100, base 50):" | 200 |
| 12 | 191 | "Cost Breakdown:" | 200 |

**race_description_panel.py** (2 sites):
| # | Line | Text | Width |
|---|------|------|-------|
| 13 | 65 | "Biological Description:" | 300 |
| 14 | 90 | "Sociological Description:" | 300 |

**race_summary_panel.py** (4 sites):
| # | Line | Text | Width | Notes |
|---|------|------|-------|-------|
| 15 | 130 | "Faction:" | `col_width` | Stored in `self.summary_labels['faction_header']` |
| 16 | 229 | "Environment:" | `col_width` | Not stored |
| 17 | 285 | "Aptitudes:" | `col_width` | Not stored |
| 18 | 318 | "Descriptions:" | `col_width` | Not stored |

**empire_panel_window.py** (5 sites):
| # | Line | Text | Width | Height | Container |
|---|------|------|-------|--------|-----------|
| 19 | 307 | "Identity" | `content_width` | `ROW_HEIGHT` | `container` param |
| 20 | 348 | "Aptitudes" | `content_width` | `ROW_HEIGHT` | `container` param |
| 21 | 400 | "Environmental Preferences" | `content_width` | `ROW_HEIGHT` | `container` param |
| 22 | 449 | "Biology" | `content_width` | `ROW_HEIGHT` | `container` param |
| 23 | 470 | "Society" | `content_width` | `ROW_HEIGHT` | `container` param |

**empire_treasury_panel.py** (1 site):
| # | Line | Text | Width | Notes |
|---|------|------|-------|-------|
| 24 | 169 | `title` (param) | calculated expression | Inside `_build_section()` method |

---

## Phases

### Phase 1: Add Helper Function + Unit Tests [Simple]
**Objective:** Add `create_section_header()` to `game/ui/utils.py` and write tests.
**Status:** Not Started

#### Task 1.1: Add `create_section_header()` to `game/ui/utils.py` [Simple]
**File:** `game/ui/utils.py`
- [ ] Add function at end of file:
  ```python
  def create_section_header(
      text: str,
      y: int,
      width: int,
      manager,
      container,
      x: int = 10,
      height: int = 25
  ) -> 'pygame_gui.elements.UILabel':
      """
      Create a standard section header UILabel.

      Consolidates the repeated pattern of creating section header labels
      with consistent styling across UI panels.

      Args:
          text: Header text to display
          y: Vertical position
          width: Label width
          manager: pygame_gui UIManager instance
          container: Parent UI container
          x: Horizontal position (default: 10)
          height: Label height (default: 25)

      Returns:
          The created UILabel element
      """
      import pygame_gui
      return pygame_gui.elements.UILabel(
          relative_rect=pygame.Rect(x, y, width, height),
          text=text,
          manager=manager,
          container=container,
          object_id="#section_header"
      )
  ```
- [ ] Add `pygame_gui` to imports at top of file if not present (prefer lazy import in function body to avoid hard dependency — `utils.py` currently only imports `pygame`)
- [ ] Verify existing tests still pass: `pytest tests/unit/ui/ -v`
**Notes:** Lazy import of pygame_gui inside the function keeps utils.py lightweight for callers that don't need it.

#### Task 1.2: Write unit tests [Simple]
**File:** `tests/unit/ui/test_ui_utils.py` (create or extend)
**Tests:** `pytest tests/unit/ui/test_ui_utils.py -v`
- [ ] Check if `test_ui_utils.py` already exists; if so, add to it
- [ ] Add test class `TestCreateSectionHeader`:
  - [ ] `test_returns_uilabel` — returns a UILabel instance
  - [ ] `test_default_x_position` — rect.x == 10
  - [ ] `test_default_height` — rect.height == 25
  - [ ] `test_custom_x` — `create_section_header(..., x=20)` → rect.x == 20
  - [ ] `test_custom_height` — `create_section_header(..., height=30)` → rect.height == 30
  - [ ] `test_object_id` — object_id contains "#section_header"
  - [ ] `test_text_set` — label text matches input
  - [ ] `test_width_matches` — rect.width matches passed width
- [ ] Run tests, verify all pass
**Notes:** May need pygame display init in fixture. Check existing test patterns for pygame_gui UI tests.

---

### Phase 2: Migrate Race Editor Panels (19 sites) [Simple]
**Objective:** Replace 19 inline UILabel constructions in 5 race panel files with `create_section_header()` calls.
**Status:** Not Started

#### Task 2.1: Migrate race_identity_panel.py (3 sites) [Simple]
**File:** `game/ui/panels/race_identity_panel.py`
**Tests:** `pytest tests/unit/ui/ -v --testmon`
- [ ] Add import: `from game.ui.utils import create_section_header`
- [ ] Site 1 (~line 101): Replace 6-line UILabel block with:
  ```python
  create_section_header("Species Identity:", y, 200, self.ui_manager, self.panel)
  ```
- [ ] Site 2 (~line 166): Replace with `create_section_header("Government:", y, 200, self.ui_manager, self.panel)`
- [ ] Site 3 (~line 268): Replace with `create_section_header("Faction:", y, 200, self.ui_manager, self.panel)`
- [ ] Run tests
**Notes:** All 3 use identical parameters (width=200, x=10, height=25). Straightforward.

#### Task 2.2: Migrate race_environment_panel.py (6 sites) [Simple]
**File:** `game/ui/panels/race_environment_panel.py`
**Tests:** `pytest tests/unit/ui/ -v --testmon`
- [ ] Add import: `from game.ui.utils import create_section_header`
- [ ] Site 4 (~line 135): Replace with `create_section_header("Homeworld Type:", y, 200, self.ui_manager, self.panel)`
- [ ] Site 5 (~line 169): Replace with `create_section_header("Gravity Preferences:", y, 200, self.ui_manager, self.panel)`
- [ ] Site 6 (~line 228): Replace with `create_section_header("Temperature Preferences:", y, 200, self.ui_manager, self.panel)`
- [ ] Site 7 (~line 287): Replace with `create_section_header("Radiation Tolerance:", y, 200, self.ui_manager, self.panel)`
- [ ] Site 8 (~line 323): Replace with `create_section_header("Water Preferences:", y, 200, self.ui_manager, self.panel)`
- [ ] Site 9 (~line 382): Replace with `create_section_header("Atmosphere Preferences (-100 toxic to +100 beneficial):", y, width, self.ui_manager, self.panel)` — note: uses variable `width`, not `200`
- [ ] Run tests
**Notes:** 5 of 6 use width=200; site 9 uses the panel `width` variable.

#### Task 2.3: Migrate race_aptitudes_panel.py (3 sites) [Simple]
**File:** `game/ui/panels/race_aptitudes_panel.py`
**Tests:** `pytest tests/unit/ui/ -v --testmon`
- [ ] Add import: `from game.ui.utils import create_section_header`
- [ ] Site 10 (~line 108): Replace with `create_section_header("Point Budget:", y, 200, self.ui_manager, self.panel)`
- [ ] Site 11 (~line 132): Replace with `create_section_header("Aptitudes (1-100, base 50):", y, 200, self.ui_manager, self.panel)`
- [ ] Site 12 (~line 191): Replace with `create_section_header("Cost Breakdown:", y, 200, self.ui_manager, self.panel)`
- [ ] Run tests
**Notes:**

#### Task 2.4: Migrate race_description_panel.py (2 sites) [Simple]
**File:** `game/ui/panels/race_description_panel.py`
**Tests:** `pytest tests/unit/ui/ -v --testmon`
- [ ] Add import: `from game.ui.utils import create_section_header`
- [ ] Site 13 (~line 65): Replace with `create_section_header("Biological Description:", y, 300, self.ui_manager, self.panel)` — note: width=300 (not 200)
- [ ] Site 14 (~line 90): Replace with `create_section_header("Sociological Description:", y, 300, self.ui_manager, self.panel)` — note: width=300
- [ ] Run tests
**Notes:** These two use width=300, wider than the identity/environment panels.

#### Task 2.5: Migrate race_summary_panel.py (4 sites) [Simple]
**File:** `game/ui/panels/race_summary_panel.py`
**Tests:** `pytest tests/unit/ui/ -v --testmon`
- [ ] Add import: `from game.ui.utils import create_section_header`
- [ ] Site 15 (~line 130): Special — result is stored: `self.summary_labels['faction_header'] = create_section_header("Faction:", y, col_width, self.ui_manager, self.panel)` — note: uses `col_width` and `x` may not be 10 (check!)
- [ ] Site 16 (~line 229): Replace with `create_section_header("Environment:", y, col_width, self.ui_manager, self.panel)` — check `x` parameter
- [ ] Site 17 (~line 285): Replace with `create_section_header("Aptitudes:", y, col_width, self.ui_manager, self.panel)` — check `x` parameter
- [ ] Site 18 (~line 318): Replace with `create_section_header("Descriptions:", y, col_width, self.ui_manager, self.panel)` — check `x` parameter
- [ ] Run tests
**Notes:** Summary panel may use variable x positions (multi-column layout). Read the actual Rect x values — if not 10, pass `x=<value>` explicitly.

---

### Phase 3: Migrate Empire/Other Panels (5 sites) [Simple]
**Objective:** Replace 5 inline UILabel constructions in empire_panel_window.py and 1 in empire_treasury_panel.py.
**Status:** Not Started

#### Task 3.1: Migrate empire_panel_window.py (5 sites) [Simple]
**File:** `game/ui/screens/empire_panel_window.py`
**Tests:** `pytest tests/unit/ui/ -v --testmon`
- [ ] Add import: `from game.ui.utils import create_section_header`
- [ ] Site 19 (~line 307): Replace with `create_section_header("Identity", y_offset, content_width, self.ui_manager, container, height=ROW_HEIGHT)` — note: uses `ROW_HEIGHT` not 25, uses `container` param not `self.panel`
- [ ] Site 20 (~line 348): Replace with `create_section_header("Aptitudes", y_offset, content_width, self.ui_manager, container, height=ROW_HEIGHT)`
- [ ] Site 21 (~line 400): Replace with `create_section_header("Environmental Preferences", y_offset, content_width, self.ui_manager, container, height=ROW_HEIGHT)`
- [ ] Site 22 (~line 449): Replace with `create_section_header("Biology", y_offset, content_width, self.ui_manager, container, height=ROW_HEIGHT)`
- [ ] Site 23 (~line 470): Replace with `create_section_header("Society", y_offset, content_width, self.ui_manager, container, height=ROW_HEIGHT)`
- [ ] Run tests
**Notes:** All 5 use `ROW_HEIGHT` constant and `container` parameter (not `self.panel`). Must pass `height=ROW_HEIGHT`.

#### Task 3.2: Migrate empire_treasury_panel.py (1 site) [Simple]
**File:** `game/ui/panels/empire_treasury_panel.py`
**Tests:** `pytest tests/unit/ui/ -v --testmon`
- [ ] Add import: `from game.ui.utils import create_section_header`
- [ ] Site 24 (~line 169): Inside `_build_section()` method. Replace 5-line UILabel block with:
  ```python
  title_label = create_section_header(
      title, y, LABEL_COL_WIDTH + len(PLANET_RESOURCES) * RESOURCE_COL_WIDTH,
      self.ui_manager, self._scroll_container, x=LEFT_MARGIN, height=ROW_HEIGHT
  )
  ```
- [ ] Verify `title_label` is still appended to `self._elements` (existing code does `self._elements.append(title_label)`)
- [ ] Run tests
**Notes:** This site uses `LEFT_MARGIN` for x and `ROW_HEIGHT` for height, and a calculated width expression. The return value is stored and appended to elements list.

---

### Phase 4: Final Verification [Simple]
**Objective:** Confirm zero regressions across full test suite.
**Status:** Not Started

#### Task 4.1: Full test suite run [Simple]
**Tests:** `pytest tests/ -n 12`
- [ ] Run full test suite
- [ ] Verify same pass count as baseline
- [ ] Verify no new warnings
**Notes:**

#### Task 4.2: Verify duplication eliminated [Simple]
- [ ] Run: `grep -rn 'object_id="#section_header"' game/ui/` — should return only `utils.py` (the helper itself)
- [ ] Verify `create_section_header` is imported in all 8 migrated files
- [ ] Verify no remaining inline `#section_header` constructions
**Notes:**

---

## Verification Checklist

### Project Start (REQUIRED)
- [ ] Run full test suite: `pytest tests/ -n 12` — all tests pass (establishes baseline)

### After Each Phase
- [ ] Run `pytest tests/ --testmon` — all affected tests pass

### Final Verification
- [ ] Full test suite: `pytest tests/ -n 12` — same pass count as baseline
- [ ] Grep for `object_id="#section_header"` — only in `game/ui/utils.py`
- [ ] Manual review: launch game, open Race Setup, verify section headers render identically

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] Phase 1 complete (helper + tests)
- [ ] Phase 2 complete (19 race panel migrations)
- [ ] Phase 3 complete (6 empire panel migrations)
- [ ] Phase 4 complete (full verification)
- [ ] All tests passing
- [ ] No remaining inline `#section_header` constructions (grep clean)
- [ ] User verified
