"""Tests for game.core.combat_types — DamageContext frozen dataclass."""
import dataclasses

import pytest

from game.core.combat_types import DamageContext


class TestDamageContext:
    """DamageContext is a frozen DTO for threading attacker identity through damage pipeline."""

    def test_create_with_all_fields(self):
        ctx = DamageContext(attacker="ship_1", source_weapon="laser", damage_type="beam")
        assert ctx.attacker == "ship_1"
        assert ctx.source_weapon == "laser"
        assert ctx.damage_type == "beam"

    def test_create_with_defaults(self):
        ctx = DamageContext()
        assert ctx.attacker is None
        assert ctx.source_weapon is None
        assert ctx.damage_type == "unknown"

    def test_frozen_immutability(self):
        ctx = DamageContext(attacker="ship_1")
        with pytest.raises(dataclasses.FrozenInstanceError):
            ctx.attacker = "ship_2"

    def test_slots(self):
        ctx = DamageContext()
        assert hasattr(ctx, "__slots__")

    def test_import_path(self):
        from game.core.combat_types import DamageContext as DC
        assert DC is DamageContext
