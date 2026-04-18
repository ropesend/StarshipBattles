"""PROJ-282 Phase 4: per-panel renderers for `FleetBattleSetupScreen`.

Each module under this package owns one panel's pygame_gui element
construction:

- `left_panel` — side dropdown, fleet list, complex toggles, end conditions
- `center_panel` — fleet hierarchy (TF/SQ), policy dropdowns, ship list
- `right_panel` — available-designs library

Panel builders are module-level functions `build(screen)` that mutate the
screen instance in-place, setting pygame_gui handle attributes (e.g.
`screen._side_dropdown`). The screen owns the `UIManager` and the handles
until Phase 8 slims it; moving the builders out is the separation that
matters here.
"""
