"""
Tests for FleetAuraManager extended coverage.

PROJ-265 Phase 3: Coverage for get_active_bonuses(), external modifier loading,
provider operational check in _recalculate(), and _get_provider_fingerprint() edge cases.
"""

from unittest.mock import MagicMock

from game.simulation.combat.fleet_aura_manager import (
    FleetAuraManager, AuraProvider,
)
from game.simulation.components.abilities.base import AbilityScope


# =============================================================================
# Helpers
# =============================================================================

def _make_ability_class(name):
    """Create a real class with the given name to satisfy type(ab).__name__ checks."""
    return type(name, (), {})


def _make_ship(team_id=0, alive=True, derelict=False, abilities=None):
    """Create a mock ship with optional fleet-scope abilities."""
    ship = MagicMock()
    ship.team_id = team_id
    ship.is_alive = alive
    ship.is_derelict = derelict
    ship.name = f"Ship_team{team_id}"
    ship.fleet_attack_bonus = 0.0
    ship.fleet_defense_bonus = 0.0

    comps = []
    if abilities:
        for ab_name, value, scope in abilities:
            # Create a real instance whose type().__name__ == ab_name
            AbClass = _make_ability_class(ab_name)
            ab = AbClass()
            ab.scope = scope
            ab.value = value
            ab.get_primary_value = lambda v=value: v
            ab.stack_group = "default"

            comp = MagicMock()
            comp.is_operational = True
            comp.ability_instances = [ab]
            comp.name = f"{ab_name}_comp"
            comps.append(comp)

    ship.get_all_components = MagicMock(return_value=comps)
    return ship


def _make_modifier_stack(team_modifiers=None, global_modifiers=None):
    """Build a `ModifierStack` equivalent to the legacy BattleConfig shape.

    PROJ-270 Phase 6.4a replacement for `_make_config`. The legacy branch
    in `FleetAuraManager.initialize(config=...)` read dict-of-dicts from
    a BattleConfig; post-PROJ-270 external modifiers flow through
    `ModifierStack(per_team=..., global_=...)` only.
    """
    from game.simulation.combat.modifier_stack import (
        ModifierEntry,
        ModifierStack,
    )
    from game.simulation.components.modifier_effects import ModifierEffect

    def _entry_from_dict(d, source_prefix):
        effect = ModifierEffect(
            stat_key=d.get("ability", ""),
            value=d.get("value", 0.0),
            operation="add",
            target_ability=None,
            source_modifier_id=d.get("ability", ""),
            source_modifier_name=d.get("source", "Unknown"),
            formula_str="",
            param_value=d.get("value", 0.0),
        )
        return ModifierEntry(
            source=d.get("source", source_prefix),
            stack_group=None,
            effect=effect,
        )

    per_team = {
        team_id: tuple(_entry_from_dict(m, f"team{team_id}") for m in mods)
        for team_id, mods in (team_modifiers or {}).items()
    }
    global_ = tuple(
        _entry_from_dict(m, "global") for m in (global_modifiers or [])
    )
    return ModifierStack(per_team=per_team, global_=global_)


# =============================================================================
# get_active_bonuses Tests
# =============================================================================


