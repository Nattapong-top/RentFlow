"""เทสสำหรับ IRepository generic interface."""

from abc import ABC
from typing import TypeVar

import pytest

from infrastructure.repository import IRepository

# สร้าง TypeVar สำหรับการทดสอบ
T = TypeVar("T")


class TestEntity:
    """Entity ทดสอบง่ายๆ."""

    def __init__(self, entity_id: str, name: str) -> None:
        """เริ่มต้น TestEntity."""
        self.id = entity_id
        self.name = name


class ConcreteRepository(IRepository[TestEntity]):
    """การใช้งาน Repository เพื่อการทดสอบ."""

    def save(self, entity: TestEntity) -> TestEntity:
        """บันทึก entity (stub implementation)."""
        return entity

    def find_by_id(self, entity_id: str) -> TestEntity:
        """ดึง entity ตาม ID (stub implementation)."""
        return TestEntity(entity_id, "test")

    def delete_by_id(self, entity_id: str) -> None:
        """ลบ entity ตาม ID (stub implementation)."""
        return

    def exists(self, entity_id: str) -> bool:
        """ตรวจสอบการมีอยู่ (stub implementation)."""
        return True


class TestIRepository:
    """เทสสำหรับ IRepository interface."""

    def test_irepository_is_abstract(self) -> None:
        """ตรวจสอบว่า IRepository เป็น abstract class."""
        assert hasattr(IRepository, "__abstractmethods__")
        abstract_methods = IRepository.__abstractmethods__
        assert "save" in abstract_methods
        assert "find_by_id" in abstract_methods
        assert "delete_by_id" in abstract_methods
        assert "exists" in abstract_methods

    def test_irepository_cannot_be_instantiated(self) -> None:
        """ตรวจสอบว่า IRepository ไม่สามารถ instantiate ได้โดยตรง."""
        with pytest.raises(TypeError):
            IRepository[TestEntity]()  # type: ignore

    def test_concrete_repository_can_be_instantiated(self) -> None:
        """ตรวจสอบว่า concrete repository สามารถ instantiate ได้."""
        repo = ConcreteRepository()
        assert isinstance(repo, IRepository)

    def test_concrete_repository_implements_save(self) -> None:
        """ตรวจสอบว่า concrete repository มี save method."""
        repo = ConcreteRepository()
        test_entity = TestEntity("id-1", "test")
        result = repo.save(test_entity)
        assert result == test_entity

    def test_concrete_repository_implements_find_by_id(self) -> None:
        """ตรวจสอบว่า concrete repository มี find_by_id method."""
        repo = ConcreteRepository()
        result = repo.find_by_id("id-1")
        assert result.id == "id-1"

    def test_concrete_repository_implements_delete_by_id(self) -> None:
        """ตรวจสอบว่า concrete repository มี delete_by_id method."""
        repo = ConcreteRepository()
        # ไม่ควรยกข้อยกเว้น
        repo.delete_by_id("id-1")

    def test_concrete_repository_implements_exists(self) -> None:
        """ตรวจสอบว่า concrete repository มี exists method."""
        repo = ConcreteRepository()
        result = repo.exists("id-1")
        assert isinstance(result, bool)

    def test_irepository_has_correct_methods_signature(self) -> None:
        """ตรวจสอบ method signatures."""
        repo = ConcreteRepository()
        assert callable(repo.save)
        assert callable(repo.find_by_id)
        assert callable(repo.delete_by_id)
        assert callable(repo.exists)

    def test_concrete_repository_inherits_from_irepository(self) -> None:
        """ตรวจสอบ inheritance hierarchy."""
        repo = ConcreteRepository()
        assert isinstance(repo, IRepository)
        assert isinstance(repo, ABC)

    def test_multiple_concrete_implementations_can_coexist(self) -> None:
        """ตรวจสอบว่า multiple concrete repositories สามารถมีอยู่ได้."""

        class AnotherConcreteRepository(IRepository[TestEntity]):
            """การใช้งาน Repository ที่สอง."""

            def save(self, entity: TestEntity) -> TestEntity:
                """บันทึก entity."""
                return entity

            def find_by_id(self, entity_id: str) -> TestEntity:
                """ดึง entity ตาม ID."""
                return TestEntity(entity_id, "another")

            def delete_by_id(self, entity_id: str) -> None:
                """ลบ entity ตาม ID."""
                return

            def exists(self, entity_id: str) -> bool:
                """ตรวจสอบการมีอยู่."""
                return False

        repo1 = ConcreteRepository()
        repo2 = AnotherConcreteRepository()

        assert isinstance(repo1, IRepository)
        assert isinstance(repo2, IRepository)
        assert repo1.exists("id-1") is True
        assert repo2.exists("id-1") is False
