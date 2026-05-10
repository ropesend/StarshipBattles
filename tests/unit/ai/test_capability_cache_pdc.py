"""
PROJ-356 regression: AI capability cache must use tag-based PDC detection.

The bug (pre-fix): `_build_capabilities_cache` filtered PDC weapons via
`w.has_ability('PDCAbility')`. No `PDCAbility` class exists anywhere — PDC
was generalized to a tag-based query in PROJ-241. The string check therefore
always returned False, leaving `pdc_components` permanently empty and
`'has_pdc'` permanently False, regardless of whether the ship actually carried
a PDC weapon.

Source: realtime-combat tech-debt review finding #9 (P1 correctness).

These tests lock in the corrected, tag-based query: the cache must consult
`Component.has_pdc_ability()` (the canonical surface) rather than a
non-existent ability class name.
"""
import pygame
import pytest
from unittest.mock import MagicMock

from game.ai.controller import AIController
from game.engine.spatial import SpatialGrid


@pytest.fixture
def mock_ship():
    """AI-owning ship — minimal stub sufficient for AIController construction."""
    ship = MagicMock()
    ship.id = 'ai_ship'
    ship.position = pygame.math.Vector2(0, 0)
    ship.get_position = MagicMock(return_value=pygame.math.Vector2(0, 0))
    ship.get_team_id = MagicMock(return_value=0)
    ship.get_movement_policy = MagicMock(return_value='kite_max')
    ship.get_targeting_policy = MagicMock(return_value='standard')
    ship.get_formation_members = MagicMock(return_value=[])
    ship.is_in_formation = MagicMock(return_value=False)
    ship.get_formation_master = MagicMock(return_value=None)
    ship.get_max_targets = MagicMock(return_value=1)
    ship.get_current_target = MagicMock(return_value=None)
    ship.get_components_by_ability = MagicMock(return_value=[])
    ship.is_alive = MagicMock(return_value=True)
    return ship


@pytest.fixture
def mock_grid():
    grid = MagicMock(spec=SpatialGrid)
    grid.query_radius = MagicMock(return_value=[])
    grid.query_radius_exact = MagicMock(return_value=[])
    return grid


@pytest.fixture
def ai_controller(mock_ship, mock_grid):
    return AIController(mock_ship, mock_grid, enemy_team_id=1)


def _make_enemy(enemy_id, weapons):
    """Build an enemy ship stub with the given weapon component list."""
    enemy = MagicMock()
    enemy.id = enemy_id
    enemy.name = enemy_id
    enemy.position = pygame.math.Vector2(100, 0)
    enemy.is_alive = True
    enemy.team_id = 1
    enemy.get_components_by_ability = MagicMock(return_value=weapons)
    return enemy


def _make_weapon(*, is_pdc: bool):
    """Build a weapon component stub.

    Mirrors the canonical tag-based PDC surface: `has_pdc_ability()` returns
    True iff any ability has 'pdc' in its tags. The string `has_ability` is
    intentionally configured to return False for `'PDCAbility'` (the dead
    pre-fix path) so any code still reaching for that path is exposed.
    """
    weapon = MagicMock()
    weapon.has_pdc_ability = MagicMock(return_value=is_pdc)
    # The pre-fix code called `w.has_ability('PDCAbility')`. No such class
    # exists; ensure mocks reflect that real components return False here.
    weapon.has_ability = MagicMock(return_value=False)
    return weapon


class TestCapabilityCachePDCTagDetection:
    """Cache must classify PDC weapons via tag-based has_pdc_ability()."""

    def test_pdc_weapon_appears_in_pdc_components(self, ai_controller):
        """A weapon component whose ability carries the 'pdc' tag must be
        listed in cache[entity_id]['pdc_components'] and 'has_pdc' is True."""
        pdc_weapon = _make_weapon(is_pdc=True)
        enemy = _make_enemy('pdc_ship', [pdc_weapon])

        cache = ai_controller._build_capabilities_cache([enemy])

        assert cache['pdc_ship']['has_pdc'] is True
        assert pdc_weapon in cache['pdc_ship']['pdc_components']
        assert len(cache['pdc_ship']['pdc_components']) == 1

    def test_non_pdc_weapon_excluded_from_pdc_components(self, ai_controller):
        """A weapon without the 'pdc' tag is in weapon_components but NOT
        pdc_components, and 'has_pdc' is False."""
        regular_weapon = _make_weapon(is_pdc=False)
        enemy = _make_enemy('regular_ship', [regular_weapon])

        cache = ai_controller._build_capabilities_cache([enemy])

        assert cache['regular_ship']['has_weapons'] is True
        assert regular_weapon in cache['regular_ship']['weapon_components']
        assert cache['regular_ship']['has_pdc'] is False
        assert cache['regular_ship']['pdc_components'] == []

    def test_mixed_weapons_only_pdc_in_pdc_components(self, ai_controller):
        """When a ship carries both a PDC and a non-PDC weapon, only the PDC
        appears in pdc_components, and 'has_pdc' is True."""
        pdc_weapon = _make_weapon(is_pdc=True)
        railgun = _make_weapon(is_pdc=False)
        enemy = _make_enemy('mixed', [railgun, pdc_weapon])

        cache = ai_controller._build_capabilities_cache([enemy])

        assert cache['mixed']['has_pdc'] is True
        assert pdc_weapon in cache['mixed']['pdc_components']
        assert railgun not in cache['mixed']['pdc_components']

    def test_does_not_call_legacy_string_ability_path(self, ai_controller):
        """Regression: the cache must not consult `has_ability('PDCAbility')`.

        No such ability class exists; the pre-fix code therefore always
        produced an empty `pdc_components`. This test asserts the dead code
        path is gone.
        """
        pdc_weapon = _make_weapon(is_pdc=True)
        enemy = _make_enemy('pdc_ship', [pdc_weapon])

        ai_controller._build_capabilities_cache([enemy])

        # The PDC tag check, not the string-named class check, is the source
        # of truth. has_ability must not be called with 'PDCAbility'.
        for call in pdc_weapon.has_ability.call_args_list:
            args, _ = call
            assert 'PDCAbility' not in args
        # And the canonical tag query must have run.
        assert pdc_weapon.has_pdc_ability.called
