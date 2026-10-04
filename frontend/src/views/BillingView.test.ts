import {mount} from "@vue/test-utils";
import {describe, expect, it, vi} from "vitest";

import BillingView from "./BillingView.vue";

const room = {
  id: "room-101",
  room_number: "101",
  rent_rate: "3000",
  occupant_type: "TENANT",
  tenant_id: "tenant-101",
  cable_exempt: false,
  has_parking: true,
};

const bill = {
  id: "BILL-room-101-2026-10",
  room_id: "room-101",
  billing_period: "2026-10",
  tenant_id: "tenant-101",
  items: [{ name: "ค่าเช่า", amount: "3000", description: null }],
  total: "4710",
};

describe("BillingView", () => {
  it("loads and displays rooms with their billing status", async () => {
    const service = {
      getRooms: vi.fn().mockResolvedValue([room]),
      getBills: vi.fn().mockResolvedValue([bill]),
      createBill: vi.fn(),
    };

    const wrapper = mount(BillingView, {
      props: { service, initialPeriod: "2026-10" },
    });
    await new Promise((resolve) => setTimeout(resolve, 0));

    expect(service.getRooms).toHaveBeenCalledOnce();
    expect(service.getBills).toHaveBeenCalledWith("2026-10");
    expect(wrapper.text()).toContain("101");
    expect(wrapper.text()).toContain("4710");
    expect(wrapper.text()).toContain("สร้างแล้ว");
  });

  it("displays a Buddhist year and requests bills with the Gregorian year", async () => {
    const service = {
      getRooms: vi.fn().mockResolvedValue([room]),
      getBills: vi.fn().mockResolvedValue([]),
      createBill: vi.fn(),
    };

    const wrapper = mount(BillingView, {
      props: { service, initialPeriod: "2026-10" },
    });
    await new Promise((resolve) => setTimeout(resolve, 0));

    expect(
      (wrapper.get('[data-testid="billing-year"]').element as HTMLInputElement)
        .value,
    ).toBe("2569");
    expect(service.getBills).toHaveBeenCalledWith("2026-10");

    await wrapper.get('[data-testid="billing-year"]').setValue("2570");
    await new Promise((resolve) => setTimeout(resolve, 0));

    expect(service.getBills).toHaveBeenLastCalledWith("2027-10");
  });

  it("submits the selected Buddhist year as a Gregorian billing period", async () => {
    const nextBill = { ...bill, billing_period: "2027-10" };
    const service = {
      getRooms: vi.fn().mockResolvedValue([room]),
      getBills: vi.fn().mockResolvedValue([]),
      createBill: vi.fn().mockResolvedValue(nextBill),
    };

    const wrapper = mount(BillingView, {
      props: { service, initialPeriod: "2026-10" },
    });
    await new Promise((resolve) => setTimeout(resolve, 0));
    await wrapper.get('[data-testid="billing-year"]').setValue("2570");
    await wrapper.get('[data-testid="water-current"]').setValue("450");
    await wrapper.get('[data-testid="water-previous"]').setValue("350");
    await wrapper.get('[data-testid="electricity-current"]').setValue("250");
    await wrapper.get('[data-testid="electricity-previous"]').setValue("200");
    await wrapper.get("form").trigger("submit.prevent");

    expect(service.createBill).toHaveBeenCalledWith({
      room_id: "room-101",
      billing_period: "2027-10",
      water_meter: [450, 350],
      electricity_meter: [250, 200],
    });
  });

  it("submits meter readings for the selected room and period", async () => {
    const service = {
      getRooms: vi.fn().mockResolvedValue([room]),
      getBills: vi.fn().mockResolvedValue([]),
      createBill: vi.fn().mockResolvedValue(bill),
    };
    const wrapper = mount(BillingView, {
      props: { service, initialPeriod: "2026-10" },
    });
    await new Promise((resolve) => setTimeout(resolve, 0));

    await wrapper.get('[data-testid="water-current"]').setValue("450");
    await wrapper.get('[data-testid="water-previous"]').setValue("350");
    await wrapper.get('[data-testid="electricity-current"]').setValue("250");
    await wrapper.get('[data-testid="electricity-previous"]').setValue("200");
    await wrapper.get("form").trigger("submit.prevent");

    expect(service.createBill).toHaveBeenCalledWith({
      room_id: "room-101",
      billing_period: "2026-10",
      water_meter: [450, 350],
      electricity_meter: [250, 200],
    });
    expect(wrapper.text()).toContain("สร้างบิลเรียบร้อยแล้ว");
    expect(wrapper.text()).toContain("4710");
  });
});