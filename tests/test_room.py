import pytest
from custom_errors.custom_errors import InvalidRentRateError, InvalidRoomError
from domain.occupant_type import OccupantType
from domain.room import Room


from decimal import Decimal


def test_create_room_success():
    room = Room(
        id="R001",
        room_number="101",
        rent_rate=2800,
        occupant_type=OccupantType.TENANT,
        tenant_id="T001",
        cable_exempt=False,
        has_parking=True,
    )
    assert room.id == "R001"
    assert room.room_number == "101"
    assert room.rent_rate == Decimal("2800")
    assert isinstance(room.rent_rate, Decimal)
    assert room.occupant_type == OccupantType.TENANT
    assert room.tenant_id == "T001"
    assert room.cable_exempt is False
    assert room.has_parking is True


def test_create_room_defaults():
    room = Room(id="R002", room_number="102", rent_rate=3000)
    assert room.occupant_type == OccupantType.TENANT
    assert room.tenant_id is None
    assert room.cable_exempt is False
    assert room.has_parking is False


def test_create_room_with_owner_occupant():
    room = Room(
        id="R003",
        room_number="103",
        rent_rate=0,
        occupant_type=OccupantType.OWNER,
    )
    assert room.occupant_type == OccupantType.OWNER


def test_create_room_negative_rent_rate_raises_error():
    with pytest.raises(InvalidRentRateError) as exc_info:
        Room(id="R001", room_number="101", rent_rate=-2800)
    assert str(exc_info.value) == "ค่าเช่าห้องต้องไม่น้อยกว่าศูนย์"


@pytest.mark.parametrize(
    "id_val, number_val, error_msg",
    [
        ("", "101", "รหัสห้องต้องไม่ว่างเปล่า"),
        ("   ", "101", "รหัสห้องต้องไม่ว่างเปล่า"),
        ("R001", "", "หมายเลขห้องต้องไม่ว่างเปล่า"),
        ("R001", "   ", "หมายเลขห้องต้องไม่ว่างเปล่า"),
    ],
)
def test_create_room_empty_fields_raises_error(
    id_val: str, number_val: str, error_msg: str
):
    with pytest.raises(InvalidRoomError) as exc_info:
        Room(id=id_val, room_number=number_val, rent_rate=2800)
    assert str(exc_info.value) == error_msg
