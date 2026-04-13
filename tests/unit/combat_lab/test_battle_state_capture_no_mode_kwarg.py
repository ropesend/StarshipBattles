"""Regression guard: `combat_lab/battle_state_capture.py` must not pass
`mode=` to `BattleState.capture_from_engine()`.

Context: PROJ-270 Phase 5.3 deleted the `BattleState.mode` field, but the
deletion audit missed 2 call sites in `combat_lab/battle_state_capture.py`
that were still passing `mode="test"`. The `BattleState.capture_from_engine()`
classmethod signature never accepted a `mode` parameter, so these calls
raised `TypeError: capture_from_engine() got an unexpected keyword argument
'mode'` on every invocation. Because the call sites were wrapped in a
broad try/except that logs a warning, the failures were silent — ship-state
snapshots simply never got captured during any Combat Lab test run.

The warning spam manifested as ~40 lines per Combat Lab run:

    Failed to capture initial state: BattleState.capture_from_engine() got
    an unexpected keyword argument 'mode'
    Failed to capture final state: BattleState.capture_from_engine() got
    an unexpected keyword argument 'mode'

Fix: delete `mode="test"` from both callers + the stale `mode:` line in
the `capture_from_engine` docstring.
"""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def test_battle_state_capture_does_not_pass_mode_kwarg():
    """`combat_lab/battle_state_capture.py` must not call capture_from_engine
    with a mode= kwarg — the parameter was deleted in PROJ-270 Phase 5.3."""
    path = REPO_ROOT / "combat_lab" / "battle_state_capture.py"
    text = path.read_text(encoding="utf-8")
    # Look for `mode=` kwarg anywhere in capture_from_engine() call sites.
    assert "mode=" not in text, (
        "combat_lab/battle_state_capture.py still passes `mode=` to "
        "BattleState.capture_from_engine(). The BattleState.mode field "
        "was deleted in PROJ-270 Phase 5.3 and capture_from_engine() "
        "never accepted a mode= parameter. Delete the kwarg."
    )


def test_capture_from_engine_docstring_does_not_mention_mode():
    """`BattleState.capture_from_engine` docstring must not list a
    `mode:` parameter — the docstring is the API contract."""
    path = REPO_ROOT / "game" / "simulation" / "battle_state.py"
    text = path.read_text(encoding="utf-8")
    # Find the capture_from_engine function body (classmethod).
    # Signature starts at "def capture_from_engine" and runs until the
    # next "def ". Look for "mode:" in between.
    start = text.find("def capture_from_engine")
    assert start > 0, "capture_from_engine signature not found"
    # Find the end of the docstring (next def after start).
    end = text.find("\n    def ", start + 1)
    if end < 0:
        end = len(text)
    body = text[start:end]
    # The docstring should not describe a `mode:` parameter.
    assert "mode: Battle mode" not in body and "        mode:" not in body, (
        "capture_from_engine docstring still lists a `mode:` parameter, "
        "but the method signature has no such parameter. Delete the "
        "stale docstring line."
    )
