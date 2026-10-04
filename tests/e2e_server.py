from domain.building_pricing import BuildingPricing
from domain.occupant_type import OccupantType
from domain.room import Room
from infrastructure.repositories.bill_dao import BillDAO
from presentation.api.app import create_app

app = create_app(
    rooms=[
        Room(
            id="room-101",
            room_number="101",
            rent_rate=3000,
            occupant_type=OccupantType.TENANT,
            tenant_id="tenant-101",
            cable_exempt=False,
            has_parking=True,
        )
    ],
    pricing=BuildingPricing(
        water_rate=8,
        electricity_rate=7,
        cable_price=60,
        parking_price=500,
    ),
    bill_repository=BillDAO(),
    allowed_origins=["http://127.0.0.1:5174"],
)
