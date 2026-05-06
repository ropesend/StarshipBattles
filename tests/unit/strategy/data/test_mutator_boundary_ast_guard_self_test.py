"""Self-test for the AST-walker helper used by the mutator-boundary guard.

PROJ-370 Phase 1: lock down the harness with synthetic in-memory fixtures
before any real boundary work flips on. The harness must catch all four
illegal-write patterns and reject all four legal-access patterns.
"""
from __future__ import annotations

import pytest

from tests.unit.strategy.data._mutator_ast_walker import find_attribute_writes


# ---- 4 illegal patterns (each must be caught) ----

ILLEGAL_BARE_STORE = """
def f(fleet):
    fleet.location = (1, 2)
"""

ILLEGAL_AUG_STORE = """
def f(fleet):
    fleet.path += [(1, 2)]
"""

ILLEGAL_SUBSCRIPT_ASSIGN = """
def f(planet):
    planet.stockpile["metals"] = 100.0
"""

ILLEGAL_METHOD_MUTATION = """
def f(planet):
    planet.populations.append(some_pop)
    planet.facilities.remove(other)
    planet.orders.pop(0)
    planet.staging_yard.clear()
    planet.populations.extend(others)
    planet.orders.insert(0, x)
"""

# ---- 4 legal access patterns (each must NOT be caught) ----

LEGAL_READ = """
def f(fleet):
    if fleet.location == (1, 2):
        return fleet.path
"""

LEGAL_LOCAL_ASSIGN = """
def f():
    location = (1, 2)
    location = (3, 4)  # local var, not attribute
    return location
"""

LEGAL_OTHER_OBJECT_ATTR = """
def f(other_obj):
    # Same attribute name on a different object — this is allowed when the
    # target_attrs check only filters by attribute name; but the helper
    # surfaces ALL such writes and lets the parameterized AST-guard test
    # apply the path-allowlist.
    other_obj.location = (1, 2)
"""

LEGAL_NESTED_READ = """
def f(fleet):
    n = len(fleet.orders)
    return fleet.orders[0] if n else None
"""

LEGAL_METHOD_CALL_NOT_MUTATION = """
def f(fleet):
    # Call to a method whose name isn't in our mutation set.
    fleet.orders.copy()
    fleet.path.index((1, 2))
"""


@pytest.mark.parametrize(
    ("source", "expected_attrs"),
    [
        (ILLEGAL_BARE_STORE, {"location"}),
        (ILLEGAL_AUG_STORE, {"path"}),
        (ILLEGAL_SUBSCRIPT_ASSIGN, {"stockpile"}),
        (ILLEGAL_METHOD_MUTATION, {"populations", "facilities", "orders", "staging_yard"}),
    ],
)
def test_illegal_writes_caught(source: str, expected_attrs: set[str]) -> None:
    """Every illegal write surfaces a hit with the matching attribute name."""
    hits = find_attribute_writes(
        source,
        target_attrs=expected_attrs,
        filename="<test>",
    )
    assert hits, "Helper failed to catch an illegal write."
    found_attrs = {hit.attr for hit in hits}
    assert found_attrs & expected_attrs, (
        f"Expected {expected_attrs}, got {found_attrs} from hits: {hits}"
    )


@pytest.mark.parametrize(
    ("source", "target_attrs"),
    [
        (LEGAL_READ, {"location", "path"}),
        (LEGAL_LOCAL_ASSIGN, {"location"}),
        (LEGAL_NESTED_READ, {"orders"}),
        (LEGAL_METHOD_CALL_NOT_MUTATION, {"orders", "path"}),
    ],
)
def test_legal_access_not_flagged(source: str, target_attrs: set[str]) -> None:
    """Reads, local assignments, and non-mutation method calls produce no hits."""
    hits = find_attribute_writes(
        source,
        target_attrs=target_attrs,
        filename="<test>",
    )
    assert hits == [], f"Helper produced false positives: {hits}"


def test_other_object_attr_is_caught_by_attr_name() -> None:
    """The walker is attribute-name-based; path-allowlist filtering happens
    at the parameterized-test layer, not the walker. So a legal-access on
    a different object that shares the attribute name IS surfaced — and
    the test layer above filters it via path allowlist."""
    hits = find_attribute_writes(
        LEGAL_OTHER_OBJECT_ATTR,
        target_attrs={"location"},
        filename="<test>",
    )
    assert len(hits) == 1
    assert hits[0].attr == "location"


def test_walker_handles_comments_and_strings() -> None:
    """Comments and string literals containing 'fleet.location = X' are not
    parsed as writes — that's the whole reason for using ast.parse over regex."""
    source = '''
def f(fleet):
    # This comment says fleet.location = (1, 2) but is not a write.
    s = "fleet.location = (1, 2)"  # nor is this string literal
    return s
'''
    hits = find_attribute_writes(
        source,
        target_attrs={"location"},
        filename="<test>",
    )
    assert hits == []


def test_walker_handles_multiline_assignments() -> None:
    """Multi-line writes are parsed correctly."""
    source = '''
def f(fleet):
    fleet.path = [
        (1, 2),
        (3, 4),
        (5, 6),
    ]
'''
    hits = find_attribute_writes(
        source,
        target_attrs={"path"},
        filename="<test>",
    )
    assert len(hits) == 1
    assert hits[0].attr == "path"
