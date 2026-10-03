"""
BillDAO - Concrete in-memory implementation of IBillRepository
รองรับ optimistic locking via version field
"""

from custom_errors.custom_errors import RepositoryOptimisticLockError
from domain.bill import Bill
from domain.billing_period import BillingPeriod
from infrastructure.repositories.bill_repository import IBillRepository


class BillDAO(IBillRepository):
    """
    BillDAO - DAO สำหรับ Bill aggregate.

    ใช้ in-memory storage (dict) สำหรับ v1
    รองรับ optimistic locking โดยการเช็ค version

    Attributes:
        _storage: dict[bill_id, Bill] - เก็บ Bill objects
        _version: dict[bill_id, version] - เก็บ current version ของแต่ละ Bill
    """

    def __init__(self) -> None:
        """เริ่มต้น BillDAO ด้วย storage ว่าง."""
        self._storage: dict[str, Bill] = {}
        self._version: dict[str, int] = {}

    def check_version(self, bill: Bill) -> None:
        """
        ตรวจสอบว่า Bill.version ตรงกับเวอร์ชันที่เก็บไว้.

        Args:
            bill: Bill entity ที่ต้องเช็ค

        Raises:
            RepositoryOptimisticLockError: ถ้า version ไม่ตรงกัน
        """
        # Bill ใหม่ → ไม่ต้องเช็ค version
        if bill.id not in self._storage:
            return

        # Bill ที่มีอยู่ → เช็คว่า version ตรงกันไหม
        stored_version = self._version[bill.id]
        if bill.version != stored_version:
            raise RepositoryOptimisticLockError(
                bill_id=bill.id,
                expected_version=bill.version,
                current_version=stored_version,
            )

    def save(self, bill: Bill) -> Bill:
        """
        บันทึก Bill พร้อม optimistic locking

        Args:
            bill: Bill entity ที่ต้องบันทึก

        Returns:
            Bill ที่บันทึกแล้ว (พร้อม version ที่อัปเดต)

        Raises:
            RepositoryOptimisticLockError: ถ้า version conflict
        """
        # เช็ค version ก่อน
        self.check_version(bill)

        # เพิ่ม version
        new_version = (bill.version or 0) + 1
        bill.version = new_version

        # เก็บ Bill
        self._storage[bill.id] = bill
        self._version[bill.id] = new_version

        return bill

    def find_by_id(self, bill_id: str) -> Bill | None:
        """
        ค้นหา Bill จาก ID

        Args:
            bill_id: Bill ID

        Returns:
            Bill | None
        """
        return self._storage.get(bill_id)

    def find_by_room_and_period(
        self, room_id: str, period: BillingPeriod
    ) -> Bill | None:
        """
        ค้นหา Bill ของห้องในรอบบิลเฉพาะ.

        Args:
            room_id: Room ID
            period: Billing period

        Returns:
            Bill | None (one or none, unique constraint)
        """
        for bill in self._storage.values():
            if bill.room_id == room_id and bill.billing_period.value == period.value:
                return bill
        return None

    def find_by_period(self, period: BillingPeriod) -> list[Bill]:
        """
        ค้นหา Bills ทั้งหมดในรอบบิลเฉพาะ.

        Args:
            period: Billing period

        Returns:
            list[Bill] (may be empty)
        """
        period_value = period.value
        return [
            bill
            for bill in self._storage.values()
            if bill.billing_period.value == period_value
        ]

    def find_all(self) -> list[Bill]:
        """
        ค้นหา Bills ทั้งหมด

        Returns:
            list[Bill]
        """
        return list(self._storage.values())

    def delete_by_id(self, bill_id: str) -> None:
        """
        ลบ Bill จาก ID

        Args:
            bill_id: Bill ID
        """
        if bill_id in self._storage:
            del self._storage[bill_id]
            del self._version[bill_id]

    def exists(self, bill_id: str) -> bool:
        """
        ตรวจสอบว่า Bill มีอยู่หรือไม่

        Args:
            bill_id: Bill ID

        Returns:
            bool
        """
        return bill_id in self._storage

    def update(self, bill: Bill) -> Bill:
        """
        อัปเดต Bill (เหมือน save แต่ semantically for updates)

        Args:
            bill: Bill entity ที่ต้องอัปเดต

        Returns:
            Bill ที่อัปเดตแล้ว
        """
        return self.save(bill)
