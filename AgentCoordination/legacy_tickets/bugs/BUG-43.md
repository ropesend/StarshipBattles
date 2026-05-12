# BUG-43: Colony view flags have white frame and wrong aspect ratio

## Description
In the strategy view the flags on the colony view should not have the white frame, and they appear to be vertically compressed, they should be the same aspect ratio as the original image.

## Priority
Medium (Visual bug)

## Status
Awaiting Confirmation

## Work Log
- 2026-01-23: Ticket created
- 2026-01-23: Fixed. Updated colony flag rendering:
  - Removed white frame border (`pygame.draw.rect` call)
  - Changed aspect ratio calculation to preserve original image proportions
  - Files modified: `game/ui/screens/strategy_renderer.py`
