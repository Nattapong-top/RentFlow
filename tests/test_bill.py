import pytest
from custom_errors.custom_errors import DuplicateBillItemError, InvalidBillItemError
from domain.bill import Bill, BillItem
from domain.billing_period import BillingPeriod


from decimal import Decimal


def test_create_bill_item_success():
    item = BillItem(name="ค่าเช่าห้อง", amount=2800, description="ค่าเช่าประจำเดือน")
    assert item.name == "ค่าเช่าห้อง"
    assert item.amount == Decimal("2800")
    assert isinstance(item.amount, Decimal)
    assert item.description == "ค่าเช่าประจำเดือน"


def test_create_bill_item_negative_amount_raises_error():
    with pytest.raises(InvalidBillItemError) as exc_info:
        BillItem(name="ค่าเช่าห้อง", amount=-100)
    assert str(exc_info.value) == "จำนวนเงินของรายการต้องไม่น้อยกว่าศูนย์"


def test_create_bill_item_empty_name_raises_error():
    with pytest.raises(InvalidBillItemError) as exc_info:
        BillItem(name="", amount=100)
    assert str(exc_info.value) == "ชื่อรายการต้องไม่ว่างเปล่า"


def test_create_bill_and_add_items():
    period = BillingPeriod(value="2026-09")
    bill = Bill(
        id="B001",
        room_id="R001",
        billing_period=period,
        tenant_id="T001",
    )
    assert bill.total == 0
    assert len(bill.items) == 0

    bill.add_item(BillItem(name="ค่าเช่าห้อง", amount=2800))
    bill.add_item(BillItem(name="ค่าน้ำ", amount=150))
    bill.add_item(BillItem(name="ค่าไฟ", amount=800))
    bill.add_item(BillItem(name="ค่าเคเบิล", amount=80))
    bill.add_item(BillItem(name="ค่าที่จอดรถ", amount=500))

    assert bill.total == Decimal("4330")
    assert isinstance(bill.total, Decimal)
    assert len(bill.items) == 5


def test_add_duplicate_item_raises_error():
    bill = Bill(
        id="B001",
        room_id="R001",
        billing_period=BillingPeriod(value="2026-09"),
    )
    bill.add_item(BillItem(name="ค่าน้ำ", amount=150))

    with pytest.raises(DuplicateBillItemError) as exc_info:
        bill.add_item(BillItem(name="ค่าน้ำ", amount=200))
    assert str(exc_info.value) == "มีรายการ 'ค่าน้ำ' อยู่ในบิลแล้ว"


def test_bill_clear_items_for_recalculate():
    bill = Bill(
        id="B001",
        room_id="R001",
        billing_period=BillingPeriod(value="2026-09"),
    )
    bill.add_item(BillItem(name="ค่าน้ำ", amount=150))
    assert bill.total == 150

    bill.clear_items()
    assert bill.total == 0
    assert len(bill.items) == 0

    # สามารถเพิ่มรายการใหม่หลัง clear ได้ (Recalculate)
    bill.add_item(BillItem(name="ค่าน้ำ", amount=200))
    assert bill.total == 200
