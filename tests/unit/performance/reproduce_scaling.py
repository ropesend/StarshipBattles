import pytest
import pygame

from game.simulation.components.component import create_component


class TestComponentScaling:

    def test_crew_scaling(self, fresh_registries):
        # Create Crew Quarters (fresh_registries already has components/modifiers loaded)
        cq = create_component("crew_quarters", registries=fresh_registries)
        assert cq is not None, "Crew Quarters should exist"

        # New Ability System: Access via get_ability
        initial_capacity = cq.get_ability('CrewCapacity').amount
        print(f"Initial Crew Capacity: {initial_capacity}")

        # Apply simple_size modifier (Scale 2)
        res = cq.add_modifier("simple_size_mount", 2.0)
        assert res, "Should successfully add modifier"

        scaled_capacity = cq.get_ability('CrewCapacity').amount
        print(f"Scaled Crew Capacity (x2): {scaled_capacity}")

        assert scaled_capacity == initial_capacity * 2, "Crew Capacity should scale linearly with size"

    def test_life_support_scaling(self, fresh_registries):
        # Create Life Support (fresh_registries already has components/modifiers loaded)
        ls = create_component("life_support", registries=fresh_registries)
        assert ls is not None, "Life Support should exist"

        initial_capacity = ls.get_ability('LifeSupportCapacity').amount
        print(f"Initial Life Support: {initial_capacity}")

        # Apply simple_size modifier (Scale 2)
        ls.add_modifier("simple_size_mount", 2.0)

        scaled_capacity = ls.get_ability('LifeSupportCapacity').amount
        print(f"Scaled Life Support (x2): {scaled_capacity}")

        assert scaled_capacity == initial_capacity * 2, "Life Support should scale linearly with size"
