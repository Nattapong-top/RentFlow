from decimal import Decimal

import pytest
from pydantic import ValidationError

from custom_errors.custom_errors import InvalidPricingError
from domain.building_pricing import BuildingPricing


def test_create_building_pricing_success():
    pricing = BuildingPricing(
        water_rate=19,
        electricity_rate=8,
        cable_price=60,
        parking_price=500,
    )
    assert pricing.water_rate == Decimal(19)
    assert isinstance(pricing.water_rate, Decimal)
    assert pricing.electricity_rate == Decimal(8)
    assert isinstance(pricing.electricity_rate, Decimal)
    assert pricing.cable_price == Decimal(60)
    assert isinstance(pricing.cable_price, Decimal)
    assert pricing.parking_price == Decimal(500)
    assert isinstance(pricing.parking_price, Decimal)


def test_create_building_pricing_with_defaults():
    pricing = BuildingPricing(water_rate=19, electricity_rate=8)
    assert pricing.water_rate == 19
    assert pricing.electricity_rate == 8
    assert pricing.cable_price == 0
    assert pricing.parking_price == 0


@pytest.mark.parametrize(
    "rates, error_message",
    [
        (
            {"water_rate": -1, "electricity_rate": 8},
            "ค่าน้ำต่อหน่วยต้องไม่น้อยกว่าศูนย์",
        ),
        (
            {"water_rate": 19, "electricity_rate": -5},
            "ค่าไฟต่อหน่วยต้องไม่น้อยกว่าศูนย์",
        ),
        (
            {"water_rate": 19, "electricity_rate": 8, "cable_price": -10},
            "ค่าเคเบิลต้องไม่น้อยกว่าศูนย์",
        ),
        (
            {"water_rate": 19, "electricity_rate": 8, "parking_price": -50},
            "ค่าจอดรถต้องไม่น้อยกว่าศูนย์",
        ),
    ],
)
def test_building_pricing_negative_rates_raise_error(rates: dict, error_message: str):
    with pytest.raises(InvalidPricingError) as exc_info:
        BuildingPricing(**rates)
    assert str(exc_info.value) == error_message


def test_building_pricing_is_frozen():
    pricing = BuildingPricing(water_rate=19, electricity_rate=8)
    with pytest.raises(ValidationError):
        pricing.water_rate = 25
