import pytest

from custom_errors.custom_errors import InvalidTenantError
from domain.tenant import Tenant


def test_create_tenant_success():
    tenant = Tenant(id="T001", name="Somchai Jaidee")
    assert tenant.id == "T001"
    assert tenant.name == "Somchai Jaidee"


@pytest.mark.parametrize(
    "id_val, name_val, error_msg",
    [
        ("", "Somchai", "รหัสผู้เช่าต้องไม่ว่างเปล่า"),
        ("   ", "Somchai", "รหัสผู้เช่าต้องไม่ว่างเปล่า"),
        ("T001", "", "ชื่อผู้เช่าต้องไม่ว่างเปล่า"),
        ("T001", "   ", "ชื่อผู้เช่าต้องไม่ว่างเปล่า"),
    ],
)
def test_create_tenant_invalid_raises_error(id_val: str, name_val: str, error_msg: str):
    with pytest.raises(InvalidTenantError) as exc_info:
        Tenant(id=id_val, name=name_val)
    assert str(exc_info.value) == error_msg
