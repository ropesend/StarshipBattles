"""Shared colonization fixtures.

PROJ-479 Task 6.2 (HLP-002): canonical `MockPlanetType` Enum covering all
variants observed in the test suite (CONTINENTAL, ICE_DWARF, ARID,
DYSON_SPHERE). Replaces 10+ near-identical inline definitions across
colonization / strategy / engine tests.
"""
from __future__ import annotations

from enum import Enum


class MockPlanetType(Enum):
    """Mock planet types for colonization tests.

    Includes every variant observed in the inline copies that this
    canonical definition replaces.
    """

    ICE_DWARF = "ICE_DWARF"
    CONTINENTAL = "CONTINENTAL"
    ARID = "ARID"
    DYSON_SPHERE = "DYSON_SPHERE"
