# Development Workflow (Micro Development) - RentFlow

Every feature must follow this workflow.

**หลักการสำคัญ**: ONE behavior at a time — ทำทีละพฤติกรรมเดียว ไม่รีบ

## Phase 1 - Understand 🤔

### Checklist
- [ ] อ่าน requirement
- [ ] ถามคำถามทุกข้อที่ไม่แน่ใจ
- [ ] สรุปความเข้าใจ
- [ ] **รอ confirmation** ✋

### Steps
1. **Requirement** - อ่านและทำความเข้าใจ requirement บิลห้องพักรายเดือน
2. **Ask Questions** - ห้ามเดา business rule ถามจนเข้าใจ 100%
3. **Requirement Summary** - สรุปความเข้าใจ (Feature, Business Rules, ผลลัพธ์)
✋ **รอ confirmation ก่อนทำต่อ**

---

## Phase 2 - Design 📐

### Checklist
- [ ] อธิบาย architecture impact (Value Objects / Entities / Domain Services / Application)
- [ ] ระบุไฟล์ที่ต้องแก้ (เช่น `domain/`, `application/`, `tests/`)
- [ ] เสนอทางเลือก (ถ้ามี)
- [ ] **รอ approval** ✋

---

## Phase 3 - Micro Development 🔴🟢

**Implement ONE business behavior at a time.**

### Step A: Write ONE Failing Test (RED)
- เขียน 1 test ที่ represent พฤติกรรมเดี่ยว (เช่น test validation ค่าติดลบ, test เงื่อนไข Owner vs Tenant)
- ทุก validation rule ใหม่ต้องมี **Custom Error** เฉพาะของตัวเองใน `custom_errors/custom_errors.py`
- รัน test เดี่ยวให้ยืนยันว่า RED 🔴

### Step B: Explain Why Test Fails
- อธิบายว่าทำไม test ถึง fail และตรงกับ business rule ไหน (เช่น BR-02, BR-03)
- ✋ **รอ approval ก่อนเขียนโค้ด**

### Step C: Implement ONLY Enough Code to Pass (GREEN)
- เขียนโค้ดให้ test pass (minimal code, no premature refactoring)
- รัน test ให้ยืนยันว่า GREEN 🟢

### Step D: Self Review
- สรุปไฟล์ที่แก้ เหตุผล และ side effects
- ✋ **รอ approval ก่อนทำ behavior ถัดไป**

---

## Phase 4 - Verification ✅

- รัน `make all-tests`
- หาก test เดิม fail ให้ใช้ Decision Tree วิเคราะห์ (Business rule เปลี่ยน / Implementation ผิด / Test ผิด) ห้ามแก้ test มั่วซั่ว

---

## Phase 5 - Refactor ♻️

- Refactor เฉพาะตอนที่ tests GREEN หมดแล้ว
- ห้ามเปลี่ยน business logic ในขั้นตอนนี้
- รัน `make all-tests` ซ้ำเพื่อยืนยัน

---

## Phase 6 - Present Result 📊

- สรุป behaviors ที่ทำ, tests ที่เพิ่ม, custom errors, files modified, risks, และ next step

---

## General Rules & Anti-Patterns

1. **Never guess business rules** — ถามป๋าจนกว่าจะชัดเจน 100%
2. **Never modify multiple business behaviors in one step** — ทำทีละ behavior เดียว
3. **Every new validation rule must define its own dedicated Custom Error**
4. **No Big Bang implementation** — ห้ามเขียนรวดเดียวจบ
5. **Always wait for approval** — รอ approval จากป๋าก่อนไปขั้นถัดไป
