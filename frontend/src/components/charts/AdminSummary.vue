<template>
  <div class="container mt-5">
    <h2 class="text-center mb-4 fw-bold text-primary">
      🧠 Admin Summary Dashboard
    </h2>

    <!-- Loading Spinner -->
    <div v-if="loading" class="text-center my-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- KPIs Section -->
    <div v-else class="row g-3 justify-content-center mb-4">
      <div
        v-for="(value, key) in kpis"
        :key="key"
        class="col-6 col-sm-4 col-md-3 col-lg-2"
      >
        <div class="kpi-card shadow-lg text-center p-3">
          <i :class="getKPIIcon(key)" class="kpi-icon mb-2"></i>
          <small class="text-white">{{ key }}</small>
          <h4 class="fw-bold text-white mt-1">{{ value }}</h4>
        </div>
      </div>
    </div>

    <!-- Charts Section -->
    <div class="row g-4">
      <div class="col-md-6" v-for="(chart, key) in chartRefs" :key="key">
        <div class="card shadow-sm border-0 chart-card">
          <div class="card-body">
            <h5 class="text-center fw-semibold text-primary mb-3">{{ chart.title }}</h5>
            <canvas :ref="key" height="250"></canvas>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { nextTick } from "vue";

export default {
  name: "AdminSummary",
  data() {
    return {
      summary: null,
      kpis: {},
      loading: true,
      chartInstances: {},
      chartRefs: {
        reservationChart: { title: "Reservations Overview" },
        revenueLineChart: { title: "Weekly Revenue Trend" },
        utilizationChart: { title: "Parking Utilization" },
        lotsSpotsChart: { title: "Lots vs Spots" },
      },
    };
  },
  async mounted() {
    await this.fetchSummary();
    if (this.summary) {
      this.setKPIs();
      await nextTick();
      this.renderCharts();
    }
    this.loading = false;
  },
  methods: {
    async fetchSummary() {
      try {
        const token = localStorage.getItem("token");
        const res = await fetch("http://127.0.0.1:8000/api/admin/summary", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!res.ok) throw new Error("Failed to fetch admin summary");
        this.summary = await res.json();
      } catch (err) {
        console.error("❌ Fetch error:", err);
      }
    },

    setKPIs() {
      this.kpis = {
        "Total Lots": this.summary.total_lots ?? 0,
        "Total Spots": this.summary.total_spots ?? 0,
        "Occupied Spots": this.summary.occupied_spots ?? 0,
        "Free Spots": this.summary.free_spots ?? 0,
        "Total Reservations": this.summary.total_reservations ?? 0,
        "Total Revenue (₹)": this.summary.total_revenue?.toFixed(2) ?? "0.00",
      };
    },

    getKPIIcon(key) {
      const icons = {
        "Total Lots": "fas fa-building fa-2x",
        "Total Spots": "fas fa-parking fa-2x",
        "Occupied Spots": "fas fa-car fa-2x",
        "Free Spots": "fas fa-car-side fa-2x",
        "Total Reservations": "fas fa-ticket-alt fa-2x",
        "Total Revenue (₹)": "fas fa-wallet fa-2x",
      };
      return icons[key] || "fas fa-chart-bar fa-2x";
    },

    renderCharts() {
      const Chart = this.$Chart;
      if (!Chart) {
        console.error("❌ Chart.js not found in global properties.");
        return;
      }

      // Clear old charts
      Object.values(this.chartInstances).forEach((chart) => chart.destroy());

      const anim = { duration: 1200, easing: "easeOutQuart" };

      // 1️⃣ Reservations Overview (Stacked Bar)
      this.chartInstances.reservationChart = new Chart(this.$refs.reservationChart, {
        type: "bar",
        data: {
          labels: ["Reservations"],
          datasets: [
            { label: "Occupied", data: [this.summary.occupied_spots], backgroundColor: "#dc3545" },
            { label: "Free", data: [this.summary.free_spots], backgroundColor: "#28a745" },
          ],
        },
        options: {
          responsive: true,
          plugins: { legend: { position: "bottom" } },
          scales: { x: { stacked: true }, y: { stacked: true, beginAtZero: true } },
          animation: anim,
        },
      });

      // 2️⃣ Weekly Revenue Trend (Line)
      const weeks = Object.keys(this.summary.weekly_revenue || {});
      const revenue = weeks.map((w) => this.summary.weekly_revenue[w]);
      this.chartInstances.revenueLineChart = new Chart(this.$refs.revenueLineChart, {
        type: "line",
        data: {
          labels: weeks.length ? weeks : ["No Data"],
          datasets: [
            {
              label: "Revenue (₹)",
              data: revenue.length ? revenue : [0],
              borderColor: "#007bff",
              backgroundColor: "rgba(0, 123, 255, 0.2)",
              fill: true,
              tension: 0.3,
            },
          ],
        },
        options: {
          responsive: true,
          plugins: { legend: { display: false } },
          scales: { y: { beginAtZero: true } },
          animation: anim,
        },
      });

      // 3️⃣ Utilization (Doughnut)
      this.chartInstances.utilizationChart = new Chart(this.$refs.utilizationChart, {
        type: "doughnut",
        data: {
          labels: ["Occupied", "Free"],
          datasets: [
            {
              data: [this.summary.occupied_spots, this.summary.free_spots],
              backgroundColor: ["#fd7e14", "#6c757d"],
            },
          ],
        },
        options: {
          responsive: true,
          plugins: { legend: { position: "bottom" } },
          animation: anim,
        },
      });

      // 4️⃣ Lots vs Spots (Bar)
      this.chartInstances.lotsSpotsChart = new Chart(this.$refs.lotsSpotsChart, {
        type: "bar",
        data: {
          labels: ["Lots", "Spots"],
          datasets: [
            { data: [this.summary.total_lots, this.summary.total_spots], backgroundColor: ["#6610f2", "#20c997"] },
          ],
        },
        options: {
          responsive: true,
          plugins: { legend: { display: false } },
          scales: { y: { beginAtZero: true } },
          animation: anim,
        },
      });
    },
  },
};
</script>

<style scoped>
.kpi-card {
  border-radius: 12px;
  background: linear-gradient(135deg, #007bff, #6610f2);
  color: #fff;
  transition: all 0.3s ease;
}
.kpi-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
}
.kpi-icon {
  font-size: 28px;
}
.chart-card {
  border-radius: 16px;
  transition: all 0.3s ease;
  min-height: 320px;
}
.chart-card:hover {
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}
</style>
