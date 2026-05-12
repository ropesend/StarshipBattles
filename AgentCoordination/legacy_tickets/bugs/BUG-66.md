# BUG-66: Design Workshop - Hide Vehicle Theme Selector During Strategy Layer

## Description

In the Design Workshop when playing the actual game, I should not be able to select different vehicle themes, currently I can select different themes, but they don't actually impact the image of the ships shown. There should not be an option to select a theme in the design workshop when playing the strategy layer.

## Priority
Medium

## Status
Awaiting Confirmation

## Work Log

### Fix
Added `hide_theme_selector` parameter to `BuilderRightPanel`. When the workshop is opened in integrated mode (from strategy layer), the theme dropdown label and control are not created. The theme is locked to the empire's theme which is set automatically in `workshop_screen.py`.

### Files Modified
- `game/ui/screens/builder/right_panel.py` - Added `hide_theme_selector` parameter, conditionally creates theme dropdown and guards refresh logic
- `game/ui/screens/workshop_screen.py` - Passes `hide_theme_selector=self.context.is_integrated()` to right panel

### Test
All 241 workshop/builder tests pass. No regressions.
