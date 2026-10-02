from pydantic import Field, BaseModel, ConfigDict, field_validator

from custom_errors.custom_errors import DoNotNegativeUnitError

class DomainValueObject(BaseModel):
    model_config = ConfigDict(frozen=True)



class Unit(DomainValueObject):
    value: int

    @field_validator('value')
    @classmethod
    def validate_value(cls, v: int) -> int:
        if v < 0:
            raise DoNotNegativeUnitError("หน่วยไม่ควรน้อยกว่าศูนย์")
        return v