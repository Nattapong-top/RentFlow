import {afterEach, describe, expect, it, vi} from "vitest";

import {BillService} from "./billService";

describe("BillService", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("loads rooms from the configured API", async () => {
    const rooms = [{
      id: "room-101",
      room_number: "101",
      rent_rate: "3000",
      occupant_type: "TENANT",
      tenant_id: "tenant-101",
      cable_exempt: false,
      has_parking: true,
    }];
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => rooms,
    });
    vi.stubGlobal("fetch", fetchMock);

    const service = new BillService("http://localhost:8000");
    const result = await service.getRooms();

    expect(result).toEqual(rooms);
    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/api/v1/rooms",
      expect.objectContaining({ method: "GET" }),
    );
  });

  it("loads bills for the selected billing period", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => [],
    });
    vi.stubGlobal("fetch", fetchMock);

    const service = new BillService("http://localhost:8000");
    await service.getBills("2026-10");

    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/api/v1/bills?period=2026-10",
      expect.objectContaining({ method: "GET" }),
    );
  });

  it("loads bill details by id", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ id: "BILL-room-101-2026-10" }),
    });
    vi.stubGlobal("fetch", fetchMock);

    const service = new BillService("http://localhost:8000");
    await service.getBill("BILL-room-101-2026-10");

    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/api/v1/bills/BILL-room-101-2026-10",
      expect.objectContaining({ method: "GET" }),
    );
  });

  it("creates a bill with meter readings but no client-supplied pricing", async () => {
    const bill = { id: "BILL-room-101-2026-10", total: "4710" };
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => bill,
    });
    vi.stubGlobal("fetch", fetchMock);
    const request = {
      room_id: "room-101",
      billing_period: "2026-10",
      water_meter: [450, 350] as [number, number],
      electricity_meter: [250, 200] as [number, number],
    };

    const service = new BillService("http://localhost:8000");
    const result = await service.createBill(request);

    expect(result).toEqual(bill);
    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/api/v1/bills",
      expect.objectContaining({
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(request),
      }),
    );
  });

  it("surfaces the Thai API error detail", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        json: async () => ({ detail: "ไม่พบห้องพักที่ระบุ" }),
      }),
    );

    const service = new BillService("http://localhost:8000");

    await expect(service.getRooms()).rejects.toThrow("ไม่พบห้องพักที่ระบุ");
  });

  it("returns a Thai message when the API cannot be reached", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("Failed to fetch")));

    const service = new BillService("http://localhost:8000");

    await expect(service.getRooms()).rejects.toThrow(
      "ไม่สามารถเชื่อมต่อกับระบบได้ กรุณาลองอีกครั้ง",
    );
  });
});