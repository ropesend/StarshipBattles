# PROJ-400 Verification Report

**Date:** 2026-05-09
**Branch:** `feat/03c-phase-aware-execution`
**Scope:** Tier 1 B-01 — fix `AttributeError` raised by deleted static wrapper in `NewGameSetupScreen._create_ui()`.

## What was done

1. **Confirmed the bug** at `game/ui/screens/new_game_setup_screen.py:348`: `self.save_name_input.set_text(self.generate_default_save_name())` — `NewGameSetupScreen.generate_default_save_name` was deleted in PROJ-392; canonical home is `NewGameSetupController.generate_default_save_name()` (`@staticmethod`, no args).
2. **TDD red:** added `TestCreateUiConstructionPath` (2 tests) to `tests/unit/ui/screens/test_new_game_setup_extended.py`. The class drives `screen._create_ui()` directly with `pygame_gui.elements` constructors patched to MagicMocks (existing `MockNewGameSetupUiBuilder` fixture skips `_create_ui` entirely, which is why the bug was missed). Pre-fix run produced the predicted `AttributeError: 'NewGameSetupScreen' object has no attribute 'generate_default_save_name'` at line 348.
3. **Fix:** replaced the call with `NewGameSetupController.generate_default_save_name()`. Mirrors the existing `NewGameSetupController.validate_save_name(...)` pattern at line 162; the import is already present at line 66 — no plumbing changes.
4. **Green:** focused TDD pair passes; `pytest tests/ -k new_game_setup -q` → 104 passed.
5. **Sweep:** `rg "self\.generate_default_save_name|self\.validate_save_name" game/` returns zero hits — single-site blind spot.

## Surprises

None. The bug was exactly where the remediation plan said it was; the fix is one line.

## Deferrals

None. PROJ-400 is single-phase and complete.
