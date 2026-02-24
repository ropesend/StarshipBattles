# Phase 3: Migrate Empire/Other Panels (6 sites)

## Task 3.1: Migrate empire_panel_window.py (5 sites)
**File:** `game/ui/screens/empire_panel_window.py`
**Tests:** `pytest tests/unit/ui/ -v --testmon`

- [ ] Add import: `from game.ui.utils import create_section_header`
- [ ] Site 19 (~line 307, "Identity"): Replace → `create_section_header("Identity", y_offset, content_width, self.ui_manager, container, height=ROW_HEIGHT)`
- [ ] Site 20 (~line 348, "Aptitudes"): Replace → `create_section_header("Aptitudes", y_offset, content_width, self.ui_manager, container, height=ROW_HEIGHT)`
- [ ] Site 21 (~line 400, "Environmental Preferences"): Replace → `create_section_header("Environmental Preferences", y_offset, content_width, self.ui_manager, container, height=ROW_HEIGHT)`
- [ ] Site 22 (~line 449, "Biology"): Replace → `create_section_header("Biology", y_offset, content_width, self.ui_manager, container, height=ROW_HEIGHT)`
- [ ] Site 23 (~line 470, "Society"): Replace → `create_section_header("Society", y_offset, content_width, self.ui_manager, container, height=ROW_HEIGHT)`
- [ ] Run tests

**Notes:** All 5 use `ROW_HEIGHT` (not 25), `container` param (not `self.panel`), and `content_width`. Must pass `height=ROW_HEIGHT` explicitly.

## Task 3.2: Migrate empire_treasury_panel.py (1 site)
**File:** `game/ui/panels/empire_treasury_panel.py`
**Tests:** `pytest tests/unit/ui/ -v --testmon`

- [ ] Add import: `from game.ui.utils import create_section_header`
- [ ] Site 24 (~line 169, inside `_build_section()`): Replace UILabel block with:
  ```python
  title_label = create_section_header(
      title, y,
      LABEL_COL_WIDTH + len(PLANET_RESOURCES) * RESOURCE_COL_WIDTH,
      self.ui_manager, self._scroll_container,
      x=LEFT_MARGIN, height=ROW_HEIGHT
  )
  ```
- [ ] Verify `self._elements.append(title_label)` is preserved on next line
- [ ] Run tests

**Notes:** Uses `LEFT_MARGIN` for x, `ROW_HEIGHT` for height, and a calculated width expression. The return value is stored and appended to `self._elements`.

## Phase 3 Completion
- [ ] All 6 sites migrated across 2 files
- [ ] All tests pass: `pytest tests/unit/ui/ -v`
- [ ] Both files import `create_section_header` from `game.ui.utils`
