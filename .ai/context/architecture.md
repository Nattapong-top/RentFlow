# Architecture — RentFlow

## สถาปัตยกรรมรวม

```
┌──────────────────────────────────────────────────────────────┐
│                    Presentation Layer                        │
│    (Future: FastAPI, Click CLI, Web UI)                     │
│    ยังไม่ implement                                          │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│                   Application Layer                          │
│  ✅ create_monthly_bill.py — UC-01: Create Monthly Bill    │
│     Responsibilities:                                        │
│     - Orchestrate ทั้ง flow                                 │
│     - Validate input (room, billing_period, pricing, meter) │
│     - Delegate to Domain Services                           │
│     - Return Bill aggregate                                 │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│                     Domain Layer                             │
│                                                              │
│  📦 Value Objects (Immutable, Frozen)                       │
│  ├── BillingPeriod(value: str) — YYYY-MM format            │
│  ├── BuildingPricing(water_rate, electricity_rate, ...)    │
│  ├── Unit(value: Decimal) — meter units                    │
│  └── PricingAmount(value: Decimal) — money amounts         │
│                                                              │
│  🏠 Entities (Mutable, with identity)                       │
│  ├── Tenant(id, name)                                      │
│  ├── Room(id, room_number, rent_rate, occupant_type, ...)  │
│  ├── BillItem(name, amount, description)                   │
│  └── Bill(id, room_id, period, items, tenant_id)           │
│                                                              │
│  ⚙️ Domain Services (Stateless, Business Logic)             │
│  ├── BillingRules — ตัดสินรายการตาม OccupantType         │
│  ├── BillingCalculator — คำนวณแต่ละรายการ                  │
│  └── MeterReadingUnit — คำนวณหน่วยมิเตอร์                   │
│                                                              │
│  ❌ Custom Errors (Domain-specific exceptions)              │
│  ├── InvalidBillingPeriodError                             │
│  ├── InvalidRentRateError                                  │
│  ├── InvalidPricingError                                   │
│  ├── DuplicateBillItemError                                │
│  ├── DecreasingUnitError                                   │
│  └── MissingRequiredDataError                              │
│                                                              │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│                Infrastructure Layer                          │
│    (Future: Database, File I/O, External APIs)             │
│    ยังไม่ implement                                          │
└──────────────────────────────────────────────────────────────┘
```

---

## Layering Rules

### Dependency Rule (The Clean Architecture)
```
                    Domain
                      ↑
    Application → Domain
                      ↑
    Infrastructure → Domain (via interfaces)

สรุป:
- Domain ไม่มี dependency ภายนอก (Pure Logic)
- Application depend on Domain
- Infrastructure depend on Domain (via Repository pattern)
```

### ห้ามทำ:
```
❌ Domain depend on Application
❌ Domain depend on Infrastructure
❌ Application depend on Infrastructure directly
❌ Business logic ใน Application/Infrastructure
```

### ต้องทำ:
```
✅ Domain: Pure business logic, no framework
✅ Application: Orchestrate, validate input, call Domain
✅ Infrastructure: Implement Repository pattern, data persistence
```

---

## Component Responsibilities

| Component | Responsibility | ห้ามทำ |
|-----------|---|---|
| **BillingPeriod** VO | Validate format YYYY-MM | Allow invalid dates |
| **BuildingPricing** VO | Store & coerce pricing rates | Allow negative values |
| **PricingAmount** VO | Validate non-negative money | Allow negative amounts |
| **Unit** VO | Validate non-negative units | Allow negative units |
| **Tenant** Entity | Hold tenant identity | Business logic |
| **Room** Entity | Hold room properties, rent_rate | Calculate charges |
| **BillItem** Entity | Hold line item data | Calculation |
| **Bill** Aggregate | Container for items, calculate total | Apply rules |
| **BillingRules** Service | Decide which items to charge | Calculate amounts |
| **BillingCalculator** Service | Calculate amounts | Decide which to charge |
| **MeterReadingUnit** Service | Calculate meter-based charges | Validation only |
| **CreateMonthlyBill** Service | Orchestrate UC-01 flow | Business rules |

---

## Data Flow — UC-01: Create Monthly Bill

