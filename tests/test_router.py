from app.services.router import route_request


def test_economics_route():
    assert (
        route_request(
            "Какая будет маржинальность товара?"
        )
        == "economics"
    )


def test_marketing_route():
    assert (
        route_request(
            "Как улучшить рекламу товара?"
        )
        == "marketing"
    )


def test_product_card_route():
    assert (
        route_request(
            "Помоги улучшить карточку товара"
        )
        == "product_card"
    )


def test_unknown_request_goes_to_support():
    assert (
        route_request(
            "У меня проблема с заказом"
        )
        == "support"
    )

def test_product_card_variations():
    assert (
        route_request(
            "Как улучшить карточку товара?"
        )
        == "product_card"
    )

    assert (
        route_request(
            "Помоги с характеристиками товара"
        )
        == "product_card"
    )

    assert (
        route_request(
            "Как сделать инфографику?"
        )
        == "product_card"
    )