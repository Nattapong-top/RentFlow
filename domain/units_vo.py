from pydantic import BaseModel, ConfigDict, field_validator

from custom_errors.custom_errors import DoNotNegativeUnitError


class DomainValueObject(BaseModel):
    model_config = ConfigDict(frozen=True)


class Unit(DomainValueObject):
    value: int

    @field_validator("value")
    @classmethod
    def validate_value(cls, v: int) -> int:
        if v < 0:
            raise DoNotNegativeUnitError("หน่วยไม่ควรน้อยกว่าศูนย์")
        return v

    def __int__(self) -> int:
        return self.value

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