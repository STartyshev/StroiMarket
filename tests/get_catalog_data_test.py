import pytest

from main import market_app
from fastapi.testclient import TestClient

client = TestClient(market_app)

@pytest.mark.asyncio
async def test_get_catalog_data():
    response = client.get("/catalog/catalog_data")
    assert response.status_code == 200
    assert response.json() == {
        "catalog_data":
            [
                {
                    "name": "Алюминиевые профиля",
                    "product_subtypes": [
                        {"name": "Тавр и Полоса алюминиевые"},
                        {"name": "Труба алюминиевая круглая"},
                        {"name": "Труба алюминиевая профильная Бокс"},
                        {"name": "Уголок алюминиевый"},
                        {"name": "Швеллер алюминиевый"}
                    ]
                },
                {
                    "name": "Металлопрокат",
                    "product_subtypes": [
                        {"name": "Листовой прокат"},
                        {"name": "Проволока и арматура"},
                        {"name": "Сетка"},
                        {"name": "Столбы, профильные трубы"},
                        {"name": "Швеллеры и уголки"}
                    ]
                },
                {
                    "name": "Пиломатериалы",
                    "product_subtypes": [
                        {"name": "Брус"},
                        {"name": "Доски строительные"},
                        {"name": "Строительная рейка и брусок"},
                        {"name": "Фанера"}
                    ]
                }
            ]
    }
