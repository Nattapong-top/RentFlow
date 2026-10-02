from decimal import Decimal
from pydantic import BaseModel, ConfigDict, field_validator

from custom_errors.custom_errors import InvalidPricingError


class BuildingPricing(BaseModel):
    model_config = ConfigDict(frozen=True)

    water_rate: Decimal
    electricity_rate: Decimal
    cable_price: Decimal = Decimal("0")
    parking_price: Decimal = Decimal("0")

    @field_validator("water_rate", mode="before")
    @classmethod
    def validate_water_rate(cls, v: object) -> Decimal:
        try:
            val = Decimal(str(v))
        except Exception:
            raise InvalidPricingError("ค่าน้ำต่อหน่วยต้องไม่น้อยกว่าศูนย์")
        if val < 0:
            raise InvalidPricingError("ค่าน้ำต่อหน่วยต้องไม่น้อยกว่าศูนย์")
        return val

    @field_validator("electricity_rate", mode="before")
    @classmethod
    def validate_electricity_rate(cls, v: object) -> Decimal:
        try:
            val = Decimal(str(v))
        except Exception:
            raise InvalidPricingError("ค่าไฟต่อหน่วยต้องไม่น้อยกว่าศูนย์")
        if val < 0:
            raise InvalidPricingError("ค่าไฟต่อหน่วยต้องไม่น้อยกว่าศูนย์")
        return val

    @field_validator("cable_price", mode="before")
    @classmethod
    def validate_cable_price(cls, v: object) -> Decimal:
        try:
            val = Decimal(str(v))
        except Exception:
            raise InvalidPricingError("ค่าเคเบิลต้องไม่น้อยกว่าศูนย์")
        if val < 0:
            raise InvalidPricingError("ค่าเคเบิลต้องไม่น้อยกว่าศูนย์")
        return val

    @field_validator("parking_price", mode="before")
    @classmethod
    def validate_parking_price(cls, v: object) -> Decimal:
        try:
            val = Decimal(str(v))
        except Exception:
            raise InvalidPricingError("ค่าจอดรถต้องไม่น้อยกว่าศูนย์")
        if val < 0:
            raise InvalidPricingError("ค่าจอดรถต้องไม่น้อยกว่าศูนย์")
        return val
