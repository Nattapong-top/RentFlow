"""อินเทอร์เฟซทั่วไปสำหรับ Repository (เก็บข้อมูล)."""

from abc import ABC, abstractmethod
from typing import TypeVar

T = TypeVar("T")


class IRepository[T](ABC):
    """ฐานนามธรรมของ Repository สำหรับบันทึก Domain Entities.

    อินเทอร์เฟซนี้กำหนดสัญญาที่ repositories ทั้งหมดต้องปฏิบัติตาม:
    - แยกตรรกะการเข้าถึงข้อมูลออกจากชั้น Domain
    - รองรับเบ็กเอนด์การจัดเก็บข้อมูลหลายแบบ (SQLite, PostgreSQL, ฯลฯ)
    - ความสามารถทดสอบผ่านการแทรก mock repositories
    - สถาปัตยกรรมชั้นแบบสะอาด (Domain → Application → Infrastructure)

    ตัวแปรประเภท T แทนประเภท Domain entity (เช่น Bill).

    ตัวอย่าง:
        >>> class BillRepository(IRepository[Bill]):
        ...     def save(self, bill: Bill) -> Bill:
        ...         # บันทึก bill ลงฐานข้อมูล
        ...         pass
    """

    @abstractmethod
    def save(self, entity: T) -> T:
        """บันทึก entity ลงฐานข้อมูล (insert หรือ update).

        สำหรับ entity ใหม่: สร้างระเบียนใหม่และส่งคืน entity ที่บันทึก
        พร้อมค่าที่ฐานข้อมูลกำหนด (เช่น version field).

        สำหรับ entity ที่มีอยู่: อัปเดตระเบียนและส่งคืน entity ที่อัปเดตแล้ว.

        Args:
            entity: Domain entity ที่ต้องบันทึก.

        Returns:
            Entity ที่บันทึกแล้วพร้อมฟิลด์ที่ฐานข้อมูลกำหนด.

        Raises:
            RepositoryDatabaseError: หากการดำเนินการฐานข้อมูลล้มเหลว
                (constraint violation, connection error, ฯลฯ).
            RepositoryOptimisticLockError: หากตรวจจับการแก้ไขพร้อมกัน
                (version mismatch on update).
        """

    @abstractmethod
    def find_by_id(self, entity_id: str) -> T:
        """ดึง entity จากฐานข้อมูลตามคีย์หลัก.

        โหลด entity และลูก entity ที่เกี่ยวข้อง (สำหรับ aggregates).
        ยกข้อยกเว้นหาก entity ไม่มีอยู่.

        Args:
            entity_id: ค่า primary key (ตัวระบุเฉพาะ).

        Returns:
            Domain entity ที่โหลดทั้งหมดจากฐานข้อมูล.

        Raises:
            RepositoryEntityNotFoundError: หาก entity ที่มี ID ดังกล่าว
                ไม่มีอยู่ในฐานข้อมูล.
            RepositoryDatabaseError: หากการดำเนินการฐานข้อมูลล้มเหลว.
        """

    @abstractmethod
    def delete_by_id(self, entity_id: str) -> None:
        """ลบ entity จากฐานข้อมูลตามคีย์หลัก.

        สำหรับ aggregates: ลบ entity รูทและลบเรียงลำดับลูก entity
        (เช่น Bill และ BillItems).

        Args:
            entity_id: ค่า primary key (ตัวระบุเฉพาะ).

        Raises:
            RepositoryEntityNotFoundError: หาก entity ที่มี ID ดังกล่าว
                ไม่มีอยู่ในฐานข้อมูล.
            RepositoryDatabaseError: หากการดำเนินการฐานข้อมูลล้มเหลว.
        """

    @abstractmethod
    def exists(self, entity_id: str) -> bool:
        """ตรวจสอบว่า entity มีอยู่ในฐานข้อมูลโดยไม่โหลดวัตถุเต็ม.

        ให้การตรวจสอบการมีอยู่ที่เบา โดยไม่ต้องโหลด entity ทั้งหมด.

        Args:
            entity_id: ค่า primary key (ตัวระบุเฉพาะ).

        Returns:
            True หาก entity มีอยู่ในฐานข้อมูล False หากไม่.

        Raises:
            RepositoryDatabaseError: หากการดำเนินการฐานข้อมูลล้มเหลว.
        """
