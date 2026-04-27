"""Race description prompt builder (PROJ-299).

Pure module-level functions that assemble chat-completion messages for
the LLM to generate biological / sociological race descriptions.

Mirrors the `build_test_battle_spec` / `build_strategy_battle_spec`
style — stateless utility, not a service registered on
ApplicationContext.

The builder reads:
- A `RaceConfig` (identity, aptitudes, environmental preferences,
  homeworld_type)
- A `captions` dict with optional 'flag', 'portrait', 'theme' entries.
  Missing entries are tolerated; the prompt substitutes a
  `{"note": "no visual reference"}` marker so the LLM doesn't invent
  visual details.

The system prompts include ONE worked example of the desired output
tone — sets style without per-request token cost on the user message.
"""
from __future__ import annotations

import json
from typing import Dict, List, Optional

from game.services.llm.types import Message, Role
from game.strategy.data.habitability_factors import FACTOR_REGISTRY
from game.strategy.data.race_config import APTITUDE_NAMES, RaceConfig

# Aptitude display names. Imported lazily inside the helper to avoid
# pulling pygame_gui via game.ui at strategy-layer import time.
_APTITUDE_DISPLAY_NAMES_CACHE: Optional[Dict[str, str]] = None


def _aptitude_display_names() -> Dict[str, str]:
    global _APTITUDE_DISPLAY_NAMES_CACHE
    if _APTITUDE_DISPLAY_NAMES_CACHE is None:
        # Hardcoded mirror of game.ui.panels.race_aptitudes_panel.APTITUDE_DISPLAY_NAMES
        # to avoid the strategy → UI dependency. If you edit one, edit
        # the other.
        _APTITUDE_DISPLAY_NAMES_CACHE = {
            "strength": "Strength",
            "intelligence": "Intelligence",
            "constitution": "Constitution",
            "dexterity": "Dexterity",
            "tolerance_other_species": "Species Tolerance",
            "cooperation": "Cooperation",
            "conflict_tolerance": "Conflict Tolerance",
        }
    return _APTITUDE_DISPLAY_NAMES_CACHE


# ============================================================================
# System prompts (each ~250 tokens with one worked EXAMPLE)
# ============================================================================


_SYSTEM_PROMPT_BIO = """\
You are a lore writer for a 4X space strategy game. The player has
just designed a custom alien species. You will be given:

  - the species' identity (name, faction, government, leader, physical
    type, society type)
  - their seven aptitudes on a 1-100 scale (50 is average)
  - their environmental preferences (gravity, temperature, water,
    pressure, atmospheric composition)
  - their homeworld type
  - structured visual descriptions of their flag, a representative
    individual, and their starship aesthetic

Your task: write a single biological description of the species,
~200-250 words, plain prose, no markdown, no headings.

Tone: immersive, specific, slightly poetic. Describe anatomy,
sensory adaptations, life cycle, and any biology suggested by the
aptitudes and environment. Show, don't tell. Avoid generic sci-fi
clichés.

EXAMPLE — for a fictional reptilian Zarlith species with high
strength + low species-tolerance, dry homeworld:

The Zarlithians are a dense-boned reptilian people, evolved on the
ochre flats of a low-water world where surface life clings to deep
caverns and basaltic shade. Their teal-scaled torsos taper to lean
limbs and a counterbalancing tail; the four amber eyes — three
clustered low, one mounted higher on the brow — give them the
panoramic predator's awareness their hunting heritage demands. They
are ovoviviparous, the brood retained internally until the young can
walk; broodings are rare, perhaps two in a Zarlithian century.
Skin oils carry a faintly sulphurous musk that closes-rank alarm
pheromones; outsiders who do not know to disregard it find Zarlithian
gatherings physically uncomfortable. Their muscles are wound tight
with lattice-fibre proteins of unusually high tensile strength,
explaining the species' reputation for raw physical power even at
unimpressive frame. They sleep in short bouts, three to four hours,
preferring the heat of the day.

OUTPUT ONLY THE DESCRIPTION. No preamble, no headings, no markdown.
"""


_SYSTEM_PROMPT_SOCIO = """\
You are a lore writer for a 4X space strategy game. The player has
just designed a custom alien species. You will be given the same
inputs as for the biological description: identity, aptitudes,
environment, homeworld, and visual descriptions of their flag,
portrait, and ship aesthetic.

Your task: write a single sociological description of the species'
civilisation — government style, social organisation, values, key
cultural quirks, and how they treat outsiders. ~200-250 words, plain
prose, no markdown, no headings.

Tone: immersive, specific, slightly poetic. Anchor concrete cultural
practices in the aptitudes and the visual aesthetic. Avoid generic
sci-fi clichés. Show, don't tell.

EXAMPLE — for the same Zarlith species (high strength, low
species-tolerance, conqueror society):

Zarlithian civilisation is organised as a tiered Imperator's court of
chosen-blooded houses; the Imperator Vex IV, like all of his line, was
raised within the inner palace from hatching and is forbidden from
walking the open street. The houses compete for prestige through
public works of brutalist scale — basalt aqueducts, fortress-temples,
and monumental signal-towers visible at any horizon. Outsiders are
afforded ritual contempt: greeted with stiff formal courtesy, then
quietly steered toward the kitchen entrance. Social standing is
measured almost entirely in displays of physical capability and
demonstrable loyalty to one's house; cleverness is suspect, and
Zarlithian academies teach engineering as a martial art rather than
as scholarship. Their crimson-and-gold banners — the predatory eagle
clutching swords — flank every public space, and the empire's ships
are sleek charcoal arrowheads, austere and unornamented save for thin
scarlet accents that mark the engine bell. Zarlithian funerals are
open-pyre and brief; mourning is performed in the workshop, by
hammering out a single perfect blade in the deceased's name.

OUTPUT ONLY THE DESCRIPTION. No preamble, no headings, no markdown.
"""


