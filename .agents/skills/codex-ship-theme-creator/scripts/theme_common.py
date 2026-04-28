"""Shared helpers for the codex ship-theme-creator skill (PROJ-314).

Updated for the unified theme.json `assets:` schema. The legacy
`<Class>_Portrait.jpg` filename convention has been retired in favour
of data-driven `assets[<class>].portrait` paths.
"""
from __future__ import annotations

import json
from pathlib import Path


# Canonical (display-name, skin-basename, portrait-basename) tuples.
# Skin and portrait basenames are now identical (PROJ-314).
CLASSES = [
    ("Escort",             "escort.png",            "escort.png"),
    ("Frigate",            "frigate.png",           "frigate.png"),
    ("Destroyer",          "destroyer.png",         "destroyer.png"),
    ("Light Cruiser",      "light_cruiser.png",     "light_cruiser.png"),
    ("Cruiser",            "cruiser.png",           "cruiser.png"),
    ("Heavy Cruiser",      "heavy_cruiser.png",     "heavy_cruiser.png"),
    ("Battle Cruiser",     "battle_cruiser.png",    "battle_cruiser.png"),
    ("Battleship",         "battleship.png",        "battleship.png"),
    ("Dreadnought",        "dreadnought.png",       "dreadnought.png"),
    ("Superdreadnought",   "super_dreadnought.png", "super_dreadnought.png"),
    ("Monitor",            "monitor.png",           "monitor.png"),
    ("Fighter (Small)",    "small_fighter.png",     "small_fighter.png"),
    ("Fighter (Medium)",   "medium_fighter.png",    "medium_fighter.png"),
    ("Fighter (Large)",    "large_fighter.png",     "large_fighter.png"),
    ("Fighter (Heavy)",    "heavy_fighter.png",     "heavy_fighter.png"),
    ("Satellite (Small)",  "small_satellite.png",   "small_satellite.png"),
    ("Satellite (Medium)", "medium_satellite.png",  "medium_satellite.png"),
    ("Satellite (Large)",  "large_satellite.png",   "large_satellite.png"),
    ("Satellite (Heavy)",  "heavy_satellite.png",   "heavy_satellite.png"),
]


def load_manifest(theme_root: Path) -> dict:
    """Load and return the theme.json payload.

    PROJ-314: returns the new schema with the top-level `assets:` block
    keyed by display-form ship-class names.
    """
    with (theme_root / "theme.json").open("r", encoding="utf-8") as handle:
        return json.load(handle)


def expected_skin_names() -> list[str]:
    return [skin for _, skin, _ in CLASSES]


def expected_portrait_names() -> list[str]:
    return [portrait for _, _, portrait in CLASSES]


def class_by_skin() -> dict[str, str]:
    return {skin: class_name for class_name, skin, _ in CLASSES}