class TestGetActiveBonuses:
    """Tests for FleetAuraManager.get_active_bonuses()."""

    def test_returns_provider_bonuses_for_team(self):
        """Returns bonuses from alive providers on the given team."""
        manager = FleetAuraManager()
        ship = _make_ship(team_id=0, abilities=[
            ("ToHitAttackModifier", 5.0, AbilityScope.FLEET),
        ])
        manager.initialize([ship])

        bonuses = manager.get_active_bonuses(team_id=0)

        assert len(bonuses) >= 1
        attack_bonuses = [b for b in bonuses if b['ability'] == 'ToHitAttackModifier']
        assert len(attack_bonuses) == 1
        assert attack_bonuses[0]['value'] == 5.0
        assert attack_bonuses[0]['active'] is True

    def test_excludes_dead_providers(self):
        """Dead ship providers are excluded from active bonuses."""
        manager = FleetAuraManager()
        alive_ship = _make_ship(team_id=0, abilities=[
            ("ToHitAttackModifier", 5.0, AbilityScope.FLEET),
        ])
        manager.initialize([alive_ship])

        # Now mark the provider ship as dead
        alive_ship.is_alive = False

        bonuses = manager.get_active_bonuses(team_id=0)

        provider_bonuses = [b for b in bonuses if b.get('source') != 'Unknown']
        assert len(provider_bonuses) == 0

    def test_excludes_derelict_providers(self):
        """Derelict ship providers are excluded from active bonuses."""
        manager = FleetAuraManager()
        ship = _make_ship(team_id=0, abilities=[
            ("ToHitAttackModifier", 5.0, AbilityScope.FLEET),
        ])
        manager.initialize([ship])

        ship.is_derelict = True

        bonuses = manager.get_active_bonuses(team_id=0)

        provider_bonuses = [b for b in bonuses if b.get('source') != 'Unknown']
        assert len(provider_bonuses) == 0

    def test_excludes_other_team_providers(self):
        """Providers from other teams are not returned."""
        manager = FleetAuraManager()
        ship_t0 = _make_ship(team_id=0, abilities=[
            ("ToHitAttackModifier", 5.0, AbilityScope.FLEET),
        ])
        ship_t1 = _make_ship(team_id=1, abilities=[
            ("ToHitDefenseModifier", 3.0, AbilityScope.FLEET),
        ])
        manager.initialize([ship_t0, ship_t1])

        bonuses_t0 = manager.get_active_bonuses(team_id=0)

        # Should only see team 0's attack modifier
        ability_names = [b['ability'] for b in bonuses_t0]
        assert 'ToHitAttackModifier' in ability_names
        assert 'ToHitDefenseModifier' not in ability_names

    def test_includes_external_modifiers(self):
        """External modifiers (from config) are included."""
        manager = FleetAuraManager()
        ship = _make_ship(team_id=0)
        stack = _make_modifier_stack(
            team_modifiers={0: [{'ability': 'ToHitAttackModifier', 'value': 2.0, 'source': 'Terrain'}]},
        )
        manager.initialize([ship], modifier_stack=stack)

        bonuses = manager.get_active_bonuses(team_id=0)

        ext_bonuses = [b for b in bonuses if b['scope'] == 'external']
        assert len(ext_bonuses) == 1
        assert ext_bonuses[0]['ability'] == 'ToHitAttackModifier'
        assert ext_bonuses[0]['value'] == 2.0

    def test_includes_global_modifiers(self):
        """Global modifiers (team_id=None) are included for any team."""
        manager = FleetAuraManager()
        ship_t0 = _make_ship(team_id=0)
        ship_t1 = _make_ship(team_id=1)
        stack = _make_modifier_stack(
            global_modifiers=[{'ability': 'ToHitDefenseModifier', 'value': 1.0, 'source': 'Storm'}],
        )
        manager.initialize([ship_t0, ship_t1], modifier_stack=stack)

        bonuses_t0 = manager.get_active_bonuses(team_id=0)
        bonuses_t1 = manager.get_active_bonuses(team_id=1)

        # Both teams should see the global modifier
        assert any(b['source'] == 'Storm' for b in bonuses_t0)
        assert any(b['source'] == 'Storm' for b in bonuses_t1)

    def test_empty_when_no_providers(self):
        """Returns empty list when no providers exist."""
        manager = FleetAuraManager()
        ship = _make_ship(team_id=0)  # No abilities
        manager.initialize([ship])

        bonuses = manager.get_active_bonuses(team_id=0)

        assert bonuses == []


# =============================================================================
# External Modifier Loading Tests
# =============================================================================


