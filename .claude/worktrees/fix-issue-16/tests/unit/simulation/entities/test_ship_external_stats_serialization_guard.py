"""PROJ-271 Phase 11.4: `ship.external_stats` must NOT be serialized.

External stats are battle-scoped composition, populated by
`FleetAuraManager._apply_bonuses` from the battle's `ModifierStack`.
They are NOT persistent ship state — they should be recomputed at
every battle start.

If `ShipSerializer.to_dict` serialized them, a ship saved mid-battle
(or from a Battle Results screen) would persist its in-battle buffs
forever. That's a concrete Rule 3 leak risk.

This test locks the invariant both behaviorally (dict doesn't
contain external_stats keys) and by source inspection."""
from pathlib import Path
from game.simulation.entities.ship_serialization import ShipSerializer


REPO_ROOT = Path(__file__).resolve().parents[4]


def _design_with_shields() -> dict:
    return {
        "name": "Cruiser",
        "ship_class": "Escort",
        "vehicle_type": "Ship",
        "design_role": "fleet_escort",
        "theme_id": "Federation",
        "layers": {
            "CORE": [{"id": "bridge"}, {"id": "shield_generator"}],
            "OUTER": [{"id": "laser_cannon"}],
            "ARMOR": [],
        },
        "_metadata": {},
    }


def test_external_stats_not_in_serialized_dict(fresh_registries):
    """A ship with populated external_stats → serialize → result
    has NO `external_stats` key (or empty dict only)."""
    ship = ShipSerializer.from_dict(_design_with_shields(), registries=fresh_registries)
    ship.external_stats = {
        "shield_bonus_add": 50.0,
        "shield_capacity_mult": 0.5,
        "damage_mult": 1.25,
    }
    data = ShipSerializer.to_dict(ship)
    # Either the key is absent, or it's an empty dict. Presence of
    # populated data means a leak.
    assert "external_stats" not in data or not data["external_stats"], (
        f"ShipSerializer.to_dict leaked external_stats into persistent "
        f"ship data: {data.get('external_stats')!r}. External stats are "
        f"battle-scoped composition, not persistent state."
    )


def test_round_tripped_ship_has_empty_external_stats(fresh_registries):
    """Serialize a ship with populated external_stats, round-trip it,
    verify the new ship starts with empty external_stats."""
    ship = ShipSerializer.from_dict(_design_with_shields(), registries=fresh_registries)
    ship.external_stats = {"shield_bonus_add": 99.0}
    data = ShipSerializer.to_dict(ship)

    # Round-trip: serialize / load / check.
    restored = ShipSerializer.from_dict(data, registries=fresh_registries)
    assert restored.external_stats == {} or not restored.external_stats, (
        f"Round-tripped ship has lingering external_stats: "
        f"{restored.external_stats!r}. FleetAuraManager should re-populate "
        f"external_stats at battle start; it must not survive serialization."
    )


def test_ship_serializer_source_does_not_write_external_stats():
    """Text-based guard: `ShipSerializer.to_dict` body must not reference
    `external_stats`. If this check fails, someone is threading the
    battle-scoped dict into persistent data — a Rule 3 leak risk."""
    import re
    path = REPO_ROOT / "game" / "simulation" / "entities" / "ship_serialization.py"
    text = path.read_text(encoding="utf-8")
    # Find the to_dict method body.
    start = text.find("def to_dict")
    assert start > 0, "ShipSerializer.to_dict not found"
    end = text.find("\n    def ", start + 1)
    if end < 0:
        end = len(text)
    body = text[start:end]
    # Strip comments (a comment explaining the exclusion is fine).
    code_lines = [ln for ln in body.splitlines() if not ln.lstrip().startswith("#")]
    code = "\n".join(code_lines)
    assert not re.search(r"\bexternal_stats\b", code), (
        "ShipSerializer.to_dict body references `external_stats` — "
        "that dict is battle-scoped composition and must NOT be written "
        "to persistent save data. Remove the reference or re-architect."
    )
