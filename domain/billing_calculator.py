from decimal import Decimal

from domain.bill import BillItem
from domain.building_pricing import BuildingPricing
from domain.meter_unit import MeterReadingUnit
from domain.room import Room
from domain.units_vo import PricingAmount, Unit


class BillingCalculator:
    """Domain service calculating amounts and creating BillItems for each billing component using Decimal."""

    def create_water_item(
        self, current_unit: int, previous_unit: int, rate: Decimal | float
    ) -> BillItem:
        rate = rate.value if hasattr(rate, "value") else rate
        rate_dec = Decimal(str(rate))
        unit_calc = MeterReadingUnit(
            current_unit=current_unit,
            previous_unit=previous_unit,
            unit_rate=rate_dec,
        )
        total_unit, total_price = unit_calc.calculate()
        desc = f"{current_unit} - {previous_unit} = {total_unit} หน่วย @ {rate_dec} บาท"
        return BillItem(
            name="ค่าน้ำ", amount=PricingAmount(value=total_price), description=desc
        )

    def create_electricity_item(
        self, current_unit: int, previous_unit: int, rate: Decimal | float
    ) -> BillItem:
        rate = rate.value if hasattr(rate, "value") else rate
        rate_dec = Decimal(str(rate))
        unit_calc = MeterReadingUnit(
            current_unit=current_unit,
            previous_unit=previous_unit,
            unit_rate=rate_dec,
        )
        total_unit, total_price = unit_calc.calculate()
        desc = f"{current_unit} - {previous_unit} = {total_unit} หน่วย @ {rate_dec} บาท"
        return BillItem(
            name="ค่าไฟ", amount=PricingAmount(value=total_price), description=desc
        )

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

    def create_parking_item(
        self,
        pricing: BuildingPricing,
        motorcycle_count: Unit | None = None,
        car_count: Unit | None = None,
    ) -> BillItem:
        # Keep the legacy call shape working until the bill creation flow
        # supplies vehicle counts from its monthly snapshot.
        if motorcycle_count is None and car_count is None:
            total_price = pricing.parking_price.value
        else:
            motorcycle_units = (
                motorcycle_count.value if motorcycle_count is not None else Decimal(0)
            )
            car_units = car_count.value if car_count is not None else Decimal(0)
            motorcycle_fee = max(motorcycle_units - Decimal(1), Decimal(0)) * Decimal(
                100
            )
            car_fee = car_units * pricing.parking_price.value
            total_price = motorcycle_fee + car_fee

        return BillItem(
            name="ค่าที่จอดรถ",
            amount=PricingAmount(value=total_price),
            description="ค่าที่จอดรถประจำเดือน",
        )
