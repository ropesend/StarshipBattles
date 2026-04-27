from __future__ import annotations

import json
from pathlib import Path


CLASSES = [
    ("Escort", "escort.png", "Escort_Portrait.jpg"),
    ("Frigate", "frigate.png", "Frigate_Portrait.jpg"),
    ("Destroyer", "destroyer.png", "Destroyer_Portrait.jpg"),
    ("Light Cruiser", "light_cruiser.png", "LightCruiser_Portrait.jpg"),
    ("Cruiser", "cruiser.png", "Cruiser_Portrait.jpg"),
    ("Heavy Cruiser", "heavy_cruiser.png", "HeavyCruiser_Portrait.jpg"),
    ("Battle Cruiser", "battlecruiser.png", "BattleCruiser_Portrait.jpg"),
    ("Battleship", "battleship.png", "Battleship_Portrait.jpg"),
    ("Dreadnought", "dreadnought.png", "Dreadnought_Portrait.jpg"),
    ("Superdreadnought", "superdreadnought.png", "SuperDreadnought_Portrait.jpg"),
    ("Monitor", "monitor.png", "Monitor_Portrait.jpg"),
    ("Fighter (Small)", "small_fighter.png", "SmallFighter_Portrait.jpg"),
    ("Fighter (Medium)", "medium_fighter.png", "MediumFighter_Portrait.jpg"),
    ("Fighter (Large)", "large_fighter.png", "LargeFighter_Portrait.jpg"),
    ("Fighter (Heavy)", "heavy_fighter.png", "HeavyFighter_Portrait.jpg"),
    ("Satellite (Small)", "small_satellite.png", "SmallSatellite_Portrait.jpg"),
    ("Satellite (Medium)", "medium_satellite.png", "MediumSatellite_Portrait.jpg"),
    ("Satellite (Large)", "large_satellite.png", "LargeSatellite_Portrait.jpg"),
    ("Satellite (Heavy)", "heavy_satellite.png", "HeavySatellite_Portrait.jpg"),
]


def load_manifest(theme_root: Path) -> dict:
    with (theme_root / "theme.json").open("r", encoding="utf-8") as handle:
        return json.load(handle)


def expected_skin_names() -> list[str]:
    return [skin for _, skin, _ in CLASSES]


def expected_portrait_names() -> list[str]:
    return [portrait for _, _, portrait in CLASSES]


def class_by_skin() -> dict[str, str]:
    return {skin: class_name for class_name, skin, _ in CLASSES}
