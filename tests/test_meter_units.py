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


def test_calculate_meter_with_negative_current_unit_raises_error():
    from custom_errors.custom_errors import DoNotNegativeUnitError

    with raises(DoNotNegativeUnitError) as e:
        MeterReadingUnit(current_unit=-5, previous_unit=10, unit_rate=19)
    assert str(e.value) == "หน่วยไม่ควรน้อยกว่าศูนย์"


def test_calculate_meter_with_negative_previous_unit_raises_error():
    from custom_errors.custom_errors import DoNotNegativeUnitError

    with raises(DoNotNegativeUnitError) as e:
        MeterReadingUnit(current_unit=10, previous_unit=-5, unit_rate=19)
    assert str(e.value) == "หน่วยไม่ควรน้อยกว่าศูนย์"


def test_calculate_meter_with_unit_vo_instances():
    from decimal import Decimal
    from domain.units_vo import Unit

    current = Unit(value=150)
    previous = Unit(value=100)
    calculator = MeterReadingUnit(
        current_unit=current, previous_unit=previous, unit_rate=8
    )
    total_unit, total_price = calculator.calculate()

    assert total_unit == 50
    assert total_price == Decimal("400")

