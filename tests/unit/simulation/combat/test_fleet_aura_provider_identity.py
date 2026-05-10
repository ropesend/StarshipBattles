"""
Tests for FleetAuraManager provider identity (PROJ-357).

Locks in single-provider behavior (characterization) and pins the
multi-provider correctness contract: when a ship has TWO same-class
providers and one is disabled, only the disabled component's value
must be removed — not both, and not neither.

Phase 1 of PROJ-357: characterization + failing-bug-proof tests.
Phase 2 reworks `AuraProvider` to bind to (component, ability_instance)
identity so these tests pass.
"""
from unittest.mock import MagicMock

from game.simulation.combat.fleet_aura_manager import FleetAuraManager
from game.simulation.components.abilities.base import AbilityScope


# =============================================================================
# Helpers
# =============================================================================

def _make_ability(name: str, value: float, scope=AbilityScope.FLEET, stack_group=None):
    """Create an ability instance whose type().__name__ matches `name`.

    Using a real class (not a Mock) is important because
    `_scan_ship` / `_recalculate` use `type(ab).__name__` for lookup
    and a same-class-multi-provider scenario requires multiple
    instances that share the same type.
    """
    AbClass = type(name, (), {})
    ab = AbClass()
    ab.scope = scope
    ab.value = value
    ab.stack_group = stack_group
    # Some aggregator paths read get_primary_value(); not used by
    # FleetAuraManager directly, but provided defensively.
    ab.get_primary_value = lambda v=value: v
    return ab


def _make_component(name: str, abilities, operational=True):
    comp = MagicMock()
    comp.name = name
    comp.is_operational = operational
    comp.ability_instances = list(abilities)
    return comp


def _make_ship(team_id=0, name="Ship", components=None, alive=True):
    ship = MagicMock()
    ship.team_id = team_id
    ship.name = name
    ship.is_alive = alive
    ship.is_derelict = False
    ship.fleet_attack_bonus = 0.0
    ship.fleet_defense_bonus = 0.0
    comps = list(components or ())
    ship.get_all_components = MagicMock(return_value=comps)
    return ship


# =============================================================================
# Single-provider characterization (current correct behavior)
# =============================================================================


class TestSingleProviderCharacterization:
    """Existing single-provider behavior must remain bit-identical."""

    def test_single_provider_contributes_value_to_teammate(self):
        """One fleet-scope ShieldProjection(value=10) → teammate sees 10."""
        ab = _make_ability("ShieldProjection", 10.0)
        comp = _make_component("ShieldProjector_A", [ab])
        provider_ship = _make_ship(team_id=0, name="Provider", components=[comp])
        teammate = _make_ship(team_id=0, name="Teammate")

        manager = FleetAuraManager()
        manager.initialize([provider_ship, teammate])

        assert manager._team_bonuses[0]["ShieldProjection"] == 10.0

    def test_disabling_only_component_drops_contribution_to_zero(self):
        """Disable the sole providing component → teammate contribution = 0."""
        ab = _make_ability("ShieldProjection", 10.0)
        comp = _make_component("ShieldProjector_A", [ab])
        provider_ship = _make_ship(team_id=0, name="Provider", components=[comp])
        teammate = _make_ship(team_id=0, name="Teammate")

        manager = FleetAuraManager()
        manager.initialize([provider_ship, teammate])
        assert manager._team_bonuses[0]["ShieldProjection"] == 10.0

        # Disable the providing component.
        comp.is_operational = False
        manager._providers_dirty = True
        manager._recalculate([provider_ship, teammate])

        assert manager._team_bonuses[0].get("ShieldProjection", 0.0) == 0.0

    def test_killing_provider_ship_drops_contribution_to_zero(self):
        """Provider ship dies → teammate contribution = 0."""
        ab = _make_ability("ShieldProjection", 10.0)
        comp = _make_component("ShieldProjector_A", [ab])
        provider_ship = _make_ship(team_id=0, name="Provider", components=[comp])
        teammate = _make_ship(team_id=0, name="Teammate")

        manager = FleetAuraManager()
        manager.initialize([provider_ship, teammate])
        assert manager._team_bonuses[0]["ShieldProjection"] == 10.0

        provider_ship.is_alive = False
        manager._providers_dirty = True
        manager._recalculate([provider_ship, teammate])

        assert manager._team_bonuses[0].get("ShieldProjection", 0.0) == 0.0


