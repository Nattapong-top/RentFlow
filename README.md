# RentFlow
แอป Python สำหรับคำนวณบิลห้องพักรายเดือน

## สถานะปัจจุบัน

โปรเจกต์มี Domain สำหรับห้อง ผู้เช่า และบิล, use case `CreateMonthlyBill` และ `BillDAO` ซึ่งเก็บข้อมูลในหน่วยความจำเท่านั้น ปัจจุบันยังไม่มี UI, REST API, Docker หรือฐานข้อมูลถาวร; แผน Vue/FastAPI/Docker อยู่ใน [`docs/action_plan_docker_api.md`](docs/action_plan_docker_api.md)

## เริ่มต้นใช้งาน

ต้องมี Python 3.13 ขึ้นไปและ [uv](https://docs.astral.sh/uv/)

```bash
uv sync --extra dev
```

## ทดสอบ

```bash
uv run pytest
```

ดูภาพรวมโครงสร้างและการคำนวณได้ที่ [`docs/architecture.md`](docs/architecture.md) และ [`docs/billing_guide.md`](docs/billing_guide.md).
