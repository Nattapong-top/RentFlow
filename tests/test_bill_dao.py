"""
ทดสอบ BillDAO implementation
"""

import pytest

from custom_errors.custom_errors import RepositoryOptimisticLockError
from domain.bill import Bill
from domain.billing_period import BillingPeriod
from infrastructure.repositories.bill_dao import BillDAO


class TestBillDAOSave:
    """ทดสอบ BillDAO.save() method"""

    def test_save_new_bill(self) -> None:
        """ตรวจสอบว่าสามารถบันทึก Bill ใหม่ได้"""
        dao = BillDAO()
        bill = Bill(
            id="bill-1",
            room_id="room-1",
            billing_period=BillingPeriod(value="2026-10"),
            tenant_id="tenant-1",
        )

        result = dao.save(bill)

        assert result.id == "bill-1"
        assert result.version == 1

    def test_save_increments_version(self) -> None:
        """ตรวจสอบว่า save() เพิ่ม version"""
        dao = BillDAO()
        bill = Bill(
            id="bill-1",
            room_id="room-1",
            billing_period=BillingPeriod(value="2026-10"),
            tenant_id="tenant-1",
            version=None,
        )

        result = dao.save(bill)

        assert result.version == 1

    def test_save_update_existing_bill(self) -> None:
        """ตรวจสอบว่าสามารถอัปเดต Bill ที่มีอยู่ได้"""
        dao = BillDAO()
        bill = Bill(
            id="bill-1",
            room_id="room-1",
            billing_period=BillingPeriod(value="2026-10"),
            tenant_id="tenant-1",
        )

        # Save first time
        result1 = dao.save(bill)
        assert result1.version == 1

        # Update with same bill but with version 1
        bill.version = 1
        result2 = dao.save(bill)

        assert result2.version == 2


class TestBillDAOCheckVersion:
    """ทดสอบ BillDAO.check_version() method"""

    def test_check_version_new_bill_no_error(self) -> None:
        """ตรวจสอบว่า new bill ไม่ raise error"""
        dao = BillDAO()
        bill = Bill(
            id="bill-1",
            room_id="room-1",
            billing_period=BillingPeriod(value="2026-10"),
            tenant_id="tenant-1",
        )

        # Should not raise
        dao.check_version(bill)

    def test_check_version_mismatch_raises_error(self) -> None:
        """ตรวจสอบว่า version mismatch raise RepositoryOptimisticLockError"""
        dao = BillDAO()

        # Save bill
        bill1 = Bill(
            id="bill-1",
            room_id="room-1",
            billing_period=BillingPeriod(value="2026-10"),
            tenant_id="tenant-1",
        )
        dao.save(bill1)

        # Try to update with wrong version
        bill2 = Bill(
            id="bill-1",
            room_id="room-1",
            billing_period=BillingPeriod(value="2026-10"),
            tenant_id="tenant-1",
            version=0,  # ผิด, ควรเป็น 1
        )

        with pytest.raises(RepositoryOptimisticLockError):
            dao.check_version(bill2)


class TestBillDAOFindById:
    """ทดสอบ BillDAO.find_by_id() method"""

    def test_find_by_id_existing(self) -> None:
        """ตรวจสอบว่าสามารถหา Bill ที่มีอยู่"""
        dao = BillDAO()
        bill = Bill(
            id="bill-1",
            room_id="room-1",
            billing_period=BillingPeriod(value="2026-10"),
            tenant_id="tenant-1",
        )
        dao.save(bill)

        result = dao.find_by_id("bill-1")

        assert result is not None
        assert result.id == "bill-1"

    def test_find_by_id_not_found(self) -> None:
        """ตรวจสอบว่าคืน None เมื่อไม่พบ Bill"""
        dao = BillDAO()

        result = dao.find_by_id("non-existent")

        assert result is None


class TestBillDAOFindByRoomAndPeriod:
    """ทดสอบ BillDAO.find_by_room_and_period() method"""

    def test_find_by_room_and_period_found(self) -> None:
        """ตรวจสอบว่าสามารถหา Bill ตามห้องและรอบบิล"""
        dao = BillDAO()
        period = BillingPeriod(value="2026-10")
        bill = Bill(
            id="bill-1",
            room_id="room-1",
            billing_period=period,
            tenant_id="tenant-1",
        )
        dao.save(bill)

        result = dao.find_by_room_and_period("room-1", period)

        assert result is not None
        assert result.id == "bill-1"

    def test_find_by_room_and_period_not_found(self) -> None:
        """ตรวจสอบว่าคืน None เมื่อไม่พบ Bill"""
        dao = BillDAO()
        period = BillingPeriod(value="2026-10")

        result = dao.find_by_room_and_period("room-1", period)

        assert result is None

    def test_find_by_room_and_period_different_period(self) -> None:
        """ตรวจสอบว่าแยก Bill ตามรอบบิล"""
        dao = BillDAO()
        bill1 = Bill(
            id="bill-1",
            room_id="room-1",
            billing_period=BillingPeriod(value="2026-10"),
            tenant_id="tenant-1",
        )
        dao.save(bill1)

        result = dao.find_by_room_and_period("room-1", BillingPeriod(value="2026-11"))

        assert result is None


