"""Shared label formatter for intrinsic ability sources (PROJ-300 D15).

Used by PROJ-301..304 adapters to keep `source_label` consistent across all
intrinsic source kinds. Without this helper, four sibling projects would
ad-hoc the format and the UI would look inconsistent.
"""


def format_intrinsic_source_label(*, entity_name: str, type_name: str) -> str:
    """Canonical label for intrinsic ability sources.

    Format: "{entity_name} ({type_name})" — e.g. "Tarsis IV (Volcanic)",
    "Sol (G-class)", "Warp Point Alpha (unstable)".

    Args:
        entity_name: Display name of the entity (planet name, star name, etc.).
        type_name: Type label (planet_type, star_type, etc.). Caller is
            responsible for any title-casing or formatting they want.

    Returns:
        Formatted label string.
    """
    return f"{entity_name} ({type_name})"
