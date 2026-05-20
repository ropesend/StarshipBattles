"""PROJ-354B Phase 1.3 — Pure replay verifier.

Pure, layer-agnostic comparison of a captured replay outcome against a
replayed outcome. Lives in ``game/simulation/replay/`` so it depends only
on simulation/replay DTOs — never on Strategy, UI, or AI. The
:class:`ReplayVerificationCoordinator` (in
``game/strategy/services/``) is the background driver that owns
threading, queueing, and sidecar IO; this module owns only the equality
oracle.

Equality is structural with two intentional relaxations rooted in the
JSON-only data contract carried by ``ReplayOutcome.data``:

    * ``list`` and ``tuple`` are treated as the same sequence type. The
      capture-side serializer (``battle_outcome_to_dict``) emits all
      tuple fields as lists because JSON has no tuple type, while
      replayed outcomes still carry the original tuples until they are
      dict-ified. Distinguishing them would produce false-positive
      diffs on every replay (PROJ-354B audit CJ-01).
    * Float scalars compare via ``math.isclose`` with tight
      tolerances. FPU nondeterminism (operation reordering, FMA
      differences) yields sub-ULP drift between two semantically
      identical battles even on the same seed; strict ``!=`` would
      flag those as failures (PROJ-354B audit CJ-02).

Each leaf mismatch produces one :class:`Difference`. List-length
mismatches emit a synthetic ``{"__len__": ...}`` payload rather than
the full lists, so the cap-25 budget isn't consumed by large blobs
(PROJ-354B audit CJ-03). The returned diff is capped at ``max_diffs``
(default 25); the ``diff_truncated`` flag and ``total_diff_count``
field record any overflow.

``verify_replay_outcome`` accepts a :class:`ReplayRecord` (whose
``outcome.data`` is the captured dict) and a freshly-replayed
:class:`BattleOutcome`. It dictifies the latter via
``battle_outcome_to_dict`` and delegates to ``compute_outcome_diff``.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

from game.simulation.battle_outcome import BattleOutcome
from game.simulation.replay.replay_record import ReplayRecord
from game.simulation.replay.replay_outcome_serde import battle_outcome_to_dict


_DEFAULT_MAX_DIFFS = 25

# Float comparison tolerances (PROJ-354B audit CJ-02). Calibrated tight
# enough to surface real divergence but loose enough to absorb FPU
# nondeterminism on simulation outputs (HP, modifier values, damage).
_FLOAT_REL_TOL = 1e-9
_FLOAT_ABS_TOL = 1e-9


@dataclass(frozen=True)
class Difference:
    """One structural mismatch between expected and actual values.

    ``path`` is a tuple of dict keys / list indices identifying the
    diverging leaf. The empty tuple denotes the root.
    """

    path: Tuple[Any, ...]
    expected: Any
    actual: Any


@dataclass(frozen=True)
class ReplayVerificationResult:
    """Outcome of :func:`verify_replay_outcome`.

    ``passed`` is True iff ``diff`` is empty AND ``diff_truncated`` is
    False (the latter guard prevents a truncated all-different diff from
    masquerading as a pass).
    """

    replay_id: str
    passed: bool
    diff: Tuple[Difference, ...]
    diff_truncated: bool
    total_diff_count: int


# ---------------------------------------------------------------------------
# Diff walker
# ---------------------------------------------------------------------------


def compute_outcome_diff(
    expected: Any,
    actual: Any,
    max_diffs: int = _DEFAULT_MAX_DIFFS,
) -> Tuple[Tuple[Difference, ...], bool, int]:
    """Walk ``expected`` and ``actual`` in lock-step; return diff + flags.

    Returns ``(diff, diff_truncated, total_diff_count)``:
        * ``diff`` — tuple of up to ``max_diffs`` differences in walk
          order.
        * ``diff_truncated`` — True iff the total exceeded ``max_diffs``.
        * ``total_diff_count`` — actual count of differences detected
          (the walker continues counting after the cap is reached so the
          caller can distinguish "20 diffs" from "200 diffs" without
          paying the cost of materializing the latter).
    """
    diffs: List[Difference] = []
    # Use a list-of-one for the count so the inner closure can mutate
    # without ``nonlocal``.
    counter = [0]

    def _record(path: Tuple[Any, ...], expected_val: Any, actual_val: Any) -> None:
        counter[0] += 1
        if len(diffs) < max_diffs:
            diffs.append(Difference(path=path, expected=expected_val, actual=actual_val))

    def _walk(path: Tuple[Any, ...], exp: Any, act: Any) -> None:
        # Both dicts: compare key sets, then walk shared keys.
        if isinstance(exp, dict) and isinstance(act, dict):
            exp_keys = set(exp.keys())
            act_keys = set(act.keys())
            if exp_keys != act_keys:
                # Missing/extra keys are leaves at this level.
                missing = exp_keys - act_keys
                extra = act_keys - exp_keys
                for k in sorted(missing, key=str):
                    _record(path + (k,), exp[k], None)
                for k in sorted(extra, key=str):
                    _record(path + (k,), None, act[k])
            for k in sorted(exp_keys & act_keys, key=str):
                _walk(path + (k,), exp[k], act[k])
            return
        # Both sequences (list or tuple): compare lengths, walk shared
        # indices. List/tuple are structurally equivalent here per the
        # JSON data contract (CJ-01).
        if isinstance(exp, (list, tuple)) and isinstance(act, (list, tuple)):
            if len(exp) != len(act):
                # CJ-03: emit a compact length-mismatch payload rather
                # than the full lists. Otherwise a single deep mismatch
                # can carry tens of KB and consume one of only 25 diff
                # slots with low-signal data.
                _record(
                    path,
                    {"__len__": len(exp)},
                    {"__len__": len(act)},
                )
                # Walk shared prefix to surface any leaf diffs.
                shared = min(len(exp), len(act))
                for i in range(shared):
                    _walk(path + (i,), exp[i], act[i])
                return
            for i in range(len(exp)):
                _walk(path + (i,), exp[i], act[i])
            return
        # CJ-01: do not flag list-vs-tuple as a type mismatch (handled
        # by the sequence branch above; this guard is belt-and-braces
        # for nested edge cases reached when one side is a sequence
        # and the other is not).
        # Type mismatch — but treat float vs int as comparable scalars
        # so e.g. ``0`` and ``0.0`` don't diverge spuriously.
        if type(exp) is not type(act):
            if not (isinstance(exp, (int, float)) and isinstance(act, (int, float))
                    and not isinstance(exp, bool) and not isinstance(act, bool)):
                _record(path, exp, act)
                return
        # Scalar comparison. CJ-02: floats compare via math.isclose;
        # bool/int and other scalars use strict ``!=``.
        if isinstance(exp, float) or isinstance(act, float):
            # bool is an int subclass; keep it on the strict path.
            if isinstance(exp, bool) or isinstance(act, bool):
                if exp != act:
                    _record(path, exp, act)
                return
            if not math.isclose(
                float(exp), float(act),
                rel_tol=_FLOAT_REL_TOL,
                abs_tol=_FLOAT_ABS_TOL,
            ):
                _record(path, exp, act)
            return
        if exp != act:
            _record(path, exp, act)

    _walk((), expected, actual)
    return tuple(diffs), counter[0] > max_diffs, counter[0]


# ---------------------------------------------------------------------------
# High-level entry
# ---------------------------------------------------------------------------


def verify_replay_outcome(
    record: ReplayRecord,
    replayed_outcome: BattleOutcome,
    *,
    max_diffs: int = _DEFAULT_MAX_DIFFS,
) -> ReplayVerificationResult:
    """Compare ``record.outcome.data`` to ``battle_outcome_to_dict(replayed_outcome)``.

    Returns a :class:`ReplayVerificationResult` describing the comparison.
    The replay is considered passing only if no differences were detected
    AND the diff was not truncated (a truncated diff means the count is
    underestimated, so we cannot certify pass).
    """
    expected_dict: Dict[str, Any] = record.outcome.data
    actual_dict: Dict[str, Any] = battle_outcome_to_dict(replayed_outcome)
    diff, truncated, total = compute_outcome_diff(
        expected_dict, actual_dict, max_diffs=max_diffs
    )
    passed = total == 0 and not truncated
    return ReplayVerificationResult(
        replay_id=record.replay_id,
        passed=passed,
        diff=diff,
        diff_truncated=truncated,
        total_diff_count=total,
    )


__all__ = [
    "Difference",
    "ReplayVerificationResult",
    "compute_outcome_diff",
    "verify_replay_outcome",
]
