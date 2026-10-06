from custom_errors.custom_errors import MissingRequiredDataError
from domain.bill import Bill
from domain.billing_calculator import BillingCalculator
from domain.billing_period import BillingPeriod
from domain.billing_rules import BillingRules
from domain.building_pricing import BuildingPricing
from domain.room import Room


class CreateMonthlyBill:
    """Application service orchestrating UC-01: Create Monthly Bill."""

    def __init__(
        self,
        rules: BillingRules | None = None,
        calculator: BillingCalculator | None = None,
    ) -> None:
        self.rules = rules or BillingRules()
        self.calculator = calculator or BillingCalculator()

    def execute(
        self,
        room: Room,
        billing_period: BillingPeriod | str,
        pricing: BuildingPricing,
        water_meter: tuple[int, int] | None = None,
        electricity_meter: tuple[int, int] | None = None,
        existing_bill: Bill | None = None,
    ) -> Bill:
        # Step 1 & 2: Validate Input
        if isinstance(billing_period, str):
            period = BillingPeriod(value=billing_period)
        else:
            period = billing_period

        # Step 5: Check Required Data (AF-01 / BR-15)
        if water_meter is None or len(water_meter) != 2:
            raise MissingRequiredDataError(
                "ข้อมูลมิเตอร์น้ำไม่ครบถ้วน กรุณาตรวจสอบข้อมูลต้นทาง"
            )
        if electricity_meter is None or len(electricity_meter) != 2:
            raise MissingRequiredDataError(
                "ข้อมูลมิเตอร์ไฟไม่ครบถ้วน กรุณาตรวจสอบข้อมูลต้นทาง"
            )

        # Step 8: Create or Update Bill (AF-02 / BR-16, BR-17)
        if existing_bill is not None:
            bill = existing_bill
            bill.clear_items()
        else:
            bill_id = f"BILL-{room.id}-{period.value}"
            bill = Bill(
                id=bill_id,
                room_id=room.id,
                billing_period=period,
                tenant_id=room.tenant_id,
            )

        bill.occupant_type = room.occupant_type
        bill.motorcycle_count = room.motorcycle_count
        bill.car_count = room.car_count
        bill.cable_enabled = room.cable_enabled

        # Step 6 & 7: Determine Bill Items & Calculate
        if self.rules.should_charge_rent(room):
            rent_item = self.calculator.create_rent_item(room)
            bill.add_item(rent_item)

        if self.rules.should_charge_water(room):
            current_w, previous_w = water_meter
            water_item = self.calculator.create_water_item(
                current_unit=current_w,
                previous_unit=previous_w,
                rate=pricing.water_rate,
            )
            bill.add_item(water_item)

        if self.rules.should_charge_electricity(room):
            current_e, previous_e = electricity_meter
            elec_item = self.calculator.create_electricity_item(
                current_unit=current_e,
                previous_unit=previous_e,
                rate=pricing.electricity_rate,
            )
            bill.add_item(elec_item)

        if self.rules.should_charge_cable(room):
            cable_item = self.calculator.create_cable_item(pricing)
            bill.add_item(cable_item)

        if self.rules.should_charge_parking(room):
            parking_item = self.calculator.create_parking_item(
                pricing,
                motorcycle_count=bill.motorcycle_count,
                car_count=bill.car_count,
            )
            bill.add_item(parking_item)

        return bill
