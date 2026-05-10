"""Contract tests for the SuperweaponRegistry (PROJ-364 Phase 2).

Pins the invariants that downstream Phase 3 dispatch (and PROJ-363
CommandSpec cross-check) relies on:
- Every spec's ``order_type`` is a real ``OrderType`` member.
- Every spec's ``event_type`` is a real ``EventType`` member.
- Every spec's ``consume_ship`` is ``bool``.
- Every spec's ``ability_name`` (when not ``None``) is registered in the
  component registry.
- Every spec's ``stabilizer_blocks`` entries are real ``OrderType`` values.
- The set of order types matches the strategic-superweapon subset of the
  PROJ-363 ``COMMAND_SPECS`` ``'superweapon'`` category (excluding
  ``SELF_DESTRUCT``).

Mirrors ``test_stabilizer_registry.py`` style.
"""
from __future__ import annotations

import pytest

from game.strategy.data.order_types import OrderType
from game.strategy.events.event_types import EventType
from game.strategy.services.superweapon_registry import (
    SUPERWEAPONS,
    SuperweaponSpec,
    find_superweapon_spec,
)


class TestSpecBasicShape:
    def test_all_specs_have_valid_order_type(self):
        for spec in SUPERWEAPONS:
            assert isinstance(spec.order_type, OrderType), (
                f"{spec.order_type!r} is not an OrderType"
            )

    def test_all_specs_have_valid_event_type(self):
        for spec in SUPERWEAPONS:
            assert isinstance(spec.event_type, EventType), (
                f"{spec.event_type!r} is not an EventType"
            )

    def test_all_specs_consume_ship_is_bool(self):
        for spec in SUPERWEAPONS:
            assert isinstance(spec.consume_ship, bool), (
                f"{spec.order_type}: consume_ship={spec.consume_ship!r} not bool"
            )

    def test_all_specs_target_type_in_allowed_set(self):
        allowed = {"planet", "dict", "none"}
        for spec in SUPERWEAPONS:
            assert spec.target_type in allowed, (
                f"{spec.order_type}: target_type={spec.target_type!r} "
                f"not in {allowed}"
            )

    def test_all_specs_stabilizer_blocks_are_order_types(self):
        for spec in SUPERWEAPONS:
            assert isinstance(spec.stabilizer_blocks, tuple)
            for member in spec.stabilizer_blocks:
                assert isinstance(member, OrderType), (
                    f"{spec.order_type}: stabilizer_blocks contains {member!r} "
                    f"which is not an OrderType"
                )

    def test_specs_are_frozen(self):
        spec = SUPERWEAPONS[0]
        with pytest.raises(Exception):  # FrozenInstanceError subclass of Exception
            spec.order_type = OrderType.MOVE  # type: ignore[misc]


class TestExpectedSuperweaponSet:
    """The 5 strategic superweapons must be present; SELF_DESTRUCT must not."""

    def test_expected_order_types(self):
        expected = {
            OrderType.IMPLODE_PLANET,
            OrderType.STELLERATE_STAR,
            OrderType.OPEN_WARP_POINT,
            OrderType.CLOSE_WARP_POINT,
            OrderType.CREATE_DYSON_SPHERE,
        }
        actual = {spec.order_type for spec in SUPERWEAPONS}
        assert actual == expected

    def test_self_destruct_excluded(self):
        assert find_superweapon_spec(OrderType.SELF_DESTRUCT) is None

    def test_only_stellerate_star_consumes_ship(self):
        suicide = [s for s in SUPERWEAPONS if s.consume_ship]
        assert len(suicide) == 1
        assert suicide[0].order_type == OrderType.STELLERATE_STAR

    def test_only_stellerate_star_has_no_ability_name(self):
        no_ability = [s for s in SUPERWEAPONS if s.ability_name is None]
        assert len(no_ability) == 1
        assert no_ability[0].order_type == OrderType.STELLERATE_STAR


class TestFindSuperweaponSpec:
    def test_lookup_returns_correct_spec(self):
        spec = find_superweapon_spec(OrderType.IMPLODE_PLANET)
        assert spec is not None
        assert spec.order_type == OrderType.IMPLODE_PLANET
        assert spec.ability_name == "DestroyPlanet"
        assert spec.event_type == EventType.PLANET_DESTROYED

    def test_lookup_returns_none_for_unregistered(self):
        # MOVE is not a superweapon
        assert find_superweapon_spec(OrderType.MOVE) is None
        # SELF_DESTRUCT is intentionally excluded
        assert find_superweapon_spec(OrderType.SELF_DESTRUCT) is None


class TestAbilityRegistryConsistency:
    """Each spec's ability_name (if not None) must be registered as a
    real component-ability in the production registry."""

    def test_ability_names_registered(self, fresh_registries):
        components = fresh_registries.components
        # Build the set of all ability names known to any component.
        # ``components`` maps component-id -> Component instance whose
        # ``abilities`` attribute is a dict of ability-name -> ability data.
        known_abilities: set[str] = set()
        for comp_id, comp in components.items():
            abilities = getattr(comp, 'abilities', None) or {}
            if isinstance(abilities, dict):
                known_abilities.update(abilities.keys())

        for spec in SUPERWEAPONS:
            if spec.ability_name is None:
                continue
            assert spec.ability_name in known_abilities, (
                f"{spec.order_type}: ability_name={spec.ability_name!r} "
                f"not found in component registry"
            )


class TestProj363CommandSpecCrossLink:
    """Cross-check against PROJ-363 COMMAND_SPECS 'superweapon' category.

    The strategic superweapon order types in this registry must equal the
    'superweapon' CommandSpecs that have a non-None order_type, minus
    SELF_DESTRUCT (intentionally excluded from PROJ-364).
    """

    def test_order_types_match_command_specs(self):
        try:
            from game.strategy.engine.commands.registry import (
                command_registry,
                seed_default_commands,
            )
        except ImportError:
            pytest.skip("PROJ-371 command_registry not available")
        if len(command_registry) == 0:
            seed_default_commands(command_registry)
        COMMAND_SPECS = tuple(command_registry.all())

        sw_command_order_types = {
            cmd.order_type for cmd in COMMAND_SPECS
            if cmd.category == 'superweapon' and cmd.order_type is not None
        }
        # COMMAND_SPECS includes SELF_DESTRUCT; PROJ-364 excludes it.
        expected_in_registry = sw_command_order_types - {OrderType.SELF_DESTRUCT}

        actual = {spec.order_type for spec in SUPERWEAPONS}
        assert actual == expected_in_registry

    def test_ability_names_match_command_specs(self):
        """Each spec's ability_name must match the action_ability_name on
        the corresponding PROJ-363 CommandSpec (when both are set)."""
        try:
            from game.strategy.engine.commands.registry import (
                command_registry,
                seed_default_commands,
            )
        except ImportError:
            pytest.skip("PROJ-371 command_registry not available")
        if len(command_registry) == 0:
            seed_default_commands(command_registry)
        COMMAND_SPECS = tuple(command_registry.all())

        cmd_by_order = {
            cmd.order_type: cmd for cmd in COMMAND_SPECS
            if cmd.category == 'superweapon' and cmd.order_type is not None
        }

        for spec in SUPERWEAPONS:
            cmd = cmd_by_order.get(spec.order_type)
            assert cmd is not None, (
                f"No CommandSpec for {spec.order_type}"
            )
            if spec.ability_name is not None:
                assert spec.ability_name == cmd.action_ability_name, (
                    f"{spec.order_type}: registry ability_name="
                    f"{spec.ability_name!r} != CommandSpec.action_ability_name="
                    f"{cmd.action_ability_name!r}"
                )
