"""Tests for strategic effect ability display helpers."""

from game.strategy.services.effect_ability_display import (
    format_intrinsic_ability_magnitude,
    make_display_name,
    make_group_key,
)


def test_make_group_key_unknown_or_malformed_payload_uses_ability_name() -> None:
    assert make_group_key("NotARealAbility", {"resource_type": "metals"}) == "NotARealAbility"
    assert make_group_key("ResourceHarvestBooster", True) == "ResourceHarvestBooster"


def test_make_group_key_environmental_damage_missing_type_uses_legacy_fallback() -> None:
    assert (
        make_group_key("EnvironmentalDamage", {"rate": 0.2})
        == "EnvironmentalDamage:environmental"
    )


def test_make_display_name_unknown_returns_ability_name() -> None:
    assert make_display_name("NotARealAbility", {"resource_type": "metals"}) == "NotARealAbility"


def test_make_display_name_derived_labels_handle_missing_grouping_fields() -> None:
    assert make_display_name("ResourceHarvestBooster", {}) == "Unknown Harvest Boost"
    assert make_display_name("EnvironmentalDamage", {}) == "Environmental Damage"


def test_format_intrinsic_ability_magnitude_rejects_unknown_and_malformed_payloads() -> None:
    assert format_intrinsic_ability_magnitude("NotARealAbility", {"multiplier": 0.5}) == ""
    assert format_intrinsic_ability_magnitude("ShieldModifier", True) == ""
    assert format_intrinsic_ability_magnitude("ShieldModifier", {"multiplier": "bad"}) == ""
    assert format_intrinsic_ability_magnitude("FuelDrain", {"rate": "bad"}) == ""


def test_format_intrinsic_ability_magnitude_renders_registered_rate_and_multiplier() -> None:
    assert format_intrinsic_ability_magnitude("StrategicSpeedModifier", {"multiplier": 1.5}) == "x1.50"
    assert format_intrinsic_ability_magnitude("EnvironmentalDamage", {"rate": 0.25}) == "-0.25 hull/turn"
    assert format_intrinsic_ability_magnitude("FuelDrain", {"rate": 0.75}) == "-0.75 fuel/turn"
