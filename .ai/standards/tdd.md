# Test Driven Development

Workflow

RED

↓

GREEN

↓

REFACTOR

---

### กฎสำคัญ (Strict Rules)

1. **ห้ามลบเทสต์เดิม:** ในการเพิ่มเทสต์ใหม่เพื่อทดสอบกรณีเพิ่มเติม (เช่น Happy Path, Sad Path) **ห้ามลบเทสต์ที่มีอยู่เดิม** ให้สร้างเทสต์ใหม่ต่อท้ายหรือแยกไฟล์เทสต์แทน
2. **Bug ทุกตัว:** ต้องมี 1 Test ที่จำลองปัญหาก่อนเริ่มแก้ไขเสมอ
3. **ทุก Feature ใหม่:** ต้องมี Unit Test และ Integration Test (ถ้าจำเป็น) ก่อน Merge
4. **Custom Error:** ทุก Feature ใหม่หรือเงื่อนไขการ Validation ต้องมีการกำหนด Custom Error เฉพาะทางเสมอ เพื่อให้แจ้งปัญหาได้ตรงจุด (อ้างอิง `domain/custom_error/domain_error.py`)

---

ทุก Feature ใหม่ต้องผ่านวงจร TDD และห้ามละเลยการตรวจสอบเทสต์ที่มีอยู่เดิม