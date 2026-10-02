from decimal import Decimal


class Billing:

    def __init__(self, rent_rate, cable_tv, water_price, electricity_price):
        rent_d = Decimal(str(rent_rate))
        cable_d = Decimal(str(cable_tv))
        water_d = Decimal(str(water_price))
        elec_d = Decimal(str(electricity_price))

        if rent_d < 0 or cable_d < 0 or water_d < 0 or elec_d < 0:
            raise ValueError("หน่วยไม่ควรน้อยกว่าศูนย์")

        self.rent_rate = rent_d
        self.cable_tv = cable_d
        self.water_price = water_d
        self.electricity_price = elec_d

    def calculate(self) -> Decimal:
        grand_total = (
            self.rent_rate + self.cable_tv + self.water_price + self.electricity_price
        )
        return grand_total
