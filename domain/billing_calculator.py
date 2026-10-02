from decimal import Decimal

from domain.bill import BillItem
from domain.building_pricing import BuildingPricing
from domain.meter_unit import MeterReadingUnit
from domain.room import Room


class BillingCalculator:
    """Domain service calculating amounts and creating BillItems for each billing component using Decimal."""

    def create_water_item(
        self, current_unit: int, previous_unit: int, rate: Decimal | int | float
    ) -> BillItem:
        rate_dec = Decimal(str(rate))
        unit_calc = MeterReadingUnit(
            current_unit=current_unit,
            previous_unit=previous_unit,
            unit_rate=rate_dec,
        )
        total_unit, total_price = unit_calc.calculate()
        desc = f"{current_unit} - {previous_unit} = {total_unit} หน่วย @ {rate_dec} บาท"
        return BillItem(name="ค่าน้ำ", amount=total_price, description=desc)

    def create_electricity_item(
        self, current_unit: int, previous_unit: int, rate: Decimal | int | float
    ) -> BillItem:
        rate_dec = Decimal(str(rate))
        unit_calc = MeterReadingUnit(
            current_unit=current_unit,
            previous_unit=previous_unit,
            unit_rate=rate_dec,
        )
        total_unit, total_price = unit_calc.calculate()
        desc = f"{current_unit} - {previous_unit} = {total_unit} หน่วย @ {rate_dec} บาท"
        return BillItem(name="ค่าไฟ", amount=total_price, description=desc)

    def create_rent_item(self, room: Room) -> BillItem:
        return BillItem(
            name="ค่าเช่าห้อง",
            amount=room.rent_rate,
            description="ค่าเช่าห้องประจำเดือน",
        )

    def create_cable_item(self, pricing: BuildingPricing) -> BillItem:
        return BillItem(
            name="ค่าเคเบิล",
            amount=pricing.cable_price,
            description="ค่าบริการเคเบิลทีวี",
        )

    def create_parking_item(self, pricing: BuildingPricing) -> BillItem:
        return BillItem(
            name="ค่าที่จอดรถ",
            amount=pricing.parking_price,
            description="ค่าที่จอดรถประจำเดือน",
        )
