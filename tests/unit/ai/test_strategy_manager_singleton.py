"""
Unit tests for StrategyManager module-level accessor pattern.

Tests the accessor behavior, direct construction, data clearing, and lazy loading.

PROJ-258: Rewritten from singleton tests to module-level accessor tests.
"""

import pytest
import threading
from unittest.mock import patch, MagicMock
from tests.fixtures.paths import get_unit_test_data_dir


class TestStrategyManagerAccessor:
    """Tests for module-level accessor pattern behavior."""

    def test_get_default_returns_same_object(self):
        """Test that get_default_strategy_manager() returns the same object on multiple calls."""
        from game.ai.strategy_manager import get_default_strategy_manager

        instance1 = get_default_strategy_manager()
        instance2 = get_default_strategy_manager()

        assert instance1 is instance2, "get_default_strategy_manager() should return same object"

    def test_direct_init_creates_new_instance(self):
        """Direct instantiation creates a NEW instance (not the default)."""
        from game.ai.strategy_manager import StrategyManager, get_default_strategy_manager

        default = get_default_strategy_manager()
        new_instance = StrategyManager()

        assert default is not new_instance, "Direct instantiation should create new instance"

    def test_clear_preserves_instance(self):
        """Test that clear() resets data but keeps the same instance."""
        from game.ai.strategy_manager import get_default_strategy_manager

        instance1 = get_default_strategy_manager()

        # Add some data
        instance1.strategies = {'test': {'name': 'Test'}}
        instance1.targeting_policies = {'policy1': {}}

        # Clear the data
        instance1.clear()

        # Instance should be the same
        instance2 = get_default_strategy_manager()
        assert instance1 is instance2, "clear() should preserve instance"

        # But data should be empty
        assert instance1.strategies == {}
        assert instance1.targeting_policies == {}
        assert instance1.movement_policies == {}

    def test_clear_resets_loaded_flag(self):
        """Test that clear() resets the _loaded flag."""
        from game.ai.strategy_manager import get_default_strategy_manager

        instance = get_default_strategy_manager()

        # Mark as loaded
        instance._loaded = True
        instance.strategies = {'test': {}}

        # Clear should reset loaded flag
        instance.clear()

        assert instance._loaded is False
        assert instance.strategies == {}


class TestStrategyManagerThreadSafety:
    """Tests for thread-safe accessor creation."""

    def test_concurrent_accessor_calls_return_same_object(self):
        """Test that concurrent calls to get_default_strategy_manager() all get the same object."""
        from game.ai.strategy_manager import get_default_strategy_manager

        results = []
        errors = []

        def get_instance():
            try:
                inst = get_default_strategy_manager()
                results.append(inst)
            except Exception as e:
                errors.append(e)

        # Create threads
        threads = [threading.Thread(target=get_instance) for _ in range(10)]

        # Start all threads nearly simultaneously
        for t in threads:
            t.start()

        # Wait for completion
        for t in threads:
            t.join()

        # No errors should have occurred
        assert len(errors) == 0, f"Got errors: {errors}"

        # All results should be the same instance
        assert len(results) == 10
        assert all(r is results[0] for r in results), "All threads should get same instance"


class TestStrategyManagerDataLoading:
    """Tests for data loading behavior."""

    def test_load_data_populates_strategies(self):
        """Test that load_data populates strategy dictionaries."""
        from game.ai.strategy_manager import get_default_strategy_manager

        manager = get_default_strategy_manager()
        manager.clear()

        # Use test data directory
        unit_test_data_dir = get_unit_test_data_dir()
        manager.load_data(
            str(unit_test_data_dir),
            targeting_file="test_targeting_policies.json",
            movement_file="test_movement_policies.json",
            strategy_file="test_combat_strategies.json"
        )

        # Should have loaded strategies
        assert len(manager.strategies) > 0, "Strategies should be loaded"
        assert len(manager.targeting_policies) > 0, "Targeting policies should be loaded"
        assert len(manager.movement_policies) > 0, "Movement policies should be loaded"

    def test_load_data_with_missing_files_uses_defaults(self):
        """Test that missing files result in empty dicts (not crashes)."""
        from game.ai.strategy_manager import get_default_strategy_manager

        manager = get_default_strategy_manager()
        manager.clear()

        # Load from non-existent directory
        manager.load_data("/nonexistent/path")

        # Should have empty dicts (not crash)
        assert manager.strategies == {}
        assert manager.targeting_policies == {}
        assert manager.movement_policies == {}


