"""PROJ-434 Phase 1: BuildQueue family accepts ``design_catalog`` and
threads it through the panel collaborators.

The four collaborators (screen + controller + drag handler + portrait
loader) share a single design-source reference. After PROJ-434 Phase 1
the canonical name on every constructor and attribute is
``design_catalog``; the value may be a ``DesignLibrary`` (Phase 1 — manager
still constructs one) or a ``DesignCatalog`` (Phase 2 onwards). Both
expose ``scan_designs`` / ``load_design_data`` / ``get_design_path``.
"""
from __future__ import annotations

from unittest.mock import MagicMock

from game.ui.panels.build_queue_controller import BuildQueueController
from game.ui.panels.build_queue_drag_handler import BuildQueueDragHandler
from game.ui.panels.build_queue_portraits import BuildQueuePortraitLoader


def test_controller_accepts_design_catalog_kwarg():
    """``BuildQueueController(design_catalog=...)`` stores it as
    ``self.design_catalog``."""
    catalog = MagicMock()
    controller = BuildQueueController(
        build_context=MagicMock(context_type="planet"),
        design_catalog=catalog,
        design_loader=MagicMock(),
        design_report=MagicMock(),
        on_queue_changed=MagicMock(),
    )
    assert controller.design_catalog is catalog


def test_drag_handler_accepts_design_catalog_kwarg():
    """``BuildQueueDragHandler(design_catalog=...)`` stores it as
    ``self.design_catalog``."""
    catalog = MagicMock()
    handler = BuildQueueDragHandler(
        portrait_loader=MagicMock(),
        design_catalog=catalog,
        on_add_to_queue=MagicMock(),
        on_refresh_queue=MagicMock(),
        on_refresh_design_report=MagicMock(),
        on_remove_from_queue=MagicMock(),
    )
    assert handler.design_catalog is catalog


def test_portrait_loader_accepts_design_catalog_positional():
    """``BuildQueuePortraitLoader(catalog, theme_supplier)`` stores it as
    ``self.design_catalog``."""
    catalog = MagicMock()
    loader = BuildQueuePortraitLoader(catalog, lambda: "Federation")
    assert loader.design_catalog is catalog
