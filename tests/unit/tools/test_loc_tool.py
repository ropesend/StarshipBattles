from Tools.loc import loc


def test_loc_tool_token_counter_is_available() -> None:
    assert loc._count_tokens("Starship Battles") > 0
