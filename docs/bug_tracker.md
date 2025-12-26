# Bug Tracker

## Active Issues
    - **[UI] Ship structure component selection indicator not visible**
    - **Reported:** 2025-12-26
    - **Description:** In the ship builder window, when I select a component or group of components in the Ship Structure section, it should remain colored the way selecting a component in the Components section keeps that component colored. Currently, when I click on a componment the background color briefly changes, then imediatly reverts.
    - **Related Issues:** 
    - **Priority:** Normal

    - [ ] **[Example] Ship mass calculation incorrect for Heavy Hulls**
    - **Reported:** 2025-12-26
    - **Description:** When selecting a Heavy Hull, the total mass seems to be off by 10%.
    - **Related Issues:** (Optional - e.g., "See [Example] Game crash on startup")
    - **Priority:** High



## Resolved Issues
- [x] **[UI] Range Mount Slider Increment Issue**
    - **Resolution:** Modified `builder_components.py` to cast slider ranges to `float`.
    - **Notes:** See `docs/lessons_learned.md` for "Float Casting for Pygame GUI Sliders".

- [x] **[Example] Game crash on startup**
    - **Resolution:** Fixed indentation error in `main.py`.
    - **Notes:** See `docs/lessons_learned.md` for details on python indentation handling.

