from app.core.request_context import generate_request_id


def test_request_id_format():
    request_id = generate_request_id()

    assert len(request_id) == 12
    assert request_id.isalnum()