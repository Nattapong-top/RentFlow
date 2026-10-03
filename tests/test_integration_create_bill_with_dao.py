"""
Integration tests: CreateMonthlyBill + BillDAO
ทดสอบ Application layer ทำงานกับ Infrastructure layer
"""

import pytest

from application.create_monthly_bill import CreateMonthlyBill
from custom_errors.custom_errors import (
    DecreasingUnitError,
    MissingRequiredDataError,
    RepositoryOptimisticLockError,
)
from domain.billing_period import BillingPeriod
from domain.building_pricing import BuildingPricing
from domain.occupant_type import OccupantType
from domain.room import Room
from domain.units_vo import PricingAmount
from infrastructure.repositories.bill_dao import BillDAO


@pytest.fixture
def dao() -> BillDAO:
    """Fresh BillDAO instance."""
    return BillDAO()


@pytest.fixture
def application_service() -> CreateMonthlyBill:
    """CreateMonthlyBill application service."""
    return CreateMonthlyBill()


@pytest.fixture
def period_2026_10() -> BillingPeriod:
    """2026-10 billing period."""
    return BillingPeriod(value="2026-10")


@pytest.fixture
def building_pricing() -> BuildingPricing:
    """Sample building pricing."""
    return BuildingPricing(
        water_rate=PricingAmount(value=8),
        electricity_rate=PricingAmount(value=7),
        cable_price=PricingAmount(value=60),
        parking_price=PricingAmount(value=500),
    )


@pytest.fixture
def room_tenant_101() -> Room:
    """Sample tenant room."""
    return Room(
        id="room-101",
        room_number="101",
        rent_rate=PricingAmount(value=3000),
        occupant_type=OccupantType.TENANT,
        cable_exempt=False,
        has_parking=True,
    )


@pytest.fixture
def room_owner_102() -> Room:
    """Sample owner room."""
    return Room(
        id="room-102",
        room_number="102",
        rent_rate=PricingAmount(value=0),
        occupant_type=OccupantType.OWNER,
        cable_exempt=False,
        has_parking=False,
    )


class TestCreateBillAndSaveToDAO:
    """ทดสอบ Happy path: Create bill → Save to DAO"""

    def test_create_bill_for_tenant_saves_to_dao(
        self,
        application_service: CreateMonthlyBill,
        dao: BillDAO,
        room_tenant_101: Room,
        period_2026_10: BillingPeriod,
        building_pricing: BuildingPricing,
    ) -> None:
        """ตรวจสอบว่าสร้าง Bill สำหรับ TENANT และบันทึกใน DAO"""
        # Create bill
        bill = application_service.execute(
            room=room_tenant_101,
            billing_period=period_2026_10,
            pricing=building_pricing,
            water_meter=(450, 350),
            electricity_meter=(250, 200),
        )

        # Save to DAO
        saved_bill = dao.save(bill)

        # Verify
        assert saved_bill.id == bill.id
        assert saved_bill.version == 1
        assert dao.exists(bill.id) is True

    def test_create_bill_for_owner_saves_to_dao(
        self,
        application_service: CreateMonthlyBill,
        dao: BillDAO,
        room_owner_102: Room,
        period_2026_10: BillingPeriod,
        building_pricing: BuildingPricing,
    ) -> None:
        """ตรวจสอบว่าสร้าง Bill สำหรับ OWNER และบันทึกใน DAO"""
        # Create bill
        bill = application_service.execute(
            room=room_owner_102,
            billing_period=period_2026_10,
            pricing=building_pricing,
            water_meter=(150, 100),
            electricity_meter=(300, 280),
        )

        # Save to DAO
        saved_bill = dao.save(bill)

        # Verify
        assert saved_bill.id == bill.id
        assert saved_bill.version == 1
        assert dao.exists(bill.id) is True


class TestBillVersionTracking:
    """ทดสอบ Version tracking end-to-end"""

    def test_bill_version_incremented_after_save(
        self,
        application_service: CreateMonthlyBill,
        dao: BillDAO,
        room_tenant_101: Room,
        period_2026_10: BillingPeriod,
        building_pricing: BuildingPricing,
    ) -> None:
        """ตรวจสอบว่า version auto-increment"""
        bill = application_service.execute(
            room=room_tenant_101,
            billing_period=period_2026_10,
            pricing=building_pricing,
            water_meter=(450, 350),
            electricity_meter=(250, 200),
        )

        # First save
        result1 = dao.save(bill)
        assert result1.version == 1

        # Second save (update)
        bill.version = 1
        result2 = dao.save(bill)
        assert result2.version == 2


