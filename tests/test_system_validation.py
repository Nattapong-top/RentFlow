"""
Task 8: System validation tests
ตรวจสอบ system integrity, performance, constraints, edge cases
"""

import pytest

from application.create_monthly_bill import CreateMonthlyBill
from custom_errors.custom_errors import (
    DecreasingUnitError,
    InvalidBillingPeriodError,
    InvalidPricingError,
)
from domain.billing_period import BillingPeriod
from domain.building_pricing import BuildingPricing
from domain.occupant_type import OccupantType
from domain.room import Room
from domain.units_vo import PricingAmount
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
def building_pricing() -> BuildingPricing:
    """Building pricing."""
    return BuildingPricing(
        water_rate=PricingAmount(value=8),
        electricity_rate=PricingAmount(value=7),
        cable_price=PricingAmount(value=60),
        parking_price=PricingAmount(value=500),
    )


class TestSystemConstraints:
    """ตรวจสอบ system constraints"""

    def test_meter_never_decreases(
        self,
        app_service: CreateMonthlyBill,
        building_pricing: BuildingPricing,
    ) -> None:
        """ตรวจสอบว่า meter decreasing ถูก reject"""
        room = Room(
            id="room-1",
            room_number="101",
            rent_rate=PricingAmount(value=3000),
            occupant_type=OccupantType.TENANT,
        )

        # Try decreasing meter
        with pytest.raises(DecreasingUnitError):
            app_service.execute(
                room=room,
                billing_period=BillingPeriod(value="2026-10"),
                pricing=building_pricing,
                water_meter=(300, 400),  # Current < Previous!
                electricity_meter=(200, 150),
            )

    def test_prices_never_negative(self) -> None:
        """ตรวจสอบว่า negative pricing ถูก reject"""
        with pytest.raises(InvalidPricingError):
            BuildingPricing(
                water_rate=PricingAmount(value=-8),  # Negative!
                electricity_rate=PricingAmount(value=7),
            )

    def test_bills_always_have_positive_total(
        self,
        app_service: CreateMonthlyBill,
        building_pricing: BuildingPricing,
    ) -> None:
        """ตรวจสอบว่า bill total > 0"""
        room = Room(
            id="room-1",
            room_number="101",
            rent_rate=PricingAmount(value=3000),
            occupant_type=OccupantType.TENANT,
        )

        bill = app_service.execute(
            room=room,
            billing_period=BillingPeriod(value="2026-10"),
            pricing=building_pricing,
            water_meter=(450, 350),
            electricity_meter=(250, 200),
        )

        assert bill.total > 0


class TestBoundaryConditions:
    """ทดสอบ edge cases และ boundary conditions"""

    def test_empty_building_no_bills(self, dao: BillDAO) -> None:
        """ตรวจสอบ empty DAO"""
        period = BillingPeriod(value="2026-10")
        bills = dao.find_by_period(period)

        assert bills == []

    def test_single_room_building(
        self,
        app_service: CreateMonthlyBill,
        dao: BillDAO,
        building_pricing: BuildingPricing,
    ) -> None:
        """ตรวจสอบ single room building"""
        room = Room(
            id="room-1",
            room_number="101",
            rent_rate=PricingAmount(value=3000),
            occupant_type=OccupantType.TENANT,
        )

        bill = app_service.execute(
            room=room,
            billing_period=BillingPeriod(value="2026-10"),
            pricing=building_pricing,
            water_meter=(450, 350),
            electricity_meter=(250, 200),
        )

        dao.save(bill)
        period = BillingPeriod(value="2026-10")
        bills = dao.find_by_period(period)

        assert len(bills) == 1

    def test_max_rooms_building(
        self,
        app_service: CreateMonthlyBill,
        dao: BillDAO,
        building_pricing: BuildingPricing,
    ) -> None:
        """ตรวจสอบ large building (20 rooms)"""
        period = BillingPeriod(value="2026-10")

        for i in range(20):
            room = Room(
                id=f"room-{i}",
                room_number=f"{i+1:03d}",
                rent_rate=PricingAmount(value=3000),
                occupant_type=OccupantType.TENANT,
            )

            bill = app_service.execute(
                room=room,
                billing_period=period,
                pricing=building_pricing,
                water_meter=(450, 350),
                electricity_meter=(250, 200),
            )

            dao.save(bill)

        bills = dao.find_by_period(period)
        assert len(bills) == 20

    def test_zero_meter_units(
        self,
        app_service: CreateMonthlyBill,
        building_pricing: BuildingPricing,
    ) -> None:
        """ตรวจสอบ zero meter usage (current == previous)"""
        room = Room(
            id="room-1",
            room_number="101",
            rent_rate=PricingAmount(value=3000),
            occupant_type=OccupantType.TENANT,
        )

        bill = app_service.execute(
            room=room,
            billing_period=BillingPeriod(value="2026-10"),
            pricing=building_pricing,
            water_meter=(350, 350),  # No usage
            electricity_meter=(200, 200),  # No usage
        )

        # Should still create bill (with 0 water/elec charges)
        assert bill.items is not None

    def test_multiple_periods_bills_isolated(
        self,
        app_service: CreateMonthlyBill,
        dao: BillDAO,
        building_pricing: BuildingPricing,
    ) -> None:
        """ตรวจสอบว่า different periods เป็น isolated"""
        room = Room(
            id="room-1",
            room_number="101",
            rent_rate=PricingAmount(value=3000),
            occupant_type=OccupantType.TENANT,
        )

        # Create bills for different periods
        bill1 = app_service.execute(
            room=room,
            billing_period=BillingPeriod(value="2026-09"),
            pricing=building_pricing,
            water_meter=(450, 350),
            electricity_meter=(250, 200),
        )

        bill2 = app_service.execute(
            room=room,
            billing_period=BillingPeriod(value="2026-10"),
            pricing=building_pricing,
            water_meter=(460, 360),
            electricity_meter=(260, 210),
        )

        dao.save(bill1)
        dao.save(bill2)

        # Query by period
        bills_09 = dao.find_by_period(BillingPeriod(value="2026-09"))
        bills_10 = dao.find_by_period(BillingPeriod(value="2026-10"))

        assert len(bills_09) == 1
        assert len(bills_10) == 1
        assert bills_09[0].id != bills_10[0].id


