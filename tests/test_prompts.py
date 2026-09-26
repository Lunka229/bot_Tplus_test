from app.services.prompts import PROMPTS


def test_all_routes_have_prompts():
    expected_routes = {
        "economics",
        "marketing",
        "product_card",
        "support",
    }

    assert expected_routes == set(PROMPTS.keys())


def test_economics_prompt_mentions_margin_tool():
    prompt = PROMPTS["economics"]

    assert "calculate_margin" in prompt
    assert "Не придумывай" in prompt


def test_prompts_are_not_identical():
    prompts = list(PROMPTS.values())

    assert len(set(prompts)) == len(prompts)