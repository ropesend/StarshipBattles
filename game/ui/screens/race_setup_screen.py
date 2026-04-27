"""Legacy import shim for `RaceSetupScreen`.

PROJ-309 Sub-phase 3.1 decomposed the original 1598-LOC
`race_setup_screen.py` into the `game.ui.screens.race_setup` package
following the PROJ-282 MVVM shape. This module is the Option-A
backwards-compatibility shim: it preserves the legacy import paths
used by `game/app.py:522` and the existing test suite.

Re-exports:
  - `RaceSetupScreen` — the wizard window class (canonical home:
    `game.ui.screens.race_setup.screen`).
  - `RaceRandomizer` — patched on this module by FEAT-12 tests via
    `patch("game.ui.screens.race_setup_screen.RaceRandomizer")`.
    Future cleanup: tests should patch the canonical path
    `game.strategy.systems.race_randomizer.RaceRandomizer`.

Note (PROJ-309 Option-B for `RaceBrowserDialog`): the leaked
`RaceBrowserDialog` re-export at the original
`from game.ui.screens.race_browser_dialog import RaceBrowserDialog`
import was used by `new_game_setup_screen.py` (1 line). That import
has been migrated in the same PROJ-309 change to point at
`game.ui.screens.race_browser_dialog` directly. We keep the
re-export here ONLY for backwards-compat with any third-party caller
that addressed it via this module path; new code must NOT use the
shim.
"""
from game.ui.screens.race_browser_dialog import RaceBrowserDialog
from game.strategy.systems.race_randomizer import RaceRandomizer
from game.ui.screens.race_setup.screen import RaceSetupScreen

__all__ = ["RaceSetupScreen", "RaceBrowserDialog", "RaceRandomizer"]
