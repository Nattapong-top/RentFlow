# RentFlow Action Plan: Dockerized Vue + FastAPI REST API

เอกสารนี้เป็น **แผนงานในอนาคต** สำหรับการพัฒนา RentFlow ในรูปแบบ **Decoupled Architecture (Vue 3 Frontend + FastAPI Backend REST API)** และการแพ็กเกจด้วย **Docker Containers** ไม่ใช่คำอธิบายระบบที่มีอยู่แล้วในปัจจุบัน

> **สถานะปัจจุบัน:** โปรเจกต์มีแกน Python สำหรับคำนวณบิลและ `BillDAO` แบบ in-memory เท่านั้น ยังไม่มี FastAPI, Vue frontend, Docker หรือฐานข้อมูลถาวร ทั้งยังไม่มี Repository สำหรับห้องหรือราคา แผนนี้จึงต้องเพิ่มแหล่งข้อมูลฝั่ง backend ที่เชื่อถือได้ก่อนให้ API ใช้ข้อมูลดังกล่าว

---

## 1. วัตถุประสงค์ (Objectives)
- แยกส่วน Frontend (Vue) และ Backend (FastAPI) ออกจากกันอย่างเด็ดขาด สื่อสารผ่าน RESTful JSON API
- ยึดมั่นใน Clean Architecture และ Domain-Driven Design (ใช้ Use Case `CreateMonthlyBill` โดยต่อยอด Repository และแหล่งข้อมูลตามความจำเป็น แทนการเขียน Business Logic ซ้ำซ้อน)
- แพ็กเกจระบบทั้งระบบให้สามารถรันบน Docker และ Docker Compose ได้อย่างราบรื่น

---

## 2. ขั้นตอนการลงมือทำ (Step-by-Step Implementation Plan)

### เฟสที่ 1: พัฒนา FastAPI REST API & Endpoints
1. **สร้าง FastAPI Application Structure**:
   - เพิ่ม `presentation/api/` หรือ `main.py` สำหรับรัน FastAPI
   - สร้าง Pydantic Schemas / DTOs สำหรับ Request/Response (เช่น `BillCreateRequest`, `BillResponse`)
2. **สร้าง API Endpoints (เป้าหมายที่วางแผนไว้)**:
   - `GET /api/v1/rooms`: ดึงรายการห้องพัก
   - `GET /api/v1/bills?period=YYYY-MM`: ดึงรายการบิลตามรอบบิล
   - `GET /api/v1/bills/{bill_id}`: ดูรายละเอียดบิล
   - `POST /api/v1/bills`: สร้างบิลใหม่ (เรียก `CreateMonthlyBill`; ต้องออกแบบและเพิ่มแหล่งข้อมูลฝั่ง backend สำหรับห้องและราคา เพราะ Repository ปัจจุบันรองรับเฉพาะบิล)
3. **Error Handling & CORS**:
   - จัดการแปลง Domain Exceptions เป็น HTTP Status Codes (`400`, `404`, `409`, `422`, `500`)
   - ตั้งค่า CORS ให้รองรับเฉพาะ Origin ของ Frontend

### เฟสที่ 2: พัฒนา Vue 3 Frontend & Service Layer
1. **สร้าง Vue 3 + TypeScript Project**:
   - จัดโครงสร้างโฟลเดอร์ (เช่น `src/views`, `src/components`, `src/services`)
2. **สร้าง API Service Layer (`src/services/billService.ts`)**:
   - แยกตรรกะการเรียก HTTP ออกจาก UI Components ใช้ Environment Variable สำหรับระบุ Backend URL
   - จัดการส่งตัวเลขเงินเป็น `string` เพื่อความแม่นยำ
3. **พัฒนาหน้าจอ UI**:
   - หน้าแสดงรายการห้องและสถานะบิล
   - ฟอร์มกรอกเลขมิเตอร์น้ำ/ไฟ และกดสั่งสร้างบิล

### เฟสที่ 3: Dockerization & Docker Compose
1. **Backend Dockerfile**:
   - เขียน `Dockerfile` สำหรับ FastAPI โดยใช้ Python 3.13 และติดตั้ง dependencies ผ่าน `uv` หรือ `pip`
2. **Frontend Dockerfile**:
   - เขียน Multi-stage `Dockerfile` สำหรับ Vue (Build ด้วย Node.js แล้วServe ผ่าน Nginx Alpine)
3. **Docker Compose (`docker-compose.yml`)**:
   - เชื่อมโยงบริการ `backend` (พอร์ต 8000) และ `frontend` (พอร์ต 80) เข้าด้วยกัน
   - ตั้งค่า Network และ Environment Variables

### เฟสที่ 4: การทดสอบและการตรวจสอบ (Testing & Validation)
1. **API Integration Tests**: ทดสอบ Endpoints ของ FastAPI ด้วย `pytest` และ `TestClient`
2. **End-to-End Testing**: ทดสอบการทำงานร่วมกันระหว่าง Vue และ FastAPI บน Docker Container จริง

---

## 3. สรุปแนวทางความปลอดภัยและความถูกต้อง
- **Source of Truth (ข้อกำหนดสำหรับระบบในอนาคต)**: Backend ต้องเป็นผู้คำนวณเงินและรับราคาจากแหล่งข้อมูลที่เชื่อถือได้ ห้ามเชื่อยอดรวมหรือราคาที่ client ส่งมา; ความสามารถนี้ยังไม่ได้ implement
- **Precision**: ข้อมูลจำนวนเงินส่งผ่าน JSON เป็น `string` เพื่อหลีกเลี่ยงปัญหา Floating-point ใน JavaScript
