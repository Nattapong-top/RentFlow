<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";

import type {
  BillResponse,
  BillServicePort,
  RoomResponse,
} from "../services/billService";
import {
  fromGregorianBillingPeriod,
  toGregorianBillingPeriod,
} from "../utils/buddhistBillingPeriod";

const props = defineProps<{
  service: BillServicePort;
  initialPeriod: string;
}>();

const initialBillingPeriod = fromGregorianBillingPeriod(props.initialPeriod);
const months = [
  "มกราคม",
  "กุมภาพันธ์",
  "มีนาคม",
  "เมษายน",
  "พฤษภาคม",
  "มิถุนายน",
  "กรกฎาคม",
  "สิงหาคม",
  "กันยายน",
  "ตุลาคม",
  "พฤศจิกายน",
  "ธันวาคม",
];
const rooms = ref<RoomResponse[]>([]);
const bills = ref<BillResponse[]>([]);
const buddhistYear = ref(String(initialBillingPeriod.year));
const selectedMonth = ref(String(initialBillingPeriod.month).padStart(2, "0"));
const period = computed(() => {
  if (!/^\d{4,5}$/.test(buddhistYear.value)) {
    return "";
  }

  const year = Number(buddhistYear.value);
  const month = Number(selectedMonth.value);
  if (year < 544 || year > 10542 || month < 1 || month > 12) {
    return "";
  }

  return toGregorianBillingPeriod(year, month);
});
const selectedRoomId = ref("");
const waterCurrent = ref("");
const waterPrevious = ref("");
const electricityCurrent = ref("");
const electricityPrevious = ref("");
const errorMessage = ref("");
const successMessage = ref("");
const loading = ref(false);
const submitting = ref(false);

const billsByRoomId = computed(
  () => new Map(bills.value.map((bill) => [bill.room_id, bill])),
);

onMounted(() => {
  void loadData();
});

watch(period, (value) => {
  successMessage.value = "";
  if (!/^\d{4}-\d{2}$/.test(value)) {
    bills.value = [];
    return;
  }
  void loadBills(value);
});

async function loadData(): Promise<void> {
  loading.value = true;
  errorMessage.value = "";
  try {
    const [loadedRooms, loadedBills] = await Promise.all([
      props.service.getRooms(),
      props.service.getBills(period.value),
    ]);
    rooms.value = loadedRooms;
    bills.value = loadedBills;
    if (!loadedRooms.some((room) => room.id === selectedRoomId.value)) {
      selectedRoomId.value = loadedRooms[0]?.id ?? "";
    }
  } catch (error) {
    errorMessage.value = getErrorMessage(error);
  } finally {
    loading.value = false;
  }
}

async function submitBill(): Promise<void> {
  errorMessage.value = "";
  successMessage.value = "";

  const meterReadings = [
    waterCurrent.value,
    waterPrevious.value,
    electricityCurrent.value,
    electricityPrevious.value,
  ];
  if (
    !selectedRoomId.value ||
    !period.value ||
    meterReadings.some((value) => value === "")
  ) {
    errorMessage.value = "กรุณาเลือกห้อง รอบบิล และกรอกเลขมิเตอร์ให้ครบถ้วน";
    return;
  }

  const readings = meterReadings.map(Number);
  if (readings.some((value) => !Number.isInteger(value) || value < 0)) {
    errorMessage.value = "เลขมิเตอร์ต้องเป็นจำนวนเต็มตั้งแต่ 0 ขึ้นไป";
    return;
  }

  submitting.value = true;
  try {
    const bill = await props.service.createBill({
      room_id: selectedRoomId.value,
      billing_period: period.value,
      water_meter: [readings[0], readings[1]],
      electricity_meter: [readings[2], readings[3]],
    });
    bills.value = [
      ...bills.value.filter((currentBill) => currentBill.room_id !== bill.room_id),
      bill,
    ];
    successMessage.value = "สร้างบิลเรียบร้อยแล้ว";
  } catch (error) {
    errorMessage.value = getErrorMessage(error);
  } finally {
    submitting.value = false;
  }
}

async function loadBills(value: string): Promise<void> {
  errorMessage.value = "";
  try {
    bills.value = await props.service.getBills(value);
  } catch (error) {
    bills.value = [];
    errorMessage.value = getErrorMessage(error);
  }
}

function getErrorMessage(error: unknown): string {
  const message = error instanceof Error ? error.message : "";
  return /[\u0e00-\u0e7f]/.test(message)
    ? message
    : "เกิดข้อผิดพลาดในการดำเนินการ กรุณาลองอีกครั้ง";
}
</script>

