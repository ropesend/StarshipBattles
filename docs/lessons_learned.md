# Lessons Learned & Technical Post-Mortems

This document serves as the long-term memory for the AI agent. Before fixing a bug, check this file to see if a similar issue has been solved before.

## [Example] Game crash on startup (2025-12-26)
**Cause:** An `IndentationError` was introduced in `main.py` during a refactor of the initialization logic. Python is sensitive to mixed tabs/spaces or incorrect block levels.
**Fix:** aligned the `try/except` block correctly.
**Prevention:**
- Always adhere to strict indentation rules (4 spaces).
- Run the code immediately after any refactor involving control flow changes.

## [UI] Range Mount Slider Increment Issue (2025-12-26)
**Cause:** The `min_val` and `max_val` from `modifiers.json` were Integers (0, 3). `pygame_gui.UIHorizontalSlider` seemingly respects the type of the range values; when given integers, it may default to integer stepping (1.0) regardless of the configured `click_increment` (0.1), or process internal math as integers.
**Fix:** Explicitly cast `min_val`, `max_val`, and `start_value` to `float` when creating the `UIHorizontalSlider`.
**Prevention:**
- When using UI sliders that require decimal precision, ALWAYS explicitly cast range limits to `float`.
- In TDD, verify not just the specific configuration values (like 0.1) but also the data types being passed to libraries.
