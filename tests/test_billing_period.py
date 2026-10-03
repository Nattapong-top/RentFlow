import pytest
from pydantic import ValidationError

from custom_errors.custom_errors import InvalidBillingPeriodError
from domain.billing_period import BillingPeriod


def test_create_valid_billing_period():
    period = BillingPeriod(value="2026-09")
    assert period.value == "2026-09"
    assert period.year == 2026
    assert period.month == 9


@pytest.mark.parametrize(
    "invalid_value",
    [
        "2026-9",
        "September",
        "2026-13",
        "2026-00",
        "2026/09",
        "26-09",
        "",
        "invalid",
    ],
)
def test_create_invalid_billing_period_raises_error(invalid_value: str):
    with pytest.raises(InvalidBillingPeriodError) as exc_info:
        BillingPeriod(value=invalid_value)
    assert str(exc_info.value) == "รูปแบบรอบบิลต้องเป็น YYYY-MM เท่านั้น เช่น 2026-09"


def test_billing_period_is_frozen():
    period = BillingPeriod(value="2026-09")
    with pytest.raises(ValidationError):
        period.value = "2026-10"
