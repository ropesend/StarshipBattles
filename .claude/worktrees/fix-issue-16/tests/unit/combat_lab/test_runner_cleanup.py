"""Regression test for TestRunner materializer cleanup.

Verifies that TestRunner.cleanup() restores the production default
ship materializer (InstanceBackedMaterializer) after Combat Lab
overrides it with DesignOnlyMaterializer in __init__.

Bug: TestRunner.__init__ calls set_default_ship_materializer(
DesignOnlyMaterializer(...)) but never restores the production
default. When the user navigates from Combat Lab to Battle Setup
in the same session, start_from_spec() pulls the tainted global
and tries to load production ship designs via the Combat Lab
file-based loader, causing FileNotFoundError.
"""
import pytest

from game.simulation.services.ship_materializer import (
    DesignOnlyMaterializer,
    InstanceBackedMaterializer,
    get_default_ship_materializer,
)


@pytest.fixture(autouse=True)
def _reset_default_materializer():
    """Reset the module-level default materializer to prevent
    cross-test pollution."""
    from game.simulation.services import ship_materializer as mod
    original = mod._default_ship_materializer
    mod._default_ship_materializer = None
    yield
    mod._default_ship_materializer = original


class TestRunnerCleanup:
    """TestRunner.cleanup() restores the production materializer."""

    def test_init_installs_design_only_materializer(self):
        """TestRunner.__init__ overrides the default with DesignOnlyMaterializer."""
        from combat_lab.runner import TestRunner
        TestRunner()
        materializer = get_default_ship_materializer()
        assert isinstance(materializer, DesignOnlyMaterializer)

    def test_cleanup_restores_instance_backed_materializer(self):
        """After cleanup(), the default reverts to InstanceBackedMaterializer."""
        from combat_lab.runner import TestRunner
        runner = TestRunner()
        runner.cleanup()
        materializer = get_default_ship_materializer()
        assert isinstance(materializer, InstanceBackedMaterializer)

    def test_cleanup_is_idempotent(self):
        """Calling cleanup() twice does not crash."""
        from combat_lab.runner import TestRunner
        runner = TestRunner()
        runner.cleanup()
        runner.cleanup()
        materializer = get_default_ship_materializer()
        assert isinstance(materializer, InstanceBackedMaterializer)
