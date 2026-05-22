"""PROJ-473 — galaxy-generation reproducibility anchors.

Two contracts (see design.md H7 + decisions.md "Output contract split"):

* **Class (a) — already-seeded, golden-pinned.** ``test_class_a_matches_golden_baseline``
  asserts the class-(a) fields (placement, star/planet physics, S9 warp
  geometry, storms, intrinsics, archetype) equal the immutable golden baseline
  captured from the PRE-CHANGE code (Task 0.0). This MUST stay green on the
  unchanged baseline and after EVERY PROJ-473 phase. A two-run same-impl check
  is NOT sufficient — only the golden comparison catches a deterministic-but-
  sequence-shifting rewrite (Codex sign-off Blocker 2).

* **Class (b) — currently-unseeded, becomes deterministic across phases.**
  ``test_full_snapshot_two_run_determinism`` is an expected-RED (xfail)
  characterization on the COMPLETE ``to_dict`` snapshot. It is RED on the
  baseline because system names (S8), images (S6/S7), and warp type/intrinsics
  (S10) are unseeded today and differ across two same-seed runs. The xfail
  tolerance narrows each phase (P0 names → P1 images → P2 warp type/intrinsics)
  and the marker is removed at the end of P2.

The N=1 retry config (hazard H2) is included in both contracts so a draw-count
shift that flips the planet-shortage retry outcome is a real regression.
"""
from __future__ import annotations

import logging
import random

import pytest

from tests.fixtures.strategy import galaxy_repro_baseline as baseline


# --------------------------------------------------------------------------
# Class (a): golden-baseline guard — green on baseline and after every phase.
# --------------------------------------------------------------------------
@pytest.mark.parametrize("config_key", [k for k, _ in baseline.BASELINE_CONFIGS])
def test_class_a_matches_golden_baseline(config_key: str) -> None:
    """Class-(a) already-seeded outputs must equal the golden baseline."""
    golden = baseline.load_golden()
    config = dict(baseline.BASELINE_CONFIGS)[config_key]
    galaxy = baseline.build_galaxy(config)
    actual = baseline.snapshot_class_a(galaxy)
    expected = golden["configs"][config_key]
    assert actual == expected, (
        f"Class-(a) galaxy output for config '{config_key}' drifted from the "
        f"PROJ-473 golden baseline. This is a determinism regression: a draw-"
        f"order or stream-topology error. See design.md H7."
    )


