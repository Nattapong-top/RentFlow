# Pipeline Flow — RentFlow Main Workflow

## Standard Flow: Create Monthly Bill (UC-01)

```
┌──────────────┐
│ 1. INPUT     │ ← room: Room, billing_period: str|BillingPeriod
└──────────────┘   pricing: BuildingPricing
       ↓           water_meter: (int, int)
┌──────────────┐   electricity_meter: (int, int)
│ 2. VALIDATE  │
└──────────────┘   
       ↓
┌──────────────┐   Step 5 (AF-01/BR-15):
│ 3. LOAD VO   │   Check water_meter ≠ None ∧ len == 2
└──────────────┘   Check electricity_meter ≠ None ∧ len == 2
       ↓           Raise MissingRequiredDataError if fail
┌──────────────┐
│ 4. APPLY     │
│ RULES        │   Step 6-7 (AF-02/BR-02-BR-15):
└──────────────┘   BillingRules.should_charge_X(room)
       ↓           → decide yes/no for each item type
┌──────────────┐
│ 5. CALCULATE │   BillingCalculator.create_X_item()
└──────────────┘   → calculate amount
       ↓
┌──────────────┐
│ 6. BUILD     │   Bill.add_item(BillItem)
│ RESULT       │   → append to items list
└──────────────┘   (check no duplicates)
       ↓
┌──────────────┐
│ 7. RETURN    │   return Bill
└──────────────┘   (Bill.total auto-calculated)
```

---

## Detailed Flow: CreateMonthlyBill.execute()

### Step 1-2: Input Validation
```python
def execute(self, room, billing_period, pricing, water_meter, electricity_meter, existing_bill):
    # Parse billing_period
    if isinstance(billing_period, str):
        period = BillingPeriod(value=billing_period)  # Validates format YYYY-MM
    else:
        period = billing_period

    # Validate required data (AF-01 / BR-15)
    if water_meter is None or len(water_meter) != 2:
        raise MissingRequiredDataError("水meter data incomplete")
    if electricity_meter is None or len(electricity_meter) != 2:
        raise MissingRequiredDataError("Electricity meter data incomplete")
```

### Step 3: Create or Clear Bill
```python
    # AF-02 / BR-16, BR-17: Recalculation
    if existing_bill is not None:
        bill = existing_bill
        bill.clear_items()  # Remove old items
    else:
        bill_id = f"BILL-{room.id}-{period.value}"
        bill = Bill(
            id=bill_id,
            room_id=room.id,
            billing_period=period,
            tenant_id=room.tenant_id,
        )
```

### Step 4-7: Apply Rules & Calculate

```python
    # ========== RENT ==========
    if self.rules.should_charge_rent(room):  # TENANT only
        rent_item = self.calculator.create_rent_item(room)
        bill.add_item(rent_item)
        # Item: name="ค่าเช่าห้อง", amount=room.rent_rate

    # ========== WATER ==========
    if self.rules.should_charge_water(room):  # TENANT + OWNER
        current_w, previous_w = water_meter
        water_item = self.calculator.create_water_item(
            current_unit=current_w,
            previous_unit=previous_w,
            rate=pricing.water_rate,
        )
        bill.add_item(water_item)
        # Item: name="ค่าน้ำ", amount=(current-previous)*rate

    # ========== ELECTRICITY ==========
    if self.rules.should_charge_electricity(room):  # TENANT + OWNER
        current_e, previous_e = electricity_meter
        elec_item = self.calculator.create_electricity_item(
            current_unit=current_e,
            previous_unit=previous_e,
            rate=pricing.electricity_rate,
        )
        bill.add_item(elec_item)
        # Item: name="ค่าไฟ", amount=(current-previous)*rate

    # ========== CABLE ==========
    if self.rules.should_charge_cable(room):  # TENANT only, if not exempt
        cable_item = self.calculator.create_cable_item(pricing)
        bill.add_item(cable_item)
        # Item: name="ค่าเคเบิล", amount=pricing.cable_price

    # ========== PARKING ==========
    if self.rules.should_charge_parking(room):  # TENANT only, if has_parking
        parking_item = self.calculator.create_parking_item(pricing)
        bill.add_item(parking_item)
        # Item: name="ค่าที่จอดรถ", amount=pricing.parking_price

    return bill
```

---

## Decision Tree: Which Items to Charge?

### For TENANT:
```
┌─ RENT
│  occupant_type == TENANT → YES
│  occupant_type == OWNER → NO

├─ WATER
│  Always YES (TENANT + OWNER)

├─ ELECTRICITY
│  Always YES (TENANT + OWNER)

├─ CABLE
│  occupant_type == TENANT
│  ∧ cable_exempt == False → YES
│  Otherwise → NO

└─ PARKING
   occupant_type == TENANT
   ∧ has_parking == True → YES
   Otherwise → NO
```

