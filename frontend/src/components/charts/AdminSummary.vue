<template>
  <div class="container mt-5">
    <h2 class="text-center mb-4 text-primary fw-bold">📊 Admin Summary Dashboard</h2>

    <!-- Highlighted KPIs -->
    <div class="row g-3 mb-4 justify-content-center">
      <div
        class="col-6 col-sm-4 col-md-3 col-lg-2"
        v-for="(value, key) in kpis"
        :key="key"
      >
        <div class="kpi-card shadow-lg text-center p-3">
          <div class="kpi-icon mb-2">
            <i :class="getKPIIcon(key)"></i>
          </div>
          <small class="text-white">{{ key }}</small>
          <h4 class="fw-bold text-white mt-1">{{ value }}</h4>
        </div>
      </div>
    </div>

    <!-- Charts -->
    <div class="row g-4">
      <div class="col-md-6">
        <div class="card shadow-lg p-3">
          <h5 class="text-center text-success">Reservations Overview</h5>
          <canvas ref="reservationChart"></canvas>
        </div>
      </div>

      <div class="col-md-6">
        <div class="card shadow-lg p-3">
          <h5 class="text-center text-info">Revenue Trends Over Weeks</h5>
          <canvas ref="revenueLineChart"></canvas>
        </div>
      </div>

      <div class="col-md-6">
        <div class="card shadow-lg p-3">
          <h5 class="text-center text-warning">Parking Utilization</h5>
          <canvas ref="utilizationChart"></canvas>
        </div>
      </div>

      <div class="col-md-6">
        <div class="card shadow-lg p-3">
          <h5 class="text-center text-danger">Lots vs Spots</h5>
          <canvas ref="lotsSpotsChart"></canvas>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "AdminSummary",
  data() {
    return {
      summary: null,
      kpis: {},
    };
  },
  async mounted() {
    await this.fetchSummary();
    if (this.summary) {
      this.setKPIs();
      this.renderCharts();
    }
  },
  methods: {
    async fetchSummary() {
      try {
        const token = localStorage.getItem("token");
        const res = await fetch("/api/admin/summary", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!res.ok) throw new Error("Failed to fetch admin summary");
        this.summary = await res.json();
      } catch (err) {
        console.error(err);
      }
    },
    setKPIs() {
      this.kpis = {
        "Total Lots": this.summary.total_lots,
        "Total Spots": this.summary.total_spots,
        "Occupied Spots": this.summary.occupied_spots,
        "Free Spots": this.summary.free_spots,
        "Total Reservations": this.summary.total_reservations,
        "Total Revenue (₹)": this.summary.total_revenue.toFixed(2),
      };
    },
    getKPIIcon(key) {
      const icons = {
        "Total Lots": "fas fa-building fa-2x",
        "Total Spots": "fas fa-parking fa-2x",
        "Occupied Spots": "fas fa-car fa-2x",
        "Free Spots": "fas fa-car-side fa-2x",
        "Total Reservations": "fas fa-receipt fa-2x",
        "Total Revenue (₹)": "fas fa-dollar-sign fa-2x",
      };
      return icons[key] || "fas fa-chart-bar fa-2x";
    },
    renderCharts() {
      const Chart = this.$Chart; // use global Chart.js

      // Reservations Stacked Bar
      new Chart(this.$refs.reservationChart, {
        type: "bar",
        data: {
          labels: ["Reservations"],
          datasets: [
            { label: "Reserved", data: [this.summary.occupied_spots], backgroundColor: "#dc3545" },
            { label: "Unreserved", data: [this.summary.free_spots], backgroundColor: "#28a745" },
          ],
        },
        options: { responsive: true, scales: { x: { stacked: true }, y: { stacked: true, beginAtZero: true } } },
      });

      // Revenue Trend Line
      const weeks = Object.keys(this.summary.weekly_revenue || {}).sort();
      const revenueData = weeks.map((w) => this.summary.weekly_revenue[w]);
      new Chart(this.$refs.revenueLineChart, {
        type: "line",
        data: { labels: weeks, datasets: [{ label: "Revenue (₹)", data: revenueData, borderColor: "#007bff", fill: false }] },
        options: { responsive: true },
      });

      // Parking Utilization Donut
      new Chart(this.$refs.utilizationChart, {
        type: "doughnut",
        data: { labels: ["Occupied", "Free"], datasets: [{ data: [this.summary.occupied_spots, this.summary.free_spots], backgroundColor: ["#fd7e14", "#6c757d"] }] },
        options: { responsive: true },
      });

      // Lots vs Spots Bar
      new Chart(this.$refs.lotsSpotsChart, {
        type: "bar",
        data: { labels: ["Lots", "Spots"], datasets: [{ data: [this.summary.total_lots, this.summary.total_spots], backgroundColor: ["#dc3545", "#6f42c1"] }] },
        options: { responsive: true },
      });
    },
  },
};
</script>

<style scoped>
.kpi-card {
  border-radius: 10px;
  padding: 15px 10px;
  background: linear-gradient(135deg, #007bff, #6610f2);
  color: #fff;
  transition: transform 0.2s, box-shadow 0.2s;
}
.kpi-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.15);
}
.kpi-icon i { font-size: 28px; }
.card { min-height: 300px; }
</style>
