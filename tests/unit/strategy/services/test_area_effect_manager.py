"""Tests for AreaEffectManager service (PROJ-189 Phase 4)."""

import pytest
from unittest.mock import MagicMock, patch

from game.core.hex_math import HexCoord
from game.strategy.data.storm import Storm, StormEffect
from game.strategy.services.area_effect_manager import (
    AreaEffectManager,
    EnvironmentalEffects,
)


class TestEnvironmentalEffects:
    """Tests for EnvironmentalEffects dataclass."""

    def test_defaults_are_neutral(self):
        """Default values should have no effect on ships."""
        effects = EnvironmentalEffects()

        assert effects.shield_capacity_mult == 1.0
        assert effects.thrust_mult == 1.0
        assert effects.strategic_mult == 1.0
        assert effects.damage_per_tick == 0.0
        assert effects.fuel_drain_per_tick == 0.0
        assert effects.in_storm is False
        assert effects.storm_names == []

    def test_custom_values(self):
        """Can create with custom values."""
        effects = EnvironmentalEffects(
            shield_capacity_mult=0.5,
            thrust_mult=0.7,
            strategic_mult=0.8,
            damage_per_tick=5.0,
            fuel_drain_per_tick=2.0,
            in_storm=True,
            storm_names=["Ion Storm Alpha"],
        )

        assert effects.shield_capacity_mult == 0.5
        assert effects.thrust_mult == 0.7
        assert effects.strategic_mult == 0.8
        assert effects.damage_per_tick == 5.0
        assert effects.fuel_drain_per_tick == 2.0
        assert effects.in_storm is True
        assert effects.storm_names == ["Ion Storm Alpha"]


