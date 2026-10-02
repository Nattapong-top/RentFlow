class Billing:
    def __init__(self, rent_rate, cable_tv, water_price, electricity_price):
        if rent_rate < 0 or cable_tv < 0 or water_price < 0 or electricity_price < 0:
            raise ValueError("หน่วยไม่ควรน้อยกว่าศูนย์")

        self.rent_rate = rent_rate
        self.cable_tv = cable_tv
        self.water_price = water_price
        self.electricity_price = electricity_price

    def calculate(self):
        grand_total = (
                self.rent_rate + self.cable_tv + self.water_price + self.electricity_price
        )
        return grand_total
