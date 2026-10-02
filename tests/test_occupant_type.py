from domain.occupant_type import OccupantType


def test_occupant_type_values():
    assert OccupantType.TENANT.value == "TENANT"
    assert OccupantType.OWNER.value == "OWNER"


def test_occupant_type_equality():
    assert OccupantType("TENANT") == OccupantType.TENANT
    assert OccupantType("OWNER") == OccupantType.OWNER