class TestAreaEffectManager:
    """Tests for AreaEffectManager service."""

    @pytest.fixture
    def manager(self):
        """Create an AreaEffectManager instance."""
        return AreaEffectManager()

    @pytest.fixture
    def mock_galaxy(self):
        """Create a mock galaxy with get_zones_at_global_hex method."""
        galaxy = MagicMock()
        galaxy.get_zones_at_global_hex = MagicMock(return_value=[])
        return galaxy

    def test_empty_hex_returns_neutral_effects(self, manager, mock_galaxy):
        """Empty hex with no zones returns neutral EnvironmentalEffects."""
        mock_galaxy.get_zones_at_global_hex.return_value = []

        result = manager.get_effects_at_global_hex(mock_galaxy, HexCoord(5, 5))

        assert result.shield_capacity_mult == 1.0
        assert result.thrust_mult == 1.0
        assert result.strategic_mult == 1.0
        assert result.damage_per_tick == 0.0
        assert result.fuel_drain_per_tick == 0.0
        assert result.in_storm is False
        assert result.storm_names == []

    def test_single_storm_returns_storm_effects(self, manager, mock_galaxy):
        """Single storm at hex returns that storm's effects."""
        storm = Storm(
            name="Ion Storm Alpha",
            storm_type="ion_storm",
            location=HexCoord(5, 5),
            hex_offsets=frozenset([HexCoord(0, 0)]),
            effects=StormEffect(
                shield_capacity_mult=0.5,
                thrust_mult=0.7,
                strategic_mult=0.8,
                damage_per_tick=5.0,
                fuel_drain_per_tick=2.0,
            ),
        )
        mock_galaxy.get_zones_at_global_hex.return_value = [storm]

        result = manager.get_effects_at_global_hex(mock_galaxy, HexCoord(5, 5))

        assert result.shield_capacity_mult == 0.5
        assert result.thrust_mult == 0.7
        assert result.strategic_mult == 0.8
        assert result.damage_per_tick == 5.0
        assert result.fuel_drain_per_tick == 2.0
        assert result.in_storm is True
        assert result.storm_names == ["Ion Storm Alpha"]

    def test_overlapping_storms_multiplicative_effects_stack(self, manager, mock_galaxy):
        """Two overlapping storms: multiplicative effects stack multiplicatively."""
        storm1 = Storm(
            name="Ion Storm Alpha",
            storm_type="ion_storm",
            location=HexCoord(5, 5),
            hex_offsets=frozenset([HexCoord(0, 0)]),
            effects=StormEffect(
                shield_capacity_mult=0.5,
                thrust_mult=0.8,
                strategic_mult=0.9,
            ),
        )
        storm2 = Storm(
            name="Plasma Storm Beta",
            storm_type="plasma_storm",
            location=HexCoord(5, 5),
            hex_offsets=frozenset([HexCoord(0, 0)]),
            effects=StormEffect(
                shield_capacity_mult=0.6,
                thrust_mult=0.7,
                strategic_mult=0.8,
            ),
        )
        mock_galaxy.get_zones_at_global_hex.return_value = [storm1, storm2]

        result = manager.get_effects_at_global_hex(mock_galaxy, HexCoord(5, 5))

        # Multiplicative stacking: 0.5 * 0.6 = 0.3
        assert result.shield_capacity_mult == pytest.approx(0.5 * 0.6)
        # 0.8 * 0.7 = 0.56
        assert result.thrust_mult == pytest.approx(0.8 * 0.7)
        # 0.9 * 0.8 = 0.72
        assert result.strategic_mult == pytest.approx(0.9 * 0.8)
        assert result.in_storm is True
        assert "Ion Storm Alpha" in result.storm_names
        assert "Plasma Storm Beta" in result.storm_names

    def test_overlapping_storms_additive_effects_sum(self, manager, mock_galaxy):
        """Two overlapping storms: additive effects (damage, fuel drain) sum."""
        storm1 = Storm(
            name="Ion Storm Alpha",
            storm_type="ion_storm",
            location=HexCoord(5, 5),
            hex_offsets=frozenset([HexCoord(0, 0)]),
            effects=StormEffect(
                damage_per_tick=5.0,
                fuel_drain_per_tick=2.0,
            ),
        )
        storm2 = Storm(
            name="Plasma Storm Beta",
            storm_type="plasma_storm",
            location=HexCoord(5, 5),
            hex_offsets=frozenset([HexCoord(0, 0)]),
            effects=StormEffect(
                damage_per_tick=3.0,
                fuel_drain_per_tick=1.5,
            ),
        )
        mock_galaxy.get_zones_at_global_hex.return_value = [storm1, storm2]

        result = manager.get_effects_at_global_hex(mock_galaxy, HexCoord(5, 5))

        # Additive: 5.0 + 3.0 = 8.0
        assert result.damage_per_tick == pytest.approx(8.0)
        # Additive: 2.0 + 1.5 = 3.5
        assert result.fuel_drain_per_tick == pytest.approx(3.5)

    def test_non_storm_zones_filtered_out(self, manager, mock_galaxy):
        """Non-storm zones (stars, planets) at hex are filtered out."""
        # Create mock non-Storm objects (stars, Dyson Spheres)
        mock_star = MagicMock(spec=['name', 'location', 'occupied_hexes'])
        mock_star.name = "Sol"

        mock_dyson = MagicMock(spec=['name', 'location', 'occupied_hexes'])
        mock_dyson.name = "Dyson Sphere"

        mock_galaxy.get_zones_at_global_hex.return_value = [mock_star, mock_dyson]

        result = manager.get_effects_at_global_hex(mock_galaxy, HexCoord(5, 5))

        # Should return neutral effects since no storms present
        assert result.shield_capacity_mult == 1.0
        assert result.thrust_mult == 1.0
        assert result.strategic_mult == 1.0
        assert result.damage_per_tick == 0.0
        assert result.fuel_drain_per_tick == 0.0
        assert result.in_storm is False
        assert result.storm_names == []

    def test_mixed_zone_types_only_storms_affect_result(self, manager, mock_galaxy):
        """Mix of storm and non-storm zones: only storms contribute to effects."""
        mock_star = MagicMock(spec=['name', 'location', 'occupied_hexes'])
        mock_star.name = "Sol"

        storm = Storm(
            name="Ion Storm Alpha",
            storm_type="ion_storm",
            location=HexCoord(5, 5),
            hex_offsets=frozenset([HexCoord(0, 0)]),
            effects=StormEffect(
                shield_capacity_mult=0.5,
                damage_per_tick=5.0,
            ),
        )

        mock_galaxy.get_zones_at_global_hex.return_value = [mock_star, storm]

        result = manager.get_effects_at_global_hex(mock_galaxy, HexCoord(5, 5))

        # Only storm effects should apply
        assert result.shield_capacity_mult == 0.5
        assert result.damage_per_tick == 5.0
        assert result.in_storm is True
        assert result.storm_names == ["Ion Storm Alpha"]

    def test_in_storm_true_only_when_storms_present(self, manager, mock_galaxy):
        """in_storm flag is True only when at least one storm is present."""
        # No storms
        mock_galaxy.get_zones_at_global_hex.return_value = []
        result = manager.get_effects_at_global_hex(mock_galaxy, HexCoord(5, 5))
        assert result.in_storm is False

        # With storm
        storm = Storm(
            name="Test Storm",
            storm_type="test",
            location=HexCoord(5, 5),
            hex_offsets=frozenset([HexCoord(0, 0)]),
            effects=StormEffect(),
        )
        mock_galaxy.get_zones_at_global_hex.return_value = [storm]
        result = manager.get_effects_at_global_hex(mock_galaxy, HexCoord(5, 5))
        assert result.in_storm is True

    def test_storm_names_lists_all_storms(self, manager, mock_galaxy):
        """storm_names should list names of all storms at the hex."""
        storm1 = Storm(
            name="Ion Storm Alpha",
            storm_type="ion_storm",
            location=HexCoord(5, 5),
            hex_offsets=frozenset([HexCoord(0, 0)]),
            effects=StormEffect(),
        )
        storm2 = Storm(
            name="Plasma Storm Beta",
            storm_type="plasma_storm",
            location=HexCoord(5, 5),
            hex_offsets=frozenset([HexCoord(0, 0)]),
            effects=StormEffect(),
        )
        storm3 = Storm(
            name="Gravity Storm Gamma",
            storm_type="gravity_storm",
            location=HexCoord(5, 5),
            hex_offsets=frozenset([HexCoord(0, 0)]),
            effects=StormEffect(),
        )
        mock_galaxy.get_zones_at_global_hex.return_value = [storm1, storm2, storm3]

        result = manager.get_effects_at_global_hex(mock_galaxy, HexCoord(5, 5))

        assert len(result.storm_names) == 3
        assert "Ion Storm Alpha" in result.storm_names
        assert "Plasma Storm Beta" in result.storm_names
        assert "Gravity Storm Gamma" in result.storm_names
