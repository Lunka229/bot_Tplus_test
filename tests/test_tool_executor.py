import json

from app.tools.executor import execute_tool


def test_execute_margin_tool():
    result = execute_tool(
        tool_name="calculate_margin",
        arguments={
            "price": 1500,
            "cost": 600,
        },
    )

    data = json.loads(result)

    assert data["price"] == 1500
    assert data["cost"] == 600
    assert data["profit"] == 900
    assert data["margin_percent"] == 60
    assert data["markup_percent"] == 150

def test_unknown_tool():
    try:
        execute_tool(
            tool_name="unknown_tool",
            arguments={},
        )
    except ValueError as exc:
        assert "Unknown tool" in str(exc)
    else:
        raise AssertionError(
            "Expected ValueError"
        )