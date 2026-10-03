from decimal import Decimal, InvalidOperation

from pydantic import BaseModel, ConfigDict, Field, field_validator

from custom_errors.custom_errors import DuplicateBillItemError, InvalidBillItemError
from domain.billing_period import BillingPeriod


class BillItem(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    amount: Decimal
    description: str = ""

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise InvalidBillItemError("ชื่อรายการต้องไม่ว่างเปล่า")
        return v.strip()

    @field_validator("amount", mode="before")
    @classmethod
    def validate_amount(cls, v: object) -> Decimal:
        try:
            val = Decimal(str(v))
        except (InvalidOperation, ValueError, TypeError):
            raise InvalidBillItemError("จำนวนเงินของรายการต้องไม่น้อยกว่าศูนย์")
        if val < 0:
            raise InvalidBillItemError("จำนวนเงินของรายการต้องไม่น้อยกว่าศูนย์")
        return val


class Bill(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    id: str
    room_id: str
    billing_period: BillingPeriod
    tenant_id: str | None = None
    items: list[BillItem] = Field(default_factory=list)

    @property
    def total(self) -> Decimal:
        return sum((item.amount for item in self.items), Decimal(0))

    def add_item(self, item: BillItem) -> None:
        if any(existing.name == item.name for existing in self.items):
            raise DuplicateBillItemError(f"มีรายการ '{item.name}' อยู่ในบิลแล้ว")
        self.items.append(item)

    def clear_items(self) -> None:
        self.items.clear()
