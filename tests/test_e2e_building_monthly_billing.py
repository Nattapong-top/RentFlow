"""
Task 7: E2E tests - Real building monthly billing workflow
จำลอง real-world building billing process
"""

import pytest

from application.create_monthly_bill import CreateMonthlyBill
from domain.billing_period import BillingPeriod
from domain.building_pricing import BuildingPricing
from domain.occupant_type import OccupantType
from domain.room import Room
from domain.tenant import Tenant
from domain.units_vo import PricingAmount, Unit
from infrastructure.repositories.bill_dao import BillDAO


@pytest.fixture
def dao() -> BillDAO:
    """Fresh DAO instance."""
    return BillDAO()


@pytest.fixture
def app_service() -> CreateMonthlyBill:
    """Application service."""
    return CreateMonthlyBill()


@pytest.fixture
def period_2026_10() -> BillingPeriod:
    """2026-10 billing period."""
    return BillingPeriod(value="2026-10")


@pytest.fixture
def building_pricing() -> BuildingPricing:
    """Standard building pricing."""
    return BuildingPricing(
        water_rate=PricingAmount(value=8),
        electricity_rate=PricingAmount(value=7),
        cable_price=PricingAmount(value=60),
        parking_price=PricingAmount(value=500),
    )


@pytest.fixture
def sample_tenants() -> dict[str, Tenant]:
    """Sample tenants."""
    return {
        "tenant-1": Tenant(id="tenant-1", name="สมชาย"),
        "tenant-2": Tenant(id="tenant-2", name="ศรีสกุล"),
    }


@pytest.fixture
def sample_rooms(sample_tenants: dict[str, Tenant]) -> dict[str, Room]:
    """Building with 5 rooms: 3 tenant, 2 owner."""
    return {
        "room-101": Room(
            id="room-101",
            room_number="101",
            rent_rate=PricingAmount(value=3000),
            occupant_type=OccupantType.TENANT,
            tenant_id="tenant-1",
            cable_exempt=False,
            has_parking=True,
            car_count=Unit(value=1),
        ),
        "room-102": Room(
            id="room-102",
            room_number="102",
            rent_rate=PricingAmount(value=3500),
            occupant_type=OccupantType.TENANT,
            tenant_id="tenant-2",
            cable_exempt=True,
            has_parking=False,
        ),
        "room-103": Room(
            id="room-103",
            room_number="103",
            rent_rate=PricingAmount(value=2500),
            occupant_type=OccupantType.TENANT,
            tenant_id=None,  # ว่างไม่มีผู้เช่า
            cable_exempt=False,
            has_parking=False,
        ),
        "room-201": Room(
            id="room-201",
            room_number="201",
            rent_rate=PricingAmount(value=0),
            occupant_type=OccupantType.OWNER,
            cable_exempt=False,
            has_parking=False,
        ),
        "room-202": Room(
            id="room-202",
            room_number="202",
            rent_rate=PricingAmount(value=0),
            occupant_type=OccupantType.OWNER,
            cable_exempt=False,
            has_parking=False,
        ),
    }


