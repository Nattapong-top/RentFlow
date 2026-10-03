from decimal import Decimal, InvalidOperation

from pydantic import BaseModel, ConfigDict, ValidationError, field_validator

from custom_errors.custom_errors import DoNotNegativeUnitError, InvalidPricingError
from domain.units_vo import PricingAmount


class BuildingPricing(BaseModel):
    model_config = ConfigDict(frozen=True)

    water_rate: Decimal
    electricity_rate: Decimal
    cable_price: Decimal = Decimal(0)
    parking_price: Decimal = Decimal(0)

    @field_validator("water_rate", mode="before")
    @classmethod
    def validate_water_rate(cls, v: object) -> Decimal:
        try:
            amount = v if isinstance(v, PricingAmount) else PricingAmount(value=v)
            return amount.value
        except (
            InvalidOperation,
            ValueError,
            TypeError,
            DoNotNegativeUnitError,
            ValidationError,
            InvalidPricingError,
        ):
            raise InvalidPricingError("ค่าน้ำต่อหน่วยต้องไม่น้อยกว่าศูนย์")

    @field_validator("electricity_rate", mode="before")
    @classmethod
    def validate_electricity_rate(cls, v: object) -> Decimal:
        try:
            amount = v if isinstance(v, PricingAmount) else PricingAmount(value=v)
            return amount.value
        except (
            InvalidOperation,
            ValueError,
            TypeError,
            DoNotNegativeUnitError,
            ValidationError,
            InvalidPricingError,
        ):
            raise InvalidPricingError("ค่าไฟต่อหน่วยต้องไม่น้อยกว่าศูนย์")

    @field_validator("cable_price", mode="before")
    @classmethod
    def validate_cable_price(cls, v: object) -> Decimal:
        try:
            amount = v if isinstance(v, PricingAmount) else PricingAmount(value=v)
            return amount.value
        except (
            InvalidOperation,
            ValueError,
            TypeError,
            DoNotNegativeUnitError,
            ValidationError,
            InvalidPricingError,
        ):
            raise InvalidPricingError("ค่าเคเบิลต้องไม่น้อยกว่าศูนย์")

    @field_validator("parking_price", mode="before")
    @classmethod
    def validate_parking_price(cls, v: object) -> Decimal:
        try:
            amount = v if isinstance(v, PricingAmount) else PricingAmount(value=v)
            return amount.value
        except (
            InvalidOperation,
            ValueError,
            TypeError,
            DoNotNegativeUnitError,
            ValidationError,
            InvalidPricingError,
        ):
            raise InvalidPricingError("ค่าจอดรถต้องไม่น้อยกว่าศูนย์")
