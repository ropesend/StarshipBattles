# Phase 3: Identity Tab UI [Medium]

**Objective:** Build the new Identity tab panel with dropdowns and text inputs
**Tests:** `pytest tests/unit/ui/panels/test_race_identity_panel.py -v`

---

## Task 3.1: Create RaceIdentityPanel Class [Medium]
**File:** `game/ui/panels/race_identity_panel.py` (NEW)
**Tests:** `pytest tests/unit/ui/panels/test_race_identity_panel.py -v`

- [x] Create `RaceIdentityPanel` class following extracted panel pattern
- [x] Constructor: `__init__(self, panel, manager, race_config)` — stores references, calls `_create_content()`
- [x] Create section: **Race Identity** (top)
  - [x] `race_name` text input: `UITextEntryLine`, placeholder "Species name (e.g., Rossarian)"
  - [x] `race_name_plural` text input: `UITextEntryLine`, placeholder "Plural (e.g., Rossarians)"
  - [x] `physical_type` dropdown: `UIDropDownMenu` with PHYSICAL_TYPES list + empty option
- [x] Create section: **Government** (middle)
  - [x] `government_type` dropdown: `UIDropDownMenu` with GOVERNMENT_TYPES list + empty option
  - [x] `government_organization` dropdown: `UIDropDownMenu` with GOVERNMENT_ORGANIZATIONS list + empty option
  - [x] `leader_title` dropdown: `UIDropDownMenu` with LEADER_TITLES list + empty option
  - [x] `society_type` dropdown: `UIDropDownMenu` with SOCIETY_TYPES list + empty option
- [x] Create section: **Faction** (bottom)
  - [x] `faction_name` text input: `UITextEntryLine`, auto-populated from race_name + government_type
  - [x] Label: "Auto-generated from Race Name + Government Type. Edit to override."
- [x] Implement auto-generation logic: when race_name or government_type changes, update faction_name if not manually overridden
- [x] Store `self._faction_name_overridden = False` flag
- [x] Write test: `test_identity_panel_creates_successfully`
- [x] Write test: `test_identity_panel_has_race_name_input`
- [x] Write test: `test_identity_panel_has_government_type_dropdown`
- [x] Write test: `test_identity_panel_has_all_dropdowns`
- [x] Run tests: all pass
**Notes:** Followed RaceEnvironmentPanel pattern. Used pygame_gui.elements.UIDropDownMenu.

---

## Task 3.2: Implement Data Synchronization Methods [Simple]
**File:** `game/ui/panels/race_identity_panel.py`
**Tests:** `pytest tests/unit/ui/panels/test_race_identity_panel.py -v -k "config"`

- [x] Implement `update_config()`: reads all UI elements → writes to race_config
  - race_config.race_name = race_name_input.get_text()
  - race_config.race_name_plural = race_name_plural_input.get_text()
  - race_config.faction_name = faction_name_input.get_text()
  - race_config.government_type = government_type_dropdown.selected_option (handle empty)
  - race_config.government_organization = government_org_dropdown.selected_option (handle empty)
  - race_config.leader_title = leader_title_dropdown.selected_option (handle empty)
  - race_config.physical_type = physical_type_dropdown.selected_option (handle empty)
  - race_config.society_type = society_type_dropdown.selected_option (handle empty)
- [x] Implement `set_from_config()`: reads race_config → sets all UI elements
  - Set text inputs with set_text()
  - Set dropdowns — handle empty string (select first/empty option)
- [x] Implement `update_labels()`: no-op for this panel (labels are static)
- [x] Write test: `test_update_config_reads_race_name`
- [x] Write test: `test_update_config_reads_government_type`
- [x] Write test: `test_set_from_config_populates_race_name`
- [x] Write test: `test_set_from_config_populates_dropdowns`
- [x] Run tests: all pass
**Notes:** Added _get_dropdown_value() helper for tuple handling.

---

## Task 3.3: Implement Faction Name Auto-Generation [Simple]
**File:** `game/ui/panels/race_identity_panel.py`
**Tests:** `pytest tests/unit/ui/panels/test_race_identity_panel.py -v -k "faction"`

- [x] Create `_auto_generate_faction_name()`: combines race_name + government_type
  - If both set: `"{race_name} {government_type}"` (e.g., "Rossarian Commonwealth")
  - If only race_name: use race_name alone
  - If only government_type: use government_type alone
  - If neither: empty string
- [x] Call auto-generate when race_name or government_type changes (and not overridden)
- [x] Track override: if user manually edits faction_name, set `_faction_name_overridden = True`
- [x] Reset override flag when loading from config if faction matches auto-generated
- [x] Write test: `test_auto_generate_faction_name_both_set`
- [x] Write test: `test_auto_generate_faction_name_race_only`
- [x] Write test: `test_auto_generate_faction_name_override_preserved`
- [x] Write test: `test_auto_generate_faction_name_resets_when_not_overridden`
- [x] Run tests: all pass
**Notes:** Added handle_event() method for UI event handling.

---

## Phase 3 Completion Checklist
- [x] All tasks above checked off
- [x] Run `pytest tests/unit/ui/panels/test_race_identity_panel.py -v` — all pass (21 tests)
- [x] Run `pytest tests/ --testmon` — no regressions
- [x] RaceIdentityPanel follows same pattern as RaceEnvironmentPanel
