from pydantic import BaseModel, ConfigDict, field_validator

from custom_errors.custom_errors import InvalidTenantError


class Tenant(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    id: str
    name: str

    @field_validator("id")
    @classmethod
    def validate_id(cls, v: str) -> str:
        if not v or not v.strip():
            raise InvalidTenantError("รหัสผู้เช่าต้องไม่ว่างเปล่า")
        return v.strip()

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise InvalidTenantError("ชื่อผู้เช่าต้องไม่ว่างเปล่า")
        return v.strip()