class TestExternalModifiers:
    """Tests for external modifier loading from BattleConfig."""

    def test_team_modifiers_applied(self):
        """Team-specific modifiers are loaded and applied."""
        manager = FleetAuraManager()
        ship = _make_ship(team_id=0)
        stack = _make_modifier_stack(
            team_modifiers={0: [{'ability': 'ToHitAttackModifier', 'value': 3.0, 'source': 'Terrain'}]},
        )
        manager.initialize([ship], modifier_stack=stack)

        assert ship.fleet_attack_bonus == 3.0

    def test_global_modifiers_applied_to_all_teams(self):
        """Global modifiers are applied to all teams."""
        manager = FleetAuraManager()
        ship_t0 = _make_ship(team_id=0)
        ship_t1 = _make_ship(team_id=1)
        stack = _make_modifier_stack(
            global_modifiers=[{'ability': 'ToHitDefenseModifier', 'value': 2.0, 'source': 'Weather'}],
        )
        manager.initialize([ship_t0, ship_t1], modifier_stack=stack)

        assert ship_t0.fleet_defense_bonus == 2.0
        assert ship_t1.fleet_defense_bonus == 2.0

    def test_no_config_no_externals(self):
        """No config means no external modifiers."""
        manager = FleetAuraManager()
        ship = _make_ship(team_id=0)
        manager.initialize([ship])

        assert len(manager._external) == 0


class TestBonusLookupDefaults:
    """Tests for direct bonus lookup default branches."""

    def test_unknown_team_returns_zero_bonuses(self):
        """Unknown team IDs have no attack or defense aura bonus."""
        manager = FleetAuraManager()
        known_ship = _make_ship(team_id=0)
        unknown_ship = _make_ship(team_id=99)
        manager.initialize([known_ship])

        assert manager.get_attack_bonus(unknown_ship) == 0.0
        assert manager.get_defense_bonus(unknown_ship) == 0.0


# =============================================================================
# Provider Fingerprint Edge Cases
# =============================================================================


class TestProviderFingerprint:
    """Tests for _get_provider_fingerprint() edge cases."""

    def test_dead_provider_has_zero_op_count(self):
        """Dead provider ship has op_count=0 in fingerprint."""
        manager = FleetAuraManager()
        ship = _make_ship(team_id=0, alive=False)
        # PROJ-357: AuraProvider now binds to (component, ability)
        # identity. Direct construction here is exercising the
        # fingerprint helper only — the identity fields are stubbed
        # so the helper has something to walk.
        stub_ab = MagicMock()
        stub_comp = MagicMock()
        stub_comp.is_operational = False
        stub_comp.ability_instances = [stub_ab]
        manager._providers = [AuraProvider(
            ship=ship, component=stub_comp, ability=stub_ab,
            ability_name="Test", value=1.0,
            scope=AbilityScope.FLEET, source_name="Ship", stack_group="default",
        )]

        fp = manager._get_provider_fingerprint([ship])

        # First entry is provider: (id, is_alive=False, is_derelict, op_count=0)
        assert fp[0][1] is False  # is_alive
        assert fp[0][3] == 0  # op_count

    def test_fingerprint_changes_on_component_destruction(self):
        """Fingerprint changes when a provider's component count changes."""
        manager = FleetAuraManager()
        comp = MagicMock()
        comp.is_operational = True

        ship = _make_ship(team_id=0, abilities=[
            ("ToHitAttackModifier", 5.0, AbilityScope.FLEET),
        ])
        manager.initialize([ship])

        fp1 = manager._get_provider_fingerprint([ship])

        # "Destroy" the component
        for c in ship.get_all_components():
            c.is_operational = False

        fp2 = manager._get_provider_fingerprint([ship])

        assert fp1 != fp2  # Fingerprint changed


# =============================================================================
# Provider Operational Check Tests
# =============================================================================