<template>
  <main class="billing-dashboard">
    <header class="dashboard-header">
      <div>
        <p class="eyebrow">RENTFLOW · BILLING</p>
        <h1>จัดการบิลรายเดือน</h1>
        <p class="dashboard-description">ติดตามสถานะห้องพักและจัดทำบิลประจำเดือน</p>
      </div>

      <div class="period-control">
        <label for="billing-month">รอบบิล</label>
        <div class="period-fields">
          <select id="billing-month" v-model="selectedMonth" data-testid="billing-month">
            <option
              v-for="(monthName, index) in months"
              :key="monthName"
              :value="String(index + 1).padStart(2, '0')"
            >
              {{ monthName }}
            </option>
          </select>
          <label class="visually-hidden" for="billing-year">ปี พ.ศ.</label>
          <input
            id="billing-year"
            v-model="buddhistYear"
            aria-label="ปี พ.ศ."
            data-testid="billing-year"
            min="544"
            max="10542"
            required
            step="1"
            type="number"
          />
        </div>
      </div>
    </header>

    <section class="dashboard-summary" aria-label="สรุปภาพรวม">
      <article class="summary-card">
        <span class="summary-label">ห้องทั้งหมด</span>
        <strong>{{ rooms.length }}</strong>
        <span class="summary-note">ห้องพักในระบบ</span>
      </article>
      <article class="summary-card summary-card-accent">
        <span class="summary-label">จัดทำบิลแล้ว</span>
        <strong>{{ bills.length }}</strong>
        <span class="summary-note">จาก {{ rooms.length }} ห้อง</span>
      </article>
      <article class="summary-card">
        <span class="summary-label">รอดำเนินการ</span>
        <strong>{{ Math.max(rooms.length - bills.length, 0) }}</strong>
        <span class="summary-note">ห้องที่ยังไม่มีบิล</span>
      </article>
    </section>

    <p v-if="loading" class="feedback feedback-info" role="status">กำลังโหลดข้อมูล...</p>
    <p v-if="errorMessage" class="feedback feedback-error" role="alert">{{ errorMessage }}</p>
    <p v-if="successMessage" class="feedback feedback-success" role="status">
      {{ successMessage }}
    </p>

    <div class="billing-workspace">
      <section class="rooms-panel" aria-labelledby="rooms-heading">
        <div class="section-heading">
          <div>
            <p class="eyebrow">OVERVIEW</p>
            <h2 id="rooms-heading">รายการห้องพัก</h2>
          </div>
          <span class="room-count">{{ rooms.length }} ห้อง</span>
        </div>

        <div v-if="rooms.length === 0 && !loading" class="empty-state">
          <span class="empty-icon" aria-hidden="true">⌂</span>
          <strong>ยังไม่มีข้อมูลห้องพัก</strong>
          <span>กรุณาตรวจสอบการเชื่อมต่อกับระบบ</span>
        </div>
        <div v-else class="table-scroll">
          <table class="rooms-table">
            <thead>
              <tr>
                <th>ห้อง</th>
                <th>ค่าเช่า</th>
                <th>สถานะบิล</th>
                <th class="amount-column">ยอดรวม</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="room in rooms" :key="room.id">
                <td>
                  <span class="room-number">{{ room.room_number }}</span>
                </td>
                <td>{{ room.rent_rate }}</td>
                <td>
                  <span
                    class="status-badge"
                    :class="billsByRoomId.has(room.id) ? 'status-billed' : 'status-pending'"
                  >
                    {{ billsByRoomId.has(room.id) ? "สร้างแล้ว" : "ยังไม่มีบิล" }}
                  </span>
                </td>
                <td class="amount-column">
                  {{ billsByRoomId.get(room.id)?.total ?? "—" }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section class="billing-panel" aria-labelledby="create-bill-heading">
        <div class="section-heading">
          <div>
            <p class="eyebrow">NEW BILL</p>
            <h2 id="create-bill-heading">สร้างบิล</h2>
          </div>
          <span class="form-icon" aria-hidden="true">＋</span>
        </div>

        <form class="billing-form" @submit.prevent="submitBill">
          <label for="room-id">ห้องพัก</label>
          <select id="room-id" v-model="selectedRoomId" required>
            <option disabled value="">เลือกห้องพัก</option>
            <option v-for="room in rooms" :key="room.id" :value="room.id">
              {{ room.room_number }}
            </option>
          </select>

          <div class="meter-grid">
            <div class="meter-field">
              <label for="water-current">มิเตอร์น้ำปัจจุบัน</label>
              <input
                id="water-current"
                v-model="waterCurrent"
                data-testid="water-current"
                min="0"
                step="1"
                required
                type="number"
              />
            </div>
            <div class="meter-field">
              <label for="water-previous">มิเตอร์น้ำครั้งก่อน</label>
              <input
                id="water-previous"
                v-model="waterPrevious"
                data-testid="water-previous"
                min="0"
                step="1"
                required
                type="number"
              />
            </div>
            <div class="meter-field">
              <label for="electricity-current">มิเตอร์ไฟปัจจุบัน</label>
              <input
                id="electricity-current"
                v-model="electricityCurrent"
                data-testid="electricity-current"
                min="0"
                step="1"
                required
                type="number"
              />
            </div>
            <div class="meter-field">
              <label for="electricity-previous">มิเตอร์ไฟครั้งก่อน</label>
              <input
                id="electricity-previous"
                v-model="electricityPrevious"
                data-testid="electricity-previous"
                min="0"
                step="1"
                required
                type="number"
              />
            </div>
          </div>

          <button :disabled="submitting || rooms.length === 0" type="submit">
            {{ submitting ? "กำลังสร้างบิล..." : "สร้างบิล" }}
          </button>
          <p class="form-note">ราคาค่าเช่าและค่าบริการคำนวณจากข้อมูลของระบบ</p>
        </form>
      </section>
    </div>
  </main>
</template>

<style>
:root {
  font-family: Inter, "Noto Sans Thai", "Segoe UI", sans-serif;
  color: #203047;
  background: #f3f6fb;
  font-synthesis: none;
  text-rendering: optimizeLegibility;
}

* {
  box-sizing: border-box;
}

body {
  min-width: 320px;
  min-height: 100vh;
  margin: 0;
  background:
    radial-gradient(ellipse at top right, rgb(219 234 254 / 55%), transparent 38rem),
    #f3f6fb;
}

button,
input,
select {
  font: inherit;
}

.billing-dashboard {
  width: min(1220px, calc(100% - 48px));
  margin: 0 auto;
  padding: 48px 0 64px;
}

.dashboard-header,
.section-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
}

