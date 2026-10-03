from decimal import Decimal

from custom_errors.custom_errors import DecreasingUnitError
from domain.units_vo import Unit


class MeterReadingUnit:

    def __init__(
        self,
        current_unit: Unit | int,
        previous_unit: Unit | int,
        unit_rate: Decimal | float,
    ) -> None:
        self.current_unit = (
            current_unit if isinstance(current_unit, Unit) else Unit(value=current_unit)
        )
        self.previous_unit = (
            previous_unit
            if isinstance(previous_unit, Unit)
            else Unit(value=previous_unit)
        )

        if self.current_unit < self.previous_unit:
            raise DecreasingUnitError("หน่วยปัจจุบันไม่ควรน้อยกว่าหน่วยก่อนหน้า")

        self.unit_rate = Decimal(str(unit_rate))

    def calculate(self) -> tuple[int, Decimal]:
        total_unit = (self.current_unit - self.previous_unit).value
        total_price = self.unit_rate * Decimal(total_unit)
        return total_unit, total_price
