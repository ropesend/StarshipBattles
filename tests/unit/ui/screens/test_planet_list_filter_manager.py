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
    """`filter_effects: Dict[str, FilterState]` — keys are effect group-keys
    (e.g. 'EnvironmentalDamage:thermal', 'ThrustModifier'). FEAT-25: per-effect
    YES/NO/IGNORE rather than the old FEAT-16 bool."""

    def test_filter_effects_empty_initially(self):
        """No effect keys until the window populates them."""
        mgr = PlanetListFilterManager()
        assert mgr.filter_effects == {}

    def test_set_all_effects_assigns_state(self):
        from game.ui.filters.filter_state import FilterState
        mgr = PlanetListFilterManager()
        mgr.filter_effects = {
            'ThrustModifier': FilterState.IGNORE,
            'FuelDrain': FilterState.IGNORE,
        }
        mgr.set_all_effects(FilterState.YES)
        assert mgr.filter_effects == {
            'ThrustModifier': FilterState.YES,
            'FuelDrain': FilterState.YES,
        }
        mgr.set_all_effects(FilterState.IGNORE)
        assert mgr.filter_effects == {
            'ThrustModifier': FilterState.IGNORE,
            'FuelDrain': FilterState.IGNORE,
        }
        mgr.set_all_effects(FilterState.NO)
        assert mgr.filter_effects == {
            'ThrustModifier': FilterState.NO,
            'FuelDrain': FilterState.NO,
        }

    def test_get_filter_state_includes_effects_as_filterstate(self):
        from game.ui.filters.filter_state import FilterState
        mgr = PlanetListFilterManager()
        mgr.filter_effects = {
            'ThrustModifier': FilterState.YES,
            'EnvironmentalDamage:thermal': FilterState.NO,
        }
        state = mgr.get_filter_state()
        assert 'effects' in state
        assert state['effects'] == {
            'ThrustModifier': FilterState.YES,
            'EnvironmentalDamage:thermal': FilterState.NO,
        }


class TestPresetRoundTrip:
    """FEAT-25: capture/apply must serialize FilterState as `.value` strings
    and round-trip back to enum members. Legacy bool values silently → IGNORE."""

    def _capture(self, filter_effects):
        from unittest.mock import MagicMock
        from game.ui.screens.planet_list_presets import capture_planet_list_state
        txt = MagicMock()
        txt.get_text.return_value = ""
        ui_filters = {
            'gravity': {'min': MagicMock(get_current_value=lambda: 0.0),
                        'max': MagicMock(get_current_value=lambda: 1.0)},
            'temp': {'min': MagicMock(get_current_value=lambda: 0),
                     'max': MagicMock(get_current_value=lambda: 100)},
            'mass': {'min': MagicMock(get_current_value=lambda: 0.0),
                     'max': MagicMock(get_current_value=lambda: 1.0)},
        }
        return capture_planet_list_state(
            columns=[],
            txt_name_filter=txt,
            filter_types={},
            filter_owner={},
            ui_filters=ui_filters,
            filter_effects=filter_effects,
        )

    def _apply(self, state, filter_effects):
        from game.ui.screens.planet_list_presets import apply_planet_list_state
        from unittest.mock import MagicMock
        ui_filters = {
            'effects': {k: MagicMock() for k in filter_effects},
            'gravity': {'min': MagicMock(), 'max': MagicMock()},
            'temp': {'min': MagicMock(), 'max': MagicMock()},
            'mass': {'min': MagicMock(), 'max': MagicMock()},
        }
        apply_planet_list_state(
            state=state,
            columns=[],
            txt_name_filter=MagicMock(),
            filter_types={},
            ui_filters=ui_filters,
            filter_owner={},
            filter_effects=filter_effects,
        )

    def test_round_trip_preserves_filter_state(self):
        from game.ui.filters.filter_state import FilterState
        original = {
            'ThrustModifier': FilterState.YES,
            'FuelDrain': FilterState.NO,
            'ShieldModifier': FilterState.IGNORE,
        }
        captured = self._capture(original)
        # Capture writes .value strings — JSON-friendly.
        assert captured['filters']['effects'] == {
            'ThrustModifier': 'yes',
            'FuelDrain': 'no',
            'ShieldModifier': 'ignore',
        }
        restored = {k: FilterState.IGNORE for k in original}
        self._apply(captured, restored)
        assert restored == original

    def test_apply_drops_legacy_bool_values_to_ignore(self):
        from game.ui.filters.filter_state import FilterState
        # Legacy FEAT-16 preset where effects were bools.
        legacy = {'filters': {'effects': {'ThrustModifier': True, 'FuelDrain': False}}}
        live = {'ThrustModifier': FilterState.YES, 'FuelDrain': FilterState.NO}
        self._apply(legacy, live)
        # Both keys reset to IGNORE (no bool→YES migration).
        assert live == {'ThrustModifier': FilterState.IGNORE, 'FuelDrain': FilterState.IGNORE}

    def test_apply_drops_invalid_string_to_ignore(self):
        from game.ui.filters.filter_state import FilterState
        bogus = {'filters': {'effects': {'ThrustModifier': 'maybe'}}}
        live = {'ThrustModifier': FilterState.YES}
        self._apply(bogus, live)
        assert live == {'ThrustModifier': FilterState.IGNORE}

    def test_apply_skips_keys_not_in_current_galaxy(self):
        from game.ui.filters.filter_state import FilterState
        saved = {'filters': {'effects': {'OldEffect': 'yes', 'ThrustModifier': 'no'}}}
        live = {'ThrustModifier': FilterState.IGNORE}  # OldEffect absent in current galaxy
        self._apply(saved, live)
        assert live == {'ThrustModifier': FilterState.NO}
        assert 'OldEffect' not in live
