# Glossary — Domain & Technical Terms

## Domain Terms (Business)

### Occupant / ผู้อยู่อาศัย
คนที่อยู่ในห้อง แบ่งเป็น 2 ประเภท:
- **TENANT** — ผู้เช่า (renting from owner)
- **OWNER** — เจ้าของ (building owner/operator)

### Billing Period / รอบบิล
ช่วงเวลาที่คิดค่า ใช้รูปแบบ YYYY-MM (e.g., 2026-09 = เดือนกันยายน 2026)

### Meter Reading / การอ่านมิเตอร์
ตัวเลขบนมิเตอร์ (water meter, electricity meter)
- **Current** — ค่าที่อ่านได้ในรอบนี้
- **Previous** — ค่าที่อ่านได้ในรอบที่แล้ว
- **Consumption** = Current - Previous

### Bill Item / รายการในบิล
หนึ่งรายการค่าใช้จ่ายในบิล (e.g., "ค่าน้ำ", "ค่าไฟ")

### Building Pricing / ราคาของอาคาร
อัตราค่าใช้จ่ายทั้งอาคาร (ไม่แตกต่างต่อห้อง):
- water_rate — บาท/หน่วยน้ำ
- electricity_rate — บาท/หน่วยไฟ
- cable_price — บาท/เดือน
- parking_price — บาท/เดือน

### Room / ห้อง
หนึ่งห้องพัก มีข้อมูล:
- id, room_number
- rent_rate (ค่าเช่า)
- occupant_type (TENANT/OWNER)
- cable_exempt (ห้ามห้องอื่นคิดเคเบิล?)
- has_parking (ห้องมีที่จอดรถไหม?)

### Rent Rate / ค่าเช่า
จำนวนเงินค่าเช่าห้องรายเดือน (ไม่เกี่ยวกับการใช้)

### Utility Charges / ค่าสาธารณูปโภค
ค่าที่ขึ้นกับการใช้:
- Water — ค่าน้ำ
- Electricity — ค่าไฟ

### Optional Charges / ค่าเสริม
ค่าที่อาจมีหรือไม่มี ขึ้นกับห้อง:
- Cable — ค่าเคเบิลทีวี
- Parking — ค่าที่จอดรถ

### Proration / การคิดตามสัดส่วน
ไม่รองรับใน v1 — คิดเต็มเดือนเสมอ (Future feature)

---

## Technical Terms (Code)

### Value Object / วัตถุค่า
Object immutable ที่ไม่มี identity หรือ lifecycle:
- **BillingPeriod** — "2026-09"
- **BuildingPricing** — rates & prices
- **PricingAmount** — 2800 บาท
- **Unit** — 100 หน่วย

ใน Pydantic: `ConfigDict(frozen=True)`

### Entity / อิเจนทิตี
Object ที่มี identity เฉพาะตัว ไม่ immutable:
- **Tenant** — ผู้เช่า ID=T001
- **Room** — ห้อง ID=R001
- **Bill** — บิล ID=BILL-R001-2026-09
- **BillItem** — รายการในบิล

ใน Pydantic: `ConfigDict(validate_assignment=True)`

### Aggregate / รวม
Entity ที่เป็น root กับ sub-entities ที่สัมพันธ์กัน:
- **Bill** (root) ← containers ← **BillItem** (sub-entities)

### Domain Service / บริการโดเมน
Class stateless ที่มี business logic:
- **BillingRules** — ตัดสินรายการ
- **BillingCalculator** — คำนวณจำนวนเงิน
- **MeterReadingUnit** — คำนวณหน่วยมิเตอร์

### Repository Pattern / แพทเทิร์นเก็บข้อมูล
(Future) Interface สำหรับ persistence:
```python
class IBillRepository:
  save(bill) → persist to DB
  find_by_id(id) → query from DB
```

### Pydantic Model / โมเดล
Schema validation & data modeling ใน Python:
- `BaseModel` — base class
- `@field_validator` — custom validation
- `ConfigDict` — model config

### Validation Mode / โหมด validation
- `mode="before"` — validate ก่อน coerce เป็น type ที่ต้องการ

### Coercion / การบังคับประเภท
เปลี่ยนประเภท input เป็น target type:
```python
# Input: rent_rate=2800 (int)
# Coerce to: PricingAmount(value=Decimal("2800"))
```

### Immutable / ไม่เปลี่ยนแปลง
Object ที่ไม่สามารถเปลี่ยนค่าได้หลังสร้าง:
```python
pricing = BuildingPricing(water_rate=19)
pricing.water_rate = 20  # ❌ ValidationError
```

