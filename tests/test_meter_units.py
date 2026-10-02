from pytest import raises

from custom_errors.custom_errors import DecreasingUnitError
from domain.meter_unit import MeterReadingUnit


def test_calculate_water_meter_success():
    # เตรียม
    current_unit = 125
    previous_unit = 99
    water_rate = 19

    # ทำ
    calculator = MeterReadingUnit(current_unit, previous_unit, water_rate)
    total_unit, total_price = calculator.calculate()

    from decimal import Decimal

    # ตรวจ
    assert total_unit == 26
    assert total_price == Decimal("494")
    assert isinstance(total_price, Decimal)


def test_calculate_water_meter_failure():
    # เตรียม
    current_unit = 5
    previous_unit = 99
    water_rate = 19

    with raises(DecreasingUnitError) as e:
        MeterReadingUnit(current_unit, previous_unit, water_rate).calculate()
    assert str(e.value) == "หน่วยปัจจุบันไม่ควรน้อยกว่าหน่วยก่อนหน้า"

