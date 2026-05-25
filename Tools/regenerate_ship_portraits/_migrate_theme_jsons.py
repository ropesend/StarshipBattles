"""One-shot migration script for PROJ-314 Phase 5.

Re-emits every theme.json under assets/Images/ShipThemes/ in the new
canonical schema. Assumes Phase 4's filename normalisation + the Phase 5
skin/portrait basename canonicalisation step have run, so every ship
class shares a single canonical basename across the whole project.

This is a single-use helper; do not import.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path("assets/Images/ShipThemes")

# Canonical basename per ship-class display name. Used for BOTH skin and
# portrait file lookups. Phase 5 normalises every theme to this set.
CANONICAL_BASENAMES: dict[str, str] = {
    "Escort":             "escort",
    "Frigate":            "frigate",
    "Destroyer":          "destroyer",
    "Light Cruiser":      "light_cruiser",
    "Cruiser":            "cruiser",
    "Heavy Cruiser":      "heavy_cruiser",
    "Battle Cruiser":     "battle_cruiser",
    "Battleship":         "battleship",
    "Dreadnought":        "dreadnought",
    "Superdreadnought":   "super_dreadnought",
    "Monitor":            "monitor",
    "Fighter (Small)":    "small_fighter",
    "Fighter (Medium)":   "medium_fighter",
    "Fighter (Large)":    "large_fighter",
    "Fighter (Heavy)":    "heavy_fighter",
    "Satellite (Small)":  "small_satellite",
    "Satellite (Medium)": "medium_satellite",
    "Satellite (Large)":  "large_satellite",
    "Satellite (Heavy)":  "heavy_satellite",
}

THEME_DESCRIPTIONS: dict[str, str] = {
    "Aetherwake": "Sleek silver hulls with luminous turquoise accents and aerodynamic curves.",
    "Atlantians": "Organic curved hulls in deep ocean blues with bioluminescent piping.",
    "Federation": "Classic clean white-and-grey starfleet hulls with red-orange running lights.",
    "Klingons": "Aggressive angular dark green plating with brass and bronze trim.",
    "Ossivine": "Pale bone-white skeletal hulls with calcified ridges and ribbed armor.",
    "Prismsteel": "Faceted chrome hulls with rainbow refractive surfaces and laser etching.",
    "Romulans": "Dark green stealth-shaped hulls with predatory swept-wing silhouettes.",
    "Thoraliens": "Dark industrial metallic ships with cyan glowing highlights.",
    "Voidforged": "Cracked obsidian hulls with magma-orange seams and shadowed crevices.",
}


def main() -> None:
    for theme_dir in sorted(ROOT.iterdir()):
        if not theme_dir.is_dir():
            continue
        theme_name = theme_dir.name
        if theme_name not in THEME_DESCRIPTIONS:
            continue  # Skip unknown.

        portraits_dir = theme_dir / "Portraits"
        has_portraits_dir = portraits_dir.is_dir()

        assets: dict[str, dict] = {}
        for cls, base in CANONICAL_BASENAMES.items():
            skin_rel = f"Skins/{base}.png"
            if not (theme_dir / skin_rel).exists():
                print(f"  WARN {theme_name}/{cls}: skin missing -> {skin_rel}")
            entry: dict[str, object] = {"skin": skin_rel, "scale": 1.0}
            if has_portraits_dir:
                portrait_rel = f"Portraits/{base}.png"
                if (theme_dir / portrait_rel).exists():
                    entry["portrait"] = portrait_rel
            assets[cls] = entry

        payload = {
            "schema_version": 1,
            "name": theme_name,
            "description": THEME_DESCRIPTIONS[theme_name],
            "image_sizes": {
                "skin": [2048, 2048],
                "portrait": [2048, 2048],
            },
            "assets": assets,
        }
        json_path = theme_dir / "theme.json"
        json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        portraits_count = sum(1 for v in assets.values() if "portrait" in v)
        print(
            f"  wrote {theme_name}/theme.json "
            f"({len(assets)} ships, {portraits_count} with portrait)"
        )


if __name__ == "__main__":
    main()
