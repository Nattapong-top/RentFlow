from domain.billing_rules import BillingRules
from domain.occupant_type import OccupantType
from domain.room import Room


def test_billing_rules_for_tenant_with_full_services():
    room = Room(
        id="R001",
        room_number="101",
        rent_rate=2800,
        occupant_type=OccupantType.TENANT,
        tenant_id="T001",
        cable_exempt=False,
        has_parking=True,
    )
    rules = BillingRules()

    assert rules.should_charge_rent(room) is True
    assert rules.should_charge_water(room) is True
    assert rules.should_charge_electricity(room) is True
    assert rules.should_charge_cable(room) is True
    assert rules.should_charge_parking(room) is True

    items = rules.determine_applicable_items(room)
    assert items == ["rent", "water", "electricity", "cable", "parking"]


def test_billing_rules_for_tenant_cable_exempt_and_no_parking():
    room = Room(
        id="R002",
        room_number="102",
        rent_rate=3000,
        occupant_type=OccupantType.TENANT,
        tenant_id="T002",
        cable_exempt=True,
        has_parking=False,
    )
    rules = BillingRules()

    assert rules.should_charge_rent(room) is True
    assert rules.should_charge_water(room) is True
    assert rules.should_charge_electricity(room) is True
    assert rules.should_charge_cable(room) is False
    assert rules.should_charge_parking(room) is False

    items = rules.determine_applicable_items(room)
    assert items == ["rent", "water", "electricity"]


def test_billing_rules_for_owner_occupant():
    room = Room(
        id="R003",
        room_number="103",
        rent_rate=0,
        occupant_type=OccupantType.OWNER,
        cable_exempt=False,
        has_parking=True,
    )
    rules = BillingRules()

    # Owner คิดแค่น้ำกับไฟ ไม่คิด Rent, Cable, Parking แม้ว่า cable_exempt=False หรือ has_parking=True
    assert rules.should_charge_rent(room) is False
    assert rules.should_charge_water(room) is True
    assert rules.should_charge_electricity(room) is True
    assert rules.should_charge_cable(room) is False
    assert rules.should_charge_parking(room) is False

    items = rules.determine_applicable_items(room)
    assert items == ["water", "electricity"]
