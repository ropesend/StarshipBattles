"""
Unit tests for StrategyMetadataService.

Tests the core strategy metadata service that provides strategy names/IDs
to the UI layer without requiring AI layer imports.
"""

import os
import pytest
import tempfile
import json
import threading
from unittest.mock import patch

from game.core.strategy_metadata import StrategyMetadataService


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset singleton before and after each test."""
    StrategyMetadataService.reset()
    yield
    StrategyMetadataService.reset()


class TestStrategyMetadataServiceSingleton:
    """Test singleton behavior."""

    def test_instance_returns_same_object(self):
        """instance() should always return the same object."""
        instance1 = StrategyMetadataService.instance()
        instance2 = StrategyMetadataService.instance()
        assert instance1 is instance2

    def test_direct_instantiation_returns_same_instance(self):
        """Direct instantiation should return the same singleton instance."""
        instance1 = StrategyMetadataService.instance()
        instance2 = StrategyMetadataService()
        assert instance1 is instance2

    def test_reset_clears_instance(self):
        """reset() should allow a new instance to be created."""
        instance1 = StrategyMetadataService.instance()
        StrategyMetadataService.reset()
        instance2 = StrategyMetadataService.instance()
        assert instance1 is not instance2

    def test_thread_safe_instance_creation(self):
        """Multiple threads should get the same instance."""
        instances = []
        errors = []

        def get_instance():
            try:
                instances.append(StrategyMetadataService.instance())
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=get_instance) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert len(instances) == 10
        assert all(i is instances[0] for i in instances)


class TestStrategyMetadataServiceData:
    """Test data operations."""

    def test_initial_strategies_empty(self):
        """New instance should have empty strategies."""
        service = StrategyMetadataService.instance()
        assert service.strategies == {}

    def test_set_strategies(self):
        """set_strategies should populate the data."""
        service = StrategyMetadataService.instance()
        strategies = {
            'aggressive': {'name': 'Aggressive'},
            'defensive': {'name': 'Defensive'}
        }
        service.set_strategies(strategies)
        assert service.strategies == strategies

    def test_set_strategies_copies_data(self):
        """set_strategies should copy, not reference original."""
        service = StrategyMetadataService.instance()
        strategies = {'aggressive': {'name': 'Aggressive'}}
        service.set_strategies(strategies)
        strategies['new_key'] = {'name': 'New'}
        assert 'new_key' not in service.strategies

    def test_clear_removes_data(self):
        """clear() should remove all strategy data."""
        service = StrategyMetadataService.instance()
        service.set_strategies({'aggressive': {'name': 'Aggressive'}})
        service.clear()
        assert service.strategies == {}


class TestStrategyMetadataServiceQueries:
    """Test query methods."""

    @pytest.fixture
    def populated_service(self):
        """Service with test data."""
        service = StrategyMetadataService.instance()
        service.set_strategies({
            'aggressive_ranged': {'name': 'Aggressive Ranged'},
            'defensive_close': {'name': 'Defensive Close'},
            'balanced': {'name': 'Balanced'},
        })
        return service

    def test_get_strategy_names_returns_sorted_list(self, populated_service):
        """get_strategy_names should return sorted display names."""
        names = populated_service.get_strategy_names()
        assert names == ['Aggressive Ranged', 'Balanced', 'Defensive Close']

    def test_get_strategy_names_empty(self):
        """get_strategy_names on empty service returns empty list."""
        service = StrategyMetadataService.instance()
        assert service.get_strategy_names() == []

    def test_get_strategy_names_uses_id_if_no_name(self):
        """Should fall back to strategy ID if name not in dict."""
        service = StrategyMetadataService.instance()
        service.set_strategies({
            'has_name': {'name': 'Display Name'},
            'no_name': {'other_field': 'value'}
        })
        names = service.get_strategy_names()
        assert 'Display Name' in names
        assert 'no_name' in names

    def test_get_strategy_display_name(self, populated_service):
        """get_strategy_display_name should resolve ID to name."""
        assert populated_service.get_strategy_display_name('aggressive_ranged') == 'Aggressive Ranged'
        assert populated_service.get_strategy_display_name('balanced') == 'Balanced'

    def test_get_strategy_display_name_unknown_returns_id(self, populated_service):
        """get_strategy_display_name should return ID if not found."""
        assert populated_service.get_strategy_display_name('unknown_strategy') == 'unknown_strategy'

    def test_get_strategy_id_by_name(self, populated_service):
        """get_strategy_id_by_name should resolve name to ID."""
        assert populated_service.get_strategy_id_by_name('Aggressive Ranged') == 'aggressive_ranged'
        assert populated_service.get_strategy_id_by_name('Balanced') == 'balanced'

    def test_get_strategy_id_by_name_unknown_returns_none(self, populated_service):
        """get_strategy_id_by_name should return None if not found."""
        assert populated_service.get_strategy_id_by_name('Unknown Strategy') is None


class TestStrategyMetadataServiceLoadData:
    """Test file loading functionality."""

    def test_load_data_from_file(self):
        """load_data should load strategies from JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test JSON file
            strategy_file = os.path.join(tmpdir, 'combat_strategies.json')
            with open(strategy_file, 'w') as f:
                json.dump({
                    'strategies': {
                        'test_strategy': {'name': 'Test Strategy'}
                    }
                }, f)

            service = StrategyMetadataService.instance()
            service.load_data(base_path=tmpdir)

            assert 'test_strategy' in service.strategies
            assert service.get_strategy_display_name('test_strategy') == 'Test Strategy'

    def test_load_data_missing_file_uses_empty(self):
        """load_data should use empty dict if file missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = StrategyMetadataService.instance()
            service.load_data(base_path=tmpdir)
            assert service.strategies == {}

    def test_load_data_custom_filename(self):
        """load_data should accept custom filename."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test JSON file with custom name
            strategy_file = os.path.join(tmpdir, 'custom_strategies.json')
            with open(strategy_file, 'w') as f:
                json.dump({
                    'strategies': {
                        'custom': {'name': 'Custom Strategy'}
                    }
                }, f)

            service = StrategyMetadataService.instance()
            service.load_data(base_path=tmpdir, strategy_file='custom_strategies.json')

            assert 'custom' in service.strategies
