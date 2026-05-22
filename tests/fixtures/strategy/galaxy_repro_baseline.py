"""PROJ-473 — golden-baseline capture helper for galaxy-generation reproducibility.

This module is the single source of truth for:

1. The fixed ``GameConfig``\\ s used by the reproducibility tests
   (:data:`BASELINE_CONFIGS`).
2. The **class-(a) already-seeded** snapshot function
   (:func:`snapshot_class_a`) — the fields that MUST stay byte-for-byte equal
   to the pre-change ("golden baseline") code after every PROJ-473 phase.
3. The **full** ``to_dict`` snapshot function (:func:`snapshot_full`) used by
   the class-(b) determinism test.
4. A CLI to (re)capture the committed golden fixture
   (``galaxy_repro_golden.json``).

Class split (decisions.md "Output contract split", design.md H7):

* **Class (a) — already-seeded, golden-pinned.** system placement
  (``global_location``), ``region_id``, ``archetype``, system
  ``intrinsic_abilities``; **warp GEOMETRY** (warp-point ``location`` keyed by
  the structural ``(src_location, dest_location)`` coordinate pair — see the
  KEYING NOTE below); per-star physics (``mass``, ``radius_hexes``,
  ``temperature``, ``luminosity``, ``spectrum``, ``star_type``, ``color``,
  ``age``) + star ``intrinsic_abilities``; per-planet physics
  (``orbit_distance``, ``mass``, ``radius``, ``surface_area``, ``density``,
  ``surface_gravity``, ``surface_pressure``, ``surface_temperature``,
  ``atmosphere``, ``planet_type``, ``surface_water``, ``tectonic_activity``,
  ``magnetic_field``, ``deposits``) + planet ``intrinsic_abilities``; storms.
* **Class (b) — currently-unseeded, NOT golden-pinned.** system ``name``,
  star/planet ``image_id`` + ``image_rotation``, warp ``warp_type``, warp
  ``intrinsic_abilities``. These differ run-to-run on the unchanged baseline;
  they become deterministic across PROJ-473 phases and are asserted only for
  two-run determinism + presence, never against the golden baseline.

KEYING NOTE (PROJ-473 implementation refinement, logged in decisions.md):
the plan said "key warp geometry by ``destination_id``". ``destination_id`` is
the destination system's *name*, which is class-(b) (random on the pre-P0
baseline). Keying geometry by name is therefore NOT stable when the fixture is
captured pre-threading. The geometry itself — the set of warp-point
``location``\\ s and which structural coordinate pair they connect — IS stable
(verified: ``warp geom keyed by (src_loc, dest_loc) equal: True``). So class-(a)
warp geometry is keyed by the stable ``(src global_location, dest
global_location)`` coordinate pair, which survives name/type drift exactly as
the plan intended.
"""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Allow ``python tests/fixtures/strategy/galaxy_repro_baseline.py`` to find the
# ``game`` package when run as a script (repo root is 4 levels up).
_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from game.strategy.data.galaxy import Galaxy
from game.strategy.engine.game_config import GameConfig, PlayerConfig
from game.strategy.engine.game_initializer import GameInitializer

# Path to the committed golden fixture (next to this helper).
GOLDEN_FIXTURE_PATH = Path(__file__).with_name("galaxy_repro_golden.json")


def _players(n: int) -> List[PlayerConfig]:
    return [PlayerConfig(name=f"P{i}", theme="Federation") for i in range(n)]


# The fixed configs the reproducibility tests run against. Each entry is
# (key, GameConfig). ``multi`` is a normal multi-system galaxy; ``n1_retry``
# is the N=1, 4-empire, radius-500, seed-37 config that is KNOWN to force
# exactly one planet-shortage retry (attempt 0 falls through, attempt 1
# succeeds) — see hazard H2. A draw-count shift that flips the retry outcome
# changes the whole lone-system galaxy and is caught as a baseline regression.
BASELINE_CONFIGS: List[Tuple[str, GameConfig]] = [
    (
        "multi",
        GameConfig(
            galaxy_radius=500,
            system_count=5,
            galaxy_type="random",
            galaxy_seed=42,
            players=_players(2),
        ),
    ),
    (
        "n1_retry",
        GameConfig(
            galaxy_radius=500,
            system_count=1,
            galaxy_type="random",
            galaxy_seed=37,
            players=_players(4),
        ),
    ),
]


