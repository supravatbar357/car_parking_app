<template>
  <div>
    <h4 class="mb-3">📊 Your Parking Summary</h4>
    <div v-if="loading" class="text-center">Loading summary...</div>
    <div v-else>
      <!-- KPI Cards -->
      <div class="row g-3 mb-4">
        <div class="col-6 col-md-3" v-for="(value, key) in kpis" :key="key">
          <div class="kpi-card text-center shadow-sm p-3">
            <h5>{{ key }}</h5>
            <p class="display-6">{{ value }}</p>
          </div>
        </div>
      </div>

      <!-- Charts -->
      <div class="row g-4">
        <div class="col-md-6">
          <div class="card p-3 shadow-sm">
            <h5>Active vs Past Bookings</h5>
            <canvas ref="bookingChart"></canvas>
          </div>
        </div>
        <div class="col-md-6">
          <div class="card p-3 shadow-sm">
            <h5>Monthly Spending</h5>
            <canvas ref="costChart"></canvas>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "UserSummary",
  data() {
    return {
      summary: null,
      kpis: {},
      loading: true,
    };
  },
  async mounted() {
    await this.fetchSummary();
    if (this.summary) {
      this.setKPIs();
      this.renderCharts();
    }
    this.loading = false;
  },
  methods: {
    async fetchSummary() {
      try {
        const token = localStorage.getItem("token");
        const res = await fetch("/api/user/summary", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!res.ok) throw new Error("Failed to fetch user summary");
        this.summary = await res.json();
      } catch (err) {
        console.error(err);
      }
    },
    setKPIs() {
      this.kpis = {
        "Total Bookings": this.summary.total_bookings,
        "Total Cost (₹)": this.summary.total_cost,
        "Active": this.summary.active,
        "Past": this.summary.past,
      };
    },
    renderCharts() {
      const Chart = this.$Chart;

      // Active vs Past Bookings Donut
      new Chart(this.$refs.bookingChart, {
        type: "doughnut",
        data: { labels: ["Active", "Past"], datasets: [{ data: [this.summary.active, this.summary.past], backgroundColor: ["#0d6efd", "#198754"] }] },
        options: { responsive: true },
      });

      // Monthly Spending Bar
      const labels = Object.keys(this.summary.monthly_cost || {});
      const data = Object.values(this.summary.monthly_cost || {});
      new Chart(this.$refs.costChart, {
        type: "bar",
        data: { labels, datasets: [{ label: "Cost (₹)", data, backgroundColor: "#ffc107" }] },
        options: { responsive: true },
      });
    },
  },
};
</script>

<style scoped>
.kpi-card {
  border-radius: 10px;
  background: linear-gradient(135deg, #007bff, #6610f2);
  color: #fff;
  padding: 15px 10px;
}
</style>
