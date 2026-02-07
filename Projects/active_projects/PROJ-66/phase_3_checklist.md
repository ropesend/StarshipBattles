# Phase 3: Identity Tab UI [Medium]

**Objective:** Build the new Identity tab panel with dropdowns and text inputs
**Tests:** `pytest tests/unit/ui/panels/test_race_identity_panel.py -v`

---

## Task 3.1: Create RaceIdentityPanel Class [Medium]
**File:** `game/ui/panels/race_identity_panel.py` (NEW)
**Tests:** `pytest tests/unit/ui/panels/test_race_identity_panel.py -v`

- [ ] Create `RaceIdentityPanel` class following extracted panel pattern
- [ ] Constructor: `__init__(self, panel, manager, race_config)` — stores references, calls `_create_content()`
- [ ] Create section: **Race Identity** (top)
  - [ ] `race_name` text input: `UITextEntryLine`, placeholder "Species name (e.g., Rossarian)"
  - [ ] `race_name_plural` text input: `UITextEntryLine`, placeholder "Plural (e.g., Rossarians)"
  - [ ] `physical_type` dropdown: `UIDropDownMenu` with PHYSICAL_TYPES list + empty option
- [ ] Create section: **Government** (middle)
  - [ ] `government_type` dropdown: `UIDropDownMenu` with GOVERNMENT_TYPES list + empty option
  - [ ] `government_organization` dropdown: `UIDropDownMenu` with GOVERNMENT_ORGANIZATIONS list + empty option
  - [ ] `leader_title` dropdown: `UIDropDownMenu` with LEADER_TITLES list + empty option
  - [ ] `society_type` dropdown: `UIDropDownMenu` with SOCIETY_TYPES list + empty option
- [ ] Create section: **Faction** (bottom)
  - [ ] `faction_name` text input: `UITextEntryLine`, auto-populated from race_name + government_type
  - [ ] Label: "Auto-generated from Race Name + Government Type. Edit to override."
- [ ] Implement auto-generation logic: when race_name or government_type changes, update faction_name if not manually overridden
- [ ] Store `self._faction_name_overridden = False` flag
- [ ] Write test: `test_identity_panel_creates_successfully`
- [ ] Write test: `test_identity_panel_has_race_name_input`
- [ ] Write test: `test_identity_panel_has_government_type_dropdown`
- [ ] Write test: `test_identity_panel_has_all_dropdowns`
- [ ] Run tests: all pass
**Notes:** Follow `RaceEnvironmentPanel` pattern exactly. Use `pygame_gui.elements.UIDropDownMenu` for selections.

---

## Task 3.2: Implement Data Synchronization Methods [Simple]
**File:** `game/ui/panels/race_identity_panel.py`
**Tests:** `pytest tests/unit/ui/panels/test_race_identity_panel.py -v -k "config"`

- [ ] Implement `update_config()`: reads all UI elements → writes to race_config
  - race_config.race_name = race_name_input.get_text()
  - race_config.race_name_plural = race_name_plural_input.get_text()
  - race_config.faction_name = faction_name_input.get_text()
  - race_config.government_type = government_type_dropdown.selected_option (handle empty)
  - race_config.government_organization = government_org_dropdown.selected_option (handle empty)
  - race_config.leader_title = leader_title_dropdown.selected_option (handle empty)
  - race_config.physical_type = physical_type_dropdown.selected_option (handle empty)
  - race_config.society_type = society_type_dropdown.selected_option (handle empty)
- [ ] Implement `set_from_config()`: reads race_config → sets all UI elements
  - Set text inputs with set_text()
  - Set dropdowns — handle empty string (select first/empty option)
- [ ] Implement `update_labels()`: no-op for this panel (labels are static)
- [ ] Write test: `test_update_config_reads_race_name`
- [ ] Write test: `test_update_config_reads_government_type`
- [ ] Write test: `test_set_from_config_populates_race_name`
- [ ] Write test: `test_set_from_config_populates_dropdowns`
- [ ] Run tests: all pass
**Notes:**

---

## Task 3.3: Implement Faction Name Auto-Generation [Simple]
**File:** `game/ui/panels/race_identity_panel.py`
**Tests:** `pytest tests/unit/ui/panels/test_race_identity_panel.py -v -k "faction"`

- [ ] Create `_auto_generate_faction_name()`: combines race_name + government_type
  - If both set: `"{race_name} {government_type}"` (e.g., "Rossarian Commonwealth")
  - If only race_name: use race_name alone
  - If only government_type: use government_type alone
  - If neither: empty string
- [ ] Call auto-generate when race_name or government_type changes (and not overridden)
- [ ] Track override: if user manually edits faction_name, set `_faction_name_overridden = True`
- [ ] Reset override flag when loading from config if faction matches auto-generated
- [ ] Write test: `test_auto_generate_faction_name_both_set`
- [ ] Write test: `test_auto_generate_faction_name_race_only`
- [ ] Write test: `test_auto_generate_faction_name_override_preserved`
- [ ] Write test: `test_auto_generate_faction_name_resets_when_not_overridden`
- [ ] Run tests: all pass
**Notes:**

---

## Phase 3 Completion Checklist
- [ ] All tasks above checked off
- [ ] Run `pytest tests/unit/ui/panels/test_race_identity_panel.py -v` — all pass
- [ ] Run `pytest tests/ --testmon` — no regressions
- [ ] RaceIdentityPanel follows same pattern as RaceEnvironmentPanel
