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
 └── develop
      └── feat/<feature-name>
```

| Branch | วัตถุประสงค์ |
|---|---|
| `main` | Production-ready code เท่านั้น |
| `develop` | Integration branch รวม feature ที่ผ่าน test แล้ว |
| `feat/xxx` | Feature branch แต่ละชิ้น (micro atomic) |

---

## 🔄 Workflow ต่อ 1 Feature

```text
1.  git checkout -b feat/<name> develop   # สร้าง feature branch
2.  เขียน test ก่อน (TDD)
3.  implement ให้ test ผ่าน
4.  make check                            # lint + format
5.  make test                             # ทุก test ต้องผ่านก่อน commit
6.  git add .
7.  git commit -m "feat: <message>"       # micro atomic commit
8.  git push -u origin feat/<name>        # push feature branch ขึ้น GitHub
9.  git checkout develop
10. git merge feat/<name> --no-ff         # merge กลับ develop
11. git push origin develop               # push develop ที่ merge แล้ว
12. git branch -d feat/<name>             # ลบ local branch
13. git push origin --delete feat/<name>  # ลบ remote branch
```

> **กฎเหล็ก:** `make test` ต้องผ่านทุก test **ก่อน** commit เสมอ

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
