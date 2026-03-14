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
Pending

## Work Log
- 2026-03-14: Created from QA Session 20260314_085600.
