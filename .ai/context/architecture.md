# Architecture

## สถาปัตยกรรมโปรเจค

> แทนที่ด้วย Diagram สถาปัตยกรรมของโปรเจคนี้

```
┌────────────────────────────────────────────────────────────────┐
│                      Presentation Layer                        │
│  [โฟลเดอร์ / ไฟล์]    ← [คำอธิบาย]                           │
└────────────────────────────────────────────────────────────────┘
                                ↓
┌────────────────────────────────────────────────────────────────┐
│                     Application Layer                          │
│  [โฟลเดอร์ / ไฟล์]    ← [คำอธิบาย]                           │
└────────────────────────────────────────────────────────────────┘
                                ↓
┌────────────────────────────────────────────────────────────────┐
│                       Domain Layer                             │
│  [โฟลเดอร์ / ไฟล์]    ← [คำอธิบาย]                           │
└────────────────────────────────────────────────────────────────┘
                                ↓
┌────────────────────────────────────────────────────────────────┐
│                   Infrastructure Layer                         │
│  [โฟลเดอร์ / ไฟล์]    ← [คำอธิบาย]                           │
└────────────────────────────────────────────────────────────────┘
```

---

## หลักการออกแบบ (Design Principles)

### 1. Dependency Rule

```
Presentation → Application → Domain ← Infrastructure
```

- **Domain** ไม่มี dependency ภายนอก (Pure Logic)
- **Application** ใช้ Domain แต่ไม่รู้จัก Infrastructure
- **Infrastructure** implement interface ที่ Domain กำหนด

### 2. Business Logic อยู่ใน Domain เท่านั้น

```
# ❌ ไม่ควรมีใน Application Layer
if some_condition:
    do_something()

# ✅ ควรอยู่ใน Domain
domain_service.evaluate(entity)
```

### 3. [หลักการเพิ่มเติมของโปรเจค]

[อธิบายหลักการเพิ่มเติม]

---

## Data Flow

```
[Input Source] ──→ [Loader/Adapter] ──→ [Domain Objects]
                                               ↓
                                     [Application Layer]
                                               ↓
                                     [Output / Export]
```

---

## Component Responsibilities

| Component | Responsibility | ห้ามทำ |
|-----------|---------------|--------|
| **[Component 1]** | [หน้าที่] | [สิ่งที่ห้ามทำ] |
| **[Component 2]** | [หน้าที่] | [สิ่งที่ห้ามทำ] |
| **[Component 3]** | [หน้าที่] | [สิ่งที่ห้ามทำ] |

---

## Test Strategy

```
Unit Tests
  ├─ [กลุ่ม test 1]
  └─ [กลุ่ม test 2]

Integration Tests
  ├─ [กลุ่ม test 1]
  └─ [กลุ่ม test 2]

System Tests
  └─ Manual / E2E
```

**Coverage Target:** [เช่น Domain layer 100%, Integration 80%+]