### For OWNER:
```
├─ RENT → NO (owner doesn't pay rent)
├─ WATER → YES
├─ ELECTRICITY → YES
├─ CABLE → NO (only for tenants)
└─ PARKING → NO (only for tenants)
```

---

## Example Execution

### Input
```python
room = Room(
    id="R001",
    room_number="101",
    rent_rate=2800,
    occupant_type=OccupantType.TENANT,
    tenant_id="T001",
    cable_exempt=False,
    has_parking=True,
)

billing_period = "2026-09"

pricing = BuildingPricing(
    water_rate=19,
    electricity_rate=8,
    cable_price=60,
    parking_price=500,
)

water_meter = (125, 99)  # (current=125, previous=99)
electricity_meter = (450, 350)  # (current=450, previous=350)
```

### Execution
```
1. Parse period → BillingPeriod(value="2026-09") ✅
2. Validate meter data → both tuples len==2 ✅
3. Create new bill → Bill(id="BILL-R001-2026-09", ...)
4. Check should_charge_rent? YES (TENANT)
   → add BillItem(name="ค่าเช่าห้อง", amount=2800)
5. Check should_charge_water? YES (always)
   → add BillItem(name="ค่าน้ำ", amount=(125-99)*19 = 494)
6. Check should_charge_electricity? YES (always)
   → add BillItem(name="ค่าไฟ", amount=(450-350)*8 = 800)
7. Check should_charge_cable? YES (TENANT ∧ not exempt)
   → add BillItem(name="ค่าเคเบิล", amount=60)
8. Check should_charge_parking? YES (TENANT ∧ has_parking)
   → add BillItem(name="ค่าที่จอดรถ", amount=500)
```

### Output Bill
```
Bill(
  id="BILL-R001-2026-09",
  room_id="R001",
  billing_period=BillingPeriod(value="2026-09"),
  tenant_id="T001",
  items=[
    BillItem(name="ค่าเช่าห้อง", amount=2800),
    BillItem(name="ค่าน้ำ", amount=494),
    BillItem(name="ค่าไฟ", amount=800),
    BillItem(name="ค่าเคเบิล", amount=60),
    BillItem(name="ค่าที่จอดรถ", amount=500),
  ],
  total=4654,  # auto-calculated
)
```

---

## Error Handling in Pipeline

```
┌─ Missing Required Data
│  water_meter or electricity_meter is None
│  → MissingRequiredDataError (raised in Step 2)

├─ Invalid Billing Period
│  billing_period format not YYYY-MM
│  → InvalidBillingPeriodError (raised in BillingPeriod.__init__)

├─ Invalid Room
│  room_number or id is empty
│  → InvalidRoomError (raised in Room.__init__)

├─ Meter Reading Decreasing
│  current_unit < previous_unit
│  → DecreasingUnitError (raised in MeterReadingUnit.__init__)

├─ Negative Pricing
│  water_rate < 0, electricity_rate < 0, etc.
│  → InvalidPricingError (raised in BuildingPricing.__init__)

├─ Duplicate Bill Item
│  add_item() called twice with same name
│  → DuplicateBillItemError (raised in Bill.add_item())

└─ Tenant Missing
   occupant_type=TENANT but tenant_id=None
   → (Warning only, may need validation)
```

---

## Pipeline Rules (สิ่งที่ Pipeline ต้องและไม่ต้องทำ)

### ❌ ไม่ควรมีใน Pipeline
```python
# ❌ Business logic ใน pipeline
if room.occupant_type == "TENANT":  # This is BillingRules job!
    charge_rent()

# ❌ Hardcoded values
if cable_price < 50:  # Use pricing parameter!
    ...
```

### ✅ ควรทำใน Pipeline
```python
# ✅ Orchestrate เท่านั้น
data = validate_input(room, period, pricing, meters)
result = billing_rules.decide(data)
amounts = calculator.calculate(data)
bill.add_items(amounts)
return bill
```

---

## Performance Considerations

```
1. Meter reading: O(1) calculation per utility
2. Bill items: O(n) where n=5 items max
3. Total execution: ~O(5) constant time
4. Memory: ~O(5) items stored in Bill

Current performance: <1ms per CreateMonthlyBill.execute()
Future optimization: Batch processing if needed
```

---

## Extension Points

```
1. Add new charge type:
   - Add to BillingRules.should_charge_X()
   - Add BillingCalculator.create_X_item()
   - Add test case

2. Change calculation logic:
   - Modify BillingCalculator.create_X_item()
   - Tests validate new logic

3. Add discount/surcharge:
   - Extend BillItem? Or create separate charge?
   - Modify BillingRules decision logic
   - Update tests

4. API integration:
   - Wrap execute() in API endpoint
   - Handle errors → HTTP responses
```
