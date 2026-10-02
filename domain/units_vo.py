from decimal import Decimal, InvalidOperation
from typing import Any
from pydantic import BaseModel, ConfigDict, field_validator

from custom_errors.custom_errors import DoNotNegativeUnitError, InvalidPricingError


class DomainValueObject(BaseModel):
    model_config = ConfigDict(frozen=True)


class Unit(DomainValueObject):
    value: Decimal

    @field_validator("value", mode="before")
    @classmethod
    def validate_value(cls, v: Any) -> Decimal:
        try:
            value = v if isinstance(v, Decimal) else Decimal(str(v))
        except (InvalidOperation, ValueError, TypeError):
            raise DoNotNegativeUnitError("หน่วยไม่ควรน้อยกว่าศูนย์")
        if value < 0:
            raise DoNotNegativeUnitError("หน่วยไม่ควรน้อยกว่าศูนย์")
        return value

    def __int__(self) -> int:
        return int(self.value)

    def __sub__(self, other: "Unit | int") -> "Unit":
        other_val = int(other)
        diff = self.value - other_val
        return Unit(value=diff)

    def __lt__(self, other: "Unit | int") -> bool:
        return self.value < int(other)

    def __le__(self, other: "Unit | int") -> bool:
        return self.value <= int(other)

    def __gt__(self, other: "Unit | int") -> bool:
        return self.value > int(other)

    def __ge__(self, other: "Unit | int") -> bool:
        return self.value >= int(other)


class PricingAmount(Unit):
    """Non-negative amount used by building pricing rules."""

    @field_validator("value", mode="before")
    @classmethod
    def validate_pricing_value(cls, v: Any) -> Decimal:
        try:
            value = v if isinstance(v, Decimal) else Decimal(str(v))
        except (InvalidOperation, ValueError, TypeError):
            raise InvalidPricingError("ค่าต้องไม่น้อยกว่าศูนย์")
        if value < 0:
            raise InvalidPricingError("ค่าต้องไม่น้อยกว่าศูนย์")
        return value

    def __str__(self) -> str:
        return str(self.value)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, PricingAmount):
            return self.value == other.value
        if isinstance(other, (Decimal, int, float)):
            return self.value == Decimal(str(other))
        return NotImplemented
