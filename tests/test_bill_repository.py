"""
ทดสอบ IBillRepository interface contract
"""

from domain.bill import Bill
from domain.billing_period import BillingPeriod
from infrastructure.repositories.bill_repository import IBillRepository


class ConcreteTestBillRepository(IBillRepository):
    """Concrete implementation สำหรับการทดสอบ interface contract"""

    def save(self, bill: Bill) -> Bill:
        """บันทึก Bill (stub)"""
        return bill

    def find_by_id(self, bill_id: str) -> Bill | None:
        """ค้นหา Bill จาก ID (stub)"""
        return None

    def find_all(self) -> list[Bill]:
        """ค้นหา Bills ทั้งหมด (stub)"""
        return []

    def delete_by_id(self, bill_id: str) -> None:
        """ลบ Bill จาก ID (stub)"""

    def exists(self, bill_id: str) -> bool:
        """ตรวจสอบการมีอยู่ (stub)"""
        return False

    def update(self, bill: Bill) -> Bill:
        """อัปเดต Bill (stub)"""
        return bill

    def find_by_room_and_period(
        self, room_id: str, period: BillingPeriod
    ) -> Bill | None:
        """ค้นหา Bill ของห้องในรอบบิลเฉพาะ (stub)"""
        return None

    def find_by_period(self, period: BillingPeriod) -> list[Bill]:
        """ค้นหา Bills ทั้งหมดในรอบบิลเฉพาะ (stub)"""
        return []


class TestIBillRepositoryInterface:
    """ทดสอบ IBillRepository interface"""

    def test_ibill_repository_is_abstract(self) -> None:
        """ตรวจสอบว่า IBillRepository เป็น abstract class"""
        assert hasattr(IBillRepository, "__abstractmethods__")

    def test_ibill_repository_has_bill_specific_methods(self) -> None:
        """ตรวจสอบว่า IBillRepository มี bill-specific methods"""
        abstract_methods = IBillRepository.__abstractmethods__
        assert "find_by_room_and_period" in abstract_methods
        assert "find_by_period" in abstract_methods

    def test_concrete_bill_repository_implements_all_methods(self) -> None:
        """ตรวจสอบว่า concrete implementation สามารถสร้าง instance ได้"""
        repo = ConcreteTestBillRepository()
        assert isinstance(repo, IBillRepository)

    def test_find_by_room_and_period_returns_bill_or_none(self) -> None:
        """ตรวจสอบว่า find_by_room_and_period คืน Bill | None"""
        repo = ConcreteTestBillRepository()
        result = repo.find_by_room_and_period("room-1", BillingPeriod(value="2026-10"))
        assert result is None or isinstance(result, Bill)

    def test_find_by_period_returns_list_of_bills(self) -> None:
        """ตรวจสอบว่า find_by_period คืน list[Bill]"""
        repo = ConcreteTestBillRepository()
        result = repo.find_by_period(BillingPeriod(value="2026-10"))
        assert isinstance(result, list)

    def test_ibill_repository_extends_irepository(self) -> None:
        """ตรวจสอบว่า IBillRepository extend IRepository"""
        from infrastructure.repository import IRepository

        # Check that IBillRepository is subclass of IRepository
        assert issubclass(IBillRepository, IRepository)

    def test_ibill_repository_has_all_irepository_methods(self) -> None:
        """ตรวจสอบว่า IBillRepository มี IRepository methods ทั้งหมด"""
        repo = ConcreteTestBillRepository()
        assert hasattr(repo, "save")
        assert hasattr(repo, "find_by_id")
        assert hasattr(repo, "find_all")
        assert hasattr(repo, "delete_by_id")
        assert hasattr(repo, "exists")
        assert hasattr(repo, "update")
