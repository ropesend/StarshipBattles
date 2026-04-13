"""Ship-level `shield_bonus_add` plumbing — PROJ-271 Phase 1 Task 1.2.

Tests that `ship.external_stats['shield_bonus_add']` raises
`ship.max_shields` by the bonus value (scaled by any
`shield_capacity_mult` also in external_stats, so the pipeline order is
`(base + flat) × mult` — user-locked decision 2026-04-13).

Follows the `test_storm_shield_interference.py` pattern of materializing
a real ship via `ShipSerializer.from_dict` + shield_generator component
whose baseline `max_shields == 500`.
"""
from game.simulation.entities.ship_serialization import ShipSerializer


def _design_with_shields() -> dict:
    """Ship with one `shield_generator` component → baseline max_shields = 500."""
    return {
        "name": "Cruiser",
        "ship_class": "Escort",
        "vehicle_type": "Ship",
        "design_role": "fleet_escort",
        "theme_id": "Federation",
        "layers": {
            "CORE": [{"id": "bridge"}, {"id": "shield_generator"}],
            "OUTER": [],
            "ARMOR": [],
        },
        "_metadata": {},
    }


def _design_without_shields() -> dict:
    """Ship with NO shield components — baseline max_shields = 0."""
    return {
        "name": "Hull",
        "ship_class": "Escort",
        "vehicle_type": "Ship",
        "design_role": "fleet_escort",
        "theme_id": "Federation",
        "layers": {
            "CORE": [{"id": "bridge"}],
            "OUTER": [],
            "ARMOR": [],
        },
        "_metadata": {},
    }


class TestShieldBonusAddPipelineAtShipLevel:
    """`ship.external_stats['shield_bonus_add']` raises `ship.max_shields`."""

    def test_baseline_max_shields_without_bonus(self, fresh_registries):
        """Ship with baseline shields only (no external_stats bonus) → max_shields == baseline."""
        ship = ShipSerializer.from_dict(_design_with_shields(), registries=fresh_registries)
        ship.recalculate_stats()
        baseline = ship.max_shields
        assert baseline == 500, (
            f"Expected baseline max_shields=500 from shield_generator, got {baseline}"
        )

    def test_flat_bonus_raises_max_shields(self, fresh_registries):
        """Baseline 500 + flat 50 → max_shields == 550.

        Flat bonus added once at ship level, mirroring a virtual extra
        shield component providing `shield_bonus_add` capacity.
        """
        ship = ShipSerializer.from_dict(_design_with_shields(), registries=fresh_registries)
        ship.external_stats = {"shield_bonus_add": 50.0}
        ship.recalculate_stats()
        assert ship.max_shields == 550, (
            f"Expected max_shields=550 (500 + 50 flat), got {ship.max_shields}"
        )

    def test_flat_bonus_stacks_with_storm_mult(self, fresh_registries):
        """Pipeline order: (base + flat) × mult.

        Baseline 500 + flat 50 = 550, then × storm 0.5 = 275.
        """
        ship = ShipSerializer.from_dict(_design_with_shields(), registries=fresh_registries)
        ship.external_stats = {
            "shield_bonus_add": 50.0,
            "shield_capacity_mult": 0.5,
        }
        ship.recalculate_stats()
        # (500 + 50) * 0.5 = 275
        assert ship.max_shields == 275, (
            f"Expected (base + flat) × mult = (500 + 50) × 0.5 = 275, "
            f"got {ship.max_shields}"
        )

    def test_flat_bonus_on_ship_with_no_shields(self, fresh_registries):
        """Ship without shield components + flat 50 → max_shields == 50.

        User semantic: flat bonus acts like a virtual extra shield
        component providing the capacity. A ship with no real shield
        components but a planet aura +50 still gets 50 shields.
        """
        ship = ShipSerializer.from_dict(_design_without_shields(), registries=fresh_registries)
        ship.recalculate_stats()
        assert ship.max_shields == 0, "Baseline check: no shield components → max_shields=0"

        ship.external_stats = {"shield_bonus_add": 50.0}
        ship.recalculate_stats()
        assert ship.max_shields == 50, (
            f"Expected max_shields=50 (flat bonus only, no component), got {ship.max_shields}"
        )

    def test_flat_bonus_stacks_with_capacity_mult_too(self, fresh_registries):
        """PROJ-271 Phase 12.1: the 'virtual extra shield component'
        semantic requires the flat bonus to be scaled by BOTH external
        `shield_capacity_mult` AND external `capacity_mult`, matching
        how real ShieldProjection components compute `capacity`.

        `capacity_mult` isn't currently populated by any fleet aura,
        but if it ever is, the flat bonus should compose identically
        to a real shield component.
        """
        ship = ShipSerializer.from_dict(_design_with_shields(), registries=fresh_registries)
        ship.external_stats = {
            "shield_bonus_add": 50.0,
            "capacity_mult": 2.0,
            "shield_capacity_mult": 0.5,
        }
        ship.recalculate_stats()
        # Real component: base_capacity 500 * 2.0 * 0.5 = 500.
        # Flat bonus: 50 * 2.0 * 0.5 = 50.
        # Total: 500 + 50 = 550.
        assert ship.max_shields == 550, (
            f"Expected flat bonus to be scaled by BOTH capacity_mult AND "
            f"shield_capacity_mult (like a real shield component). "
            f"Got max_shields={ship.max_shields}"
        )

    def test_zero_flat_bonus_is_neutral(self, fresh_registries):
        """`shield_bonus_add` of 0.0 has no effect — max_shields unchanged."""
        ship = ShipSerializer.from_dict(_design_with_shields(), registries=fresh_registries)
        ship.external_stats = {"shield_bonus_add": 0.0}
        ship.recalculate_stats()
        assert ship.max_shields == 500