class TestProviderOperationalCheck:
    """Tests for component-destruction-removes-aura in _recalculate()."""

    def test_destroyed_component_removes_aura(self):
        """When the aura-providing component is destroyed, bonus disappears."""
        manager = FleetAuraManager()
        ship = _make_ship(team_id=0, abilities=[
            ("ToHitAttackModifier", 5.0, AbilityScope.FLEET),
        ])
        manager.initialize([ship])

        assert ship.fleet_attack_bonus == 5.0

        # "Destroy" all components on the ship
        for comp in ship.get_all_components():
            comp.is_operational = False

        # Force recalculate
        manager._providers_dirty = True
        manager._recalculate([ship])

        assert ship.fleet_attack_bonus == 0.0


# =============================================================================
# PROJ-270 Phase 9 Task 9.5: _log_placeholder_once coverage
# =============================================================================


class TestLogPlaceholderOnce:
    """Verify `_log_placeholder_once` emits a WARNING exactly once per source.

    PROJ-270 Phase 6.4 added the warning so compiler authors get feedback
    when a new modifier source lacks a stat_key mapping. Task 6.4 was marked
    complete but had no test — skeptic audit flagged this as test-quality gap.
    """

    def test_placeholder_entry_emits_warning_once_per_source(self, caplog):
        """Two entries from the same source → exactly one WARNING."""
        import logging
        from game.simulation.combat.modifier_stack import (
            ModifierEntry, ModifierStack,
        )
        from game.simulation.components.modifier_effects import ModifierEffect

        def _placeholder_entry(source: str) -> ModifierEntry:
            effect = ModifierEffect(
                stat_key="placeholder",
                value=0.0,
                operation="multiply",
                target_ability=None,
                source_modifier_id=source,
                source_modifier_name=source,
                formula_str="",
                param_value=0.0,
            )
            return ModifierEntry(source=source, stack_group=None, effect=effect)

        stack = ModifierStack(
            per_team={
                0: (
                    _placeholder_entry("Storm A"),
                    _placeholder_entry("Storm A"),  # duplicate source
                    _placeholder_entry("Storm B"),
                ),
            },
            global_=(),
        )
        ship = _make_ship(team_id=0)
        manager = FleetAuraManager()

        with caplog.at_level(logging.WARNING, logger="game.simulation.combat.fleet_aura_manager"):
            manager.initialize([ship], modifier_stack=stack)

        placeholder_warnings = [
            r for r in caplog.records
            if "placeholder" in r.getMessage().lower()
        ]
        # Storm A warned once (not twice); Storm B warned once. Total = 2.
        assert len(placeholder_warnings) == 2, (
            f"Expected 2 warnings (one per unique source), got "
            f"{len(placeholder_warnings)}: {[r.getMessage() for r in placeholder_warnings]}"
        )

    def test_placeholder_warning_mentions_source_name(self, caplog):
        """Warning message must identify which source was placeholder."""
        import logging
        from game.simulation.combat.modifier_stack import (
            ModifierEntry, ModifierStack,
        )
        from game.simulation.components.modifier_effects import ModifierEffect

        effect = ModifierEffect(
            stat_key="placeholder",
            value=0.0,
            operation="multiply",
            target_ability=None,
            source_modifier_id="TestStorm",
            source_modifier_name="TestStorm",
            formula_str="",
            param_value=0.0,
        )
        entry = ModifierEntry(source="TestStorm", stack_group=None, effect=effect)
        stack = ModifierStack(per_team={0: (entry,)}, global_=())
        ship = _make_ship(team_id=0)
        manager = FleetAuraManager()

        with caplog.at_level(logging.WARNING, logger="game.simulation.combat.fleet_aura_manager"):
            manager.initialize([ship], modifier_stack=stack)

        messages = [r.getMessage() for r in caplog.records if "placeholder" in r.getMessage().lower()]
        assert any("TestStorm" in m for m in messages), (
            f"Warning should mention source 'TestStorm'; got: {messages}"
        )
