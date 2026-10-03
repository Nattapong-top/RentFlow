from decimal import InvalidOperation

from pydantic import BaseModel, ConfigDict, ValidationError, field_validator

from custom_errors.custom_errors import InvalidPricingError
from domain.units_vo import PricingAmount


class BuildingPricing(BaseModel):
    model_config = ConfigDict(frozen=True)

    water_rate: PricingAmount
    electricity_rate: PricingAmount
    cable_price: PricingAmount = PricingAmount(value=0)
    parking_price: PricingAmount = PricingAmount(value=0)

    @field_validator(
        "water_rate", "electricity_rate", "cable_price", "parking_price", mode="before"
    )
    @classmethod
    def coerce_to_pricing_amount(cls, v: object) -> PricingAmount:
        if isinstance(v, PricingAmount):
            return v
        try:
            return PricingAmount(value=v)
        except (
            InvalidPricingError,
            InvalidOperation,
            ValueError,
            TypeError,
            ValidationError,
        ):
            raise InvalidPricingError("ค่าต้องไม่น้อยกว่าศูนย์")
