"""PROJ-438 Phase 3: pin the post-container ``ShipInstance`` surface shape.

Phase 3 — like Phase 2 — collapsed to a documentation + invariant pass
after the audit. The blast-radius check ruled out removing
``IShipInstance.cargo_contents`` from the protocol (~30+ test files), and
PROJ-436 Phase 9 already absorbed the largest structural cleanup. The
remaining ``ShipInstance`` shape is the intentional post-storage residue
held together by D2 default (a) — keep inline ``design_data`` and the
thin entry-point shims documented in PROJ-425 Phase 5d/5e.

This file pins the post-Phase-9 categorical shape so future drift
surfaces immediately: a regression that re-adds a deleted legacy field
(``carried_items``, ``_CarriedItemsProxy``, ``_items_to_bay_inventory``,
etc.) or removes one of the explicitly-retained guardrail entry points
breaks one of the ratchets below.

The companion AST guard at ``tests/static_guards/test_no_legacy_storage_fields.py``
covers the storage-side fields; this file covers the broader categorical
shape.
"""
from __future__ import annotations

from game.core.protocols import IShipInstance
from game.strategy.data.ship_instance import ShipInstance


class TestShipInstanceCategoricalShape:
    """Pin the post-Phase-9 ``ShipInstance`` attribute/method categories."""

    def test_owned_identity_fields_present(self) -> None:
        for attr in ("instance_id", "design_id", "name", "owner_id", "serial"):
            assert attr in ShipInstance.__annotations__ or hasattr(
                ShipInstance, attr
            ), f"Owned identity field missing: {attr}"

    def test_owned_design_data_remains_inline(self) -> None:
        """D2 default (a): ``design_data`` stays inline as durable state.
        Removing this in favor of design-lookup-by-id would trigger the
        910-caller sweep that Phase 3 is explicitly bounded away from."""
        assert "design_data" in ShipInstance.__annotations__, (
            "design_data must remain an inline dataclass field per D2 (a)"
        )

    def test_owned_runtime_state_fields_present(self) -> None:
        for attr in (
            "current_hp",
            "_consumable_levels",
            "_cargo_contents",
            "bay_inventory",
            "component_toggles",
            "activation_states",
            "components",
        ):
            assert attr in ShipInstance.__annotations__, (
                f"Owned runtime-state field missing: {attr}"
            )

    def test_status_flags_present(self) -> None:
        for attr in ("is_alive", "is_derelict", "is_operational"):
            assert attr in ShipInstance.__annotations__

    def test_delegate_manager_slots_present(self) -> None:
        """The four delegate-manager slots are PROJ-425 contract; they
        must exist so external mocks can find them and so the post-init
        wiring does not break under accidental removal."""
        for attr in ("_resource_mgr", "_cargo_mgr", "_display_fmt", "_bridge"):
            assert attr in ShipInstance.__annotations__, (
                f"Delegate manager slot missing: {attr}"
            )


class TestShipInstanceLegacyShimDocumentation:
    """Pin that the post-Phase-9 / PROJ-436 / PROJ-425 retained shims
    remain explicitly documented (not accidentally retained)."""

    def test_consumable_levels_property_is_backcompat_shim(self) -> None:
        prop = ShipInstance.__dict__.get("consumable_levels")
        assert isinstance(prop, property)
        doc = prop.__doc__ or ""
        assert "deletion shim" in doc.lower() or "backward-compat" in doc.lower(), (
            "consumable_levels property must remain explicitly marked as a "
            "backward-compat shim (PROJ-436 Phase 3f rationale)."
        )

    def test_cargo_contents_property_is_backcompat_shim(self) -> None:
        prop = ShipInstance.__dict__.get("cargo_contents")
        assert isinstance(prop, property)
        doc = prop.__doc__ or ""
        assert "deletion shim" in doc.lower() or "backward-compat" in doc.lower(), (
            "cargo_contents property must remain explicitly marked as a "
            "backward-compat shim (PROJ-436 Phase 3f rationale)."
        )

    def test_class_docstring_documents_categories(self) -> None:
        """Phase 3 narrowing: class docstring categorizes the post-Phase-9
        attribute/method shape (Owned identity, Owned durable state, Owned
        runtime state, Status flags, Delegates, Protocol-aliases,
        Retained-shim entry points)."""
        doc = ShipInstance.__doc__ or ""
        required = [
            "Owned identity",
            "Owned durable state",
            "Owned runtime state",
            "Retained-shim entry points",
        ]
        missing = [h for h in required if h not in doc]
        assert not missing, (
            f"ShipInstance class docstring missing post-Phase-9 categories: "
            f"{missing}"
        )


class TestIShipInstanceProtocolContract:
    """Pin the post-Phase-9 ``IShipInstance`` protocol shape."""

    def test_protocol_declares_minimum_surface(self) -> None:
        """Protocol must declare the read-side attributes UI/DTO consumers
        depend on. Removing any of these triggers a multi-file sweep."""
        members = set(IShipInstance.__dict__) - {"_is_protocol", "_is_runtime_protocol"}
        # The expected stable contract surface — extensions OK, removals must
        # be intentional and accompanied by caller sweep.
        for attr in (
            "design_id",
            "design_name",
            "design_data",
            "hull_class",
            "cargo_contents",
            "ship_name",
            "serial_number",
            "get_calculated_stats",
        ):
            assert attr in members, (
                f"IShipInstance protocol missing post-Phase-9 member: {attr}"
            )

    def test_cargo_contents_protocol_doc_flags_future_removal(self) -> None:
        """``IShipInstance.cargo_contents`` is the most legacy-shaped entry
        in the protocol — a dict view over a renamed private field. Its
        docstring must explicitly note the future-removal intent so a
        future project knows the right direction (push consumers toward
        ``cargo_container()`` / ``ShipCargoManager`` and only then remove
        the protocol entry).
        """
        prop = IShipInstance.__dict__.get("cargo_contents")
        assert isinstance(prop, property)
        doc = (prop.__doc__ or "").lower()
        assert "phase 3f" in doc or "backward-compat" in doc or "legacy" in doc, (
            "IShipInstance.cargo_contents docstring must signal its "
            "backward-compat / legacy status so future removals are scoped."
        )
        assert "prefer" in doc or "container" in doc or "manager" in doc, (
            "IShipInstance.cargo_contents docstring must point readers at "
            "the preferred Container / ShipCargoManager surface."
        )