class TestBillRecalculation:
    """ทดสอบ Recalculation scenarios"""

    def test_recalculate_existing_bill_updates_version(
        self,
        application_service: CreateMonthlyBill,
        dao: BillDAO,
        room_tenant_101: Room,
        period_2026_10: BillingPeriod,
        building_pricing: BuildingPricing,
    ) -> None:
        """ตรวจสอบ recalculate เพิ่ม version"""
        # Create and save initial bill
        bill = application_service.execute(
            room=room_tenant_101,
            billing_period=period_2026_10,
            pricing=building_pricing,
            water_meter=(450, 350),
            electricity_meter=(250, 200),
        )
        saved = dao.save(bill)
        version_1 = saved.version

        # Recalculate (clear items + add new ones)
        bill_id = saved.id
        bill.clear_items()
        bill.version = version_1

        # Create again with same inputs
        recalc_bill = application_service.execute(
            room=room_tenant_101,
            billing_period=period_2026_10,
            pricing=building_pricing,
            water_meter=(450, 350),
            electricity_meter=(250, 200),
        )
        recalc_bill.id = bill_id
        recalc_bill.version = version_1

        # Save recalculated
        result = dao.save(recalc_bill)

        assert result.version == version_1 + 1

    def test_recalculate_detects_concurrent_modification(
        self,
        application_service: CreateMonthlyBill,
        dao: BillDAO,
        room_tenant_101: Room,
        period_2026_10: BillingPeriod,
        building_pricing: BuildingPricing,
    ) -> None:
        """ตรวจสอบว่า recalculate detect concurrent modification"""
        # Create and save initial bill
        bill = application_service.execute(
            room=room_tenant_101,
            billing_period=period_2026_10,
            pricing=building_pricing,
            water_meter=(450, 350),
            electricity_meter=(250, 200),
        )
        saved = dao.save(bill)

        # Simulate concurrent modification
        # User 1 updates
        bill.version = 1
        dao.save(bill)  # Now version is 2

        # User 2 tries to update with old version
        bill2 = application_service.execute(
            room=room_tenant_101,
            billing_period=period_2026_10,
            pricing=building_pricing,
            water_meter=(450, 350),
            electricity_meter=(250, 200),
        )
        bill2.id = saved.id
        bill2.version = 1  # Outdated!

        with pytest.raises(RepositoryOptimisticLockError):
            dao.save(bill2)


class TestBillQuerying:
    """ทดสอบ Query from DAO"""

    def test_find_bill_by_room_and_period(
        self,
        application_service: CreateMonthlyBill,
        dao: BillDAO,
        room_tenant_101: Room,
        period_2026_10: BillingPeriod,
        building_pricing: BuildingPricing,
    ) -> None:
        """ตรวจสอบว่า find_by_room_and_period ทำงาน"""
        # Create and save
        bill = application_service.execute(
            room=room_tenant_101,
            billing_period=period_2026_10,
            pricing=building_pricing,
            water_meter=(450, 350),
            electricity_meter=(250, 200),
        )
        dao.save(bill)

        # Query
        found = dao.find_by_room_and_period("room-101", period_2026_10)

        assert found is not None
        assert found.id == bill.id
        assert found.room_id == "room-101"

    def test_find_bills_by_period_returns_all(
        self,
        application_service: CreateMonthlyBill,
        dao: BillDAO,
        room_tenant_101: Room,
        room_owner_102: Room,
        period_2026_10: BillingPeriod,
        building_pricing: BuildingPricing,
    ) -> None:
        """ตรวจสอบว่า find_by_period คืน Bills ทั้งหมด"""
        # Create and save 2 bills
        bill1 = application_service.execute(
            room=room_tenant_101,
            billing_period=period_2026_10,
            pricing=building_pricing,
            water_meter=(450, 350),
            electricity_meter=(250, 200),
        )
        bill2 = application_service.execute(
            room=room_owner_102,
            billing_period=period_2026_10,
            pricing=building_pricing,
            water_meter=(150, 100),
            electricity_meter=(300, 280),
        )

        dao.save(bill1)
        dao.save(bill2)

        # Query
        results = dao.find_by_period(period_2026_10)

        assert len(results) == 2
        assert any(b.id == bill1.id for b in results)
        assert any(b.id == bill2.id for b in results)


class TestErrorScenarios:
    """ทดสอบ Error handling"""

    def test_missing_meter_data_raises_error(
        self,
        application_service: CreateMonthlyBill,
        room_tenant_101: Room,
        period_2026_10: BillingPeriod,
        building_pricing: BuildingPricing,
    ) -> None:
        """ตรวจสอบว่า missing meter data raise error"""
        with pytest.raises(MissingRequiredDataError):
            application_service.execute(
                room=room_tenant_101,
                billing_period=period_2026_10,
                pricing=building_pricing,
                water_meter=None,  # Missing!
                electricity_meter=(250, 200),
            )

    def test_meter_decreasing_raises_error(
        self,
        application_service: CreateMonthlyBill,
        room_tenant_101: Room,
        period_2026_10: BillingPeriod,
        building_pricing: BuildingPricing,
    ) -> None:
        """ตรวจสอบว่า meter decreasing raise error"""
        with pytest.raises(DecreasingUnitError):
            application_service.execute(
                room=room_tenant_101,
                billing_period=period_2026_10,
                pricing=building_pricing,
                water_meter=(250, 350),  # Decreasing!
                electricity_meter=(250, 200),
            )

    def test_concurrent_update_raises_error(
        self,
        application_service: CreateMonthlyBill,
        dao: BillDAO,
        room_tenant_101: Room,
        period_2026_10: BillingPeriod,
        building_pricing: BuildingPricing,
    ) -> None:
        """ตรวจสอบว่า concurrent update raise error"""
        # Create and save
        bill = application_service.execute(
            room=room_tenant_101,
            billing_period=period_2026_10,
            pricing=building_pricing,
            water_meter=(450, 350),
            electricity_meter=(250, 200),
        )
        saved = dao.save(bill)

        # Try to update with wrong version
        bill.id = saved.id
        bill.version = 0  # Wrong!

        with pytest.raises(RepositoryOptimisticLockError):
            dao.save(bill)
