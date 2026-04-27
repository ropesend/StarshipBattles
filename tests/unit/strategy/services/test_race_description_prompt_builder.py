"""Tests for race_description_prompt_builder (PROJ-299 Phase 3)."""
from __future__ import annotations

import pytest

from game.services.llm.types import Message, Role
from game.strategy.data.race_config import RaceConfig


# ============================================================================
# Test fixtures
# ============================================================================


def _sample_race(**overrides) -> RaceConfig:
    """Build a RaceConfig with sensible defaults for prompt testing."""
    defaults = dict(
        race_id="rid",
        name="Zarlith",
        faction_name="Zarlith Empire",
        race_name="Zarlith",
        race_name_plural="Zarlithians",
        government_type="Empire",
        government_organization="Autocracy",
        leader_title="Imperator",
        leader_name="Vex IV",
        physical_type="Reptilian",
        society_type="Conquerors",
        flag_id="flag_zarlith_001",
        portrait_id="zarlith_portrait.jpg",
        theme_id="Federation",
        homeworld_type="ARID",
        aptitude_strength=80,
        aptitude_intelligence=60,
        aptitude_constitution=70,
        aptitude_dexterity=55,
        aptitude_tolerance_other_species=20,
        aptitude_cooperation=45,
        aptitude_conflict_tolerance=85,
    )
    defaults.update(overrides)
    return RaceConfig(**defaults)


def _sample_captions(*, with_flag=True, with_portrait=True, with_theme=True) -> dict:
    captions: dict = {}
    if with_flag:
        captions["flag"] = {
            "schema_version": 1,
            "geometry": "Vertical bicolour with central emblem.",
            "color_palette": "Crimson and gold.",
            "symbolism": "Predatory eagle clutching swords.",
            "cultural_hints": "Imperial society, martial nobility.",
            "mood": "aggressive",
            "distinctive_traits": "Sword-shaped wing feathers.",
        }
    if with_portrait:
        captions["portrait"] = {
            "schema_version": 1,
            "anatomy": "Bipedal reptilian, 2m tall.",
            "coloration": "Teal scales, ochre belly.",
            "attire_and_adornment": "Bronze breastplate.",
            "posture_and_expression": "Upright, gaze steady.",
            "technology_level_hint": "industrial",
            "distinctive_traits": "Four eyes in a vertical column.",
        }
    if with_theme:
        captions["theme"] = {
            "schema_version": 1,
            "hull_geometry": "Arrowhead silhouette.",
            "materials_and_finish": "Matte charcoal composite.",
            "design_philosophy": "Speed and stealth.",
            "color_scheme": "Charcoal with scarlet accents.",
            "technology_level_hint": "advanced",
            "distinctive_traits": "Twin knife-thin nacelles.",
        }
    return captions


# ============================================================================
# Bio prompt
# ============================================================================


