"""
Tests for fleet construction queue save/load.

PROJ-67 Phase 6: Verify fleet build state persists across save/load cycles.
"""

import pytest
import tempfile
import os
import json
import shutil
from unittest.mock import MagicMock

from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import Order, OrderType
from game.core.hex_math import HexCoord
from game.strategy.data.empire import Empire
from game.strategy.data.ship_instance import ShipInstance


class TestFleetConstructionQueueSaveLoad:
    """Tests for fleet construction_queue persistence."""

    @pytest.fixture
    def temp_save_dir(self):
        """Create a temporary directory for save files."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

    @pytest.fixture
    def make_mock_ship(self):
        """Factory for creating mock ship instances."""
        def _make(name="Test Ship"):
            mock = MagicMock(spec=ShipInstance)
            mock.name = name
            mock.design_id = name
            mock.instance_id = f"mock-{name}"
            mock.is_combat_capable.return_value = True
            mock.design_data = {
                'name': name,
                'vehicle_type': 'Ship',
                'layers': {'core': []}
            }
            mock.to_dict.return_value = {
                'instance_id': mock.instance_id,
                'design_id': name,
                'name': name,
                'owner_id': 0,
                'design_data': mock.design_data,
                'components': {},
            }
            return mock
        return _make

    def test_save_game_with_fleet_construction_queue(self, temp_save_dir, make_mock_ship):
        """Test save game with fleet that has construction_queue items."""
        # Create fleet with construction queue
        fleet = Fleet("f1", 0, HexCoord(5, 3))
        fleet.ships.append(make_mock_ship(name="Yard Ship"))
        fleet.construction_queue = [
            {"design_id": "destroyer_1", "type": "ship", "turns_remaining": 5},
            {"design_id": "fighter_wing", "type": "fighter", "turns_remaining": 2},
        ]

        # Serialize
        d = fleet.to_dict()
        d['location'] = [5, 3]  # Fix HexCoord serialization

        # Verify construction_queue in serialized data
        assert 'construction_queue' in d
        assert len(d['construction_queue']) == 2
        assert d['construction_queue'][0]['design_id'] == 'destroyer_1'
        assert d['construction_queue'][0]['turns_remaining'] == 5
        assert d['construction_queue'][1]['type'] == 'fighter'

    def test_load_game_restores_fleet_construction_queue(self, temp_save_dir):
        """Test load game restores fleet construction_queue."""
        # Simulated save data
        fleet_data = {
            'id': 'f1',
            'owner_id': 0,
            'location': [5, 3],
            'speed': 5.0,
            'ships': [],
            'orders': [],
            'path': [],
            'construction_queue': [
                {"design_id": "cruiser", "type": "ship", "turns_remaining": 8},
                {"design_id": "station", "type": "complex", "turns_remaining": 12},
            ],
        }

        # Deserialize
        fleet = Fleet.from_dict(fleet_data)

        # Verify queue restored
        assert len(fleet.construction_queue) == 2
        assert fleet.construction_queue[0]['design_id'] == 'cruiser'
        assert fleet.construction_queue[0]['turns_remaining'] == 8
        assert fleet.construction_queue[1]['type'] == 'complex'

    def test_save_game_with_build_order_and_load_restores(self, temp_save_dir, make_mock_ship):
        """Test save/load preserves BUILD order along with queue."""
        # Create fleet with BUILD order
        fleet = Fleet("f1", 0, HexCoord(5, 3))
        fleet.ships.append(make_mock_ship(name="Yard Ship"))
        fleet.add_order(Order(OrderType.BUILD))
        fleet.construction_queue = [
            {"design_id": "battleship", "type": "ship", "turns_remaining": 15}
        ]

        # Serialize
        d = fleet.to_dict()
        d['location'] = [5, 3]

        # Verify BUILD order in serialized data
        assert len(d['orders']) == 1
        assert d['orders'][0]['type'] == 'BUILD'

        # Deserialize
        restored = Fleet.from_dict(d)

        # Verify BUILD order and queue restored
        assert len(restored.orders) == 1
        assert restored.orders[0].type == OrderType.BUILD
        assert len(restored.construction_queue) == 1
        assert restored.construction_queue[0]['design_id'] == 'battleship'

    def test_roundtrip_preserves_full_fleet_state(self, temp_save_dir, make_mock_ship):
        """Test complete round-trip save/load preserves full fleet build state."""
        # Create fleet with full build state
        original = Fleet("test_fleet", 0, HexCoord(10, -5))
        original.ships.append(make_mock_ship(name="Construction Ship"))
        original.ships.append(make_mock_ship(name="Escort"))
        original.add_order(Order(OrderType.BUILD))
        original.construction_queue = [
            {"design_id": "destroyer", "type": "ship", "turns_remaining": 5},
            {"design_id": "frigate", "type": "ship", "turns_remaining": 3},
            {"design_id": "factory", "type": "complex", "turns_remaining": 10},
        ]

        # Serialize
        d = original.to_dict()
        d['location'] = [10, -5]  # Fix HexCoord

        # Deserialize
        restored = Fleet.from_dict(d)

        # Verify full state restored
        assert restored.id == original.id
        assert restored.owner_id == original.owner_id
        assert restored.location == original.location
        assert len(restored.ships) == 2
        assert len(restored.orders) == 1
        assert restored.orders[0].type == OrderType.BUILD
        assert len(restored.construction_queue) == 3
        assert restored.construction_queue[0] == original.construction_queue[0]
        assert restored.construction_queue[1] == original.construction_queue[1]
        assert restored.construction_queue[2] == original.construction_queue[2]

    def test_is_building_preserved_after_roundtrip(self, temp_save_dir, make_mock_ship):
        """Test is_building property works correctly after load."""
        # Create fleet in building state
        original = Fleet("f1", 0, HexCoord(0, 0))
        original.ships.append(make_mock_ship(name="Yard Ship"))
        original.add_order(Order(OrderType.BUILD))
        original.construction_queue = [
            {"design_id": "ship", "type": "ship", "turns_remaining": 3}
        ]

        assert original.is_building is True

        # Serialize and deserialize
        d = original.to_dict()
        d['location'] = [0, 0]
        restored = Fleet.from_dict(d)

        # is_building should still be True
        assert restored.is_building is True

    def test_empty_construction_queue_preserved(self, temp_save_dir, make_mock_ship):
        """Test empty construction queue is preserved (not omitted)."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        fleet.ships.append(make_mock_ship(name="Ship"))
        fleet.construction_queue = []  # Explicitly empty

        d = fleet.to_dict()
        d['location'] = [0, 0]

        restored = Fleet.from_dict(d)

        assert restored.construction_queue == []
        assert restored.is_building is False
