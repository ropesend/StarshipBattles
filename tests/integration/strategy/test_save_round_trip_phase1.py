"""PROJ-372 Phase 1: save round-trip equality after the stars.py split.

Asserts that ``Star.to_dict() -> from_dict() -> to_dict()`` is a
fixed-point on a freshly-generated star and a directly-constructed
spectrum. Phase 5 introduces the canonical full-galaxy round-trip
test; this is a Phase-1 boundary check.
"""
from __future__ import annotations

import random

from game.strategy.data.spectrum import Spectrum
from game.strategy.data.stars import Star
from game.strategy.generation.star_generator import StarGenerator


def test_star_to_dict_from_dict_round_trip() -> None:
    random.seed(42)
    gen = StarGenerator(image_registry=None)
    stars = gen.generate_system_stars("RoundTrip")
    assert stars, "StarGenerator returned no stars"

    for s in stars:
        d = s.to_dict()
        s2 = Star.from_dict(d)
        d2 = s2.to_dict()
        assert d == d2, f"Round-trip drift on {s.name}"


def test_spectrum_round_trip() -> None:
    s = Spectrum(
        gamma_ray=0.1, xray=0.2, ultraviolet=0.3, blue=0.4, green=0.5,
        red=0.6, infrared=0.7, microwave=0.8, radio=0.9,
    )
    s2 = Spectrum.from_dict(s.to_dict())
    assert s == s2


def test_star_intrinsic_abilities_round_trip() -> None:
    random.seed(7)
    gen = StarGenerator(image_registry=None)
    stars = gen.generate_system_stars("Pulsar")
    star = stars[0]
    star.intrinsic_abilities = {"PulsarFlash": {"intensity": 0.5}}
    s2 = Star.from_dict(star.to_dict())
    assert s2.intrinsic_abilities == {"PulsarFlash": {"intensity": 0.5}}
