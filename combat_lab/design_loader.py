"""Combat Lab design loader — `design_id -> design_dict` (PROJ-274).

Module-level helper so the PROJ-274 `DesignOnlyMaterializer` can load
Combat Lab ship JSONs without requiring a scenario instance. Replaces
the per-scenario `_load_ship(design_id)` closure pattern that Combat
Lab test execution used before PROJ-274.

Path convention: `combat_lab/data/ships/{design_id}` where `design_id`
is treated as the JSON filename (e.g., `Test_Attacker_Beam.json`).
Combat Lab scenarios set `ShipSpec.design_id = filename` — matching the
historical `scenario._load_ship(filename)` behavior byte-for-byte.
"""
from __future__ import annotations

import json
import os
from typing import Any, Dict


_DATA_DIR_CACHE: str | None = None


def _get_data_dir() -> str:
    """Return the absolute path to `combat_lab/data/`.

    Cached across calls. Mirrors the logic used by
    `combat_lab/scenarios/base.py::_get_test_data_dir` but without
    requiring a scenario instance.
    """
    global _DATA_DIR_CACHE
    if _DATA_DIR_CACHE is None:
        # This file lives in combat_lab/design_loader.py, so data/
        # is one level down from its parent.
        module_dir = os.path.dirname(os.path.abspath(__file__))
        _DATA_DIR_CACHE = os.path.join(module_dir, "data")
    return _DATA_DIR_CACHE


def load_combat_lab_design(design_id: str) -> Dict[str, Any]:
    """Load a ship design JSON by filename from `combat_lab/data/ships/`.

    Raises:
        FileNotFoundError: if `design_id` doesn't resolve to a real file.
        json.JSONDecodeError: if the file exists but isn't valid JSON.
    """
    ship_path = os.path.join(_get_data_dir(), "ships", design_id)
    if not os.path.exists(ship_path):
        raise FileNotFoundError(
            f"Ship file not found: {ship_path}\n"
            f"Combat Lab ships live in combat_lab/data/ships/."
        )
    with open(ship_path, "r", encoding="utf-8") as f:
        return json.load(f)


__all__ = ["load_combat_lab_design"]
