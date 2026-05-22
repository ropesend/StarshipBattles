"""PROJ-477 Phase 3 Task 3.1 — `_get_empire_context` off the session getattr.

``SystemTreePanel._get_empire_context`` used to resolve the live session via
``getattr(scene, 'session')`` and read ``active_empire``/``registries`` off it
— a dynamic getattr that bypassed the AST session guard. It now reads the scene
accessors ``scene.active_empire_id`` + ``scene.registries`` directly, so it
never touches the (Phase-3-retired) ``session`` getter.

``_get_empire_context`` ignores ``self`` (it reads only its ``scene_interface``
argument), so it is exercised as an unbound method against stub scenes.
"""
from __future__ import annotations

from types import SimpleNamespace

from game.ui.panels.system_tree_panel import SystemTreePanel


def _ctx(scene_interface):
    # _get_empire_context does not use `self`; call unbound with a placeholder.
    return SystemTreePanel._get_empire_context(object(), scene_interface)


def test_reads_active_empire_id_and_registries_without_session() -> None:
    registries = object()
    scene = SimpleNamespace(active_empire_id=7, registries=registries)
    # No `.session` attribute at all — proves the getattr path is gone.
    iface = SimpleNamespace(scene=scene)

    empire_id, regs = _ctx(iface)

    assert empire_id == 7
    assert regs is registries


def test_returns_none_when_no_scene() -> None:
    iface = SimpleNamespace(scene=None)
    assert _ctx(iface) == (None, None)


def test_returns_none_empire_when_no_active_empire() -> None:
    scene = SimpleNamespace(active_empire_id=None, registries=object())
    iface = SimpleNamespace(scene=scene)
    empire_id, regs = _ctx(iface)
    assert empire_id is None
    assert regs is scene.registries


def test_does_not_read_session_attribute() -> None:
    """If the rewire regressed to ``getattr(scene, 'session')`` this scene —
    which raises on a ``.session`` access — would blow up."""

    class _NoSession:
        active_empire_id = 3
        registries = "regs"

        @property
        def session(self):  # pragma: no cover - must never be hit
            raise AssertionError("_get_empire_context must not read scene.session")

    iface = SimpleNamespace(scene=_NoSession())
    empire_id, regs = _ctx(iface)
    assert empire_id == 3
    assert regs == "regs"
