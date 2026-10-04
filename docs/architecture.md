# RentFlow Architecture & Design

RentFlow เป็นแกนระบบ Python สำหรับคำนวณบิลห้องพักรายเดือน โดยจัดโค้ดแยกเป็น Domain, Application และ Infrastructure ตามแนวคิด **Domain-Driven Design (DDD)** และ **Clean Architecture**

---

## 1. โครงสร้างโปรเจกต์ (Project Structure)

โค้ด Python ปัจจุบันแบ่งเป็นเลเยอร์หลักดังนี้:

```text
RentFlow/
├── application/         # Application Services (Orchestration & Use Cases)
├── domain/              # Domain Models, Value Objects, Business Rules & Domain Services
├── infrastructure/      # Infrastructure & Persistence (Repositories, DAOs)
├── presentation/        # พื้นที่สำหรับ Presentation; ยังไม่มี source code ปัจจุบัน
├── custom_errors/       # Custom Exception Classes
├── tests/               # Unit & Integration Tests
└── docs/                # Project Documentation
```

---

## 2. รายละเอียดแต่ละเลเยอร์ (Layer Details)

### A. Domain Layer (`domain/`)
เป็นส่วนของโมเดลและกฎธุรกิจ:
- **`bill.py`**: มีทั้ง `Bill` และ `BillItem`; บิลคำนวณยอดรวมจากรายการด้วย `Decimal`
- **`billing_calculator.py`**: สร้างรายการค่าเช่า ค่าน้ำ ค่าไฟ ค่าเคเบิล และค่าที่จอดรถ โดยใช้ `Decimal`
- **`billing_period.py`**: Value Object สำหรับตรวจรูปแบบรอบบิล `YYYY-MM`
- **`billing_rules.py`**: เลือกรายการที่คิดตามประเภทผู้พักและค่าตั้งค่าของห้อง
- **`building_pricing.py`**: อัตราค่าน้ำ ค่าไฟ ค่าเคเบิล และค่าที่จอดรถ
- **`meter_unit.py` & `units_vo.py`**: Value Objects สำหรับหน่วยมิเตอร์และจำนวนเงิน
- **`room.py`, `tenant.py` & `occupant_type.py`**: ข้อมูลห้อง ผู้เช่า และประเภทผู้พัก

### B. Application Layer (`application/`)
ทำหน้าที่ประสานงานกับ Domain:
- **`create_monthly_bill.py`**: `CreateMonthlyBill` ตรวจสอบข้อมูลมิเตอร์ ใช้กฎและเครื่องคำนวณเพื่อสร้างหรือคำนวณรายการใหม่ใน `Bill` แล้วคืน `Bill` ให้ผู้เรียก; ปัจจุบันไม่ได้อ่านข้อมูลจาก Repository หรือบันทึกบิลเอง

### C. Infrastructure Layer (`infrastructure/`)
มีสัญญา Repository และการจัดเก็บบิลแบบ in-memory:
- **`repository.py`**: สัญญา Repository ทั่วไป
- **`repositories/bill_repository.py`**: สัญญาสำหรับค้นหาบิลตามห้องและรอบบิล
- **`repositories/bill_dao.py`**: `BillDAO` เก็บบิลในหน่วยความจำ (`dict`) พร้อมตรวจ version; ยังไม่ใช่ฐานข้อมูลถาวร

### D. Presentation Layer (`presentation/`)
โฟลเดอร์ยังไม่มีไฟล์ source code ของ UI หรือ API; จึงยังไม่มีหน้าจอหรือ endpoint ที่ใช้งานได้ในปัจจุบัน

---

## 3. จุดเด่นทางเทคนิค (Technical Highlights)
1. **Precision Calculation**: ใช้ `decimal.Decimal` คำนวณมูลค่าเงิน
2. **Test Coverage**: มี Unit Tests และ Integration Tests ใน `tests/` สำหรับ Domain, use case และ repository
3. **Domain Errors**: ใช้ Custom Exceptions เช่น `MissingRequiredDataError` เมื่อข้อมูลมิเตอร์ไม่ครบ

> **สถานะปัจจุบัน:** โปรเจกต์เป็นแกน Python สำหรับคำนวณบิล ยังไม่มี Frontend, REST API, Docker หรือฐานข้อมูลถาวร