class TestDataIntegrity:
    """ทดสอบ data integrity"""

    def test_no_data_loss_on_recalculation(
        self,
        app_service: CreateMonthlyBill,
        dao: BillDAO,
        building_pricing: BuildingPricing,
    ) -> None:
        """ตรวจสอบว่า recalculate ไม่ lose data"""
        room = Room(
            id="room-1",
            room_number="101",
            rent_rate=PricingAmount(value=3000),
            occupant_type=OccupantType.TENANT,
        )

        # Create and save
        bill = app_service.execute(
            room=room,
            billing_period=BillingPeriod(value="2026-10"),
            pricing=building_pricing,
            water_meter=(450, 350),
            electricity_meter=(250, 200),
        )
        saved = dao.save(bill)
        bill_id = saved.id
        original_total = saved.total

        # Recalculate with same data
        bill.clear_items()
        bill.version = 1
        recalc = app_service.execute(
            room=room,
            billing_period=BillingPeriod(value="2026-10"),
            pricing=building_pricing,
            water_meter=(450, 350),
            electricity_meter=(250, 200),
        )
        recalc.id = bill_id
        recalc.version = 1
        recalc_saved = dao.save(recalc)

        # Verify total is same
        assert recalc_saved.total == original_total

    def test_version_never_goes_backward(
        self,
        app_service: CreateMonthlyBill,
        dao: BillDAO,
        building_pricing: BuildingPricing,
    ) -> None:
        """ตรวจสอบว่า version ไม่เพิ่มขึ้น"""
        room = Room(
            id="room-1",
            room_number="101",
            rent_rate=PricingAmount(value=3000),
            occupant_type=OccupantType.TENANT,
        )

        bill = app_service.execute(
            room=room,
            billing_period=BillingPeriod(value="2026-10"),
            pricing=building_pricing,
            water_meter=(450, 350),
            electricity_meter=(250, 200),
        )

        v1 = dao.save(bill).version
        bill.version = v1
        v2 = dao.save(bill).version
        bill.version = v2
        v3 = dao.save(bill).version

        assert v1 == 1
        assert v2 == 2
        assert v3 == 3
        assert v1 < v2 < v3


class TestDateValidation:
    """ทดสอบ date/period validation"""

    def test_valid_billing_periods(self) -> None:
        """ตรวจสอบ valid period formats"""
        valid_periods = ["2026-01", "2026-10", "2026-12", "2000-01", "9999-12"]

        for period_str in valid_periods:
            period = BillingPeriod(value=period_str)
            assert period.value == period_str

    def test_invalid_billing_period_formats(self) -> None:
        """ตรวจสอบ invalid period formats ถูก reject"""
        invalid_periods = ["2026-13", "2026-00", "26-10", "2026/10"]

        for period_str in invalid_periods:
            with pytest.raises(InvalidBillingPeriodError):
                BillingPeriod(value=period_str)
