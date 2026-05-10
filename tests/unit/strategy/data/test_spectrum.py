"""PROJ-372 Phase 1: Spectrum unit tests (post-extraction).

Spectrum lives in its own module now; these tests cover the
to_dict/from_dict round-trip, output aggregation, and the
PersistenceException path on malformed data.
"""
from __future__ import annotations

import pytest

from game.core.exceptions import PersistenceException
from game.strategy.data.spectrum import Spectrum


def _sample_spectrum() -> Spectrum:
    return Spectrum(
        gamma_ray=1.0, xray=2.0, ultraviolet=3.0, blue=4.0, green=5.0,
        red=6.0, infrared=7.0, microwave=8.0, radio=9.0,
    )


def test_get_total_output_sums_all_bands() -> None:
    assert _sample_spectrum().get_total_output() == 45.0


def test_to_dict_round_trip() -> None:
    s = _sample_spectrum()
    d = s.to_dict()
    s2 = Spectrum.from_dict(d)
    assert s == s2
    assert s2.to_dict() == d


def test_from_dict_missing_key_raises() -> None:
    bad = _sample_spectrum().to_dict()
    del bad["radio"]
    with pytest.raises(PersistenceException):
        Spectrum.from_dict(bad)


def test_from_dict_negative_value_raises() -> None:
    bad = _sample_spectrum().to_dict()
    bad["xray"] = -0.1
    with pytest.raises(PersistenceException):
        Spectrum.from_dict(bad)


def test_stars_module_re_exports_spectrum() -> None:
    """Backward-compat: external code imports Spectrum from stars.py."""
    from game.strategy.data import stars

    assert stars.Spectrum is Spectrum
