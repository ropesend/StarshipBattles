"""
Tests for stats panel section visibility resolution.

Tests the data-driven visibility engine that determines which stat sections
to show based on:
1. Section visibility rules (always, ability_present, dynamic)
2. Always-visible overrides per vehicle type
"""
import pytest
from unittest.mock import MagicMock


def _make_mock_ship(vehicle_type="Ship", abilities=None):
    """Create a mock ship with specified abilities on its components."""
    ship = MagicMock()
    ship.vehicle_type = vehicle_type
    ship.layers = {}

    if abilities is None:
        abilities = []

    # Create mock components with specified abilities
    components = []
    for ab_name in abilities:
        comp = MagicMock()
        comp.has_ability = lambda name, ab=ab_name: name == ab
        components.append(comp)

    ship.get_all_components = MagicMock(return_value=components)
    return ship


class TestResolveSectionVisibility:
    """Tests for resolve_section_visibility function."""

    def test_always_visible_section_shown(self):
        """Sections with visibility='always' are always shown."""
        from game.ui.screens.builder.stats_config import resolve_section_visibility
        from game.ui.screens.builder.stat_definitions import SectionDefinition

        section = SectionDefinition(
            key="main", title="Main Systems", column=1, order=10,
            visibility="always", items=[]
        )
        ship = _make_mock_ship()

        assert resolve_section_visibility(section, ship, "Ship", {}) is True

    def test_ability_present_shown_when_ability_exists(self):
        """Sections with ability_present visibility show when ship has the ability."""
        from game.ui.screens.builder.stats_config import resolve_section_visibility
        from game.ui.screens.builder.stat_definitions import SectionDefinition

        section = SectionDefinition(
            key="shields", title="Shields", column=1, order=30,
            visibility={"type": "ability_present", "abilities": ["ShieldProjection"]},
            items=[]
        )
        ship = _make_mock_ship(abilities=["ShieldProjection"])

        assert resolve_section_visibility(section, ship, "Ship", {}) is True

    def test_ability_present_hidden_when_no_ability(self):
        """Sections with ability_present visibility hide when ship lacks the ability."""
        from game.ui.screens.builder.stats_config import resolve_section_visibility
        from game.ui.screens.builder.stat_definitions import SectionDefinition

        section = SectionDefinition(
            key="shields", title="Shields", column=1, order=30,
            visibility={"type": "ability_present", "abilities": ["ShieldProjection"]},
            items=[]
        )
        ship = _make_mock_ship(abilities=[])

        assert resolve_section_visibility(section, ship, "Ship", {}) is False

    def test_always_visible_override_shows_section(self):
        """Sections in always_visible list for vehicle type are shown even without abilities."""
        from game.ui.screens.builder.stats_config import resolve_section_visibility
        from game.ui.screens.builder.stat_definitions import SectionDefinition

        section = SectionDefinition(
            key="maneuvering", title="Maneuvering", column=1, order=20,
            visibility={"type": "ability_present", "abilities": ["CombatPropulsion"]},
            items=[]
        )
        ship = _make_mock_ship(abilities=[])  # No propulsion
        always_visible = {"Ship": ["main", "maneuvering"]}

        assert resolve_section_visibility(section, ship, "Ship", always_visible) is True

    def test_always_visible_override_not_applied_to_wrong_type(self):
        """Always-visible override for Ship does not apply to Drop Pod."""
        from game.ui.screens.builder.stats_config import resolve_section_visibility
        from game.ui.screens.builder.stat_definitions import SectionDefinition

        section = SectionDefinition(
            key="maneuvering", title="Maneuvering", column=1, order=20,
            visibility={"type": "ability_present", "abilities": ["CombatPropulsion"]},
            items=[]
        )
        ship = _make_mock_ship(vehicle_type="Drop Pod", abilities=[])
        always_visible = {"Ship": ["main", "maneuvering"]}

        assert resolve_section_visibility(section, ship, "Drop Pod", always_visible) is False

    def test_multiple_abilities_any_match(self):
        """Section shows if ship has ANY of the listed abilities."""
        from game.ui.screens.builder.stats_config import resolve_section_visibility
        from game.ui.screens.builder.stat_definitions import SectionDefinition

        section = SectionDefinition(
            key="maneuvering", title="Maneuvering", column=1, order=20,
            visibility={"type": "ability_present", "abilities": ["CombatPropulsion", "ManeuveringThruster"]},
            items=[]
        )
        # Ship has ManeuveringThruster but not CombatPropulsion
        ship = _make_mock_ship(abilities=["ManeuveringThruster"])

        assert resolve_section_visibility(section, ship, "Ship", {}) is True

    def test_dynamic_visibility_shown_when_generator_returns_rows(self):
        """Dynamic sections show when their generator returns non-empty rows."""
        from game.ui.screens.builder.stats_config import resolve_section_visibility
        from game.ui.screens.builder.stat_definitions import SectionDefinition, StatDefinition

        section = SectionDefinition(
            key="logistics", title="Logistics", column=2, order=10,
            visibility={"type": "dynamic", "generator": "logistics"},
            items=[], generator="logistics"
        )
        ship = _make_mock_ship()

        # Provide a generator registry that returns rows
        generators = {"logistics": lambda s: [StatDefinition(id="fuel", label="Fuel")]}

        assert resolve_section_visibility(section, ship, "Ship", {}, generators=generators) is True

    def test_dynamic_visibility_hidden_when_generator_returns_empty(self):
        """Dynamic sections hide when their generator returns no rows."""
        from game.ui.screens.builder.stats_config import resolve_section_visibility
        from game.ui.screens.builder.stat_definitions import SectionDefinition

        section = SectionDefinition(
            key="logistics", title="Logistics", column=2, order=10,
            visibility={"type": "dynamic", "generator": "logistics"},
            items=[], generator="logistics"
        )
        ship = _make_mock_ship()

        generators = {"logistics": lambda s: []}

        assert resolve_section_visibility(section, ship, "Ship", {}, generators=generators) is False


class TestSectionDefinition:
    """Tests for SectionDefinition data class."""

    def test_creation(self):
        """SectionDefinition can be created with required fields."""
        from game.ui.screens.builder.stat_definitions import SectionDefinition

        section = SectionDefinition(
            key="main", title="Main Systems", column=1, order=10,
            visibility="always", items=[]
        )
        assert section.key == "main"
        assert section.title == "Main Systems"
        assert section.column == 1
        assert section.order == 10
        assert section.visibility == "always"

    def test_optional_generator(self):
        """SectionDefinition generator defaults to None."""
        from game.ui.screens.builder.stat_definitions import SectionDefinition

        section = SectionDefinition(
            key="main", title="Main", column=1, order=10,
            visibility="always", items=[]
        )
        assert section.generator is None

    def test_with_generator(self):
        """SectionDefinition can hold a generator name."""
        from game.ui.screens.builder.stat_definitions import SectionDefinition

        section = SectionDefinition(
            key="logistics", title="Logistics", column=2, order=10,
            visibility={"type": "dynamic"}, items=[], generator="logistics"
        )
        assert section.generator == "logistics"
