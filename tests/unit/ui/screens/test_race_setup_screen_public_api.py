"""PROJ-309 Sub-phase 3.1 — Public API contract for race_setup_screen.

Pins the public symbols importable via the legacy module path so the
post-decomposition shim remains backwards-compatible with the two
production callers (`game/app.py` and
`game/ui/screens/new_game_setup_screen.py`) plus
`tests/unit/ui/screens/test_race_setup_screen.py`.

Pre-split this file MUST pass.

Per the design at
`Projects/active_projects/PROJ-309/findings/race_setup_screen_decomposition.md`:
- `RaceSetupScreen` — the wizard window class. Stable Option-A shim
  guaranteed.
- `RaceBrowserDialog` — leaked re-export from `race_setup_screen.py`'s
  module-level imports. Used today by
  `new_game_setup_screen.py:405`. Pinned for this refactor; the design
  schedules a single-line migration in this same change to make the
  consumer import from `race_browser_dialog` directly. Once the migration
  lands the assertion below switches from "must be importable" to "must
  NOT be importable" — keeping that switch in this test file so the
  contract is reviewable in one place.
- `RaceRandomizer` — re-exported via the module's `from ... import`.
  Patched by `tests/unit/ui/screens/test_race_setup_screen.py`'s FEAT-12
  tests (e.g. `patch("game.ui.screens.race_setup_screen.RaceRandomizer")`).
  The shim must keep this name addressable.
"""
from __future__ import annotations


def test_race_setup_screen_class_importable_from_legacy_path() -> None:
    """`RaceSetupScreen` must remain importable from
    `game.ui.screens.race_setup_screen` so `app.py` and
    `new_game_setup_screen.py` keep working."""
    from game.ui.screens.race_setup_screen import RaceSetupScreen

    # It must be the actual class (not None/sentinel).
    assert isinstance(RaceSetupScreen, type)
    assert RaceSetupScreen.__name__ == "RaceSetupScreen"


def test_race_randomizer_patchable_via_legacy_module_path() -> None:
    """The FEAT-12 tests patch `RaceRandomizer` on this module:
        with patch("game.ui.screens.race_setup_screen.RaceRandomizer") as mock_rand:
    The attribute must therefore be addressable on the module object."""
    import game.ui.screens.race_setup_screen as mod

    assert hasattr(mod, "RaceRandomizer")


def test_race_browser_dialog_currently_importable_from_legacy_path() -> None:
    """`RaceBrowserDialog` is reachable via `race_setup_screen` today
    (line 35 import bleed). `new_game_setup_screen.py:405` relies on it.

    This test pins the CURRENT import path. The design scheduled
    Option-B migration of the single consumer in this same refactor
    (caller will switch to `from game.ui.screens.race_browser_dialog
    import RaceBrowserDialog`). Once that import migration lands the
    leaked re-export can be deleted from the shim — at which point this
    test becomes redundant, NOT failing (the symbol stays addressable
    via its real home `race_browser_dialog`)."""
    from game.ui.screens.race_setup_screen import RaceBrowserDialog

    assert isinstance(RaceBrowserDialog, type)
    assert RaceBrowserDialog.__name__ == "RaceBrowserDialog"
