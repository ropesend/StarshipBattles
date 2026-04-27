"""Shared resource-display helpers for UI panels.

Hosts the small set of presentation constants and functions that more than
one resource-rendering panel needs (Empire Treasury, Planet Report, etc.)
so neither panel owns them privately.

Currently provides:
  - `RESOURCE_ABBREVIATIONS`: 3-letter labels rendered under the icon in
    icon-column headers.
  - `get_resource_abbreviation`: lookup with a `res[:3].title()` fallback
    so adding a new resource to `data/resources.json` produces a
    reasonable column header without a code change.
  - `get_displayed_resource_ids`: catalog-driven list of resource ids
    grouped (planetary first, then operational), so the same column set
    is used everywhere we render every-resource grids.
"""
from __future__ import annotations

from typing import List

from game.core.resources import ResourceCatalog


RESOURCE_ABBREVIATIONS = {
    "metals": "Met",
    "organics": "Org",
    "vapors": "Vap",
    "radioactives": "Rad",
    "exotics": "Exo",
    "fuel": "Fue",
    "energy": "Eng",
    "ammo": "Amm",
}


def get_resource_abbreviation(resource_id: str) -> str:
    """Return the 3-letter column-header label for a resource.

    Falls back to the first three chars title-cased so resources added
    to `data/resources.json` without a manual abbreviation entry still
    render a readable header (e.g. `dilithium` -> `Dil`).
    """
    return RESOURCE_ABBREVIATIONS.get(resource_id, resource_id[:3].title())


def get_displayed_resource_ids() -> List[str]:
    """Return the resource ids to show in every-resource grids.

    Order: planetary group first (the harvested/refined materials), then
    operational group (fuel/energy/ammo). Driven by `display_group` in
    `data/resources.json` so adding a resource appears as a new column
    automatically with no UI code change.
    """
    catalog = ResourceCatalog.from_json()
    return (
        [d.id for d in catalog.by_display_group("planetary")]
        + [d.id for d in catalog.by_display_group("operational")]
    )
