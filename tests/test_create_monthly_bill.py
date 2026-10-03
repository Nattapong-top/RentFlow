import pytest

from application.create_monthly_bill import CreateMonthlyBill
from custom_errors.custom_errors import DecreasingUnitError, MissingRequiredDataError
from domain.bill import Bill
from domain.billing_period import BillingPeriod
from domain.building_pricing import BuildingPricing
from domain.occupant_type import OccupantType
from domain.room import Room


@pytest.fixture
def standard_pricing():
    return BuildingPricing(
        water_rate=19,
        electricity_rate=8,
        cable_price=60,
        parking_price=500,
    )


@pytest.fixture
def tenant_room():
    return Room(
        id="R101",
        room_number="101",
        rent_rate=2800,
        occupant_type=OccupantType.TENANT,
        tenant_id="T001",
        cable_exempt=False,
        has_parking=True,
    )


@pytest.fixture
def owner_room():
    return Room(
        id="R102",
        room_number="102",
        rent_rate=0,
        occupant_type=OccupantType.OWNER,
        cable_exempt=False,
        has_parking=True,
    )


def test_create_monthly_bill_for_tenant_all_items(standard_pricing, tenant_room):
    service = CreateMonthlyBill()
    period = BillingPeriod(value="2026-09")

    bill = service.execute(
        room=tenant_room,
        billing_period=period,
        pricing=standard_pricing,
        water_meter=(125, 99),  # 26 units * 19 = 494
        electricity_meter=(450, 350),  # 100 units * 8 = 800
    )

    # 2800 (Rent) + 494 (Water) + 800 (Elec) + 60 (Cable) + 500 (Parking) = 4654
    assert bill.total == 4654
    assert len(bill.items) == 5
    assert bill.room_id == "R101"
    assert bill.billing_period.value == "2026-09"
    assert bill.tenant_id == "T001"


def test_create_monthly_bill_for_tenant_exemptions(standard_pricing):
    room = Room(
        id="R103",
        room_number="103",
        rent_rate=3000,
        occupant_type=OccupantType.TENANT,
        tenant_id="T002",
        cable_exempt=True,
        has_parking=False,
    )
    service = CreateMonthlyBill()

    bill = service.execute(
        room=room,
        billing_period="2026-09",
        pricing=standard_pricing,
        water_meter=(110, 100),  # 10 units * 19 = 190
        electricity_meter=(250, 200),  # 50 units * 8 = 400
    )

    # 3000 (Rent) + 190 (Water) + 400 (Elec) = 3590
    assert bill.total == 3590
    assert len(bill.items) == 3


def test_create_monthly_bill_for_owner_only_utilities(standard_pricing, owner_room):
    service = CreateMonthlyBill()

    bill = service.execute(
        room=owner_room,
        billing_period="2026-09",
        pricing=standard_pricing,
        water_meter=(125, 99),  # 26 units * 19 = 494
        electricity_meter=(450, 350),  # 100 units * 8 = 800
    )

    # Owner คิดเฉพาะ Water (494) + Electricity (800) = 1294 (ไม่คิด Rent, Cable, Parking)
    assert bill.total == 1294
    assert len(bill.items) == 2
    item_names = [item.name for item in bill.items]
    assert "ค่าน้ำ" in item_names
    assert "ค่าไฟ" in item_names
    assert "ค่าเช่าห้อง" not in item_names
    assert "ค่าเคเบิล" not in item_names
    assert "ค่าที่จอดรถ" not in item_names


def test_create_monthly_bill_missing_meter_raises_error(standard_pricing, tenant_room):
    service = CreateMonthlyBill()

    with pytest.raises(MissingRequiredDataError) as exc_info:
        service.execute(
            room=tenant_room,
            billing_period="2026-09",
            pricing=standard_pricing,
            water_meter=None,
            electricity_meter=(450, 350),
        )
    assert str(exc_info.value) == "ข้อมูลมิเตอร์น้ำไม่ครบถ้วน กรุณาตรวจสอบข้อมูลต้นทาง"


def test_create_monthly_bill_decreasing_meter_raises_error(
    standard_pricing, tenant_room
):
    service = CreateMonthlyBill()

    with pytest.raises(DecreasingUnitError) as exc_info:
        service.execute(
            room=tenant_room,
            billing_period="2026-09",
            pricing=standard_pricing,
            water_meter=(50, 99),  # 50 < 99
            electricity_meter=(450, 350),
        )
    assert str(exc_info.value) == "หน่วยปัจจุบันไม่ควรน้อยกว่าหน่วยก่อนหน้า"


def test_recalculate_existing_bill_preserves_bill_id(standard_pricing, tenant_room):
    service = CreateMonthlyBill()
    period = BillingPeriod(value="2026-09")

    # บิลเดิม ID: B-ORIGINAL-001
    existing_bill = Bill(
        id="B-ORIGINAL-001",
        room_id=tenant_room.id,
        billing_period=period,
        tenant_id=tenant_room.tenant_id,
    )

    recalculated_bill = service.execute(
        room=tenant_room,
        billing_period=period,
        pricing=standard_pricing,
        water_meter=(125, 99),
        electricity_meter=(450, 350),
        existing_bill=existing_bill,
    )

    # BR-17: Recalculate ใช้ Bill ID เดิม ไม่สร้าง ID ใหม่
    assert recalculated_bill.id == "B-ORIGINAL-001"
    assert recalculated_bill.total == 4654
