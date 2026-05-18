"""File-existence guard: ``game/strategy/engine/commands/specs.py`` must stay deleted.

PROJ-371 Phase 2 retired ``commands/specs.py``; the
:class:`CommandRegistry` is the single source of truth for command
metadata. Re-introducing a module at that exact path would silently
resurrect the pre-PROJ-371 architecture even if no ``COMMAND_SPECS``
tuple literal appears.

Paired with ``tests/unit/strategy/engine/test_no_specs_tuple_literal.py``:
together they block both ways of reintroducing the deleted module —
file existence (this guard) and the tuple-literal anti-pattern.
"""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RETIRED_SPECS_PATH = REPO_ROOT / "game" / "strategy" / "engine" / "commands" / "specs.py"


def test_specs_module_must_not_re_emerge() -> None:
    """``game/strategy/engine/commands/specs.py`` must not exist."""
    assert not RETIRED_SPECS_PATH.exists(), (
        "commands/specs.py was retired in PROJ-371 Phase 2. "
        "If a new commands config module is needed, choose a different name."
    )
