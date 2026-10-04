# RentFlow Action Plan: Dockerized Vue + FastAPI REST API

เอกสารนี้สรุปสถานะและวิธีใช้งาน RentFlow ซึ่งมี Vue 3 frontend, FastAPI REST API และ Docker Compose แล้ว โดย Nginx ให้บริการหน้าเว็บและ proxy API บน origin เดียว

> **สถานะปัจจุบัน:** มี FastAPI endpoints และ Vue frontend แล้ว; runtime composition และรายการห้อง/ราคาสำหรับ Docker เป็นข้อมูล demo เท่านั้น ส่วนบิลจัดเก็บใน `BillDAO` แบบ in-memory และหายเมื่อ backend container ถูกสร้างใหม่ ไม่มีฐานข้อมูลถาวร

---

## 1. วัตถุประสงค์ (Objectives)
- แยกส่วน Frontend (Vue) และ Backend (FastAPI) ออกจากกันอย่างเด็ดขาด สื่อสารผ่าน RESTful JSON API
- ยึดมั่นใน Clean Architecture และ Domain-Driven Design (ใช้ Use Case `CreateMonthlyBill` โดยต่อยอด Repository และแหล่งข้อมูลตามความจำเป็น แทนการเขียน Business Logic ซ้ำซ้อน)
- แพ็กเกจระบบทั้งระบบให้สามารถรันบน Docker และ Docker Compose ได้อย่างราบรื่น

---

## 2. สถานะและวิธีใช้งาน

### เฟสที่ 1–2: API และ Frontend
- FastAPI ให้บริการ endpoints สำหรับ rooms และ bills ใต้ `/api/v1`; Vue เรียกผ่าน `frontend/src/services/billService.ts`
- จำนวนเงินใน request/response ใช้ string เพื่อหลีกเลี่ยงความคลาดเคลื่อนจาก floating point ใน JavaScript

### เฟสที่ 3: Dockerization & Docker Compose (ดำเนินการแล้ว)
- `presentation/api/main.py` เป็น runtime composition root สำหรับข้อมูล demo: ห้อง 101 และ demo pricing; ไม่ import จาก `tests/`
- `Dockerfile` สร้าง backend ด้วย Python 3.13 และติดตั้ง dependencies จาก `uv.lock`; `uvicorn` เป็น runtime dependency
- `frontend/Dockerfile` build Vue ด้วย Node.js แล้วเสิร์ฟ static files ด้วย Nginx Alpine
- Nginx proxy `/api/` ไปยัง `backend:8000`; browser ใช้ origin เดียว จึงไม่ต้องเปิด backend port หรือพึ่ง CORS ข้าม origin
- `docker-compose.yml` เปิด frontend ที่ host port 80 โดยปริยาย (ปรับได้ด้วย `RENTFLOW_WEB_PORT`) และรอ backend health check ก่อนเริ่ม frontend

### เริ่มระบบ
รันจาก project root โดยต้องติดตั้ง Docker และเปิด Docker Engine แล้ว:

```powershell
docker compose config
docker compose build
docker compose up -d
docker compose ps
```

เปิดหน้าเว็บที่ `http://localhost:80` (หรือ `http://localhost`) และตรวจ API ผ่าน frontend proxy ด้วย PowerShell:

```powershell
Invoke-RestMethod -Uri http://localhost:80/api/v1/rooms
```

เปลี่ยน host port ได้ก่อนเริ่ม stack เช่น:

```powershell
$env:RENTFLOW_WEB_PORT = '8081'
docker compose up -d --build
```

จากนั้นเข้า `http://localhost:8081` หากต้องดู log ใช้ `docker compose logs -f` และหยุด/ลบ containers กับ network ด้วย:

```powershell
docker compose down
```

### ข้อจำกัดข้อมูลและการตรวจสอบ
- ห้องและราคาใน `presentation/api/main.py` เป็นข้อมูล demo ไม่ใช่ข้อมูล production
- บิลเก็บใน `BillDAO` แบบ in-memory เท่านั้น; ข้อมูลจะหายเมื่อ backend process/container restart หรือถูกสร้างใหม่ ไม่มี database หรือ volume สำหรับ persistence
- ตรวจ backend/frontend และชุดทดสอบด้วย `docker compose build`, `make all-tests` และ `npm test` จาก `frontend/`

---

## 3. สรุปแนวทางความปลอดภัยและความถูกต้อง
- **Source of Truth (ข้อกำหนดสำหรับระบบในอนาคต)**: Backend ต้องเป็นผู้คำนวณเงินและรับราคาจากแหล่งข้อมูลที่เชื่อถือได้ ห้ามเชื่อยอดรวมหรือราคาที่ client ส่งมา; ความสามารถนี้ยังไม่ได้ implement
- **Precision**: ข้อมูลจำนวนเงินส่งผ่าน JSON เป็น `string` เพื่อหลีกเลี่ยงปัญหา Floating-point ใน JavaScript
