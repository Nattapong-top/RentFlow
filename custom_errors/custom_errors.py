class DomainErrors(Exception):
    pass


class DecreasingUnitError(DomainErrors):
    pass


class DoNotNegativeUnitError(DomainErrors):
    pass


class InvalidBillingPeriodError(DomainErrors):
    pass


class InvalidPricingError(DomainErrors):
    pass


class InvalidTenantError(DomainErrors):
    pass


class InvalidRoomError(DomainErrors):
    pass


class InvalidRentRateError(DomainErrors):
    pass


class InvalidBillItemError(DomainErrors):
    pass


class DuplicateBillItemError(DomainErrors):
    pass


class MissingRequiredDataError(DomainErrors):
    pass


# ========================================
# ข้อผิดพลาดของชั้น Repository (Infrastructure)
# ========================================


class RepositoryError(Exception):
    """ข้อผิดพลาดฐานของชั้น Repository."""


class RepositoryEntityNotFoundError(RepositoryError):
    """ยกขึ้นเมื่อไม่พบ entity ในฐานข้อมูล."""

    def __init__(self, entity_id: str, table: str) -> None:
        """เริ่มต้นข้อผิดพลาดด้วย ID entity และชื่อตาราง.

        Args:
            entity_id: ID ของ entity ที่ไม่พบ.
            table: ชื่อตารางฐานข้อมูลที่ entity ควรมีอยู่.
        """
        self.entity_id = entity_id
        self.table = table
        super().__init__(f"ไม่พบ entity {entity_id} ในตาราง {table}")


class RepositoryDatabaseError(RepositoryError):
    """ยกขึ้นเมื่อการดำเนินการฐานข้อมูลล้มเหลว."""

    def __init__(self, message: str) -> None:
        """เริ่มต้นข้อผิดพลาดด้วยข้อความข้อผิดพลาดฐานข้อมูล.

        Args:
            message: คำอธิบายข้อผิดพลาดฐานข้อมูล.
        """
        super().__init__(message)


class RepositoryOptimisticLockError(RepositoryError):
    """ยกขึ้นเมื่อตรวจจับการแก้ไขพร้อมกัน (version mismatch)."""

    def __init__(
        self, bill_id: str, expected_version: int, current_version: int | None
    ) -> None:
        """เริ่มต้นข้อผิดพลาดด้วยรายละเอียดความขัดแย้งเวอร์ชัน.

        Args:
            bill_id: ID ของ Bill ที่มีความขัดแย้งเวอร์ชัน.
            expected_version: เวอร์ชันที่เราคาดว่าจะพบ.
            current_version: เวอร์ชันจริงที่พบในฐานข้อมูล.
        """
        self.bill_id = bill_id
        self.expected_version = expected_version
        self.current_version = current_version
        super().__init__(
            f"ตรวจจับการแก้ไขพร้อมกันของ Bill {bill_id}. "
            f"คาดว่าเวอร์ชัน {expected_version} แต่พบ {current_version}"
        )
