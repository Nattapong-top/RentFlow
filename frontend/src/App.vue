<script setup lang="ts">
import BillingView from "./views/BillingView.vue";
import { BillService } from "./services/billService";
import { getCurrentGregorianBillingPeriod } from "./utils/buddhistBillingPeriod";

const service = new BillService(import.meta.env.VITE_API_BASE_URL);
const initialPeriod = getCurrentGregorianBillingPeriod();
</script>

<template>
  <BillingView :service="service" :initial-period="initialPeriod" />
</template>