.dashboard-header h1,
.section-heading h2 {
  margin: 0;
  color: #18283f;
  letter-spacing: -0.035em;
}

.dashboard-header h1 {
  font-size: clamp(1.8rem, 4vw, 2.5rem);
  line-height: 1.2;
}

.dashboard-description {
  margin: 10px 0 0;
  color: #738198;
}

.eyebrow {
  margin: 0 0 8px;
  color: #6178a2;
  font-size: 0.69rem;
  font-weight: 800;
  letter-spacing: 0.14em;
}

.period-control {
  display: grid;
  min-width: 260px;
  gap: 8px;
}

.period-control > label,
.billing-form > label,
.meter-field label {
  color: #52627a;
  font-size: 0.84rem;
  font-weight: 700;
}

.period-fields {
  display: grid;
  grid-template-columns: minmax(0, 1.35fr) minmax(90px, 0.8fr);
  gap: 10px;
}

.period-fields select,
.period-fields input,
.billing-form select,
.meter-field input {
  width: 100%;
  min-height: 46px;
  border: 1px solid #dce4ef;
  border-radius: 11px;
  outline: none;
  background: #fff;
  color: #25364f;
  padding: 0 13px;
  transition: border-color 150ms ease, box-shadow 150ms ease;
}

.period-fields select:focus,
.period-fields input:focus,
.billing-form select:focus,
.meter-field input:focus {
  border-color: #6586c9;
  box-shadow: 0 0 0 3px rgb(84 121 190 / 14%);
}

.dashboard-summary {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  margin: 32px 0 24px;
}

.summary-card {
  display: grid;
  min-height: 145px;
  align-content: space-between;
  gap: 12px;
  border: 1px solid #e6ebf3;
  border-radius: 17px;
  background: rgb(255 255 255 / 90%);
  padding: 20px 22px;
  box-shadow: 0 8px 24px rgb(27 48 82 / 4%);
}

.summary-card-accent {
  border-color: #d8e4fb;
  background: linear-gradient(135deg, #edf4ff, #fff 82%);
}

.summary-label {
  color: #697991;
  font-size: 0.82rem;
  font-weight: 700;
}

.summary-card strong {
  color: #203a67;
  font-size: 2rem;
  line-height: 1;
}

.summary-note {
  color: #8793a5;
  font-size: 0.75rem;
}

.billing-workspace {
  display: grid;
  grid-template-columns: minmax(0, 1.35fr) minmax(320px, 0.85fr);
  align-items: start;
  gap: 20px;
}

.rooms-panel,
.billing-panel {
  min-width: 0;
  border: 1px solid #e6ebf3;
  border-radius: 18px;
  background: #fff;
  padding: 24px;
  box-shadow: 0 12px 32px rgb(27 48 82 / 5%);
}

.section-heading {
  margin-bottom: 20px;
}

.section-heading h2 {
  font-size: 1.2rem;
}

.room-count {
  border-radius: 20px;
  background: #f0f4fa;
  color: #5f6e84;
  padding: 7px 11px;
  font-size: 0.75rem;
  font-weight: 700;
  white-space: nowrap;
}

.table-scroll {
  overflow-x: auto;
}

.rooms-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  white-space: nowrap;
}

