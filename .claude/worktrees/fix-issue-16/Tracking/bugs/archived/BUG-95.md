# BUG-95: Load Species dialog — hover/click only registers in top and bottom margins of each row button

## Description

In the "Load Species" dialog (New Game Setup), hovering over a species row only triggers the highlight effect when the mouse is in the top or bottom edge of the button. Hovering over the center of the row — where the species portrait, flag, ship preview, and name label are displayed — does not register.

The root cause is in `race_browser_dialog.py` `_create_race_row()`: the portrait images (60x60 at y+10), flag image, ship preview, and name label are all created as **sibling elements** in the same `scroll_container` as the row button, rather than as children of the button. Because they are created after the button, they sit higher in pygame_gui's z-order and intercept mouse events. Only the narrow margins at the top (~10px) and bottom (~5px) of the 75px-tall button — where no overlay element exists — remain responsive.

**Fix approach:** Either make the overlay elements non-interactive (e.g., set them to not consume mouse events), or restructure so they are children of the button.

### Screenshots

[![Mouse over center of row — no highlight](../../tools/qa_observer/session_data/20260314_085600/images/bug_capture_085722.png)](../../tools/qa_observer/session_data/20260314_085600/images/bug_capture_085722.png)
*Mouse positioned over the center/name area of the first species button — no hover highlight*

[![Mouse in upper third — highlight active](../../tools/qa_observer/session_data/20260314_085600/images/bug_capture_085741.png)](../../tools/qa_observer/session_data/20260314_085600/images/bug_capture_085741.png)
*Mouse in upper margin of the button — hover highlight appears (bright border)*

[![Mouse in lower third — highlight active](../../tools/qa_observer/session_data/20260314_085600/images/bug_capture_085753.png)](../../tools/qa_observer/session_data/20260314_085600/images/bug_capture_085753.png)
*Mouse in lower margin of the button — hover highlight also works*

## Priority
Medium

## Status
Awaiting Confirmation

## Work Log
- 2026-03-14: Created from QA Session 20260314_085600.
- 2026-03-14: **Fixed.** Root cause confirmed: portrait, flag, ship preview (UIImage) and name label (UILabel) elements were created as siblings of the row button in the same scroll_container, sitting higher in pygame_gui's z-order and intercepting hover/click events.
  - **Phase 0:** No active projects touching this file. No doc discrepancies.
  - **Phase 1:** Confirmed overlay elements block `hover_point` → `check_hover` → `_handle_hovering` chain in pygame_gui UIManager.
  - **Phase 2:** Added `test_row_uses_composite_surface_with_button_overlay` test verifying row has exactly 2 elements (UIImage background + UIButton on top).
  - **Phase 3:** Restructured row architecture — instead of 5 sibling elements (button + 3 images + label), now uses 2 elements:
    1. **Composite UIImage** (low z-order, `starting_height=0`) — all visual content (portrait, flag, ship, name) rendered onto a single `pygame.Surface` via new `_render_row_surface()` method.
    2. **Transparent UIButton** (higher z-order, created after image) — handles all hover/click events with no visual interference.
    This eliminates the z-order conflict at the architectural level rather than patching individual elements.
  - **Files modified:** `game/ui/screens/race_browser_dialog.py`, `tests/unit/ui/test_race_browser_dialog.py`
  - **Tests:** 17/17 race browser dialog tests pass.

---
### Implementation Rejected [2026-03-14 10:30]
**Reason:** The fix has made it so that all of the buttons are blank, the species names and ship graphics are not visible.
**New Constraints:** The composite surface approach renders content but it is not displaying on the buttons. The visual content (species name, ship preview) must be visible to the user, not just present as a surface object.
---

- 2026-03-14: **Fix v3 — Deep Investigation.** Root cause of blank buttons: the UIImage (composite surface) was placed at z=0 *behind* the UIButton, but UIButton has an opaque themed background that paints over everything beneath it. The composite surface was rendered correctly but invisible.
  - **Phase 2.5 Design Review:** The two-element approach (UIImage + UIButton) is architecturally wrong — you cannot place visible content behind an opaque element. The correct design is a single element.
  - **Solution:** Single UIButton per row. The composite surface is set as the button's **foreground image** via `button.normal_images = [composite]` (plus hovered/selected/disabled variants). pygame_gui renders button content in order: background → images → text. Since `text=""`, the composite renders directly on the button's background.
  - Image positions set to `(0, 0)` (top-left) since the composite fills the full button area.
  - `button.rebuild()` called after setting images to apply the change.
  - **Result:** One element per row. No z-order conflicts. No separate UIImage. Button handles both display and interaction.
  - **Files modified:** `game/ui/screens/race_browser_dialog.py`, `tests/unit/ui/test_race_browser_dialog.py`
  - **Tests:** 17/17 race browser dialog tests pass. 13176/13176 full suite pass.