### Frozen / ตรึง
ใน Pydantic: VO ต้องตรึงหมดหลังสร้าง

### Custom Error / ข้อผิดพลาดเฉพาะ
Exception class ที่ inherit จาก `DomainErrors`:
- InvalidBillingPeriodError
- InvalidPricingError
- DecreasingUnitError
- etc.

### Decimal / ตัวเลขทศนิยม
ไม่ใช้ `float` → ใช้ `Decimal` สำหรับเงิน
```python
from decimal import Decimal
price = Decimal("2800.00")  # ✅
price = 2800.0  # ❌ float is imprecise
```

### Orchestration / การประสานงาน
Application Service ที่เรียก Domain Services:
```python
class CreateMonthlyBill:
  def execute(self, room, period, pricing, ...):
    rules.should_charge_X()  # ask
    calculator.create_X_item()  # calculate
    bill.add_item()  # build
```

### Unit Testing / การทดสอบหน่วย
Test ที่ test 1 component โดยลำพัง:
- `test_billing_period.py` → test BillingPeriod VO only
- `test_room.py` → test Room Entity only

### Integration Testing / การทดสอบการรวม
Test ที่ test หลาย components พร้อมกัน:
- `test_create_monthly_bill.py` → Application + Domain

### Type Annotation / อธิบายประเภท
ระบุประเภท argument & return:
```python
def create_rent_item(self, room: Room) -> BillItem:
  ...
```

### Pydantic ConfigDict / การกำหนด config
```python
model_config = ConfigDict(
  frozen=True,  # immutable
  validate_assignment=True,  # validate on assignment
)
```

### Validator / ตัวตรวจสอบ
Function ที่ validate field:
```python
@field_validator("rent_rate", mode="before")
@classmethod
def validate_rent_rate(cls, v):
  # v is input value
  return PricingAmount(value=v)
```

---

## Architectural Terms

### Layered Architecture / สถาปัตยกรรมชั้น
```
Presentation ← Application ← Domain → Infrastructure
```
แต่ละชั้นมี responsibility แตกต่าง

### Dependency Rule / กฎ dependency
- Domain → ไม่มี dependency ภายนอก
- Application → depend Domain
- Infrastructure → depend Domain (via Repository)

### Clean Architecture / Clean Arch
Architecture ที่ main business logic (Domain) ไม่ขึ้นกับ framework

### Separation of Concerns / แยกกิจการ
แต่ละ class ทำหน้าที่เดียว:
- Validation → VO/Entity validators
- Calculation → Domain Services
- Orchestration → Application Services

### Testability / ความทดสอบได้
Code ที่ง่ายต่อการเขียน unit test

### DRY (Don't Repeat Yourself) / ไม่ซ้ำการเขียน
Avoid code duplication:
- shared logic → Domain Service
- shared validation → VO/Entity

---

## Git & Workflow Terms

### feat/ branch / branch feature
Branch สำหรับ feature/refactor ใหม่:
- `feat/remove-dead-code`
- `feat/fill-ai-context-docs`

### PR / Pull Request
ส่งขอ merge code ขึ้น GitHub

### Auto-Merge / merge อัตโนมัติ
PR จะ merge เองเมื่อ:
- GitHub Actions ✅ PASS
- Branch protection ตั้งค่าแล้ว

### CI/CD Pipeline / ไปป์ไลน์
Automated build, test, deploy:
- GitHub Actions → run `make all-tests`

---

## Metric Terms

### Test Coverage / ความครอบคลุมการทดสอบ
Percentage ของ code ที่ต้อง test
- Current: Domain layer ≈ 100%
- Target: 80%+ across all layers

### Cyclomatic Complexity / ความซับซ้อนวนซ้ำ
จำนวน independent paths ใน code
- Lower = simpler = more testable

---

## Document Abbreviations

| Abbr | Full | ความหมาย |
|---|---|---|
| VO | Value Object | วัตถุค่า |
| UC-01 | Use Case 1 | Use case ที่ 1 (Create Monthly Bill) |
| BR-01 | Business Rule 1 | business rule ที่ 1 |
| AF-01 | Application Flow 1 | flow ใน application |
| TENANT | | ผู้เช่า |
| OWNER | | เจ้าของ |
| YYYY-MM | | Format ปี-เดือน |
| DB | Database | ฐานข้อมูล |
| API | | Application Programming Interface |
| CLI | | Command Line Interface |
| MVP | Minimum Viable Product | ผลิตภัณฑ์ขั้นต่ำที่ใช้ได้ |
| v1 | Version 1 | เวอร์ชันที่ 1 |
| Future | | ทำในเวอร์ชันต่อไป |
