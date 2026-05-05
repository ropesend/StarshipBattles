"""Direct helper coverage for race randomizer branch behavior."""

import random

from game.strategy.systems.race_randomizer import RaceRandomizer, _resolve_rng


def test_resolve_rng_returns_provided_instance() -> None:
    rng = random.Random(123)

    resolved = _resolve_rng(rng)

    assert resolved is rng


def test_resolve_rng_none_returns_fresh_random_instances() -> None:
    first = _resolve_rng(None)
    second = _resolve_rng(None)

    assert isinstance(first, random.Random)
    assert isinstance(second, random.Random)
    assert first is not second


def test_pick_name_entry_prefers_portrait_names() -> None:
    data = {
        "portraits": {
            "portrait_a": {
                "names": [{"name": "Aurelian", "plural": "Aurelians"}],
            },
        },
        "fallback_names": [{"name": "Fallback", "plural": "Fallbacks"}],
    }

    entry = RaceRandomizer._pick_name_entry(data, "portrait_a", random.Random(1))

    assert entry == {"name": "Aurelian", "plural": "Aurelians"}


def test_pick_name_entry_empty_portrait_names_uses_fallback() -> None:
    data = {
        "portraits": {"portrait_a": {"names": []}},
        "fallback_names": [{"name": "Fallback", "plural": "Fallbacks"}],
    }

    entry = RaceRandomizer._pick_name_entry(data, "portrait_a", random.Random(1))

    assert entry == {"name": "Fallback", "plural": "Fallbacks"}


def test_pick_name_entry_without_fallback_returns_unknown() -> None:
    entry = RaceRandomizer._pick_name_entry(
        {"portraits": {"portrait_a": {"names": []}}},
        "portrait_a",
        random.Random(1),
    )

    assert entry == {"name": "Unknown", "plural": "Unknown"}


def test_pick_leader_prefers_portrait_leaders() -> None:
    data = {
        "portraits": {"portrait_a": {"leaders": ["Director Vale"]}},
        "fallback_leaders": ["Fallback Leader"],
    }

    leader = RaceRandomizer._pick_leader(data, "portrait_a", random.Random(1))

    assert leader == "Director Vale"


def test_pick_leader_empty_portrait_leaders_uses_fallback() -> None:
    data = {
        "portraits": {"portrait_a": {"leaders": []}},
        "fallback_leaders": ["Fallback Leader"],
    }

    leader = RaceRandomizer._pick_leader(data, "portrait_a", random.Random(1))

    assert leader == "Fallback Leader"


def test_pick_leader_without_fallback_returns_generic_leader() -> None:
    leader = RaceRandomizer._pick_leader(
        {"portraits": {"portrait_a": {"leaders": []}}},
        "portrait_a",
        random.Random(1),
    )

    assert leader == "Leader"