# ============================================================================
# Public API
# ============================================================================


def build_bio_prompt(
    race_config: RaceConfig, captions: Dict[str, Optional[dict]]
) -> List[Message]:
    """Build the chat-completion messages for a biological description.

    Args:
        race_config: The player's race configuration.
        captions: Dict with optional keys 'flag', 'portrait', 'theme'
            mapping to parsed sidecar dicts. Missing keys are treated
            as no-caption (a `{"note": "no visual reference"}` marker
            is substituted in the prompt).

    Returns:
        A list of `Message` ready to pass to `LLMProvider.complete()`.
    """
    return [
        Message(role=Role.SYSTEM, content=_SYSTEM_PROMPT_BIO),
        Message(role=Role.USER, content=_render_user_payload(race_config, captions)),
    ]


def build_socio_prompt(
    race_config: RaceConfig, captions: Dict[str, Optional[dict]]
) -> List[Message]:
    """Build the chat-completion messages for a sociological description.

    Same shape as `build_bio_prompt`; differs only in the system prompt.
    """
    return [
        Message(role=Role.SYSTEM, content=_SYSTEM_PROMPT_SOCIO),
        Message(role=Role.USER, content=_render_user_payload(race_config, captions)),
    ]


# ============================================================================
# Helpers
# ============================================================================


def _render_user_payload(
    race_config: RaceConfig, captions: Dict[str, Optional[dict]]
) -> str:
    """Assemble the user-message JSON-shaped payload as a readable string."""
    payload = {
        "identity": _render_identity(race_config),
        "homeworld_type": race_config.homeworld_type or "(unspecified)",
        "aptitudes": _render_aptitudes(race_config),
        "environment": _render_preferences(race_config),
        "flag_caption": _render_caption_or_note(captions.get("flag")),
        "portrait_caption": _render_caption_or_note(captions.get("portrait")),
        "theme_caption": _render_caption_or_note(captions.get("theme")),
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)


def _render_identity(race_config: RaceConfig) -> Dict[str, str]:
    return {
        "race_name": race_config.race_name or race_config.name,
        "race_name_plural": race_config.race_name_plural,
        "faction_name": race_config.faction_name,
        "government_type": race_config.government_type,
        "government_organization": race_config.government_organization,
        "leader_title": race_config.leader_title,
        "leader_name": race_config.leader_name,
        "physical_type": race_config.physical_type,
        "society_type": race_config.society_type,
    }


def _render_aptitudes(race_config: RaceConfig) -> Dict[str, str]:
    """Returns {display_name: 'value/100'} for each of the 7 aptitudes."""
    display_names = _aptitude_display_names()
    out: Dict[str, str] = {}
    for apt_name in APTITUDE_NAMES:
        display = display_names[apt_name]
        value = getattr(race_config, f"aptitude_{apt_name}")
        out[display] = f"{value}/100"
    return out


def _render_preferences(race_config: RaceConfig) -> Dict[str, str]:
    """Render `preferences` as {display_name: 'setpoint ±tolerance display_unit'}.

    Only includes factors that are present in both `preferences` and
    `FACTOR_REGISTRY`, so an unknown extra preference doesn't crash.
    """
    out: Dict[str, str] = {}
    for factor_id, pref in race_config.preferences.items():
        factor = FACTOR_REGISTRY.get(factor_id)
        if factor is None:
            continue
        scale = factor.display_scale
        precision = factor.display_precision
        unit = factor.display_unit
        sp = pref.setpoint * scale
        tol = pref.tolerance * scale
        sp_str = f"{sp:.{precision}f}"
        tol_str = f"{tol:.{precision}f}"
        unit_suffix = f" {unit}" if unit else ""
        out[factor.display_name] = f"{sp_str}{unit_suffix} (tolerance ±{tol_str}{unit_suffix})"
    return out


def _render_caption_or_note(caption: Optional[dict]) -> dict:
    """Return the caption dict, or a no-visual-reference marker."""
    if caption is None:
        return {"note": "no visual reference available for this asset"}
    return caption


__all__ = ["build_bio_prompt", "build_socio_prompt"]
