from domain.occupant_type import OccupantType
from domain.room import Room


class BillingRules:
    """Domain service determining applicable billing items based on occupant type and room settings."""

    def should_charge_rent(self, room: Room) -> bool:
        return room.occupant_type == OccupantType.TENANT

    def should_charge_water(self, room: Room) -> bool:
        return True

    def should_charge_electricity(self, room: Room) -> bool:
        return True

    def should_charge_cable(self, room: Room) -> bool:
        if room.occupant_type == OccupantType.OWNER:
            return False
        return not room.cable_exempt

    def should_charge_parking(self, room: Room) -> bool:
        if room.occupant_type == OccupantType.OWNER:
            return False
        return room.has_parking

    def determine_applicable_items(self, room: Room) -> list[str]:
        items: list[str] = []
        if self.should_charge_rent(room):
            items.append("rent")
        if self.should_charge_water(room):
            items.append("water")
        if self.should_charge_electricity(room):
            items.append("electricity")
        if self.should_charge_cable(room):
            items.append("cable")
        if self.should_charge_parking(room):
            items.append("parking")
        return items
