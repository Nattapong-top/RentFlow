import pytest

from custom_errors.custom_errors import DecreasingUnitError
from domain.billing_calculator import BillingCalculator
from domain.building_pricing import BuildingPricing
from domain.room import Room


def test_calculate_water_bill_item():
    calculator = BillingCalculator()
    item = calculator.create_water_item(current_unit=125, previous_unit=99, rate=19)

    assert item.name == "ค่าน้ำ"
    assert item.amount == 494
    assert item.description == "125 - 99 = 26 หน่วย @ 19 บาท"


def test_calculate_electricity_bill_item():
    calculator = BillingCalculator()
    item = calculator.create_electricity_item(
        current_unit=450, previous_unit=350, rate=8
    )

    assert item.name == "ค่าไฟ"
    assert item.amount == 800
    assert item.description == "450 - 350 = 100 หน่วย @ 8 บาท"


def test_calculate_water_decreasing_meter_raises_error():
    calculator = BillingCalculator()
    with pytest.raises(DecreasingUnitError) as exc_info:
        calculator.create_water_item(current_unit=50, previous_unit=99, rate=19)
    assert str(exc_info.value) == "หน่วยปัจจุบันไม่ควรน้อยกว่าหน่วยก่อนหน้า"


def test_calculate_electricity_decreasing_meter_raises_error():
    calculator = BillingCalculator()
    with pytest.raises(DecreasingUnitError) as exc_info:
        calculator.create_electricity_item(current_unit=300, previous_unit=350, rate=8)
    assert str(exc_info.value) == "หน่วยปัจจุบันไม่ควรน้อยกว่าหน่วยก่อนหน้า"


def test_calculate_rent_bill_item():
    calculator = BillingCalculator()
    room = Room(id="R001", room_number="101", rent_rate=2800)
    item = calculator.create_rent_item(room)

    assert item.name == "ค่าเช่าห้อง"
    assert item.amount == 2800
    assert item.description == "ค่าเช่าห้องประจำเดือน"


def test_calculate_cable_bill_item():
    calculator = BillingCalculator()
    pricing = BuildingPricing(water_rate=19, electricity_rate=8, cable_price=60)
    item = calculator.create_cable_item(pricing)

    assert item.name == "ค่าเคเบิล"
    assert item.amount == 60


def test_calculate_parking_bill_item():
    calculator = BillingCalculator()
    pricing = BuildingPricing(water_rate=19, electricity_rate=8, parking_price=500)
    item = calculator.create_parking_item(pricing, motorcycle_count=1, car_count=1)

    assert item.name == "ค่าที่จอดรถ"
    assert item.amount == 500


@pytest.mark.parametrize(
    ("motorcycle_count", "car_count", "expected_amount"),
    [
        (0, 0, 0),
        (1, 0, 0),
        (2, 0, 100),
        (3, 0, 200),
        (0, 1, 500),
        (1, 1, 500),
        (2, 1, 600),
        (3, 1, 700),
    ],
)
def test_calculate_parking_bill_by_vehicle_counts(
    motorcycle_count, car_count, expected_amount
):
    calculator = BillingCalculator()
    pricing = BuildingPricing(water_rate=19, electricity_rate=8, parking_price=500)

    item = calculator.create_parking_item(
        pricing,
        motorcycle_count=motorcycle_count,
        car_count=car_count,
    )

    assert item.amount == expected_amount
