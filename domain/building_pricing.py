from decimal import Decimal

from pydantic import BaseModel, ConfigDict, field_validator

from custom_errors.custom_errors import InvalidPricingError
from domain.units_vo import PricingAmount


class BuildingPricing(BaseModel):
    model_config = ConfigDict(frozen=True)

    water_rate: Decimal
    electricity_rate: Decimal
    cable_price: Decimal = Decimal("0")
    parking_price: Decimal = Decimal("0")

    @field_validator("water_rate", "electricity_rate", "cable_price", "parking_price", mode="before")
    @classmethod
    def coerce_to_pricing_amount(cls, v: object, info: object) -> Decimal:
        field_name = getattr(info, "field_name", "")
        _error_messages = {
            "water_rate": "ค่าน้ำต่อหน่วยต้องไม่น้อยกว่าศูนย์",
            "electricity_rate": "ค่าไฟต่อหน่วยต้องไม่น้อยกว่าศูนย์",
            "cable_price": "ค่าเคเบิลต้องไม่น้อยกว่าศูนย์",
            "parking_price": "ค่าจอดรถต้องไม่น้อยกว่าศูนย์",
        }
        msg = _error_messages.get(field_name, "ค่าต้องไม่น้อยกว่าศูนย์")
        try:
            amount = v if isinstance(v, PricingAmount) else PricingAmount(value=v)
            return amount.value
        except Exception:
            raise InvalidPricingError(msg)
