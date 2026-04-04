"""Tests for extended AbilityScope enum values (EMPIRE, ALLIED_EMPIRE)."""
import pytest
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
        """Should have 9 total scopes (including FLEET)."""
        assert len(AbilityScope) == 9
