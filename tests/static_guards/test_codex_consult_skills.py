from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_ROOT = REPO_ROOT / ".agents" / "skills"


def _read_skill(skill_name: str) -> str:
    return (SKILL_ROOT / skill_name / "SKILL.md").read_text(encoding="utf-8")


def _read_openai_yaml(skill_name: str) -> str:
    return (SKILL_ROOT / skill_name / "agents" / "openai.yaml").read_text(
        encoding="utf-8"
    )


def test_codex_consult_skills_exist_with_codex_frontmatter_and_ui_metadata() -> None:
    for skill_name in (
        "codex-starship-consult",
        "codex-starship-consult-respond",
    ):
        skill_dir = SKILL_ROOT / skill_name
        skill_md = skill_dir / "SKILL.md"
        openai_yaml = skill_dir / "agents" / "openai.yaml"

        assert skill_md.exists(), skill_md
        assert openai_yaml.exists(), openai_yaml

        text = _read_skill(skill_name)
        metadata = _read_openai_yaml(skill_name)

        assert f"name: {skill_name}" in text
        assert "description:" in text
        assert "argument-hint" not in text
        assert f"${skill_name}" in metadata
        assert "display_name:" in metadata
        assert "short_description:" in metadata


def test_codex_starship_consult_documents_harmonized_initiator_contract() -> None:
    text = _read_skill("codex-starship-consult")

    assert "AgentCoordination/protocols/partner_cli.md" in text
    assert "AgentCoordination/protocols/consult_prompt_block.md" in text
    assert "Tools/agent_coordination/partner_invoke.py" in text
    assert "AgentCoordination/Scratchpad/Consult/" in text
    assert "consult/v1" in text
    assert "planning" in text
    assert "mid-project-review" in text
    assert "pre-final-check" in text
    assert "deep-dive" in text
    assert "gemini" in text.lower()
    assert "--dry-run" in text
    assert "--allow-tests" in text
    assert "pairwise" in text.lower()
    assert "not a three-way" in text.lower()
    assert "No implementation delegation" in text
    assert "complete error artifact" in text
    assert "Starship Battles consult constraints:" not in text


def test_codex_starship_consult_documents_gemini_initiator_contract() -> None:
    text = _read_skill("codex-starship-consult")
    metadata = _read_openai_yaml("codex-starship-consult")

    assert "--with <claude|opencode|gemini|both>" in text
    assert "Gemini" in metadata
    assert "embed the full `request.md` text" in text
    assert "Do not substitute another topic" in text
    assert "from: gemini" in text
    assert "to: codex" in text
    assert "no preamble or postamble" in text.lower()
    assert "expected_from=partner" in text
    assert "expected_to=\"codex\"" in text


def test_codex_starship_consult_respond_documents_read_only_response_contract() -> None:
    text = _read_skill("codex-starship-consult-respond")

    assert "--request <path>" in text
    assert "consult/v1" in text
    assert "complete: true" in text
    assert "exit_status: ok" in text
    assert "## Findings" in text
    assert "## Risks" in text
    assert "## Open questions" in text
    assert "Do not edit production code" in text
    assert "Do not edit tracked docs" in text
    assert "Run tests only when" in text
    assert "allow_tests: true" in text
    assert "docs/_ignore/" in text
    assert "response.md" in text
    assert "AgentCoordination/protocols/consult_prompt_block.md" in text
    assert "must write `response.md`" in text
    assert "same-directory `.tmp_*`" in text
    assert "not an acceptable fallback" in text
    assert "what context or evidence is missing" in text
    assert "or make the final assistant message exactly this artifact" not in text
