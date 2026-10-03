# Project Overview: RentFlow

## สถานะ

- ✅ **เสร็จแล้ว:** Domain layer, Value Objects (PricingAmount), Entity (Room, Bill, Tenant), Domain Services (BillingRules, BillingCalculator), Application Service (CreateMonthlyBill), Tests (63/63), CI/CD (GitHub Actions)
- 🚧 **กำลังทำ:** Documentation (`.ai/context/` เอกสาร)
- ⏳ **รอทำ:** Infrastructure layer (Database), Presentation layer (API/CLI)

---

## ภาพรวมโปรเจค

**ชื่อโปรเจค:** RentFlow — Monthly Rent Billing System

**จุดประสงค์:** ระบบคำนวณและสร้างบิลรายเดือนสำหรับหอพัก/อพาร์ตเมนต์ โดยรองรับการคิดค่าใช้จ่ายหลายประเภท (ค่าเช่า, ค่าน้ำ, ค่าไฟ, ค่าเคเบิล, ค่าที่จอดรถ) และจำแนกการคิดตามประเภทผู้อยู่อาศัย (Tenant vs Owner)

**ผู้ใช้หลัก:** Property managers, building administrators

---

## Tech Stack

| Layer | Technology | เหตุผล |
|-------|-----------|--------|
| Language | Python 3.13 | Modern, strong typing support, good for domain modeling |
| Framework | Pydantic v2 | Schema validation, data modeling, strong validation support |
| Testing | pytest | Industry standard, excellent plugin ecosystem |
| Linting | ruff + black | Fast, modern Python formatter + linter |
| Type Check | mypy | Static type checking |
| CI/CD | GitHub Actions | Auto-Merge PR เมื่อ tests pass |
| Package Manager | uv | Fast Python package manager |

---

## โครงสร้างโปรเจค

```
RentFlow/
├── .ai/                          ← AI documentation & context
│   ├── context/
│   │   ├── project.md           ← This file
│   │   ├── domain_rules.md      ← Business rules
│   │   ├── architecture.md      ← Design patterns & layers
│   │   ├── pipeline.md          ← Main workflow
│   │   └── glossary.md          ← Domain & tech terms
│   ├── memory/
│   │   ├── changelog.md         ← Version history
│   │   ├── decisions.md         ← Why we chose X over Y
│   │   ├── lessons_learned.md   ← Process improvements
│   │   └── known_issues.md      ← Known bugs/limitations
│   ├── standards/
│   │   ├── workflow.md          ← Development workflow (Micro Dev, TDD)
│   │   ├── workproject.md       ← Git workflow, branch strategy, feature order
│   │   ├── coding_style.md      ← Code style guidelines
│   │   ├── tdd.md               ← Test-Driven Development rules
│   │   └── git.md               ← Git commit conventions
│
├── domain/                        ← Domain layer (business logic)
│   ├── bill.py                  ← Aggregate: Bill + BillItem
│   ├── billing_calculator.py    ← Domain Service: คำนวณแต่ละรายการ
│   ├── billing_period.py        ← Value Object: รอบบิล (YYYY-MM)
│   ├── billing_rules.py         ← Domain Service: ตัดสินรายการตาม OccupantType
│   ├── building_pricing.py      ← Value Object: ราคาของอาคาร
│   ├── meter_unit.py            ← Entity: คำนวณหน่วยมิเตอร์
│   ├── occupant_type.py         ← Enum: TENANT / OWNER
│   ├── room.py                  ← Entity: ห้อง
│   ├── tenant.py                ← Entity: ผู้เช่า
│   └── units_vo.py              ← Value Objects: Unit, PricingAmount
│
├── application/                   ← Application layer (orchestration)
│   └── create_monthly_bill.py   ← Use Case: UC-01 Create Monthly Bill
│
├── custom_errors/                 ← Custom domain errors
│   └── custom_errors.py         ← Error hierarchy
│
├── tests/                         ← Test suite
│   ├── test_bill.py
│   ├── test_billing_calculator.py
│   ├── test_billing_period.py
│   ├── test_billing_rules.py
│   ├── test_building_pricing.py
│   ├── test_create_monthly_bill.py
│   ├── test_meter_units.py
│   ├── test_occupant_type.py
│   ├── test_room.py
│   ├── test_tenant.py
│   └── test_unit_vo.py
│
├── .github/workflows/
│   └── ci.yml                   ← GitHub Actions: lint, test, auto-merge PR
│
├── pyproject.toml               ← Python project config
├── Makefile                     ← Build commands
├── AGENTS.md                    ← AI workflow rules
└── README.md                    ← Project README

```

---

## สถานะการพัฒนา

### ✅ เสร็จแล้ว

| Component | สถานะ | Tests |
|-----------|-------|-------|
| `BillingPeriod` VO | ✅ Done | 10 tests |
| `BuildingPricing` VO | ✅ Done | 7 tests |
| `Unit` / `PricingAmount` VO | ✅ Done | 2 tests |
| `OccupantType` Enum | ✅ Done | 2 tests |
| `Tenant` Entity | ✅ Done | 5 tests |
| `Room` Entity | ✅ Done | 8 tests |
| `BillItem` / `Bill` Aggregate | ✅ Done | 6 tests |
| `BillingRules` Domain Service | ✅ Done | 3 tests |
| `BillingCalculator` Domain Service | ✅ Done | 7 tests |
| `MeterReadingUnit` Domain Service | ✅ Done | 5 tests |
| `CreateMonthlyBill` Application Service | ✅ Done | 6 tests |

**Total: 63 tests ✅ PASS**

### 🚧 กำลังทำ

| งาน | สถานะ | หมายเหตุ |
|-----|-------|----------|
| `.ai/context/` documentation | 🚧 In Progress | กรอก 5 ไฟล์ (project, domain_rules, architecture, pipeline, glossary) |

### ⏳ รอทำ

| งาน | สถานะ | หมายเหตุ |
|-----|-------|----------|
| Infrastructure layer (DB persistence) | ⏳ Planned | Repository pattern, data mapper |
| Presentation layer (API/CLI) | ⏳ Planned | FastAPI or Click CLI |
| E2E tests | ⏳ Planned | Integration with infrastructure |
| Documentation (user guide) | ⏳ Planned | API docs, setup guide |

---

## สิ่งที่ยังค้างอยู่

- [ ] กรอก `.ai/context/domain_rules.md` — Business rules
- [ ] กรอก `.ai/context/architecture.md` — Design patterns
- [ ] กรอก `.ai/context/pipeline.md` — Main workflow
- [ ] กรอก `.ai/context/glossary.md` — Domain terms
- [ ] ลบ `domain/billing_rent.py` ✅ Done (removed in feat/remove-dead-code)
- [ ] Infrastructure layer (Repository pattern, DB)
- [ ] Presentation layer (API or CLI)