class TestBuildBioPrompt:
    def test_returns_list_of_messages(self):
        from game.strategy.services.race_description_prompt_builder import (
            build_bio_prompt,
        )

        messages = build_bio_prompt(_sample_race(), _sample_captions())
        assert isinstance(messages, list)
        assert len(messages) >= 2
        assert all(isinstance(m, Message) for m in messages)

    def test_first_message_is_system(self):
        from game.strategy.services.race_description_prompt_builder import (
            build_bio_prompt,
        )

        messages = build_bio_prompt(_sample_race(), _sample_captions())
        assert messages[0].role == Role.SYSTEM

    def test_last_message_is_user(self):
        from game.strategy.services.race_description_prompt_builder import (
            build_bio_prompt,
        )

        messages = build_bio_prompt(_sample_race(), _sample_captions())
        assert messages[-1].role == Role.USER

    def test_system_prompt_includes_few_shot_marker(self):
        """System prompt should include the worked-example marker."""
        from game.strategy.services.race_description_prompt_builder import (
            build_bio_prompt,
        )

        messages = build_bio_prompt(_sample_race(), _sample_captions())
        # Some recognisable substring from the few-shot example
        assert "EXAMPLE" in messages[0].content or "example" in messages[0].content

    def test_user_prompt_includes_identity_fields(self):
        from game.strategy.services.race_description_prompt_builder import (
            build_bio_prompt,
        )

        messages = build_bio_prompt(_sample_race(), _sample_captions())
        user = messages[-1].content
        assert "Zarlith" in user
        assert "Empire" in user
        assert "Imperator" in user
        assert "Vex IV" in user
        assert "Reptilian" in user

    def test_user_prompt_includes_all_seven_aptitudes_with_display_names(self):
        from game.strategy.services.race_description_prompt_builder import (
            build_bio_prompt,
        )

        messages = build_bio_prompt(_sample_race(), _sample_captions())
        user = messages[-1].content
        for display_name in (
            "Strength", "Intelligence", "Constitution", "Dexterity",
            "Species Tolerance", "Cooperation", "Conflict Tolerance",
        ):
            assert display_name in user, f"missing aptitude '{display_name}' in prompt"
        # And the values
        assert "80" in user  # strength
        assert "20" in user  # tolerance

    def test_user_prompt_includes_environmental_preferences(self):
        from game.strategy.services.race_description_prompt_builder import (
            build_bio_prompt,
        )

        messages = build_bio_prompt(_sample_race(), _sample_captions())
        user = messages[-1].content
        # FACTOR_REGISTRY display names
        assert "Gravity" in user
        assert "Temperature" in user

    def test_user_prompt_includes_homeworld_type(self):
        from game.strategy.services.race_description_prompt_builder import (
            build_bio_prompt,
        )

        messages = build_bio_prompt(_sample_race(), _sample_captions())
        assert "ARID" in messages[-1].content

    def test_user_prompt_includes_caption_content(self):
        from game.strategy.services.race_description_prompt_builder import (
            build_bio_prompt,
        )

        messages = build_bio_prompt(_sample_race(), _sample_captions())
        user = messages[-1].content
        # Substrings from the sample captions
        assert "Predatory eagle" in user
        assert "Bipedal reptilian" in user
        assert "Arrowhead silhouette" in user

    def test_missing_caption_inserts_no_visual_reference_note(self):
        from game.strategy.services.race_description_prompt_builder import (
            build_bio_prompt,
        )

        # No flag caption
        captions = _sample_captions(with_flag=False)
        messages = build_bio_prompt(_sample_race(), captions)
        user = messages[-1].content
        assert "no visual reference" in user.lower()

    def test_deterministic_for_same_input(self):
        from game.strategy.services.race_description_prompt_builder import (
            build_bio_prompt,
        )

        a = build_bio_prompt(_sample_race(), _sample_captions())
        b = build_bio_prompt(_sample_race(), _sample_captions())
        assert [(m.role, m.content) for m in a] == [(m.role, m.content) for m in b]


# ============================================================================
# Socio prompt
# ============================================================================


class TestBuildSocioPrompt:
    def test_returns_messages_with_socio_focused_system_prompt(self):
        from game.strategy.services.race_description_prompt_builder import (
            build_socio_prompt,
        )

        messages = build_socio_prompt(_sample_race(), _sample_captions())
        assert messages[0].role == Role.SYSTEM
        # The socio system prompt must be different from the bio one
        from game.strategy.services.race_description_prompt_builder import (
            build_bio_prompt,
        )
        bio_messages = build_bio_prompt(_sample_race(), _sample_captions())
        assert messages[0].content != bio_messages[0].content

    def test_socio_user_prompt_includes_identity_and_aptitudes(self):
        from game.strategy.services.race_description_prompt_builder import (
            build_socio_prompt,
        )

        messages = build_socio_prompt(_sample_race(), _sample_captions())
        user = messages[-1].content
        assert "Zarlith" in user
        assert "Cooperation" in user
        assert "Conflict Tolerance" in user

    def test_socio_includes_caption_content(self):
        from game.strategy.services.race_description_prompt_builder import (
            build_socio_prompt,
        )

        messages = build_socio_prompt(_sample_race(), _sample_captions())
        user = messages[-1].content
        assert "Imperial society" in user

    def test_missing_all_captions_does_not_raise(self):
        from game.strategy.services.race_description_prompt_builder import (
            build_socio_prompt,
        )

        # All captions missing
        messages = build_socio_prompt(
            _sample_race(),
            _sample_captions(with_flag=False, with_portrait=False, with_theme=False),
        )
        user = messages[-1].content
        # All three should have the no-visual-reference marker
        assert user.lower().count("no visual reference") >= 3
