# Pipeline Flow

## Standard Flow ของโปรเจค

> อธิบาย flow การทำงานหลักของโปรเจค ตั้งแต่ input ถึง output

```
┌──────────────┐
│ 1. Input     │ ← [รับข้อมูลจากที่ไหน: File, API, DB, etc.]
└──────────────┘
       ↓
┌──────────────┐
│ 2. Parse     │ ← [แปลงข้อมูลเป็น Domain Objects]
└──────────────┘
       ↓
┌──────────────┐
│ 3. Process   │ ← [ประมวลผลตาม Business Logic]
└──────────────┘
       ↓
┌──────────────┐
│ 4. Validate  │ ← [ตรวจสอบผลลัพธ์]
└──────────────┘
       ↓
┌──────────────┐
│ 5. Output    │ ← [ส่งออกผลลัพธ์: File, API, DB, etc.]
└──────────────┘
```

---

## Pipeline Rules (สิ่งที่ Pipeline ควรและไม่ควรทำ)

### ❌ ไม่ควรมีใน Pipeline

```
# ❌ Business logic ใน pipeline
if some_business_condition:
    do_something()

# ❌ Hardcoded values
if value < 0.20:
    ...
```

### ✅ ควรทำใน Pipeline

```
# ✅ Orchestrate เท่านั้น
data = loader.load(source)
result = domain_service.process(data)
exporter.export(result, destination)
```

---

## Separation of Concerns

- **Domain:** ตัดสินใจ (What to do?)
- **Pipeline:** Execute (Actually do it)
- **Infrastructure:** I/O (How to read/write?)

---

## Performance Considerations

1. [Consideration 1: เช่น ใช้ streaming สำหรับไฟล์ใหญ่]
2. [Consideration 2: เช่น cache ผลคำนวณที่ใช้บ่อย]
3. [Consideration 3]

**Current Performance** (ถ้ามี benchmark):
- [Operation]: ~[X]s
- [Operation]: ~[X]s