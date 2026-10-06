from decimal import Decimal

from pydantic import BaseModel, ConfigDict, ValidationError, field_validator

from custom_errors.custom_errors import (
    InvalidPricingError,
    InvalidRentRateError,
    InvalidRoomError,
)
from domain.occupant_type import OccupantType
from domain.units_vo import PricingAmount, Unit


class Room(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    id: str
    room_number: str
    rent_rate: PricingAmount
    occupant_type: OccupantType = OccupantType.TENANT
    tenant_id: str | None = None
    cable_exempt: bool = False
    has_parking: bool = False
    motorcycle_count: Unit = Unit(value=Decimal(0))
    car_count: Unit = Unit(value=Decimal(0))
    cable_enabled: bool = True

    @field_validator("id")
    @classmethod
    def validate_id(cls, v: str) -> str:
        if not v or not v.strip():
            raise InvalidRoomError("รหัสห้องต้องไม่ว่างเปล่า")
        return v.strip()

    @field_validator("room_number")
    @classmethod
    def validate_room_number(cls, v: str) -> str:
        if not v or not v.strip():
            raise InvalidRoomError("หมายเลขห้องต้องไม่ว่างเปล่า")
        return v.strip()

    @field_validator("rent_rate", mode="before")
    @classmethod
    def validate_rent_rate(cls, value: object) -> PricingAmount:
        try:
            if isinstance(value, PricingAmount):
                return value

            return PricingAmount(value=Decimal(str(value)))
        except (InvalidPricingError, ValueError, TypeError, ValidationError):
            raise InvalidRentRateError("ค่าเช่าห้องต้องไม่น้อยกว่าศูนย์")
