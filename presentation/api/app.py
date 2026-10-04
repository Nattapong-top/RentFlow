from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict
from starlette.exceptions import HTTPException as StarletteHTTPException

from application.create_monthly_bill import CreateMonthlyBill
from custom_errors.custom_errors import DomainErrors
from domain.bill import Bill
from domain.billing_period import BillingPeriod
from domain.building_pricing import BuildingPricing
from domain.room import Room
from infrastructure.repositories.bill_repository import IBillRepository


class BillCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    room_id: str
    billing_period: str
    water_meter: tuple[int, int]
    electricity_meter: tuple[int, int]


class RoomResponse(BaseModel):
    id: str
    room_number: str
    rent_rate: str
    occupant_type: str
    tenant_id: str | None
    cable_exempt: bool
    has_parking: bool


class BillItemResponse(BaseModel):
    name: str
    amount: str
    description: str | None


class BillResponse(BaseModel):
    id: str
    room_id: str
    billing_period: str
    tenant_id: str | None
    items: list[BillItemResponse]
    total: str


def create_app(
    rooms: list[Room], pricing: BuildingPricing, bill_repository: IBillRepository
) -> FastAPI:
    app = FastAPI()

    @app.exception_handler(DomainErrors)
    async def handle_domain_error(
        request: Request, error: DomainErrors
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={"detail": str(error)},
        )

    @app.exception_handler(RequestValidationError)
    async def handle_request_validation_error(
        request: Request, error: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={"detail": "ข้อมูลคำขอไม่ถูกต้อง"},
        )

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_exception(
        request: Request, error: StarletteHTTPException
    ) -> JSONResponse:
        detail = error.detail
        if detail == "Not Found":
            detail = "ไม่พบเส้นทางที่ร้องขอ"
        elif detail == "Method Not Allowed":
            detail = "ไม่อนุญาตให้ใช้วิธีการร้องขอนี้"

        return JSONResponse(
            status_code=error.status_code,
            content={"detail": detail},
            headers=error.headers,
        )

    app.state.rooms = {room.id: room for room in rooms}
    app.state.pricing = pricing
    app.state.bill_repository = bill_repository
    create_monthly_bill = CreateMonthlyBill()

    @app.get("/api/v1/rooms", response_model=list[RoomResponse])
    def list_rooms() -> list[RoomResponse]:
        return [
            RoomResponse(
                id=room.id,
                room_number=room.room_number,
                rent_rate=str(room.rent_rate),
                occupant_type=room.occupant_type.value,
                tenant_id=room.tenant_id,
                cable_exempt=room.cable_exempt,
                has_parking=room.has_parking,
            )
            for room in app.state.rooms.values()
        ]

    @app.get("/api/v1/bills", response_model=list[BillResponse])
    def list_bills(period: str) -> list[BillResponse]:
        billing_period = BillingPeriod(value=period)
        bills = app.state.bill_repository.find_by_period(billing_period)
        return [to_bill_response(bill) for bill in bills]

    @app.get("/api/v1/bills/{bill_id}", response_model=BillResponse)
    def get_bill(bill_id: str) -> BillResponse:
        bill = app.state.bill_repository.find_by_id(bill_id)
        if bill is None:
            raise HTTPException(status_code=404, detail="ไม่พบบิลที่ร้องขอ")
        return to_bill_response(bill)

    @app.post("/api/v1/bills", status_code=201, response_model=BillResponse)
    def create_bill(request: BillCreateRequest) -> BillResponse:
        billing_period = BillingPeriod(value=request.billing_period)
        room = app.state.rooms.get(request.room_id)
        if room is None:
            raise HTTPException(status_code=404, detail="ไม่พบห้องพักที่ระบุ")

        existing_bill = app.state.bill_repository.find_by_room_and_period(
            room.id, billing_period
        )
        if existing_bill is not None:
            raise HTTPException(
                status_code=409, detail="มีบิลของห้องนี้ในรอบบิลดังกล่าวแล้ว"
            )

        bill = create_monthly_bill.execute(
            room=room,
            billing_period=billing_period,
            pricing=app.state.pricing,
            water_meter=request.water_meter,
            electricity_meter=request.electricity_meter,
        )
        saved_bill = app.state.bill_repository.save(bill)
        return to_bill_response(saved_bill)

    return app


def to_bill_response(bill: Bill) -> BillResponse:
    return BillResponse(
        id=bill.id,
        room_id=bill.room_id,
        billing_period=bill.billing_period.value,
        tenant_id=bill.tenant_id,
        items=[
            BillItemResponse(
                name=item.name,
                amount=str(item.amount),
                description=item.description,
            )
            for item in bill.items
        ],
        total=str(bill.total),
    )