.rooms-table th {
  border-bottom: 1px solid #edf0f5;
  color: #8994a5;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 12px 10px;
}

.rooms-table td {
  border-bottom: 1px solid #f0f2f6;
  color: #58677d;
  font-size: 0.83rem;
  padding: 15px 10px;
}

.rooms-table tbody tr:last-child td {
  border-bottom: 0;
}

.room-number {
  color: #263955;
  font-weight: 800;
}

.amount-column {
  text-align: right !important;
  font-variant-numeric: tabular-nums;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  border-radius: 20px;
  padding: 6px 9px;
  font-size: 0.69rem;
  font-weight: 700;
}

.status-billed {
  background: #e8f6ef;
  color: #248456;
}

.status-pending {
  background: #fff4df;
  color: #a56b0a;
}

.form-icon,
.empty-icon {
  display: grid;
  width: 38px;
  height: 38px;
  place-items: center;
  border-radius: 12px;
  background: #eef4ff;
  color: #4c70b4;
  font-size: 1.4rem;
}

.billing-form {
  display: grid;
  gap: 10px;
}

.meter-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px 12px;
  margin: 8px 0 4px;
}

.meter-field {
  display: grid;
  min-width: 0;
  gap: 7px;
}

.meter-field label {
  font-size: 0.75rem;
}

.meter-field input {
  min-height: 43px;
  padding: 0 10px;
}

.billing-form button {
  min-height: 48px;
  margin-top: 4px;
  border: 0;
  border-radius: 11px;
  background: #315d9f;
  color: white;
  cursor: pointer;
  font-weight: 800;
  transition: background 150ms ease, transform 150ms ease;
}

.billing-form button:hover:not(:disabled) {
  transform: translateY(-1px);
  background: #274d86;
}

.billing-form button:disabled {
  cursor: not-allowed;
  opacity: 0.55;
}

.form-note {
  margin: 0;
  color: #8793a5;
  font-size: 0.71rem;
  text-align: center;
}

.feedback {
  border-radius: 11px;
  margin: 0 0 16px;
  padding: 12px 15px;
  font-size: 0.88rem;
}

.feedback-info {
  background: #edf4ff;
  color: #345f9e;
}

.feedback-error {
  background: #fff0ef;
  color: #a23b33;
}

.feedback-success {
  background: #eaf7ef;
  color: #247647;
}

.empty-state {
  display: grid;
  min-height: 210px;
  align-content: center;
  justify-items: center;
  gap: 10px;
  color: #748198;
  text-align: center;
}

.empty-state strong {
  color: #344660;
}

.empty-icon {
  width: 48px;
  height: 48px;
  font-size: 1.7rem;
}

.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  clip-path: inset(50%);
}

@media (max-width: 900px) {
  .billing-workspace {
    grid-template-columns: minmax(0, 1fr);
  }
}

@media (max-width: 640px) {
  .billing-dashboard {
    width: min(100% - 28px, 520px);
    padding-top: 28px;
  }

  .dashboard-header {
    align-items: stretch;
    flex-direction: column;
    gap: 20px;
  }

  .period-control {
    min-width: 0;
  }

  .dashboard-summary {
    gap: 9px;
    margin-top: 20px;
  }

  .summary-card {
    min-height: 120px;
    gap: 8px;
    padding: 14px 12px;
  }

  .summary-label {
    font-size: 0.69rem;
  }

  .summary-card strong {
    font-size: 1.65rem;
  }

  .summary-note {
    font-size: 0.65rem;
  }

  .rooms-panel,
  .billing-panel {
    border-radius: 15px;
    padding: 17px 14px;
  }

  .rooms-table th,
  .rooms-table td {
    padding-right: 7px;
    padding-left: 7px;
  }
}

@media (max-width: 380px) {
  .dashboard-summary {
    grid-template-columns: 1fr;
  }

  .summary-card {
    min-height: 98px;
  }

  .meter-grid {
    grid-template-columns: minmax(0, 1fr);
  }
}
</style>
