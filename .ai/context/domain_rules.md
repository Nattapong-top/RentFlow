# Domain Rules — RentFlow Billing System

## Business Rules หลัก

### Occupant Type Classification

| OccupantType | ค่าเช่า | ค่าน้ำ | ค่าไฟ | ค่าเคเบิล | ค่าที่จอดรถ | หมายเหตุ |
|---|---|---|---|---|---|---|
| **TENANT** | ✅ | ✅ | ✅ | ✅ (ถ้าไม่ exempt) | ✅ (ถ้ามี) | Residents renting rooms |
| **OWNER** | ❌ | ✅ | ✅ | ❌ | ❌ | Building owner/operator |

---

## Business Rules ละเอียด

### BR-01: Billing Period Format
```
- Format: YYYY-MM (เช่น 2026-09)
- Valid year: 1900-9999
- Valid month: 01-12
- Error: InvalidBillingPeriodError
```

### BR-02: Tenant Billing Rules
**ผู้เช่า (TENANT) ต้องคิดค่า:**
1. **ค่าเช่าห้อง** — `Room.rent_rate` (fixed per month)
2. **ค่าน้ำ** — คำนวณจาก meter: `(current - previous) × rate`
3. **ค่าไฟ** — คำนวณจาก meter: `(current - previous) × rate`
4. **ค่าเคเบิล** — `BuildingPricing.cable_price` (ถ้า `room.cable_exempt == False`)
5. **ค่าที่จอดรถ** — `BuildingPricing.parking_price` (ถ้า `room.has_parking == True`)

### BR-03: Owner Billing Rules
**เจ้าของ (OWNER) คิดแค่:**
1. **ค่าน้ำ** — คำนวณจาก meter: `(current - previous) × rate`
2. **ค่าไฟ** — คำนวณจาก meter: `(current - previous) × rate`

**ไม่คิด:** ค่าเช่า, ค่าเคเบิล, ค่าที่จอดรถ

### BR-04: Room Rent Rate Validation
```
- rent_rate ≥ 0 (ไม่ติดลบ)
- Type: PricingAmount (Value Object)
- Error: InvalidRentRateError
```

### BR-05: Meter Reading Validation
```
- current_unit ≥ previous_unit (ห้ามลดลง)
- current_unit ≥ 0 (ไม่ติดลบ)
- previous_unit ≥ 0 (ไม่ติดลบ)
- Error: DecreasingUnitError
```

### BR-06: Utility Rates (Water & Electricity)
```
- water_rate ≥ 0 (บาท/หน่วย)
- electricity_rate ≥ 0 (บาท/หน่วย)
- Type: PricingAmount
- Error: InvalidPricingError
```

### BR-07: Optional Charges
```
- cable_price ≥ 0 (default: 0)
- parking_price ≥ 0 (default: 0)
- Type: PricingAmount
- Error: InvalidPricingError
```

### BR-08: Bill Item Uniqueness
```
- ห้ามเพิ่มรายการซ้ำในบิลเดียวกัน
- Check: item.name must be unique per bill
- Error: DuplicateBillItemError
```

### BR-09: Bill Recalculation
```
- Recalculate existing bill → ใช้ Bill.id เดิม
- ลบรายการเก่าด้วย clear_items()
- เพิ่มรายการใหม่
- Bill.id ไม่เปลี่ยน
```

### BR-10: Meter Reading Calculation
```
Formula: (current_unit - previous_unit) × rate = total_charge
Example:
  - current_unit: 450
  - previous_unit: 350
  - rate: 8 บาท/หน่วย
  - total = (450 - 350) × 8 = 100 × 8 = 800 บาท
```

### BR-11: Bill Total Calculation
```
total = sum of all BillItem.amount
Example:
  - Rent: 2800
  - Water: 150
  - Electricity: 800
  - Cable: 60
  - Parking: 500
  - TOTAL: 4310 บาท
```

### BR-12: Tenant ID Association
```
- Bill.tenant_id = Room.tenant_id (nullable)
- Room.occupant_type == TENANT → must have tenant_id
- Room.occupant_type == OWNER → tenant_id = None
```

### BR-13: Required Data for CreateMonthlyBill
```
UC-01 Input validation:
- room: Room (ต้องมี id, room_number, rent_rate, occupant_type)
- billing_period: BillingPeriod (YYYY-MM format)
- pricing: BuildingPricing (water_rate, electricity_rate)
- water_meter: tuple[int, int] = (current, previous) ← ต้องมี!
- electricity_meter: tuple[int, int] = (current, previous) ← ต้องมี!

Error: MissingRequiredDataError ถ้าขาด meter data
```

### BR-14: Cable Exemption
```
- room.cable_exempt == True → ไม่คิดค่าเคเบิล
- room.cable_exempt == False → คิดค่าเคเบิล (ถ้า TENANT)
- Owner ไม่ได้คิดเคเบิลเลย
```

### BR-15: Parking Availability
```
- room.has_parking == True → คิดค่าที่จอดรถ (ถ้า TENANT)
- room.has_parking == False → ไม่คิดค่าที่จอดรถ
- Owner ไม่ได้คิดค่าจอดรถเลย
```

---

## Constraints (ข้อจำกัด)

### Data Constraints
```
1. ทั้ง Rent Rate, Pricing Amount ต้องไม่ติดลบ
2. Meter reading ต้อง >= 0 และ current >= previous
3. Bill items ห้ามซ้ำชื่อภายในบิลเดียวกัน
4. Bill recalculation ต้องใช้ Bill.id เดิม
```

### Business Constraints
```
1. Tenant บังคับต้องมี meter data (water + electricity)
2. Owner คิดเฉพาะน้ำ+ไฟ ไม่คิด rent
3. Cable/Parking ต้องกำหนดตอนสร้าง Room
4. Proration ไม่รองรับ v1 (คิดเต็มเดือน)
```

### Validation Constraints
```
1. ทุก input ต้อง validate ก่อนสร้าง Bill
2. ถ้า meter ไม่ครบ → stop ไม่ให้สร้าง
3. ถ้า meter decreasing → stop ไม่ให้สร้าง
4. Custom errors ต้องใช้ตัวเฉพาะของแต่ละ rule
```

---

## Invariants (สิ่งที่ต้องจริงเสมอ)

```
1. Bill.total ≥ 0 (ยอดรวมไม่ติดลบ)
2. Bill.total = sum(item.amount for item in items)
3. PricingAmount.value ≥ 0 เสมอ
4. BillingPeriod ต้องเป็น YYYY-MM format เท่านั้น
5. Bill items ไม่มีซ้ำชื่อ
6. Room.rent_rate ≥ 0
7. Meter reading: current ≥ previous ≥ 0
```

---

## ข้อสังเกต

- **Version 1 Limitation:** ไม่รองรับ Proration (ผู้เช่าเปลี่ยนกลางเดือน) → คิดเต็มเดือนเสมอ
- **Future Enhancement:** อาจต้องเพิ่ม discount/surcharge mechanism
- **Future Enhancement:** Multi-currency support (ปัจจุบัน hardcoded THB)
