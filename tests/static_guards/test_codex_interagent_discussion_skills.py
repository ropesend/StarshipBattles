from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILL_ROOT = ROOT / ".agents" / "skills"
DISCUSSION_SKILLS = (
    "codex-discuss-start",
    "codex-discuss-respond",
    "codex-discuss-continue",
)


def _read_skill(name: str) -> str:
    return (SKILL_ROOT / name / "SKILL.md").read_text(encoding="utf-8")


def _read_openai_yaml(name: str) -> str:
    return (SKILL_ROOT / name / "agents" / "openai.yaml").read_text(encoding="utf-8")


def _contains_unprefixed_message_filename(text: str) -> bool:
    pattern = r"(?<!arc\d{2}_)00[1-9]_(?:codex|claude)_to_(?:codex|claude)\.md"
    return re.search(pattern, text) is not None


def test_codex_discussion_skills_exist_with_matching_frontmatter() -> None:
    expected = {
        "codex-discuss-start": "Start an inter-agent discussion with Claude Code and/or OpenCode",
        "codex-discuss-respond": "Respond as Codex in a v2.6 inter-agent discussion with Claude Code and/or OpenCode",
        "codex-discuss-continue": "Continue an ended v2.6 inter-agent discussion",
    }

    for skill_name, description_fragment in expected.items():
        text = _read_skill(skill_name)

        assert text.startswith("---\n")
        assert f"name: {skill_name}\n" in text
        assert description_fragment in text


def test_codex_discussion_skills_document_shared_protocol() -> None:
    for skill_name in DISCUSSION_SKILLS:
        text = _read_skill(skill_name)

        assert "interagent-discussion/v1" in text
        assert "AgentCoordination/protocols/interagent_discussion.md" in text
        assert "claude" in text
        assert "codex" in text
        assert "opencode" in text
        assert "^arc\\d{2}_\\d{3}_(claude|codex|opencode)_to_(claude|codex|opencode)\\.md$" in text
        assert "message_index" in text
        assert "agent_turn" in text
        assert "participants" in text
        assert "turn_order" in text
        assert "status: continue" in text
        assert "continue | consensus | needs-user" in text
        assert "outcome.md" in text
        assert "temporary file" in text
        assert "same-directory" in text
        assert "complete: true" in text
        assert "ack_arc<NN>_<MMM>_<from>_to_<to>_<acker>.md" in text
        assert "heartbeat" in text.lower()
        assert "last_seen_message" in text


def test_codex_discussion_skills_drop_unprefixed_message_compatibility() -> None:
    for skill_name in DISCUSSION_SKILLS:
        text = _read_skill(skill_name)

        assert not _contains_unprefixed_message_filename(text)
        assert "treated as `arc: 1`" not in text
        assert "treated as arc 1" not in text
        assert "???_*_to_*.md" not in text
        assert "c:\\Dev\\StarshipBattles" not in text
        assert "C:\\Dev2\\StarshipBattles" not in text
        assert "C:\\Dev\\Starship Battles" not in text


def test_codex_discussion_skills_document_v2_refinements() -> None:
    for skill_name in DISCUSSION_SKILLS:
        text = _read_skill(skill_name)

        assert "frontmatter on line 1" in text
        assert "plans/" in text
        assert "revision:" in text
        assert ".tmp_*" in text
        assert "extension_requested_cap: <extended_cap>" in text
        assert "extension_accepted: true" in text
        assert "message_cap: <extended_cap>" in text
        assert "user_facing_agent" in text
        assert "implementation_owner" in text

    for skill_name in ("codex-discuss-start", "codex-discuss-continue"):
        text = _read_skill(skill_name)

        assert "User-supplied context" in text
        assert "topic.md" in text


def test_codex_discussion_message_examples_put_frontmatter_first() -> None:
    for skill_name in DISCUSSION_SKILLS:
        text = _read_skill(skill_name)

        assert "visible prefix" not in text
        assert "Codex message 001\n\n---" not in text
        assert "Codex message 002\n\n---" not in text


def test_codex_discussion_skills_document_v21_implementation_notes() -> None:
    for skill_name in DISCUSSION_SKILLS:
        text = _read_skill(skill_name)
        frontmatter = text.split("---", 2)[1]

        assert "argument-hint:" not in frontmatter
        assert ".tmp_<guid>.md" in text
        assert ".md.tmp" not in text
        assert "retry once" in text.lower()
        assert "Poll every 30 seconds" in text
        assert "same terminal status" in text
        assert "write `outcome.md`" in text
        assert "pre-flight checks must not mutate" in text.lower()
        assert "final segment contains whitespace" in text
        assert "host-neutral" in text or "<repo-root>" in text


def test_codex_discussion_skills_document_v26_protocol() -> None:
    for skill_name in DISCUSSION_SKILLS:
        text = _read_skill(skill_name)

        assert "v2.4_three_party_spec_r002.md" not in text
        assert "protocol_version: 2.6" in text
        assert "v2.2_spec_r002.md" not in text
        assert "arc01_001" in text
        assert "v2.3" in text
        assert "readback" in text
        assert "ended_at_arc" in text
        assert "implementation_owner" in text
        assert "outcome_arc<NN>.md" in text
        assert "plans/<name>_r001.md" in text
        assert "Never overwrite" in text
        assert "parent folder" in text
        assert "mandatory observer" in text.lower()
        assert "warn" in text.lower()
        assert "halt" in text.lower()


def test_codex_discussion_start_documents_parent_and_slug() -> None:
    text = _read_skill("codex-discuss-start")

    assert "[--folder <parent>] [--slug <slug>] [--with <agents>] [context...]" in text
    assert "YYYYMMDDTHHMMSSZ_<slug>" in text
    assert "Do not infer a slug" in text
    assert "Accepted values are `claude`, `opencode`" in text


def test_codex_discussion_respond_documents_parent_discovery() -> None:
    text = _read_skill("codex-discuss-respond")
    prompt = _read_openai_yaml("codex-discuss-respond")

    assert "Accept either an exact discussion leaf or a parent folder" in text
    assert "scan immediate child" in text
    assert "Zero candidates: poll the parent" in text
    assert "ended leaves are handled by `codex-discuss-continue`" in text
    assert "candidate child folder names" in text

    assert "polls briefly" in prompt
    assert "v2.6" in prompt


def test_codex_discussion_continue_documents_no_args_role_aware_flow() -> None:
    text = _read_skill("codex-discuss-continue")
    prompt = _read_openai_yaml("codex-discuss-continue")

    assert "[--folder <path>] [context...]" in text
    assert "<folder> [context...]" not in text
    assert "No positional folder" in text
    assert "<repo-root>/AgentCoordination/Scratchpad/Discussion" in text
    assert "parent folder and scan immediate children" in text
    assert "original starter" in text
    assert "authorized continuation starter" in text
    assert "outcome_arc<NN>.md" in text

    assert "[--folder <path>] [context...]" in prompt
    assert "authorized continuation starter" in prompt
    assert "v2.6" in prompt
