"""Tests for extended AbilityScope enum values (EMPIRE, ALLIED_EMPIRE, ENEMY_*, PLAYER_*)."""
from game.simulation.components.abilities.base import AbilityScope


class TestAbilityScopeExtensions:
    """Verify new EMPIRE and ALLIED_EMPIRE scope values."""

    def test_empire_scope_exists(self):
        """EMPIRE scope should be a valid AbilityScope value."""
        scope = AbilityScope("empire")
        assert scope == AbilityScope.EMPIRE

    def test_allied_empire_scope_exists(self):
        """ALLIED_EMPIRE scope should be a valid AbilityScope value."""
        scope = AbilityScope("allied_empire")
        assert scope == AbilityScope.ALLIED_EMPIRE

    def test_existing_scopes_unchanged(self):
        """Existing scopes should still work."""
        assert AbilityScope("self") == AbilityScope.SELF
        assert AbilityScope("sector") == AbilityScope.SECTOR
        assert AbilityScope("system") == AbilityScope.SYSTEM
        assert AbilityScope("planet") == AbilityScope.PLANET
        assert AbilityScope("allied_sector") == AbilityScope.ALLIED_SECTOR
        assert AbilityScope("allied_system") == AbilityScope.ALLIED_SYSTEM

    def test_all_scopes_count(self):
        """Should have 13 total scopes."""
        assert len(AbilityScope) == 13


class TestEnemyScopes:
    """Verify ENEMY_SECTOR and ENEMY_SYSTEM scope values."""

    def test_enemy_sector_scope_exists(self):
        """ENEMY_SECTOR scope should be a valid AbilityScope value."""
        scope = AbilityScope("enemy_sector")
        assert scope == AbilityScope.ENEMY_SECTOR

    def test_enemy_system_scope_exists(self):
        """ENEMY_SYSTEM scope should be a valid AbilityScope value."""
        scope = AbilityScope("enemy_system")
        assert scope == AbilityScope.ENEMY_SYSTEM

    def test_enemy_sector_string_value(self):
        """ENEMY_SECTOR value should be lowercase string for JSON compatibility."""
        assert AbilityScope.ENEMY_SECTOR.value == "enemy_sector"

    def test_enemy_system_string_value(self):
        """ENEMY_SYSTEM value should be lowercase string for JSON compatibility."""
        assert AbilityScope.ENEMY_SYSTEM.value == "enemy_system"


class TestPlayerScopes:
    """Verify PLAYER_SECTOR and PLAYER_SYSTEM scope values."""

    def test_player_sector_scope_exists(self):
        """PLAYER_SECTOR scope should be a valid AbilityScope value."""
        scope = AbilityScope("player_sector")
        assert scope == AbilityScope.PLAYER_SECTOR

    def test_player_system_scope_exists(self):
        """PLAYER_SYSTEM scope should be a valid AbilityScope value."""
        scope = AbilityScope("player_system")
        assert scope == AbilityScope.PLAYER_SYSTEM

    def test_player_sector_string_value(self):
        """PLAYER_SECTOR value should be lowercase string for JSON compatibility."""
        assert AbilityScope.PLAYER_SECTOR.value == "player_sector"

    def test_player_system_string_value(self):
        """PLAYER_SYSTEM value should be lowercase string for JSON compatibility."""
        assert AbilityScope.PLAYER_SYSTEM.value == "player_system"
