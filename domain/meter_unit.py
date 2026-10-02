from decimal import Decimal

from custom_errors.custom_errors import DecreasingUnitError


class MeterReadingUnit:

    def __init__(
        self,
        current_unit: int,
        previous_unit: int,
        unit_rate: Decimal | int | float,
    ) -> None:
        if current_unit < previous_unit:
            raise DecreasingUnitError("หน่วยปัจจุบันไม่ควรน้อยกว่าหน่วยก่อนหน้า")

        self.current_unit = current_unit
        self.previous_unit = previous_unit
        self.unit_rate = Decimal(str(unit_rate))

    def calculate(self) -> tuple[int, Decimal]:
        total_unit = self.current_unit - self.previous_unit
        total_price = self.unit_rate * Decimal(total_unit)
        return total_unit, total_price
