"""
IBillRepository interface - Bill specific repository contract
"""

from abc import ABC, abstractmethod

from domain.bill import Bill
from domain.billing_period import BillingPeriod
from infrastructure.repository import IRepository


class IBillRepository(IRepository[Bill], ABC):
    """
    Bill-specific repository interface
    ขยาย IRepository[Bill] ด้วย Bill-specific query methods
    """

    @abstractmethod
    def find_by_room_and_period(
        self, room_id: str, period: BillingPeriod
    ) -> Bill | None:
        """
        ค้นหา Bill ของห้องในรอบบิลเฉพาะ

        Args:
            room_id: Room ID
            period: Billing period (YYYY-MM)

        Returns:
            Bill | None (one or none, unique constraint)
        """

    @abstractmethod
    def find_by_period(self, period: BillingPeriod) -> list[Bill]:
        """
        ค้นหา Bills ทั้งหมดในรอบบิลเฉพาะ

        Args:
            period: Billing period (YYYY-MM)

        Returns:
            list[Bill] (may be empty)
        """
