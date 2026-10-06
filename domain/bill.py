from decimal import Decimal, InvalidOperation

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from custom_errors.custom_errors import (
    DuplicateBillItemError,
    InvalidBillItemError,
    InvalidPricingError,
)
from domain.billing_period import BillingPeriod
from domain.occupant_type import OccupantType
from domain.units_vo import PricingAmount, Unit


class BillItem(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    amount: PricingAmount
    description: str = ""

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise InvalidBillItemError("ชื่อรายการต้องไม่ว่างเปล่า")
        return v.strip()

    @field_validator("amount", mode="before")
    @classmethod
    def coerce_to_pricing_amount(cls, v: object) -> PricingAmount:
        if isinstance(v, PricingAmount):
            return v
        try:
            return PricingAmount(value=v)
        except (
            InvalidOperation,
            ValueError,
            TypeError,
            ValidationError,
            InvalidPricingError,
        ):
            raise InvalidBillItemError("จำนวนเงินของรายการต้องไม่น้อยกว่าศูนย์")


class Bill(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    id: str
    room_id: str
    billing_period: BillingPeriod
    tenant_id: str | None = None
    occupant_type: OccupantType = OccupantType.TENANT
    motorcycle_count: Unit = Unit(value=Decimal(0))
    car_count: Unit = Unit(value=Decimal(0))
    cable_enabled: bool = True
    items: list[BillItem] = Field(default_factory=list)
    version: int | None = None  # สำหรับ optimistic locking ในชั้น repository

    @property
    def total(self) -> Decimal:
        """คืนค่าจำนวนเงินรวมของบิล."""
        return sum((item.amount.value for item in self.items), Decimal(0))

    def add_item(self, item: BillItem) -> None:
        """เพิ่มรายการลงในบิล (ตรวจสอบการซ้ำกัน)."""
        if any(existing.name == item.name for existing in self.items):
            raise DuplicateBillItemError(f"มีรายการ '{item.name}' อยู่ในบิลแล้ว")
        self.items.append(item)

    def clear_items(self) -> None:
        """ล้างรายการทั้งหมดออกจากบิล."""
        self.items.clear()