class TestBillDAOFindByPeriod:
    """ทดสอบ BillDAO.find_by_period() method"""

    def test_find_by_period_multiple_bills(self) -> None:
        """ตรวจสอบว่าหา Bills หลายอันในรอบบิลเดียว"""
        dao = BillDAO()
        period = BillingPeriod(value="2026-10")

        bill1 = Bill(
            id="bill-1",
            room_id="room-1",
            billing_period=period,
            tenant_id="tenant-1",
        )
        bill2 = Bill(
            id="bill-2",
            room_id="room-2",
            billing_period=period,
            tenant_id="tenant-2",
        )

        dao.save(bill1)
        dao.save(bill2)

        result = dao.find_by_period(period)

        assert len(result) == 2
        assert any(b.id == "bill-1" for b in result)
        assert any(b.id == "bill-2" for b in result)

    def test_find_by_period_empty_list(self) -> None:
        """ตรวจสอบว่าคืน empty list เมื่อไม่พบ"""
        dao = BillDAO()
        period = BillingPeriod(value="2026-10")

        result = dao.find_by_period(period)

        assert result == []


class TestBillDAOFindAll:
    """ทดสอบ BillDAO.find_all() method"""

    def test_find_all_returns_all_bills(self) -> None:
        """ตรวจสอบว่า find_all() คืน Bills ทั้งหมด"""
        dao = BillDAO()

        bill1 = Bill(
            id="bill-1",
            room_id="room-1",
            billing_period=BillingPeriod(value="2026-10"),
            tenant_id="tenant-1",
        )
        bill2 = Bill(
            id="bill-2",
            room_id="room-2",
            billing_period=BillingPeriod(value="2026-11"),
            tenant_id="tenant-2",
        )

        dao.save(bill1)
        dao.save(bill2)

        result = dao.find_all()

        assert len(result) == 2


class TestBillDAOExists:
    """ทดสอบ BillDAO.exists() method"""

    def test_exists_returns_true(self) -> None:
        """ตรวจสอบว่า exists() คืน True เมื่อมี Bill"""
        dao = BillDAO()
        bill = Bill(
            id="bill-1",
            room_id="room-1",
            billing_period=BillingPeriod(value="2026-10"),
            tenant_id="tenant-1",
        )
        dao.save(bill)

        result = dao.exists("bill-1")

        assert result is True

    def test_exists_returns_false(self) -> None:
        """ตรวจสอบว่า exists() คืน False เมื่อไม่มี Bill"""
        dao = BillDAO()

        result = dao.exists("non-existent")

        assert result is False


class TestBillDAODeleteById:
    """ทดสอบ BillDAO.delete_by_id() method"""

    def test_delete_by_id_removes_bill(self) -> None:
        """ตรวจสอบว่า delete_by_id() ลบ Bill"""
        dao = BillDAO()
        bill = Bill(
            id="bill-1",
            room_id="room-1",
            billing_period=BillingPeriod(value="2026-10"),
            tenant_id="tenant-1",
        )
        dao.save(bill)

        dao.delete_by_id("bill-1")

        assert dao.find_by_id("bill-1") is None


class TestBillDAOUpdate:
    """ทดสอบ BillDAO.update() method"""

    def test_update_bill(self) -> None:
        """ตรวจสอบว่า update() สามารถอัปเดต Bill"""
        dao = BillDAO()
        bill = Bill(
            id="bill-1",
            room_id="room-1",
            billing_period=BillingPeriod(value="2026-10"),
            tenant_id="tenant-1",
        )
        dao.save(bill)

        # Update
        bill.version = 1
        result2 = dao.update(bill)

        assert result2.version == 2


class TestBillDAOIntegration:
    """ทดสอบ BillDAO integration scenarios"""

    def test_concurrent_update_detection(self) -> None:
        """ตรวจสอบการตรวจจับการแก้ไขพร้อมกัน"""
        dao = BillDAO()

        bill1 = Bill(
            id="bill-1",
            room_id="room-1",
            billing_period=BillingPeriod(value="2026-10"),
            tenant_id="tenant-1",
        )
        dao.save(bill1)

        # Simulate concurrent update - user 1 tries to update with old version
        bill2 = Bill(
            id="bill-1",
            room_id="room-1",
            billing_period=BillingPeriod(value="2026-10"),
            tenant_id="tenant-1",
            version=1,  # correct version at this point
        )
        dao.save(bill2)  # Now version is 2

        # User 2 tries to update with old version 1
        bill3 = Bill(
            id="bill-1",
            room_id="room-1",
            billing_period=BillingPeriod(value="2026-10"),
            tenant_id="tenant-1",
            version=1,  # outdated!
        )

        with pytest.raises(RepositoryOptimisticLockError):
            dao.save(bill3)

    def test_version_persists_after_save(self) -> None:
        """ตรวจสอบว่า version ยังคงตั้งไว้หลังจาก save"""
        dao = BillDAO()

        bill = Bill(
            id="bill-1",
            room_id="room-1",
            billing_period=BillingPeriod(value="2026-10"),
            tenant_id="tenant-1",
        )
        result = dao.save(bill)

        fetched = dao.find_by_id("bill-1")

        assert fetched is not None
        assert fetched.version == result.version == 1
