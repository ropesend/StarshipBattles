"""Tests for `TaskForce.formation` field (PROJ-269 Phase 4 Task 4.1).

`TaskForce.formation: Optional[FormationSpec]` stores the formation
authored for this task force; `None` means "use design-role default"
(resolved at battle-start by `FormationResolver`).
"""
from game.core.math import Vector2
from game.simulation.combat.formation import FormationShape, FormationSpec
from game.strategy.data.task_force import TaskForce


def test_task_force_has_formation_field_default_none():
    tf = TaskForce(name="Alpha")
    assert hasattr(tf, "formation")
    assert tf.formation is None


def test_task_force_formation_setter():
    tf = TaskForce(name="Alpha")
    tf.formation = FormationSpec(shape=FormationShape.WEDGE, spacing=150.0)
    assert tf.formation is not None
    assert tf.formation.shape == FormationShape.WEDGE
    assert tf.formation.spacing == 150.0


def test_task_force_serialization_round_trip_with_formation():
    tf = TaskForce(name="Alpha")
    tf.formation = FormationSpec(
        shape=FormationShape.CARRIER_PROTECTED,
        spacing=200.0,
    )
    data = tf.to_dict()
    assert "formation" in data
    restored = TaskForce.from_dict(data)
    assert restored.formation is not None
    assert restored.formation.shape == FormationShape.CARRIER_PROTECTED
    assert restored.formation.spacing == 200.0


def test_task_force_serialization_without_formation_omits_key():
    """A TaskForce with `formation=None` shouldn't bloat the save dict
    with a None formation entry."""
    tf = TaskForce(name="Alpha")
    data = tf.to_dict()
    # Either not present OR explicitly None — both acceptable.
    if "formation" in data:
        assert data["formation"] is None


def test_task_force_from_dict_missing_formation_defaults_none():
    tf = TaskForce(name="Alpha")
    data = tf.to_dict()
    data.pop("formation", None)
    restored = TaskForce.from_dict(data)
    assert restored.formation is None


def test_custom_formation_roundtrips_positions():
    tf = TaskForce(name="CustomTF")
    tf.formation = FormationSpec(
        shape=FormationShape.CUSTOM,
        spacing=100.0,
        custom_positions=(Vector2(10.0, 20.0), Vector2(30.0, 40.0)),
    )
    data = tf.to_dict()
    restored = TaskForce.from_dict(data)
    assert restored.formation is not None
    assert restored.formation.shape == FormationShape.CUSTOM
    assert len(restored.formation.custom_positions) == 2
    assert restored.formation.custom_positions[0].x == 10.0
    assert restored.formation.custom_positions[1].y == 40.0
