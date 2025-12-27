# Bug Tracker

## Active Issues
- [ ] **[Example] Ship mass calculation incorrect for Heavy Hulls**
    - **Reported:** 2025-12-26
    - **Description:** When selecting a Heavy Hull, the total mass seems to be off by 10%.
    - **Related Issues:** (Optional - e.g., "See [Example] Game crash on startup")
    - **Priority:** High



## Resolved Issues
- [x] **[UI] Ship structure component selection indicator not visible**
    - **Resolution:** 
        1. Added `deselect_all()` to `BuilderLeftPanel` and hooked it to Layer Panel events.
        2. Updated `LayerPanel` to check `self.builder.selected_component_group` (object identity) for selection state instead of volatile hash keys.
    - **Notes:** See `docs/lessons_learned.md` for "UI Selection State & Volatile Identifiers".

- [x] **[UI] Range Mount Slider Increment Issue**
    - **Resolution:** Modified `builder_components.py` to cast slider ranges to `float`.
    - **Notes:** See `docs/lessons_learned.md` for "Float Casting for Pygame GUI Sliders".

- [x] **[Example] Game crash on startup**
    - **Resolution:** Fixed indentation error in `main.py`.
    - **Notes:** See `docs/lessons_learned.md` for details on python indentation handling.

