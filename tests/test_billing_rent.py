import pytest

from domain.billing_rent import Billing


def test_create_billing():
    # เตรียม
    rent_rate = 2800
    cable_tv = 60
    water_price = 190
    electricity_price = 1080

    # ทำ
    billing = Billing(rent_rate, cable_tv, water_price, electricity_price)
    grand_total = billing.calculate()

    # ตรวจ
    assert grand_total == 4130


def test_create_billing_fail():
    rent_rate = -2800
    cable_tv = 60
    water_price = 190
    electricity_price = 1080

    with pytest.raises(ValueError) as e:
        Billing(rent_rate, cable_tv, water_price, electricity_price)
    assert str(e.value) == 'หน่วยไม่ควรน้อยกว่าศูนย์'