def test_n1_retry_actually_fires() -> None:
    """Hazard H2: the n1_retry config must actually exercise the planet-shortage
    seed-bump retry path (attempt > 0), otherwise the golden guard would not
    catch a retry-flipping draw-count shift."""
    config = dict(baseline.BASELINE_CONFIGS)["n1_retry"]
    logger = logging.getLogger("game.strategy.engine.game_initializer")

    records: list[logging.LogRecord] = []

    class _Capture(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            records.append(record)

    handler = _Capture()
    prev_level = logger.level
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    try:
        baseline.build_galaxy(config)
    finally:
        logger.removeHandler(handler)
        logger.setLevel(prev_level)

    shortage_logs = [r for r in records if "planet shortage" in r.getMessage()]
    assert shortage_logs, (
        "n1_retry config did not trigger a planet-shortage retry; pick a "
        "seed/empire combo that forces attempt > 0 (hazard H2)."
    )


# --------------------------------------------------------------------------
# Class (b): full-snapshot two-run determinism — GREEN since end of Phase 2.
# --------------------------------------------------------------------------
# PROJ-473 brought every class-(b) field onto a seeded stream: names (P0),
# images (P1), warp type/intrinsics (P2). The full snapshot — including the
# previously-unseeded image_id/image_rotation/warp_type/warp intrinsic fields —
# is now deterministic across two same-seed runs, so the expected-RED xfail
# marker has been REMOVED (Phase 2 Task 2.2). This now asserts strictly.
@pytest.mark.parametrize("config_key", [k for k, _ in baseline.BASELINE_CONFIGS])
def test_full_snapshot_two_run_determinism(config_key: str) -> None:
    """Two same-seed runs of the CURRENT code must produce identical FULL
    snapshots (no stripping). GREEN now that ALL class-(b) fields are seeded
    (end of Phase 2)."""
    config = dict(baseline.BASELINE_CONFIGS)[config_key]
    # tolerated=frozenset() => compare the complete snapshot, including the
    # still-unseeded image / warp-type fields.
    snap1 = baseline.snapshot_full(baseline.build_galaxy(config), tolerated=frozenset())
    snap2 = baseline.snapshot_full(baseline.build_galaxy(config), tolerated=frozenset())
    assert snap1 == snap2


@pytest.mark.parametrize("config_key", [k for k, _ in baseline.BASELINE_CONFIGS])
def test_class_b_seeded_fields_are_deterministic(config_key: str) -> None:
    """Class-(b) fields that have ALREADY been brought onto a seeded stream
    must be deterministic across two same-seed runs. The tolerance set
    (:data:`baseline.CLASS_B_STILL_NONDETERMINISTIC`) shrinks each phase; this
    test asserts everything OUTSIDE it is stable.

    P0: system ``name`` is asserted (now seeded). image_id/image_rotation/
    warp_type/warp intrinsic_abilities are still tolerated (P1/P2).
    """
    config = dict(baseline.BASELINE_CONFIGS)[config_key]
    snap1 = baseline.snapshot_full(baseline.build_galaxy(config))
    snap2 = baseline.snapshot_full(baseline.build_galaxy(config))
    assert snap1 == snap2


# --------------------------------------------------------------------------
# Global-state companion assertion — coarse tripwire only (flips in Phase 3).
# --------------------------------------------------------------------------
def test_generation_does_not_touch_global_random_state() -> None:
    """Phase 3: with the two load-bearing ``random.seed`` calls removed and all
    generation draws on seeded per-instance streams, a full ``initialize()`` run
    must NOT mutate module-level ``random`` state.

    NOTE (coarse tripwire only — necessary but NOT sufficient): an unchanged
    ``getstate()`` proves the global seed is gone, but does NOT by itself prove
    determinism (a fresh unseeded ``Random()`` fallback would also leave global
    state untouched while producing nondeterministic output). The authoritative
    determinism proof is ``test_full_snapshot_two_run_determinism`` +
    ``test_class_a_matches_golden_baseline`` above.
    """
    config = dict(baseline.BASELINE_CONFIGS)["multi"]
    # Perturb global state to a known non-default position first, so a stray
    # module-level draw inside generation would be detectable as a change.
    random.seed(0xC0FFEE)
    before = random.getstate()
    baseline.build_galaxy(config)
    after = random.getstate()
    assert before == after, (
        "Galaxy generation mutated module-level random state. Some draw on the "
        "generation path still reads global random instead of a seeded "
        "per-instance stream. See PROJ-473 Phase 3 / the Pattern #18 guard."
    )


def test_no_rng_public_facade_does_not_touch_global_random_state() -> None:
    """PROJ-473 Task 3.3 / Codex audit finding (f): the backward-compatible
    public facade contract is that ``Galaxy.generate_systems(rng=None)``
    normalizes the missing streams to fresh seeded ``Random`` instances at one
    composition site — it must NOT fall back to module-level ``random``.

    A no-rng caller is allowed to be non-reproducible (no fixed seed), but it
    must never read or perturb the global module RNG (that is the latent
    determinism hole design.md flagged and the Pattern #18 guard exists to
    prevent escaping into).
    """
    from game.strategy.data.galaxy import Galaxy

    random.seed(0xBEEF)
    before = random.getstate()
    galaxy = Galaxy(radius=2000)
    galaxy.generate_systems(count=3, min_dist=100)  # no rng at all
    galaxy.generate_warp_lanes()  # no rng at all
    after = random.getstate()
    assert before == after, (
        "The no-rng public generation facade touched module-level random "
        "state. Per the backward-compatible-facade contract (decisions.md "
        "Task 3.3) it must normalize rng=None to fresh per-instance Random "
        "streams, not consume module random."
    )