```
Input:
  room: Room
  billing_period: BillingPeriod
  pricing: BuildingPricing
  water_meter: (current, previous)
  electricity_meter: (current, previous)
                              ↓
        ┌─────────────────────┴──────────────────────┐
        ↓                                             ↓
   VALIDATE INPUT                            CHECK REQUIRED DATA
   - room ≠ None                            - meter tuples not empty
   - period format YYYY-MM                  - raise MissingRequiredDataError
   - pricing amounts ≥ 0                       if missing
        ↓                                             ↓
        └─────────────────────┬──────────────────────┘
                              ↓
                    CREATE OR CLEAR BILL
                    (existing_bill? → clear_items())
                              ↓
        ┌─────────────────────┴──────────────────────┐
        ↓                                             ↓
   CALL BillingRules.should_charge_X               CALL BillingCalculator.create_X_item
   for each charge type                           with pricing, room data
   (rent, water, electricity, cable, parking)
        ↓                                             ↓
   Decide: YES/NO                                Calculate: amount, description
   based on:                                  based on:
   - room.occupant_type                       - room properties
   - room.cable_exempt                        - meter readings
   - room.has_parking                         - rates
        ↓                                             ↓
        └─────────────────────┬──────────────────────┘
                              ↓
                       ADD ITEMS TO BILL
                       bill.add_item(item)
                       (check duplicate names)
                              ↓
                        RETURN BILL
                (Bill.total auto-calculated)
```

---

## Design Patterns Used

### 1. Domain-Driven Design (DDD)
- **Entities** — Objects with identity (Tenant, Room, Bill)
- **Value Objects** — Immutable objects defined by value (BillingPeriod, PricingAmount)
- **Aggregates** — Bill is root, BillItem is part
- **Domain Services** — Stateless logic (BillingRules, BillingCalculator)
- **Custom Errors** — Domain-specific exceptions

### 2. Layered Architecture
```
Presentation ← Application ← Domain → Infrastructure
                                        (via Repository)
```

### 3. Repository Pattern (Future)
```
interface IRepository<T>:
  save(entity: T)
  find_by_id(id: str) → T
  
BillRepository: IRepository[Bill]
  save(bill) → DB insert/update
  find_by_id(bill_id) → query DB
```

### 4. Dependency Injection (Pydantic)
```python
CreateMonthlyBill:
  __init__(self, rules=None, calculator=None):
    self.rules = rules or BillingRules()
    self.calculator = calculator or BillingCalculator()
```

### 5. Value Object Pattern
```python
class PricingAmount(BaseModel):
  value: Decimal  # Validated ≥ 0
  # Immutable (frozen=True)
```

---

## Data Types & Validation Strategy

### Validation Layers
```
1. Pydantic Model Level
   @field_validator("rent_rate", mode="before")
   → Coerce input → PricingAmount

2. Value Object Level
   PricingAmount.__init__
   → Validate value ≥ 0
   → Raise InvalidPricingError if fail

3. Entity Level
   Room.__init__
   → Validate room_number not empty
   → Validate rent_rate is PricingAmount
   → Raise InvalidRoomError if fail

4. Domain Service Level
   BillingRules.should_charge_rent()
   → Check occupant_type == TENANT
```

### Error Handling Strategy
```
Each domain rule has dedicated Custom Error:
- Invalid input → Custom error raised immediately
- Cannot continue → Raise error, don't hide it
- Caller (Application) → Catch & handle

Example:
  try:
    room = Room(id="", room_number="101", rent_rate=2800)
  except InvalidRoomError as e:
    log("Room validation failed: " + str(e))
    raise
```

---

## Testability

### Layering supports isolation:
```
✅ Unit test Domain: No DB, no framework
✅ Unit test Value Objects: Pure logic
✅ Integration test Application: Mock Domain
✅ E2E test (Future): Real DB, real Application
```

### Current Test Structure:
```
tests/
├── test_bill.py (Aggregate)
├── test_billing_calculator.py (Domain Service)
├── test_billing_period.py (VO)
├── test_billing_rules.py (Domain Service)
├── test_building_pricing.py (VO)
├── test_create_monthly_bill.py (Application Service)
├── test_meter_units.py (Domain Service)
├── test_occupant_type.py (Enum)
├── test_room.py (Entity)
├── test_tenant.py (Entity)
└── test_unit_vo.py (VO)
```

---

## Scalability Notes

### Current Design supports:
```
✅ Multi-building: Pass different BuildingPricing per building
✅ Different rate structures: BuildingPricing is flexible
✅ Proration (Future): Extend BillingCalculator
✅ Discount/Surcharge: Add to BillItem creation
✅ API/CLI: Application Service is framework-agnostic
```

### Future Infrastructure Integration:
```
Domain → doesn't change
Application → doesn't change
Presentation → Add FastAPI/Click

Add Repository pattern:
  interface IBillRepository
  class BillRepository(impl IBillRepository)
    def save(bill) → database insert
    def find(period) → database query
```
