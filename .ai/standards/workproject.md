# RentFlow — Project Workflow & Specifications

## 📌 Overview

แอปคำนวณบิลห้องพักรายเดือน (Monthly Rent Billing System)

| รายการ | รายละเอียด |
|---|---|
| Repository | https://github.com/Nattapong-top/RentFlow |
| Language | Python ≥ 3.13 |
| Framework | Pydantic v2 |
| Test | pytest |
| Lint | ruff + black |
| Type Check | mypy |

---

## 🌿 Branch Strategy

```text
main
 └── feat/<feature-name>
```

| Branch | วัตถุประสงค์ |
|---|---|
| `main` | Production-ready code เท่านั้น (ทุก commit ต้องผ่าน GitHub Actions) |
| `feat/xxx` | Feature branch แต่ละชิ้น (micro atomic, สร้างจาก main) |

---

## 🔄 Workflow ต่อ 1 Feature

ใช้ GitHub PR + Auto-Merge (GitHub Actions จะ merge เองเมื่อ Actions ✅ pass)

```text
1.  git pull origin main                 # sync latest main
2.  git checkout -b feat/<name>          # สร้าง feature branch จาก main
3.  # ... implement + test (TDD)
4.  make all-tests                       # ต้องผ่านทั้งหมดก่อน commit
5.  git add <files>
6.  git commit -m "feat: <message>"      # atomic commit
7.  git push origin feat/<name>          # push feature branch ขึ้น GitHub
8.  # สร้าง Pull Request บน GitHub
9.  # รอ GitHub Actions ✅ pass
10. # GitHub Auto-Merge จะ merge เมื่อ Actions ✅
11. git checkout main
12. git pull origin main                 # sync commit ที่ถูก merge
13. git branch -d feat/<name>            # ลบ local branch
14. git push origin --delete feat/<name> # ลบ remote branch
```

> **กฎเหล็ก:** 
> - `make all-tests` ต้องผ่านทั้งหมดก่อน commit เสมอ
> - PR ต้องผ่าน GitHub Actions ก่อน merge
> - Auto-Merge ตั้งแล้ว → PR จะ merge เองเมื่อ Actions ✅

---

## 📦 Feature Implementation Order

เรียงตาม dependency (ทำก่อน-หลัง)

### Layer 1 — Value Objects (ไม่มี dependency)
1. `BillingPeriod` — validate format `YYYY-MM`
2. `BuildingPricing` — water_rate, electricity_rate, cable_price, parking_price (validate ค่าติดลบ)
3. `OccupantType` enum — `TENANT` / `OWNER`

### Layer 2 — Entities
4. `Tenant(id, name)`
5. `Room(id, room_number, rent_rate, occupant_type)` (validate rent_rate ≥ 0)
6. `BillItem`, `Bill` + `calculate_total()` (add item, sum total)

### Layer 3 — Domain Services
7. `BillingRules` — ตัดสินรายการตาม OccupantType (Tenant ได้ครบ 5 รายการ, Owner ได้แค่น้ำ+ไฟ)
8. `BillingCalculator` — คำนวณแต่ละรายการ (น้ำ, ไฟ, ค่าเช่า, cable, parking)

### Layer 4 — Application Service
9. `CreateMonthlyBill` — orchestrate ทั้ง flow ทั้ง Tenant และ Owner

---

## 🏗️ Architecture Overview

```text
API / UI
    ↓
Application
└── CreateMonthlyBill          ← orchestrates use case

Domain
├── Value Objects
│   ├── BillingPeriod          ← YYYY-MM format
│   ├── BuildingPricing        ← water/electricity/cable/parking rates
│   ├── Unit                   ← meter unit
│   └── OccupantType           ← TENANT / OWNER enum
│
├── Entities
│   ├── Room                   ← id, room_number, rent_rate, occupant_type
│   ├── Tenant                 ← id, name
│   ├── BillItem               ← label, amount
│   └── Bill                   ← bill_id, room, period, items, total
│
└── Domain Services
    ├── MeterReadingUnit       ← คำนวณหน่วย meter
    ├── BillingRules           ← ตัดสินรายการใน Bill ตาม OccupantType
    └── BillingCalculator      ← คำนวณจำนวนเงินแต่ละรายการ
```

---

## 📋 Business Rules สำคัญ

| ID | Business Rule |
|---|---|
| BR-01 | Billing Period ใช้รูปแบบ `YYYY-MM` เท่านั้น |
| BR-02 | Tenant คิด: Rent, Water, Electricity, Cable, Parking (ถ้ามี) |
| BR-03 | Owner คิด: Water, Electricity เท่านั้น (ไม่คิด Rent, Cable, Parking) |
| BR-04 | Water / Electricity คำนวณจาก `(Current - Previous) × Rate` |
| BR-05 | Current Meter < Previous Meter → หยุดทันที แจ้งให้แก้ Source Data |
| BR-06 | ถ้า Meter ไม่ครบ → หยุด ไม่ตีเป็น 0 อัตโนมัติ |
| BR-07 | Tenant เปลี่ยนกลางเดือน → คิดเต็มเดือน (v1 ไม่ทำ Proration) |
| BR-08 | Recalculate Bill → ใช้ Bill ID เดิม ไม่สร้าง ID ใหม่ |

---

## 🛠️ Make Commands

```bash
make check      # lint (ruff) + format check (black)
make fix        # auto-fix lint + format
make test       # run pytest
make coverage   # pytest with coverage
make typecheck  # mypy type check
make all-tests  # check + fix + test + diff + status
```