class TestStrategyManagerLazyLoading:
    """Tests for lazy loading behavior."""

    def test_fresh_instance_not_loaded(self):
        """Test that a fresh instance has not loaded data yet."""
        from game.ai.strategy_manager import StrategyManager

        # Create a fresh instance (not the default)
        manager = StrategyManager()

        # _loaded flag should be False (no disk I/O yet)
        assert manager._loaded is False, \
            "Fresh instance should not have loaded data yet"

    def test_ensure_loaded_triggers_once(self):
        """Test that ensure_loaded() only loads data once."""
        from game.ai.strategy_manager import get_default_strategy_manager

        manager = get_default_strategy_manager()
        manager.clear()
        manager._loaded = False

        # First call should load
        with patch.object(manager, 'load_data') as mock_load:
            manager.ensure_loaded()
            assert mock_load.called, "First ensure_loaded() should call load_data()"

        # Mark as loaded
        manager._loaded = True

        # Second call should not load again
        with patch.object(manager, 'load_data') as mock_load:
            manager.ensure_loaded()
            assert not mock_load.called, "Second ensure_loaded() should not call load_data()"

    def test_get_strategy_triggers_ensure_loaded(self):
        """Test that get_strategy() calls ensure_loaded()."""
        from game.ai.strategy_manager import get_default_strategy_manager

        manager = get_default_strategy_manager()

        with patch.object(manager, 'ensure_loaded') as mock_ensure:
            manager.get_strategy('any_id')
            assert mock_ensure.called, "get_strategy() should call ensure_loaded()"

    def test_get_targeting_policy_triggers_ensure_loaded(self):
        """Test that get_targeting_policy() calls ensure_loaded()."""
        from game.ai.strategy_manager import get_default_strategy_manager

        manager = get_default_strategy_manager()

        with patch.object(manager, 'ensure_loaded') as mock_ensure:
            manager.get_targeting_policy('any_id')
            assert mock_ensure.called, "get_targeting_policy() should call ensure_loaded()"

    def test_get_movement_policy_triggers_ensure_loaded(self):
        """Test that get_movement_policy() calls ensure_loaded()."""
        from game.ai.strategy_manager import get_default_strategy_manager

        manager = get_default_strategy_manager()

        with patch.object(manager, 'ensure_loaded') as mock_ensure:
            manager.get_movement_policy('any_id')
            assert mock_ensure.called, "get_movement_policy() should call ensure_loaded()"


class TestStrategyManagerDefaults:
    """Tests for default value behavior."""

    def test_get_strategy_returns_default_for_unknown_id(self):
        """Test that get_strategy returns default for unknown strategy."""
        from game.ai.strategy_manager import get_default_strategy_manager

        manager = get_default_strategy_manager()
        manager._loaded = True  # Skip loading

        result = manager.get_strategy('nonexistent_strategy')

        # Should return default strategy
        assert 'name' in result
        assert result == manager.defaults['strategy']

    def test_get_targeting_policy_returns_default_for_unknown_id(self):
        """Test that get_targeting_policy returns default for unknown policy."""
        from game.ai.strategy_manager import get_default_strategy_manager

        manager = get_default_strategy_manager()
        manager._loaded = True

        result = manager.get_targeting_policy('nonexistent_policy')

        assert 'rules' in result
        assert result == manager.defaults['targeting']

    def test_get_movement_policy_returns_default_for_unknown_id(self):
        """Test that get_movement_policy returns default for unknown policy."""
        from game.ai.strategy_manager import get_default_strategy_manager

        manager = get_default_strategy_manager()
        manager._loaded = True

        result = manager.get_movement_policy('nonexistent_policy')

        assert 'behavior' in result
        assert result == manager.defaults['movement']


class TestStrategyManagerResolve:
    """Tests for strategy resolution."""

    def test_resolve_strategy_combines_policies(self):
        """Test that resolve_strategy combines strategy with policies."""
        from game.ai.strategy_manager import get_default_strategy_manager

        manager = get_default_strategy_manager()
        manager._loaded = True

        # Set up test data
        manager.strategies = {
            'test_strat': {
                'name': 'Test Strategy',
                'targeting_policy': 'test_targeting',
                'movement_policy': 'test_movement'
            }
        }
        manager.targeting_policies = {
            'test_targeting': {'name': 'Test Targeting', 'rules': []}
        }
        manager.movement_policies = {
            'test_movement': {'behavior': 'kite', 'engage_distance': 'max_range'}
        }

        resolved = manager.resolve_strategy('test_strat')

        assert 'definition' in resolved
        assert 'targeting' in resolved
        assert 'movement' in resolved

        assert resolved['definition']['name'] == 'Test Strategy'
        assert resolved['targeting']['name'] == 'Test Targeting'
        assert resolved['movement']['behavior'] == 'kite'