def _round(value: Any) -> Any:
    """Round floats for stable JSON comparison (full float precision is
    deterministic but JSON round-trips can introduce noise; rounding to a
    high precision keeps byte-for-byte stability without false negatives)."""
    if isinstance(value, float):
        return round(value, 9)
    if isinstance(value, dict):
        return {k: _round(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_round(v) for v in value]
    return value


def _star_class_a(star_dict: Dict[str, Any]) -> Dict[str, Any]:
    keys = (
        "mass", "radius_hexes", "temperature", "luminosity", "spectrum",
        "star_type", "color", "age", "intrinsic_abilities",
    )
    return {k: _round(star_dict.get(k)) for k in keys}


def _planet_class_a(planet_dict: Dict[str, Any]) -> Dict[str, Any]:
    keys = (
        "orbit_distance", "mass", "radius", "surface_area", "density",
        "surface_gravity", "surface_pressure", "surface_temperature",
        "atmosphere", "planet_type", "surface_water", "tectonic_activity",
        "magnetic_field", "deposits", "intrinsic_abilities",
    )
    return {k: _round(planet_dict.get(k)) for k in keys}


def _warp_geometry_class_a(galaxy: Galaxy) -> Dict[str, str]:
    """Class-(a) warp GEOMETRY (S9): warp-point ``location`` keyed by the
    stable structural ``(src_location, dest_location)`` coordinate pair.

    Keyed by coordinates (not ``destination_id`` / name) so name drift on the
    pre-P0 baseline does not perturb the comparison. See module KEYING NOTE.
    """
    name_to_loc = {
        sys.name: str(sys.global_location) for sys in galaxy.systems.values()
    }
    out: Dict[str, str] = {}
    for sys in galaxy.systems.values():
        src = str(sys.global_location)
        for wp in sys.warp_points:
            dest = name_to_loc.get(wp.destination_id, "?")
            out[f"{src}->{dest}"] = str(wp.location)
    return out


def snapshot_class_a(galaxy: Galaxy) -> Dict[str, Any]:
    """Class-(a) already-seeded snapshot — golden-pinned, must be preserved
    byte-for-byte after every PROJ-473 phase."""
    systems: List[Dict[str, Any]] = []
    for sys in galaxy.systems.values():
        sd = sys.to_dict()
        systems.append({
            "global_location": _round(sd.get("global_location")),
            "region_id": sd.get("region_id"),
            "archetype": sd.get("archetype"),
            "intrinsic_abilities": _round(sd.get("intrinsic_abilities")),
            "stars": [_star_class_a(s) for s in sd.get("stars", [])],
            "planets": [_planet_class_a(p) for p in sd.get("planets", [])],
            "storms": _round(sd.get("storms", [])),
        })
    # Stable ordering by global_location string.
    systems.sort(key=lambda s: json.dumps(s["global_location"], sort_keys=True))
    return {
        "systems": systems,
        "warp_geometry": _warp_geometry_class_a(galaxy),
    }


# Class-(b) fields that are still NON-deterministic at a given PROJ-473 phase.
# The full-snapshot two-run determinism test strips these before comparing.
# The set shrank each phase and is now EMPTY (end of Phase 2): names (P0),
# images (P1), and warp type/intrinsics (P2) are all on seeded streams, so the
# full snapshot is deterministic and the xfail marker has been removed.
#   P0: names seeded   -> stripped images + warp type/intrinsics
#   P1: images seeded  -> stripped warp type/intrinsics
#   P2: warp seeded    -> strip nothing (xfail dropped) [CURRENT]
CLASS_B_STILL_NONDETERMINISTIC: frozenset[str] = frozenset()


def _strip_class_b(value: Any, tolerated: frozenset[str]) -> Any:
    """Recursively drop tolerated still-nondeterministic class-(b) keys.

    ``warp_type`` and warp ``intrinsic_abilities`` are paired (S10): when
    ``warp_type`` is tolerated, a warp point's ``intrinsic_abilities`` is also
    stripped (it is rolled from the warp_type). Star/planet
    ``intrinsic_abilities`` are class-(a) and never stripped — they are keyed
    off seeded physics, not the unseeded image/warp streams.
    """
    if isinstance(value, dict):
        out: Dict[str, Any] = {}
        is_warp_point = "destination_id" in value and "warp_type" in value
        for k, v in value.items():
            if k in tolerated:
                continue
            if is_warp_point and "warp_type" in tolerated and k == "intrinsic_abilities":
                continue
            out[k] = _strip_class_b(v, tolerated)
        return out
    if isinstance(value, list):
        return [_strip_class_b(v, tolerated) for v in value]
    return value


def snapshot_full(
    galaxy: Galaxy,
    tolerated: frozenset[str] = CLASS_B_STILL_NONDETERMINISTIC,
) -> Any:
    """Full save-visible snapshot (every ``to_dict`` field, class (a) + (b)),
    with the still-nondeterministic class-(b) fields stripped per ``tolerated``."""
    systems = [
        _strip_class_b(_round(sys.to_dict()), tolerated)
        for sys in galaxy.systems.values()
    ]
    systems.sort(key=lambda s: json.dumps(s["global_location"], sort_keys=True))
    return systems


def build_galaxy(config: GameConfig) -> Galaxy:
    """Run ``GameInitializer.initialize`` and return the generated galaxy."""
    galaxy, _empires = GameInitializer.initialize(config)
    return galaxy


def capture_golden() -> Dict[str, Any]:
    """Capture the class-(a) golden baseline for every config."""
    snapshot: Dict[str, Any] = {
        "_doc": (
            "PROJ-473 golden baseline of class-(a) already-seeded galaxy "
            "generation outputs, captured from the pre-change code. Do NOT "
            "regenerate after threading work begins — it is the immutable "
            "'what current code generates' reference. Regenerate ONLY if the "
            "intended generated output legitimately changes (it must not for "
            "this project). See tests/fixtures/strategy/galaxy_repro_baseline.py."
        ),
        "configs": {},
    }
    for key, config in BASELINE_CONFIGS:
        snapshot["configs"][key] = snapshot_class_a(build_galaxy(config))
    return snapshot


def load_golden() -> Dict[str, Any]:
    with open(GOLDEN_FIXTURE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    logging.disable(logging.CRITICAL)
    data = capture_golden()
    with open(GOLDEN_FIXTURE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    print(f"Wrote golden baseline to {GOLDEN_FIXTURE_PATH}")


if __name__ == "__main__":
    main()
