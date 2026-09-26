from app.tools.definitions import MARGIN_TOOL


def test_margin_tool_definition():
    function = MARGIN_TOOL["function"]

    assert function["name"] == "calculate_margin"

    assert "price" in (
        function["parameters"]["properties"]
    )

    assert "cost" in (
        function["parameters"]["properties"]
    )

    assert set(
        function["parameters"]["required"]
    ) == {"price", "cost"}