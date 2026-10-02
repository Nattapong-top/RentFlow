from pydantic import BaseModel, ConfigDict, field_validator

from custom_errors.custom_errors import InvalidPricingError


class BuildingPricing(BaseModel):
    model_config = ConfigDict(frozen=True)

    water_rate: float | int
    electricity_rate: float | int
    cable_price: float | int = 0
    parking_price: float | int = 0

    @field_validator("water_rate")
    @classmethod
    def validate_water_rate(cls, v: float | int) -> float | int:
        if v < 0:
            raise InvalidPricingError("ค่าน้ำต่อหน่วยต้องไม่น้อยกว่าศูนย์")
        return v

    @field_validator("electricity_rate")
    @classmethod
    def validate_electricity_rate(cls, v: float | int) -> float | int:
        if v < 0:
            raise InvalidPricingError("ค่าไฟต่อหน่วยต้องไม่น้อยกว่าศูนย์")
        return v

    @field_validator("cable_price")
    @classmethod
    def validate_cable_price(cls, v: float | int) -> float | int:
        if v < 0:
            raise InvalidPricingError("ค่าเคเบิลต้องไม่น้อยกว่าศูนย์")
        return v

    @field_validator("parking_price")
    @classmethod
    def validate_parking_price(cls, v: float | int) -> float | int:
        if v < 0:
            raise InvalidPricingError("ค่าจอดรถต้องไม่น้อยกว่าศูนย์")
        return v
