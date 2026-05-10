from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
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
        "codex-discuss-start": "Start an inter-agent discussion with Claude Code",
        "codex-discuss-respond": "Respond in an inter-agent discussion with Claude Code",
        "codex-discuss-continue": "Continue an inter-agent discussion with Claude Code",
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
        assert "arc01_001_codex_to_claude.md" in text
        assert "arc01_001_claude_to_codex.md" in text
        assert "arc01_010" in text
        assert "^arc\\d{2}_\\d{3}_(claude|codex)_to_(claude|codex)\\.md$" in text
        assert "message_index" in text
        assert "agent_turn" in text
        assert "status: continue" in text
        assert "continue | consensus | needs-user" in text
        assert "outcome.md" in text
        assert "temporary file" in text
        assert "heartbeat_codex.txt" in text
        assert "heartbeat_claude.txt" in text


def test_codex_discussion_skills_drop_unprefixed_message_compatibility() -> None:
    for skill_name in DISCUSSION_SKILLS:
        text = _read_skill(skill_name)

        assert not _contains_unprefixed_message_filename(text)
        assert "treated as `arc: 1`" not in text
        assert "treated as arc 1" not in text
        assert "???_*_to_*.md" not in text


def test_codex_discussion_skills_document_v2_refinements() -> None:
    for skill_name in DISCUSSION_SKILLS:
        text = _read_skill(skill_name)

        assert "frontmatter on line 1" in text
        assert "User-supplied context" in text
        assert "topic.md" in text
        assert "plans/" in text
        assert "revision:" in text
        assert ".tmp_*" in text
        assert "extension_requested_cap: 20" in text
        assert "extension_accepted: true" in text
        assert "message_cap: 20" in text
        assert "Handover proposal" in text
        assert "user_facing_agent" in text


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
        assert "Start-Sleep -Seconds 30" in text
        assert "second matching terminal" in text
        assert "write `outcome.md` immediately" in text
        assert "pre-flight checks must not mutate" in text
        assert "final segment contains whitespace" in text
        assert "host-neutral" in text


def test_codex_discussion_skills_document_v23_protocol() -> None:
    for skill_name in DISCUSSION_SKILLS:
        text = _read_skill(skill_name)

        assert "v2.3_spec_r001.md" in text
        assert "v2.2_spec_r002.md" not in text
        assert "arc01_001" in text
        assert "arc02_001" in text
        assert "arc: <int>" in text
        assert "ended_at_arc" in text
        assert "implementation_owner" in text
        assert "outcome_arc<NN>.md" in text
        assert "plans/<name>_r001.md" in text
        assert "Never overwrite" in text
        assert "parent folder" in text


def test_codex_discussion_start_documents_parent_and_slug() -> None:
    text = _read_skill("codex-discuss-start")

    assert "<parent> [--slug <slug>] [context...]" in text
    assert "YYYYMMDDTHHMMSSZ_<slug>" in text
    assert "Do not infer a slug" in text


def test_codex_discussion_respond_documents_parent_discovery() -> None:
    text = _read_skill("codex-discuss-respond")
    prompt = _read_openai_yaml("codex-discuss-respond")

    assert "accept either the exact discussion leaf or a parent folder" in text
    assert "scan immediate children" in text
    assert "Zero candidates: poll the parent" in text
    assert "Claude may still be creating the discussion leaf" in text
    assert "folder creation and first message" in text
    assert "Multiple candidates" in text

    assert "polls briefly" in prompt


def test_codex_discussion_continue_documents_no_args_role_aware_flow() -> None:
    text = _read_skill("codex-discuss-continue")
    prompt = _read_openai_yaml("codex-discuss-continue")

    assert "[--folder <path>] [context...]" in text
    assert "<folder> [context...]" not in text
    assert "No positional folder" in text
    assert "c:\\Dev\\StarshipBattles\\AgentCoordination\\Scratchpad\\Discussion\\" in text
    assert "most-recent leaf" in text
    assert "protocol-matching files" in text
    assert "heartbeat files, temp files, and plans do not contribute" in text
    assert "original starter" in text
    assert "warn-and-ignore" in text
    assert "The starter's forwarded context is canonical" in text

    assert "[--folder <path>] [context...]" in prompt
    assert "most recent ended" in prompt
