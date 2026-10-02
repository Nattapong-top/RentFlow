import re
from pydantic import BaseModel, ConfigDict, field_validator

from custom_errors.custom_errors import InvalidBillingPeriodError


class DomainValueObject(BaseModel):
    model_config = ConfigDict(frozen=True)


class BillingPeriod(DomainValueObject):
    value: str

    @field_validator("value")
    @classmethod
    def validate_period(cls, v: str) -> str:
        pattern = r"^\d{4}-(0[1-9]|1[0-2])$"
        if not isinstance(v, str) or not re.match(pattern, v):
            raise InvalidBillingPeriodError(
                "รูปแบบรอบบิลต้องเป็น YYYY-MM เท่านั้น เช่น 2026-09"
            )
        return v

    @property
    def year(self) -> int:
        return int(self.value.split("-")[0])

    @property
    def month(self) -> int:
        return int(self.value.split("-")[1])
