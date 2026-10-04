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
  <main>
    <h1>จัดการบิลรายเดือน</h1>

    <label for="billing-month">เดือน</label>
    <select id="billing-month" v-model="selectedMonth" data-testid="billing-month">
      <option
        v-for="(monthName, index) in months"
        :key="monthName"
        :value="String(index + 1).padStart(2, '0')"
      >
        {{ monthName }}
      </option>
    </select>
    <label for="billing-year">ปี พ.ศ.</label>
    <input
      id="billing-year"
      v-model="buddhistYear"
      data-testid="billing-year"
      min="544"
      max="10542"
      required
      step="1"
      type="number"
    />
    <p v-if="loading" role="status">กำลังโหลดข้อมูล...</p>
    <p v-if="errorMessage" role="alert">{{ errorMessage }}</p>
    <p v-if="successMessage" role="status">{{ successMessage }}</p>

    <section aria-labelledby="rooms-heading">
      <h2 id="rooms-heading">รายการห้องพัก</h2>
      <table>
        <thead>
          <tr>
            <th>ห้อง</th>
            <th>ค่าเช่า</th>
            <th>สถานะบิล</th>
            <th>ยอดรวม</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="room in rooms" :key="room.id">
            <td>{{ room.room_number }}</td>
            <td>{{ room.rent_rate }}</td>
            <td>{{ billsByRoomId.has(room.id) ? "สร้างแล้ว" : "ยังไม่มีบิล" }}</td>
            <td>{{ billsByRoomId.get(room.id)?.total ?? "—" }}</td>
          </tr>
        </tbody>
      </table>
    </section>

    <section aria-labelledby="create-bill-heading">
      <h2 id="create-bill-heading">สร้างบิล</h2>
      <form @submit.prevent="submitBill">
        <label for="room-id">ห้องพัก</label>
        <select id="room-id" v-model="selectedRoomId" required>
          <option disabled value="">เลือกห้องพัก</option>
          <option v-for="room in rooms" :key="room.id" :value="room.id">
            {{ room.room_number }}
          </option>
        </select>

        <label for="water-current">มิเตอร์น้ำปัจจุบัน</label>
        <input id="water-current" v-model="waterCurrent" data-testid="water-current" min="0" step="1" required type="number" />
        <label for="water-previous">มิเตอร์น้ำครั้งก่อน</label>
        <input id="water-previous" v-model="waterPrevious" data-testid="water-previous" min="0" step="1" required type="number" />
        <label for="electricity-current">มิเตอร์ไฟปัจจุบัน</label>
        <input id="electricity-current" v-model="electricityCurrent" data-testid="electricity-current" min="0" step="1" required type="number" />
        <label for="electricity-previous">มิเตอร์ไฟครั้งก่อน</label>
        <input id="electricity-previous" v-model="electricityPrevious" data-testid="electricity-previous" min="0" step="1" required type="number" />

        <button :disabled="submitting || rooms.length === 0" type="submit">
          {{ submitting ? "กำลังสร้างบิล..." : "สร้างบิล" }}
        </button>
      </form>
    </section>
  </main>
</template>
