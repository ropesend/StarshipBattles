"""
Unit tests for StrategyManager singleton pattern.

Tests the singleton behavior, thread safety, data clearing, and lazy loading.
"""

import pytest
import threading
import time
from unittest.mock import patch, MagicMock
from tests.fixtures.paths import get_unit_test_data_dir


class TestStrategyManagerSingleton:
    """Tests for singleton pattern behavior."""

    def test_instance_returns_same_object(self):
        """Test that instance() returns the same object on multiple calls."""
        from game.ai.controller import StrategyManager

        instance1 = StrategyManager.instance()
        instance2 = StrategyManager.instance()

        assert instance1 is instance2, "instance() should return same object"

    def test_direct_init_raises_after_instance_exists(self):
        """Test that direct __init__ raises exception when singleton exists."""
        from game.ai.controller import StrategyManager

        # Ensure instance exists
        _ = StrategyManager.instance()

        # Direct instantiation should raise
        with pytest.raises(Exception) as exc_info:
            StrategyManager()

        assert "singleton" in str(exc_info.value).lower()

    def test_reset_destroys_instance(self):
        """Test that reset() destroys the singleton instance."""
        from game.ai.controller import StrategyManager

        # Get initial instance
        instance1 = StrategyManager.instance()

        # Reset should destroy it
        StrategyManager.reset()

        # Next call should create new instance
        instance2 = StrategyManager.instance()

        assert instance1 is not instance2, "reset() should destroy instance"

    def test_clear_preserves_instance(self):
        """Test that clear() resets data but keeps the same instance."""
        from game.ai.controller import StrategyManager

        instance1 = StrategyManager.instance()

        # Add some data
        instance1.strategies = {'test': {'name': 'Test'}}
        instance1.targeting_policies = {'policy1': {}}

        # Clear the data
        instance1.clear()

        # Instance should be the same
        instance2 = StrategyManager.instance()
        assert instance1 is instance2, "clear() should preserve instance"

        # But data should be empty
        assert instance1.strategies == {}
        assert instance1.targeting_policies == {}
        assert instance1.movement_policies == {}


class TestStrategyManagerThreadSafety:
    """Tests for thread-safe singleton creation."""

    def test_concurrent_instance_calls_return_same_object(self):
        """Test that concurrent calls to instance() all get the same object."""
        from game.ai.controller import StrategyManager

        # Reset to start fresh
        StrategyManager.reset()

        results = []
        errors = []

        def get_instance():
            try:
                inst = StrategyManager.instance()
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
        from game.ai.controller import StrategyManager

        manager = StrategyManager.instance()
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
        from game.ai.controller import StrategyManager

        manager = StrategyManager.instance()
        manager.clear()

        # Load from non-existent directory
        manager.load_data("/nonexistent/path")

        # Should have empty dicts (not crash)
        assert manager.strategies == {}
        assert manager.targeting_policies == {}
        assert manager.movement_policies == {}


class TestStrategyManagerLazyLoading:
    """Tests for lazy loading behavior."""

    def test_no_data_loaded_on_import(self):
        """Test that importing the module doesn't trigger disk I/O."""
        from game.ai.controller import StrategyManager

        # Reset the singleton completely
        StrategyManager.reset()

        # Create a fresh instance
        manager = StrategyManager.instance()

        # _loaded flag should be False (no disk I/O yet)
        assert getattr(manager, '_loaded', False) is False, \
            "Fresh instance should not have loaded data yet"

    def test_ensure_loaded_triggers_once(self):
        """Test that ensure_loaded() only loads data once."""
        from game.ai.controller import StrategyManager

        manager = StrategyManager.instance()
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
        from game.ai.controller import StrategyManager

        manager = StrategyManager.instance()

        with patch.object(manager, 'ensure_loaded') as mock_ensure:
            manager.get_strategy('any_id')
            assert mock_ensure.called, "get_strategy() should call ensure_loaded()"

    def test_get_targeting_policy_triggers_ensure_loaded(self):
        """Test that get_targeting_policy() calls ensure_loaded()."""
        from game.ai.controller import StrategyManager

        manager = StrategyManager.instance()

        with patch.object(manager, 'ensure_loaded') as mock_ensure:
            manager.get_targeting_policy('any_id')
            assert mock_ensure.called, "get_targeting_policy() should call ensure_loaded()"

    def test_get_movement_policy_triggers_ensure_loaded(self):
        """Test that get_movement_policy() calls ensure_loaded()."""
        from game.ai.controller import StrategyManager

        manager = StrategyManager.instance()

        with patch.object(manager, 'ensure_loaded') as mock_ensure:
            manager.get_movement_policy('any_id')
            assert mock_ensure.called, "get_movement_policy() should call ensure_loaded()"


class TestStrategyManagerDefaults:
    """Tests for default value behavior."""

    def test_get_strategy_returns_default_for_unknown_id(self):
        """Test that get_strategy returns default for unknown strategy."""
        from game.ai.controller import StrategyManager

        manager = StrategyManager.instance()
        manager._loaded = True  # Skip loading

        result = manager.get_strategy('nonexistent_strategy')

        # Should return default strategy
        assert 'name' in result
        assert result == manager.defaults['strategy']

    def test_get_targeting_policy_returns_default_for_unknown_id(self):
        """Test that get_targeting_policy returns default for unknown policy."""
        from game.ai.controller import StrategyManager

        manager = StrategyManager.instance()
        manager._loaded = True

        result = manager.get_targeting_policy('nonexistent_policy')

        assert 'rules' in result
        assert result == manager.defaults['targeting']

    def test_get_movement_policy_returns_default_for_unknown_id(self):
        """Test that get_movement_policy returns default for unknown policy."""
        from game.ai.controller import StrategyManager

        manager = StrategyManager.instance()
        manager._loaded = True

        result = manager.get_movement_policy('nonexistent_policy')

        assert 'behavior' in result
        assert result == manager.defaults['movement']


class TestStrategyManagerResolve:
    """Tests for strategy resolution."""

    def test_resolve_strategy_combines_policies(self):
        """Test that resolve_strategy combines strategy with policies."""
        from game.ai.controller import StrategyManager

        manager = StrategyManager.instance()
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
