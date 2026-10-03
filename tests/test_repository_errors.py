"""เทสสำหรับข้อผิดพลาด Repository Layer."""

import pytest

from custom_errors.custom_errors import (
    RepositoryDatabaseError,
    RepositoryEntityNotFoundError,
    RepositoryError,
    RepositoryOptimisticLockError,
)


class TestRepositoryError:
    """เทสสำหรับ RepositoryError base class."""

    def test_repository_error_can_be_raised(self) -> None:
        """ตรวจสอบว่า RepositoryError สามารถยกขึ้นได้."""
        with pytest.raises(RepositoryError):
            raise RepositoryError("ข้อผิดพลาด Repository")

    def test_repository_error_inherits_from_exception(self) -> None:
        """ตรวจสอบว่า RepositoryError extends Exception."""
        error = RepositoryError("ข้อผิดพลาด")
        assert isinstance(error, Exception)

    def test_repository_error_message(self) -> None:
        """ตรวจสอบข้อความข้อผิดพลาด."""
        message = "ข้อผิดพลาดทดสอบ"
        error = RepositoryError(message)
        assert str(error) == message


class TestRepositoryEntityNotFoundError:
    """เทสสำหรับ RepositoryEntityNotFoundError."""

    def test_entity_not_found_error_with_entity_id_and_table(self) -> None:
        """ตรวจสอบ error message ที่มี entity_id และ table."""
        entity_id = "bill-123"
        table = "bills"
        error = RepositoryEntityNotFoundError(entity_id, table)

        assert error.entity_id == entity_id
        assert error.table == table
        assert str(error) == f"ไม่พบ entity {entity_id} ในตาราง {table}"

    def test_entity_not_found_error_inherits_from_repository_error(self) -> None:
        """ตรวจสอบ inheritance hierarchy."""
        error = RepositoryEntityNotFoundError("id-1", "table-1")
        assert isinstance(error, RepositoryError)
        assert isinstance(error, Exception)

    def test_entity_not_found_error_can_be_caught_as_repository_error(self) -> None:
        """ตรวจสอบว่า error สามารถจับได้ว่าเป็น RepositoryError."""
        with pytest.raises(RepositoryError):
            raise RepositoryEntityNotFoundError("bill-456", "bills")


class TestRepositoryDatabaseError:
    """เทสสำหรับ RepositoryDatabaseError."""

    def test_database_error_with_message(self) -> None:
        """ตรวจสอบ error message."""
        message = "การเชื่อมต่อฐานข้อมูลล้มเหลว"
        error = RepositoryDatabaseError(message)
        assert str(error) == message

    def test_database_error_inherits_from_repository_error(self) -> None:
        """ตรวจสอบ inheritance hierarchy."""
        error = RepositoryDatabaseError("ข้อผิดพลาดใด ๆ")
        assert isinstance(error, RepositoryError)
        assert isinstance(error, Exception)

    def test_database_error_can_be_caught_as_repository_error(self) -> None:
        """ตรวจสอบว่า error สามารถจับได้ว่าเป็น RepositoryError."""
        with pytest.raises(RepositoryError):
            raise RepositoryDatabaseError("ข้อผิดพลาดฐานข้อมูล")


class TestRepositoryOptimisticLockError:
    """เทสสำหรับ RepositoryOptimisticLockError."""

    def test_optimistic_lock_error_with_version_conflict(self) -> None:
        """ตรวจสอบ error message ที่มี version conflict details."""
        bill_id = "bill-789"
        expected_version = 5
        current_version = 6
        error = RepositoryOptimisticLockError(
            bill_id, expected_version, current_version
        )

        assert error.bill_id == bill_id
        assert error.expected_version == expected_version
        assert error.current_version == current_version
        assert (
            "ตรวจจับการแก้ไขพร้อมกัน" in str(error)
            and "Bill" in str(error)
            and str(expected_version) in str(error)
            and str(current_version) in str(error)
        )

    def test_optimistic_lock_error_with_none_current_version(self) -> None:
        """ตรวจสอบ error เมื่อ current_version เป็น None."""
        bill_id = "bill-999"
        expected_version = 1
        error = RepositoryOptimisticLockError(bill_id, expected_version, None)

        assert error.bill_id == bill_id
        assert error.expected_version == expected_version
        assert error.current_version is None
        assert "None" in str(error)

    def test_optimistic_lock_error_inherits_from_repository_error(self) -> None:
        """ตรวจสอบ inheritance hierarchy."""
        error = RepositoryOptimisticLockError("bill-1", 1, 2)
        assert isinstance(error, RepositoryError)
        assert isinstance(error, Exception)

    def test_optimistic_lock_error_can_be_caught_as_repository_error(self) -> None:
        """ตรวจสอบว่า error สามารถจับได้ว่าเป็น RepositoryError."""
        with pytest.raises(RepositoryError):
            raise RepositoryOptimisticLockError("bill-111", 1, 2)


class TestErrorHierarchy:
    """เทสสำหรับ error inheritance hierarchy."""

    def test_all_repository_errors_inherit_from_repository_error(self) -> None:
        """ตรวจสอบว่า repository errors ทั้งหมด extends RepositoryError."""
        errors = [
            RepositoryEntityNotFoundError("id", "table"),
            RepositoryDatabaseError("message"),
            RepositoryOptimisticLockError("bill-id", 1, 2),
        ]

        for error in errors:
            assert isinstance(error, RepositoryError)

    def test_all_repository_errors_inherit_from_exception(self) -> None:
        """ตรวจสอบว่า repository errors ทั้งหมด extends Exception."""
        errors = [
            RepositoryEntityNotFoundError("id", "table"),
            RepositoryDatabaseError("message"),
            RepositoryOptimisticLockError("bill-id", 1, 2),
        ]

        for error in errors:
            assert isinstance(error, Exception)
