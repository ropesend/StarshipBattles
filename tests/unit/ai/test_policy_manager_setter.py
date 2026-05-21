"""PROJ-471 Task 2.2 -- setter for _default_policy_manager."""

from game.ai.policy_manager import (
    PolicyManager,
    get_default_policy_manager,
    set_default_policy_manager,
)


def test_setter_installs_instance_returned_by_getter():
    mgr = PolicyManager()
    set_default_policy_manager(mgr)
    assert get_default_policy_manager() is mgr
