from fastapi.testclient import TestClient

from presentation.api.main import app


def test_demo_api_app_exposes_sample_room() -> None:
    response = TestClient(app).get("/api/v1/rooms")

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
