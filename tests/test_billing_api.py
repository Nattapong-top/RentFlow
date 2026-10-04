import pytest
from fastapi.testclient import TestClient

from domain.building_pricing import BuildingPricing
from domain.occupant_type import OccupantType
from domain.room import Room
from infrastructure.repositories.bill_dao import BillDAO
from presentation.api.app import create_app


@pytest.fixture
def tenant_room() -> Room:
    return Room(
        id="room-101",
        room_number="101",
        rent_rate=3000,
        occupant_type=OccupantType.TENANT,
        tenant_id="tenant-101",
        cable_exempt=False,
        has_parking=True,
    )


@pytest.fixture
def building_pricing() -> BuildingPricing:
    return BuildingPricing(
        water_rate=8,
        electricity_rate=7,
        cable_price=60,
        parking_price=500,
    )


@pytest.fixture
def bill_repository() -> BillDAO:
    return BillDAO()


@pytest.fixture
def client(
    tenant_room: Room,
    building_pricing: BuildingPricing,
    bill_repository: BillDAO,
) -> TestClient:
    app = create_app(
        rooms=[tenant_room],
        pricing=building_pricing,
        bill_repository=bill_repository,
    )
    return TestClient(app)


@pytest.fixture
def bill_request() -> dict[str, object]:
    return {
        "room_id": "room-101",
        "billing_period": "2026-10",
        "water_meter": [450, 350],
        "electricity_meter": [250, 200],
    }


def test_list_rooms_returns_backend_catalog_and_string_prices(
    client: TestClient,
) -> None:
    response = client.get("/api/v1/rooms")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": "room-101",
            "room_number": "101",
            "rent_rate": "3000",
            "occupant_type": "TENANT",
            "tenant_id": "tenant-101",
            "cable_exempt": False,
            "has_parking": True,
        }
    ]


def test_create_bill_uses_backend_pricing_and_returns_string_amounts(
    client: TestClient, bill_request: dict[str, object]
) -> None:
    response = client.post("/api/v1/bills", json=bill_request)

    assert response.status_code == 201
    assert response.json()["id"] == "BILL-room-101-2026-10"
    assert response.json()["total"] == "4710"
    assert all(isinstance(item["amount"], str) for item in response.json()["items"])


def test_create_bill_persists_through_injected_repository(
    client: TestClient,
    bill_repository: BillDAO,
    bill_request: dict[str, object],
) -> None:
    response = client.post("/api/v1/bills", json=bill_request)

    assert response.status_code == 201
    assert bill_repository.find_by_id(response.json()["id"]) is not None


def test_create_bill_rejects_client_supplied_pricing(
    client: TestClient, bill_request: dict[str, object]
) -> None:
    bill_request["pricing"] = {
        "water_rate": "0",
        "electricity_rate": "0",
        "cable_price": "0",
        "parking_price": "0",
    }

    response = client.post("/api/v1/bills", json=bill_request)

    assert response.status_code == 422
    assert response.json()["detail"] == "ข้อมูลคำขอไม่ถูกต้อง"


def test_list_bills_by_period_returns_created_bill(
    client: TestClient, bill_request: dict[str, object]
) -> None:
    created = client.post("/api/v1/bills", json=bill_request)

    response = client.get("/api/v1/bills", params={"period": "2026-10"})

    assert response.status_code == 200
    assert [bill["id"] for bill in response.json()] == [created.json()["id"]]


def test_list_bills_returns_422_for_invalid_period(client: TestClient) -> None:
    response = client.get("/api/v1/bills", params={"period": "2026-13"})

    assert response.status_code == 422
    assert response.json()["detail"] == (
        "รูปแบบรอบบิลต้องเป็น YYYY-MM เท่านั้น เช่น 2026-09"
    )


def test_get_bill_returns_404_when_bill_does_not_exist(client: TestClient) -> None:
    response = client.get("/api/v1/bills/not-found")

    assert response.status_code == 404
    assert response.json()["detail"] == "ไม่พบบิลที่ร้องขอ"


def test_create_bill_returns_404_for_unknown_room(
    client: TestClient, bill_request: dict[str, object]
) -> None:
    bill_request["room_id"] = "unknown-room"

    response = client.post("/api/v1/bills", json=bill_request)

    assert response.status_code == 404
    assert response.json()["detail"] == "ไม่พบห้องพักที่ระบุ"


def test_create_bill_returns_422_for_decreasing_meter(
    client: TestClient, bill_request: dict[str, object]
) -> None:
    bill_request["water_meter"] = [350, 450]

    response = client.post("/api/v1/bills", json=bill_request)

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert any("\u0e00" <= character <= "\u0e7f" for character in detail)
    assert not any(character.isascii() and character.isalpha() for character in detail)


def test_create_bill_returns_409_when_room_period_already_has_bill(
    client: TestClient, bill_request: dict[str, object]
) -> None:
    first_response = client.post("/api/v1/bills", json=bill_request)
    second_response = client.post("/api/v1/bills", json=bill_request)

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "มีบิลของห้องนี้ในรอบบิลดังกล่าวแล้ว"


def test_request_validation_error_is_returned_in_thai(client: TestClient) -> None:
    response = client.post("/api/v1/bills", json={})

    assert response.status_code == 422
    assert response.json()["detail"] == "ข้อมูลคำขอไม่ถูกต้อง"


def test_unknown_endpoint_error_is_returned_in_thai(client: TestClient) -> None:
    response = client.get("/api/v1/unknown")

    assert response.status_code == 404
    assert response.json()["detail"] == "ไม่พบเส้นทางที่ร้องขอ"


def test_method_not_allowed_error_is_returned_in_thai(client: TestClient) -> None:
    response = client.post("/api/v1/rooms")

    assert response.status_code == 405
    assert response.json()["detail"] == "ไม่อนุญาตให้ใช้วิธีการร้องขอนี้"
    assert response.headers["allow"] == "GET"
