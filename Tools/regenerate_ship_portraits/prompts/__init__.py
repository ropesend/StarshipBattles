"""Prompt templates for AI portrait generation (PROJ-314).

Exposes :func:`build_prompt` which assembles a final prompt string from
a theme description and a per-ship-class style anchor.
"""
from __future__ import annotations


# Per-ship-class visual descriptions used as composition anchors.
# These describe the silhouette and role; the theme's `description`
# field provides the visual style.
SHIP_CLASS_STYLE_ANCHORS: dict[str, str] = {
    "Escort":             "compact small fast attack escort, sleek angular hull, paired engines",
    "Frigate":            "small mid-tonnage frigate, balanced silhouette, twin engines",
    "Destroyer":          "narrow long destroyer, prominent forward weapons, three engines",
    "Light Cruiser":      "agile light cruiser, mid-range silhouette, command bridge",
    "Cruiser":            "balanced cruiser, mid-tonnage hull, four engines",
    "Heavy Cruiser":      "armored heavy cruiser, broad hull, layered weapon batteries",
    "Battle Cruiser":     "long fast battle cruiser, large engines, prominent main guns",
    "Battleship":         "massive battleship, broad armored hull, multiple turret batteries",
    "Dreadnought":        "imposing dreadnought, large bulk hull, heavy main armament",
    "Superdreadnought":   "colossal superdreadnought, vast armored hull, multiple gun decks",
    "Monitor":            "low-profile monitor, oversized main weapon dwarfing the hull",
    "Fighter (Small)":    "tiny single-seat fighter, sleek streamlined cockpit, twin guns",
    "Fighter (Medium)":   "medium fighter, dual cockpit pods, four wing-mounted guns",
    "Fighter (Large)":    "large fighter, heavy weapon mounts, reinforced wings",
    "Fighter (Heavy)":    "heavy assault fighter, gun-bristling hull, oversized engines",
    "Satellite (Small)":  "small unmanned satellite, modular sensor cluster, solar fins",
    "Satellite (Medium)": "medium satellite, robust sensor array, omnidirectional antennae",
    "Satellite (Large)":  "large platform satellite, weapon turrets, communication dishes",
    "Satellite (Heavy)":  "heavy weapon-platform satellite, multi-turret hull, defensive arrays",
}


def build_prompt(
    theme_name: str,
    theme_description: str,
    ship_class: str,
) -> str:
    """Compose the final prompt sent to ``gpt-image-2``.

    Args:
        theme_name: Human-readable theme name (e.g. "Federation").
        theme_description: ``description`` field from theme.json.
        ship_class: Display-form ship-class key (e.g. "Battleship").

    Returns:
        A multi-paragraph prompt suitable for direct submission.
    """
    anchor = SHIP_CLASS_STYLE_ANCHORS.get(
        ship_class,
        f"{ship_class.lower()} starship",
    )
    description = theme_description or f"{theme_name} faction starships"
    return (
        f"Stylised side-profile portrait of a {anchor} starship "
        f"of the {theme_name} faction. "
        f"Visual style: {description}. "
        f"Composition: centered, full-ship silhouette in 3/4 profile, "
        f"dramatic but readable lighting, transparent or neutral dark "
        f"background, no text, no logos, no humans, no backgrounds with "
        f"planets or stars, only the ship. "
        f"Render at 2048x2048 square aspect ratio with the ship occupying "
        f"~80% of the frame."
    )


__all__ = ["build_prompt", "SHIP_CLASS_STYLE_ANCHORS"]
