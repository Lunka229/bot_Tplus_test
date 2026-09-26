MARGIN_TOOL = {
    "type": "function",
    "function": {
        "name": "calculate_margin",
        "description": (
            "Рассчитывает прибыль, маржинальность "
            "и наценку товара по цене и себестоимости."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "price": {
                    "type": "number",
                    "description": (
                        "Цена продажи товара в рублях."
                    ),
                },
                "cost": {
                    "type": "number",
                    "description": (
                        "Себестоимость товара в рублях."
                    ),
                },
            },
            "required": [
                "price",
                "cost",
            ],
        },
    },
}