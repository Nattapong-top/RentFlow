from domain.billing_rules import BillingRules
from domain.occupant_type import OccupantType
from domain.room import Room
from domain.units_vo import Unit


def test_billing_rules_for_tenant_with_full_services():
    room = Room(
        id="R001",
        room_number="101",
        rent_rate=2800,
        occupant_type=OccupantType.TENANT,
        tenant_id="T001",
        cable_exempt=False,
        has_parking=True,
        car_count=Unit(value=1),
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


def test_billing_rules_for_tenant_with_cable_disabled():
    room = Room(
        id="R004",
        room_number="104",
        rent_rate=3000,
        occupant_type=OccupantType.TENANT,
        cable_enabled=False,
    )
    rules = BillingRules()

    assert rules.should_charge_cable(room) is False
    assert rules.determine_applicable_items(room) == [
        "rent",
        "water",
        "electricity",
    ]


def test_billing_rules_for_tenant_parking_uses_vehicle_counts():
    room = Room(
        id="R005",
        room_number="105",
        rent_rate=3000,
        occupant_type=OccupantType.TENANT,
        has_parking=False,
        motorcycle_count=Unit(value=1),
        car_count=Unit(value=1),
    )
    rules = BillingRules()

    assert rules.should_charge_parking(room) is True


def test_billing_rules_for_one_free_motorcycle_has_no_parking_item():
    room = Room(
        id="R006",
        room_number="106",
        rent_rate=3000,
        occupant_type=OccupantType.TENANT,
        has_parking=True,
        motorcycle_count=Unit(value=1),
        car_count=Unit(value=0),
    )
    rules = BillingRules()

    assert rules.should_charge_parking(room) is False


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
