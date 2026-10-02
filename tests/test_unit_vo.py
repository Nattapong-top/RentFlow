from pytest import raises

from custom_errors.custom_errors import DoNotNegativeUnitError
from domain.units_vo import Unit


def test_nuit_vo_should_create_unit_success():

    unit = Unit(value=1)
    assert unit.value == 1

def test_nuit_vo_should_error_when_unit_negative():
    with raises(DoNotNegativeUnitError) as err:
        Unit(value=-1)

    assert str(err.value) == f"หน่วยไม่ควรน้อยกว่าศูนย์"