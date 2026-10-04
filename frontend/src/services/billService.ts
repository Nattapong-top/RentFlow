export interface RoomResponse {
  id: string;
  room_number: string;
  rent_rate: string;
  occupant_type: string;
  tenant_id: string | null;
  cable_exempt: boolean;
  has_parking: boolean;
}

export interface BillItemResponse {
  name: string;
  amount: string;
  description: string | null;
}

export interface BillResponse {
  id: string;
  room_id: string;
  billing_period: string;
  tenant_id: string | null;
  items: BillItemResponse[];
  total: string;
}

export interface BillCreateRequest {
  room_id: string;
  billing_period: string;
  water_meter: [number, number];
  electricity_meter: [number, number];
}

export interface BillServicePort {
  getRooms(): Promise<RoomResponse[]>;
  getBills(period: string): Promise<BillResponse[]>;
  createBill(request: BillCreateRequest): Promise<BillResponse>;
}

export class BillService implements BillServicePort {
  private readonly baseUrl: string;

  constructor(baseUrl = import.meta.env.VITE_API_BASE_URL) {
    this.baseUrl = baseUrl.replace(/\/+$/, "");
  }

  getRooms(): Promise<RoomResponse[]> {
    return this.request<RoomResponse[]>("/api/v1/rooms");
  }

  getBills(period: string): Promise<BillResponse[]> {
    return this.request<BillResponse[]>(
      `/api/v1/bills?period=${encodeURIComponent(period)}`,
    );
  }

  getBill(billId: string): Promise<BillResponse> {
    return this.request<BillResponse>(
      `/api/v1/bills/${encodeURIComponent(billId)}`,
    );
  }

  createBill(request: BillCreateRequest): Promise<BillResponse> {
    return this.request<BillResponse>("/api/v1/bills", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request),
    });
  }

  private async request<T>(path: string, init: RequestInit = {}): Promise<T> {
    let response: Response;
    try {
      response = await fetch(`${this.baseUrl}${path}`, {
        ...init,
        method: init.method ?? "GET",
      });
    } catch {
      throw new Error("ไม่สามารถเชื่อมต่อกับระบบได้ กรุณาลองอีกครั้ง");
    }

    if (!response.ok) {
      let detail: string | undefined;
      try {
        const body: { detail?: unknown } = await response.json();
        if (typeof body.detail === "string") {
          detail = body.detail;
        }
      } catch {
        // Use a localized fallback when the server response is not JSON.
      }

      throw new Error(detail ?? "เกิดข้อผิดพลาดในการเชื่อมต่อกับระบบ");
    }

    return await response.json() as Promise<T>;
  }
}
