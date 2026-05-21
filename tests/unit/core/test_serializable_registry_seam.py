"""PROJ-471 Task 2.9 -- test-isolation seam for _SERIALIZABLE_REGISTRY."""

from game.core import json_utils
from game.core.json_utils import (
    register_serializable,
    get_serializable_registry,
    clear_serializable_registry,
)


def test_clear_serializable_registry_restores_baseline():
    baseline = get_serializable_registry()

    @register_serializable("proj471_probe_type")
    class _Probe:
        pass

    assert "proj471_probe_type" in get_serializable_registry()

    clear_serializable_registry(baseline)

    assert "proj471_probe_type" not in get_serializable_registry()
    assert get_serializable_registry() == baseline


def test_clear_serializable_registry_default_empties():
    baseline = get_serializable_registry()
    try:
        @register_serializable("proj471_probe_type_2")
        class _Probe2:
            pass

        clear_serializable_registry()
        assert get_serializable_registry() == {}
    finally:
        # Restore the real baseline so we don't poison other tests in-process.
        clear_serializable_registry(baseline)
    assert get_serializable_registry() == baseline
