"""Tests for PlanetListFilterManager.

PROJ-220 Phase 5 Task 5.1: Extracts filter state management from
PlanetListWindow into a dedicated, testable manager class.
"""
from game.ui.screens.planet_list_filter_manager import PlanetListFilterManager
from game.ui.filters.filter_state_manager import FilterStateManager


# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------

class TestPlanetListFilterManagerInit:
    """Verify default initialization of filter state."""

    def test_all_types_true_initially(self):
        """All 11 planet types should be enabled by default."""
        mgr = PlanetListFilterManager()
        assert all(v is True for v in mgr.filter_types.values())
        assert len(mgr.filter_types) == 11

    def test_expected_type_keys(self):
        """Should have the 11 standard planet type keys."""
        mgr = PlanetListFilterManager()
        expected = {
            'Continental', 'Arid', 'Pelagic', 'Magma', 'Cryoplanet',
            'Barren', 'Jovian', 'Ice Giant', 'Chthonian', 'Ice Dwarf',
            'Planetoid',
        }
        assert set(mgr.filter_types.keys()) == expected

    def test_all_owners_true_initially(self):
        """All 3 owner categories should be enabled by default."""
        mgr = PlanetListFilterManager()
        assert mgr.filter_owner == {'Player': True, 'Enemy': True, 'Unowned': True}

    def test_search_text_empty_initially(self):
        """Search text should be empty string by default."""
        mgr = PlanetListFilterManager()
        assert mgr.search_text == ""

    def test_has_tri_state_manager(self):
        """Should have a FilterStateManager for future binary filters."""
        mgr = PlanetListFilterManager()
        assert isinstance(mgr.tri_state_manager, FilterStateManager)

    def test_filter_ranges_default(self):
        """Filter ranges should have default values."""
        mgr = PlanetListFilterManager()
        assert 'gravity' in mgr.filter_ranges
        assert 'temp' in mgr.filter_ranges
        assert 'mass' in mgr.filter_ranges


# ---------------------------------------------------------------------------
# Toggle Methods
# ---------------------------------------------------------------------------

class TestToggleType:
    """Test toggle_type() method."""

    def test_toggle_type_returns_new_state(self):
        """toggle_type() should return the new state."""
        mgr = PlanetListFilterManager()
        result = mgr.toggle_type('Continental')
        assert result is False

    def test_toggle_type_flips_state(self):
        """toggle_type() should flip the boolean state."""
        mgr = PlanetListFilterManager()
        mgr.toggle_type('Arid')
        assert mgr.filter_types['Arid'] is False
        mgr.toggle_type('Arid')
        assert mgr.filter_types['Arid'] is True

    def test_toggle_type_unknown_returns_false(self):
        """toggle_type() for unknown type returns False."""
        mgr = PlanetListFilterManager()
        result = mgr.toggle_type('Unknown')
        assert result is False


class TestToggleOwner:
    """Test toggle_owner() method."""

    def test_toggle_owner_returns_new_state(self):
        """toggle_owner() should return the new state."""
        mgr = PlanetListFilterManager()
        result = mgr.toggle_owner('Player')
        assert result is False

    def test_toggle_owner_flips_state(self):
        """toggle_owner() should flip the boolean state."""
        mgr = PlanetListFilterManager()
        mgr.toggle_owner('Enemy')
        assert mgr.filter_owner['Enemy'] is False
        mgr.toggle_owner('Enemy')
        assert mgr.filter_owner['Enemy'] is True


# ---------------------------------------------------------------------------
# Set All Methods
# ---------------------------------------------------------------------------

class TestSetAll:
    """Test set_all_types() and set_all_owners() methods."""

    def test_set_all_types_false(self):
        """set_all_types(False) should disable all types."""
        mgr = PlanetListFilterManager()
        mgr.set_all_types(False)
        assert all(v is False for v in mgr.filter_types.values())

    def test_set_all_types_true(self):
        """set_all_types(True) should enable all types."""
        mgr = PlanetListFilterManager()
        mgr.set_all_types(False)  # Disable first
        mgr.set_all_types(True)
        assert all(v is True for v in mgr.filter_types.values())

    def test_set_all_owners_false(self):
        """set_all_owners(False) should disable all owner categories."""
        mgr = PlanetListFilterManager()
        mgr.set_all_owners(False)
        assert all(v is False for v in mgr.filter_owner.values())

    def test_set_all_owners_true(self):
        """set_all_owners(True) should enable all owner categories."""
        mgr = PlanetListFilterManager()
        mgr.set_all_owners(False)
        mgr.set_all_owners(True)
        assert all(v is True for v in mgr.filter_owner.values())


# ---------------------------------------------------------------------------
# get_filter_state
# ---------------------------------------------------------------------------

class TestGetFilterState:
    """Test get_filter_state() returns complete state."""

    def test_returns_dict_with_required_keys(self):
        """get_filter_state() should contain types, owner, search_text."""
        mgr = PlanetListFilterManager()
        state = mgr.get_filter_state()
        assert 'types' in state
        assert 'owner' in state
        assert 'search_text' in state
        assert 'ranges' in state

    def test_state_reflects_current_values(self):
        """get_filter_state() should reflect current filter values."""
        mgr = PlanetListFilterManager()
        mgr.toggle_type('Arid')
        mgr.toggle_owner('Enemy')
        mgr.search_text = "test"
        state = mgr.get_filter_state()
        assert state['types']['Arid'] is False
        assert state['owner']['Enemy'] is False
        assert state['search_text'] == "test"


# ---------------------------------------------------------------------------
# FEAT-16: filter_effects state — dynamically populated from effect-keys
# computed against the current galaxy. Different from `filter_types`/
# `filter_owner` in that there is no fixed key-set; the manager initializes
# with an empty dict and the window populates it after `gather_planets`.
# ---------------------------------------------------------------------------


class TestFilterEffects:
    """`filter_effects: Dict[str, bool]` — keys are effect group-keys
    (e.g. 'EnvironmentalDamage:thermal', 'ThrustModifier')."""

    def test_filter_effects_empty_initially(self):
        """No effect keys until the window populates them."""
        mgr = PlanetListFilterManager()
        assert mgr.filter_effects == {}

    def test_set_all_effects_toggles_all(self):
        mgr = PlanetListFilterManager()
        mgr.filter_effects = {'ThrustModifier': True, 'FuelDrain': True}
        mgr.set_all_effects(False)
        assert mgr.filter_effects == {'ThrustModifier': False, 'FuelDrain': False}
        mgr.set_all_effects(True)
        assert mgr.filter_effects == {'ThrustModifier': True, 'FuelDrain': True}

    def test_get_filter_state_includes_effects(self):
        mgr = PlanetListFilterManager()
        mgr.filter_effects = {'ThrustModifier': True, 'EnvironmentalDamage:thermal': False}
        state = mgr.get_filter_state()
        assert 'effects' in state
        assert state['effects'] == {'ThrustModifier': True, 'EnvironmentalDamage:thermal': False}