# =============================================================================
# Multi-provider correctness (failing on main pre-PROJ-357 fix)
# =============================================================================


class TestSameClassMultiProviderIdentity:
    """Two same-class providers on one ship — disabling one must remove only that."""

    def test_same_class_multi_provider_disable(self):
        """
        Ship has ShieldProjection A(value=10, group='alpha') and
        B(value=5, group='beta'). Distinct stack groups → SUM (15).
        Disable A. Expected: B remains operational, contribution = 5.

        Pre-fix on main: `_recalculate` walks the ship looking for
        ANY same-class operational ability and treats both providers
        as live, yielding 15 instead of 5.
        """
        ab_a = _make_ability("ShieldProjection", 10.0, stack_group="alpha")
        ab_b = _make_ability("ShieldProjection", 5.0, stack_group="beta")
        comp_a = _make_component("ShieldProjector_A", [ab_a])
        comp_b = _make_component("ShieldProjector_B", [ab_b])
        provider_ship = _make_ship(
            team_id=0, name="Provider", components=[comp_a, comp_b]
        )
        teammate = _make_ship(team_id=0, name="Teammate")

        manager = FleetAuraManager()
        manager.initialize([provider_ship, teammate])

        # Distinct stack groups SUM: 10 + 5 = 15
        assert manager._team_bonuses[0]["ShieldProjection"] == 15.0

        # Disable component A only
        comp_a.is_operational = False
        manager._providers_dirty = True
        manager._recalculate([provider_ship, teammate])

        # Only B remains: contribution should be 5 (NOT 15)
        assert manager._team_bonuses[0]["ShieldProjection"] == 5.0

    def test_same_class_multi_provider_disable_other(self):
        """Symmetric: disable B instead of A. Expected contribution = 10."""
        ab_a = _make_ability("ShieldProjection", 10.0, stack_group="alpha")
        ab_b = _make_ability("ShieldProjection", 5.0, stack_group="beta")
        comp_a = _make_component("ShieldProjector_A", [ab_a])
        comp_b = _make_component("ShieldProjector_B", [ab_b])
        provider_ship = _make_ship(
            team_id=0, name="Provider", components=[comp_a, comp_b]
        )
        teammate = _make_ship(team_id=0, name="Teammate")

        manager = FleetAuraManager()
        manager.initialize([provider_ship, teammate])
        assert manager._team_bonuses[0]["ShieldProjection"] == 15.0

        comp_b.is_operational = False
        manager._providers_dirty = True
        manager._recalculate([provider_ship, teammate])

        assert manager._team_bonuses[0]["ShieldProjection"] == 10.0

    def test_same_class_multi_provider_same_stack_group_max(self):
        """
        Same stack_group → MAX semantics: disable the higher one and the
        contribution drops to the lower; disable the lower and it stays
        at the higher. This pins MAX-semantics correctness.
        """
        ab_a = _make_ability("ShieldProjection", 10.0, stack_group="redundant")
        ab_b = _make_ability("ShieldProjection", 5.0, stack_group="redundant")
        comp_a = _make_component("ShieldProjector_A", [ab_a])
        comp_b = _make_component("ShieldProjector_B", [ab_b])
        provider_ship = _make_ship(
            team_id=0, name="Provider", components=[comp_a, comp_b]
        )
        teammate = _make_ship(team_id=0, name="Teammate")

        manager = FleetAuraManager()
        manager.initialize([provider_ship, teammate])

        # MAX(10, 5) = 10
        assert manager._team_bonuses[0]["ShieldProjection"] == 10.0

        # Disable A (the higher) → MAX(5) = 5
        comp_a.is_operational = False
        manager._providers_dirty = True
        manager._recalculate([provider_ship, teammate])
        assert manager._team_bonuses[0]["ShieldProjection"] == 5.0

        # Re-enable A, disable B (the lower) → MAX(10) = 10
        comp_a.is_operational = True
        comp_b.is_operational = False
        manager._providers_dirty = True
        manager._recalculate([provider_ship, teammate])
        assert manager._team_bonuses[0]["ShieldProjection"] == 10.0

    def test_same_class_multi_provider_ship_disable_removes_all(self):
        """Provider ship dies with two same-class providers → both gone."""
        ab_a = _make_ability("ShieldProjection", 10.0, stack_group="alpha")
        ab_b = _make_ability("ShieldProjection", 5.0, stack_group="beta")
        comp_a = _make_component("ShieldProjector_A", [ab_a])
        comp_b = _make_component("ShieldProjector_B", [ab_b])
        provider_ship = _make_ship(
            team_id=0, name="Provider", components=[comp_a, comp_b]
        )
        teammate = _make_ship(team_id=0, name="Teammate")

        manager = FleetAuraManager()
        manager.initialize([provider_ship, teammate])
        assert manager._team_bonuses[0]["ShieldProjection"] == 15.0

        provider_ship.is_alive = False
        manager._providers_dirty = True
        manager._recalculate([provider_ship, teammate])

        assert manager._team_bonuses[0].get("ShieldProjection", 0.0) == 0.0

    def test_derelict_provider_ship_does_not_contribute(self):
        """
        PROJ-357 audit (CQ-001): a derelict provider ship must not
        contribute fleet auras. Math path, registration scan, and
        `get_active_bonuses()` UI must all agree.
        """
        ab = _make_ability("ShieldProjection", 10.0)
        comp = _make_component("ShieldProjector_A", [ab])
        provider_ship = _make_ship(team_id=0, name="Provider", components=[comp])
        teammate = _make_ship(team_id=0, name="Teammate")

        manager = FleetAuraManager()
        manager.initialize([provider_ship, teammate])
        assert manager._team_bonuses[0]["ShieldProjection"] == 10.0

        # Mark the provider derelict — bonus must drop to 0 and the
        # provider must be skipped (but not dropped) so recovery can
        # restore the contribution without a re-scan.
        provider_ship.is_derelict = True
        manager._providers_dirty = True
        manager._recalculate([provider_ship, teammate])
        assert manager._team_bonuses[0].get("ShieldProjection", 0.0) == 0.0
        # Provider entry retained (skip-not-drop policy).
        assert any(p.ship is provider_ship for p in manager._providers)
        # UI agrees — derelict ship contributes no active bonuses.
        ui = manager.get_active_bonuses(team_id=0)
        assert all(entry['source'] != f"{comp.name} ({provider_ship.name})" for entry in ui)

        # Recovery (no longer derelict) restores the contribution.
        provider_ship.is_derelict = False
        manager._providers_dirty = True
        manager._recalculate([provider_ship, teammate])
        assert manager._team_bonuses[0]["ShieldProjection"] == 10.0

    def test_initialize_skips_derelict_provider_ship(self):
        """
        PROJ-357 audit (CQ-001): `initialize()` must not scan a ship that
        starts the battle derelict — matches the `_recalculate()` skip
        and `get_active_bonuses()` UI filter.
        """
        ab = _make_ability("ShieldProjection", 10.0)
        comp = _make_component("ShieldProjector_A", [ab])
        provider_ship = _make_ship(team_id=0, name="Provider", components=[comp])
        provider_ship.is_derelict = True
        teammate = _make_ship(team_id=0, name="Teammate")

        manager = FleetAuraManager()
        manager.initialize([provider_ship, teammate])

        # No provider was registered for the derelict ship.
        assert all(p.ship is not provider_ship for p in manager._providers)
        assert manager._team_bonuses[0].get("ShieldProjection", 0.0) == 0.0

    def test_unregister_provider_ship_removes_all_entries(self):
        """unregister_ship() with two same-class providers: all entries gone."""
        ab_a = _make_ability("ShieldProjection", 10.0, stack_group="alpha")
        ab_b = _make_ability("ShieldProjection", 5.0, stack_group="beta")
        comp_a = _make_component("ShieldProjector_A", [ab_a])
        comp_b = _make_component("ShieldProjector_B", [ab_b])
        provider_ship = _make_ship(
            team_id=0, name="Provider", components=[comp_a, comp_b]
        )
        teammate = _make_ship(team_id=0, name="Teammate")

        manager = FleetAuraManager()
        manager.initialize([provider_ship, teammate])
        assert len(manager._providers) == 2

        manager.unregister_ship(provider_ship, [teammate])

        # No provider entries reference the removed ship
        assert all(p.ship is not provider_ship for p in manager._providers)
        assert manager._team_bonuses[0].get("ShieldProjection", 0.0) == 0.0
