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


def test_capture_battle_state_does_not_swallow_programming_errors():
    """PROJ-271 Phase 5.3: the try/except in `capture_battle_state()`
    must catch only OSError (IO failures) — NOT `Exception` broadly.

    A broad `except Exception` swallowed the `mode=` TypeError for
    months after PROJ-270 Phase 5.3 deleted the kwarg. Narrowing to
    OSError means programming errors (AttributeError, TypeError,
    ValueError) propagate as real failures."""
    import re
    path = REPO_ROOT / "combat_lab" / "battle_state_capture.py"
    text = path.read_text(encoding="utf-8")
    # Find the capture_battle_state function body.
    start = text.find("def capture_battle_state")
    assert start > 0, "capture_battle_state signature not found"
    end = text.find("\ndef ", start + 1)
    if end < 0:
        end = len(text)
    body = text[start:end]
    # Strip comment lines (the rationale for the narrowing MAY mention
    # the phrase `except Exception`; we only want to flag actual code).
    code_lines = [ln for ln in body.splitlines() if not ln.lstrip().startswith("#")]
    code = "\n".join(code_lines)
    # Match `except Exception:` or `except Exception as X:` as an
    # actual except clause, not a comment.
    pattern = re.compile(r"^\s*except\s+Exception\b", re.MULTILINE)
    assert not pattern.search(code), (
        "capture_battle_state() still catches `except Exception` — this is "
        "the broad pattern that swallowed the `mode=` TypeError for months. "
        "PROJ-271 Phase 5.3 narrowed it to `except OSError` so programming "
        "errors propagate as real failures."
    )


def test_capture_battle_state_propagates_type_error_instead_of_swallowing():
    """PROJ-271 Phase 5.3: if `BattleState.capture_from_engine` raises
    a TypeError or similar (API drift, bad signature), the error must
    propagate — NOT be silently swallowed into a returned None.

    Pre-Phase 5.3, the broad `except Exception` caught everything; any
    signature drift turned into ~40 silent warning lines per run. With
    `except OSError` only, programming errors surface immediately so
    they can be fixed instead of accumulating.
    """
    import pytest
    from combat_lab.battle_state_capture import capture_battle_state

    # An engine stub with no `tick_count` / `ships` — BattleState
    # capture will raise AttributeError or TypeError trying to access
    # the interface. The narrowed except clause must let that propagate.
    class BrokenEngine:
        pass

    with pytest.raises((AttributeError, TypeError, ValueError)):
        capture_battle_state(
            BrokenEngine(), test_id="TEST-PHASE5", state_type="final", seed=42,
        )


def test_battle_state_capture_class_method_does_not_swallow_programming_errors():
    """PROJ-271 Phase 6 (audit follow-up): `BattleStateCapture._capture_state`
    (the class method used by the LIVE production path via context
    manager) must also catch only OSError — not `Exception`.

    Phase 5 narrowed the module-level `capture_battle_state()` but
    missed the class method `_capture_state` that the live caller
    (`test_executor.py:247 BattleStateCapture(...)`) actually uses.
    Same broad-except pattern would swallow the same class of bugs."""
    import re
    path = REPO_ROOT / "combat_lab" / "battle_state_capture.py"
    text = path.read_text(encoding="utf-8")
    # Find the _capture_state class method body.
    start = text.find("def _capture_state")
    assert start > 0, "_capture_state signature not found"
    end = text.find("\n    def ", start + 1)
    if end < 0:
        end = len(text)
    body = text[start:end]
    code_lines = [ln for ln in body.splitlines() if not ln.lstrip().startswith("#")]
    code = "\n".join(code_lines)
    pattern = re.compile(r"^\s*except\s+Exception\b", re.MULTILINE)
    assert not pattern.search(code), (
        "BattleStateCapture._capture_state() still catches `except Exception` "
        "— this is the live production path via the context manager at "
        "test_executor.py:247. The module-level `capture_battle_state` was "
        "narrowed in Phase 5 but this class method was missed. Narrow to "
        "`except OSError`."
    )


def test_battle_state_capture_class_method_propagates_type_error():
    """PROJ-271 Phase 6 (audit follow-up): the class-method variant
    must propagate programming errors just like the module function."""
    import pytest
    from combat_lab.battle_state_capture import BattleStateCapture

    # Engine stub that will cause BattleState.capture_from_engine to
    # raise AttributeError/TypeError — the class method must let it
    # propagate, not silently return None.
    class BrokenEngine:
        pass

    capture = BattleStateCapture(engine=BrokenEngine(), test_id="TEST-PHASE6", seed=42)
    # _timestamp + _battle_id normally set by __enter__; set manually
    # to reach the _capture_state body.
    capture._timestamp = "2026-04-13T00:00:00"
    capture._battle_id = "test-battle-id"
    with pytest.raises((AttributeError, TypeError, ValueError)):
        capture._capture_state("final")


def test_capture_battle_state_still_handles_disk_errors_gracefully(tmp_path, monkeypatch):
    """PROJ-271 Phase 5.3: OSError (disk full, permission denied,
    directory-creation failure) is still caught and returns None.

    The Phase 5.3 narrowing only exposed programming errors —
    environmental IO failures remain non-fatal so batch test runs
    don't explode on a single full-disk write."""
    import os
    from unittest.mock import patch
    from combat_lab import battle_state_capture

    monkeypatch.setattr(battle_state_capture, "BATTLE_STATES_DIR", str(tmp_path))

    # Simulate a disk write failure at the open() call.
    with patch(
        "builtins.open", side_effect=OSError("disk full"),
    ):
        from unittest.mock import MagicMock
        from game.simulation.battle_state import BattleState
        # Build a state object that CAN serialize — but the `open()`
        # call is the failure point. We sidestep `capture_from_engine`
        # here because we're proving the OSError-catching branch.
        with patch.object(
            BattleState, "capture_from_engine",
            return_value=MagicMock(to_json=lambda indent=None: '{"ok":1}'),
        ):
            result = battle_state_capture.capture_battle_state(
                MagicMock(), test_id="TEST-OSERR", state_type="final", seed=1,
            )
    # OSError was caught: returned None, did not crash.
    assert result is None