class TestE2EBuildingMonthlyBillingWorkflow:
    """E2E: Full building monthly billing process"""

    def test_create_bills_for_all_rooms_in_building(
        self,
        app_service: CreateMonthlyBill,
        dao: BillDAO,
        period_2026_10: BillingPeriod,
        building_pricing: BuildingPricing,
        sample_rooms: dict[str, Room],
    ) -> None:
        """ตรวจสอบว่าสร้าง bills สำหรับทุกห้องในอาคาร"""
        meter_readings = {
            "room-101": {"water": (450, 350), "elec": (250, 200)},
            "room-102": {"water": (280, 250), "elec": (180, 150)},
            "room-103": {"water": (350, 300), "elec": (200, 180)},
            "room-201": {"water": (500, 400), "elec": (350, 320)},
            "room-202": {"water": (400, 350), "elec": (300, 270)},
        }

        # Create and save bills
        for room_id, readings in meter_readings.items():
            room = sample_rooms[room_id]
            bill = app_service.execute(
                room=room,
                billing_period=period_2026_10,
                pricing=building_pricing,
                water_meter=readings["water"],
                electricity_meter=readings["elec"],
            )
            dao.save(bill)

        # Verify all saved
        all_bills = dao.find_by_period(period_2026_10)
        assert len(all_bills) == 5

    def test_mixed_tenant_owner_billing_rules(
        self,
        app_service: CreateMonthlyBill,
        period_2026_10: BillingPeriod,
        building_pricing: BuildingPricing,
        sample_rooms: dict[str, Room],
    ) -> None:
        """ตรวจสอบว่า TENANT vs OWNER charges ถูกต้อง"""
        # Tenant room
        tenant_bill = app_service.execute(
            room=sample_rooms["room-101"],
            billing_period=period_2026_10,
            pricing=building_pricing,
            water_meter=(450, 350),
            electricity_meter=(250, 200),
        )

        # Owner room
        owner_bill = app_service.execute(
            room=sample_rooms["room-201"],
            billing_period=period_2026_10,
            pricing=building_pricing,
            water_meter=(500, 400),
            electricity_meter=(350, 320),
        )

        # Tenant should have rent + utilities + cable + parking
        tenant_items = {item.name for item in tenant_bill.items}
        assert "ค่าเช่าห้อง" in tenant_items
        assert "ค่าน้ำ" in tenant_items
        assert "ค่าไฟ" in tenant_items
        assert "ค่าเคเบิล" in tenant_items
        assert "ค่าที่จอดรถ" in tenant_items

        # Owner should have only utilities (no rent, cable, parking)
        owner_items = {item.name for item in owner_bill.items}
        assert "ค่าเช่าห้อง" not in owner_items
        assert "ค่าน้ำ" in owner_items
        assert "ค่าไฟ" in owner_items
        assert "ค่าเคเบิล" not in owner_items
        assert "ค่าที่จอดรถ" not in owner_items

    def test_cable_exempt_tenant_no_cable_charge(
        self,
        app_service: CreateMonthlyBill,
        period_2026_10: BillingPeriod,
        building_pricing: BuildingPricing,
        sample_rooms: dict[str, Room],
    ) -> None:
        """ตรวจสอบ cable_exempt room ไม่คิดค่าเคเบิล"""
        bill = app_service.execute(
            room=sample_rooms["room-102"],  # cable_exempt=True
            billing_period=period_2026_10,
            pricing=building_pricing,
            water_meter=(280, 250),
            electricity_meter=(180, 150),
        )

        item_names = {item.name for item in bill.items}
        assert "ค่าเคเบิล" not in item_names

    def test_tenant_with_parking_includes_parking_charge(
        self,
        app_service: CreateMonthlyBill,
        period_2026_10: BillingPeriod,
        building_pricing: BuildingPricing,
        sample_rooms: dict[str, Room],
    ) -> None:
        """ตรวจสอบ has_parking room คิดค่าจอดรถ"""
        bill = app_service.execute(
            room=sample_rooms["room-101"],  # has_parking=True
            billing_period=period_2026_10,
            pricing=building_pricing,
            water_meter=(450, 350),
            electricity_meter=(250, 200),
        )

        item_names = {item.name for item in bill.items}
        assert "ค่าที่จอดรถ" in item_names

    def test_owner_no_rent_no_cable_no_parking(
        self,
        app_service: CreateMonthlyBill,
        period_2026_10: BillingPeriod,
        building_pricing: BuildingPricing,
        sample_rooms: dict[str, Room],
    ) -> None:
        """ตรวจสอบ OWNER ไม่มี rent, cable, parking charge"""
        bill = app_service.execute(
            room=sample_rooms["room-201"],
            billing_period=period_2026_10,
            pricing=building_pricing,
            water_meter=(500, 400),
            electricity_meter=(350, 320),
        )

        item_names = {item.name for item in bill.items}
        assert "ค่าเช่าห้อง" not in item_names
        assert "ค่าเคเบิล" not in item_names
        assert "ค่าที่จอดรถ" not in item_names

    def test_all_bills_persisted_and_queryable(
        self,
        app_service: CreateMonthlyBill,
        dao: BillDAO,
        period_2026_10: BillingPeriod,
        building_pricing: BuildingPricing,
        sample_rooms: dict[str, Room],
    ) -> None:
        """ตรวจสอบว่า bills บันทึกและค้นหาได้"""
        # Create and save multiple bills
        for room_id in ["room-101", "room-102", "room-201"]:
            room = sample_rooms[room_id]
            bill = app_service.execute(
                room=room,
                billing_period=period_2026_10,
                pricing=building_pricing,
                water_meter=(400, 300),
                electricity_meter=(200, 150),
            )
            dao.save(bill)

        # Query and verify
        bills = dao.find_by_period(period_2026_10)
        assert len(bills) == 3

        for bill in bills:
            fetched = dao.find_by_id(bill.id)
            assert fetched is not None
            assert fetched.billing_period.value == "2026-10"

    def test_version_tracking_across_operations(
        self,
        app_service: CreateMonthlyBill,
        dao: BillDAO,
        period_2026_10: BillingPeriod,
        building_pricing: BuildingPricing,
        sample_rooms: dict[str, Room],
    ) -> None:
        """ตรวจสอบ version tracking ตลอด workflow"""
        room = sample_rooms["room-101"]

        # Create bill
        bill = app_service.execute(
            room=room,
            billing_period=period_2026_10,
            pricing=building_pricing,
            water_meter=(450, 350),
            electricity_meter=(250, 200),
        )

        # First save
        saved1 = dao.save(bill)
        assert saved1.version == 1

        # Recalculate
        bill.clear_items()
        bill.version = 1
        recalc = app_service.execute(
            room=room,
            billing_period=period_2026_10,
            pricing=building_pricing,
            water_meter=(460, 360),  # Different readings
            electricity_meter=(260, 210),
        )
        recalc.id = bill.id
        recalc.version = 1

        # Second save
        saved2 = dao.save(recalc)
        assert saved2.version == 2

        # Verify fetched version
        fetched = dao.find_by_id(bill.id)
        assert fetched is not None
        assert fetched.version == 2
