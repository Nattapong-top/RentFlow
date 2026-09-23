from custom_errors.custom_errors import DecreasingUnitError


class CalculatorMeterUnit:
    def __init__(self, current_unit, previous_unit, unit_rate):
        self.current_unit = current_unit
        self.previous_unit = previous_unit
        self.unit_rate = unit_rate

    def calculate(self):
        if self.current_unit < self.previous_unit:
            raise DecreasingUnitError("หน่วยปัจจุบันไม่ควรน้อยกว่าหน่วยก่อนหน้า")

        total_unit = self.current_unit - self.previous_unit
        total_price = self.unit_rate * total_unit
        return total_unit, total_price
