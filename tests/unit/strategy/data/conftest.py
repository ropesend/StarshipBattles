"""Pytest fixture bridge for ``tests/unit/strategy/data/`` (PROJ-378).

Exposes ``make_galaxy_stub()`` as the ``galaxy_stub`` pytest fixture so
unit tests in this directory can inject a stubbed ``Galaxy`` without an
explicit import. Cross-tree callers (e.g. integration tests) import
``make_galaxy_stub`` directly from ``tests.fixtures.galaxy_fixtures``.
"""
from __future__ import annotations

import pytest

from tests.fixtures.galaxy_fixtures import make_galaxy_stub


@pytest.fixture
def galaxy_stub():
    """Minimal post-PROJ-372 ``Galaxy`` with ``_state``/``_registry``/``_spatial`` wired."""
    return make_galaxy_stub()
