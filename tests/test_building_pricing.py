from decimal import Decimal

import pytest
from pydantic import ValidationError

from custom_errors.custom_errors import InvalidPricingError
from domain.building_pricing import BuildingPricing
from domain.units_vo import PricingAmount


def test_create_building_pricing_success():
    pricing = BuildingPricing(
        water_rate=19,
        electricity_rate=8,
        cable_price=60,
        parking_price=500,
    )
    assert pricing.water_rate == PricingAmount(value=19)
    assert isinstance(pricing.water_rate, PricingAmount)
    assert pricing.water_rate.value == Decimal(19)
    assert pricing.electricity_rate == PricingAmount(value=8)
    assert isinstance(pricing.electricity_rate, PricingAmount)
    assert pricing.electricity_rate.value == Decimal(8)
    assert pricing.cable_price == PricingAmount(value=60)
    assert isinstance(pricing.cable_price, PricingAmount)
    assert pricing.cable_price.value == Decimal(60)
    assert pricing.parking_price == PricingAmount(value=500)
    assert isinstance(pricing.parking_price, PricingAmount)
    assert pricing.parking_price.value == Decimal(500)


def test_create_building_pricing_with_defaults():
    pricing = BuildingPricing(water_rate=19, electricity_rate=8)
    assert pricing.water_rate == PricingAmount(value=19)
    assert pricing.electricity_rate == PricingAmount(value=8)
    assert pricing.cable_price == PricingAmount(value=0)
    assert pricing.parking_price == PricingAmount(value=0)


@pytest.mark.parametrize(
    "rates",
    [
        {"water_rate": -1, "electricity_rate": 8},
        {"water_rate": 19, "electricity_rate": -5},
        {"water_rate": 19, "electricity_rate": 8, "cable_price": -10},
        {"water_rate": 19, "electricity_rate": 8, "parking_price": -50},
    ],
)
def test_building_pricing_negative_rates_raise_error(rates: dict):
    with pytest.raises((InvalidPricingError, ValidationError)):
        BuildingPricing(**rates)


def test_building_pricing_is_frozen():
    pricing = BuildingPricing(water_rate=19, electricity_rate=8)
    with pytest.raises(ValidationError):
        pricing.water_rate = 25
