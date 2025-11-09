<template>
  <div class="container mt-4">
    <h2 class="text-center mb-4 fw-bold text-primary">
      👤 User Summary Dashboard
    </h2>

    <!-- Loading Spinner -->
    <div v-if="loading" class="text-center my-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- Summary Cards -->
    <div v-else class="row g-4">
      <div
        class="col-md-3"
        v-for="(value, key) in kpis"
        :key="key"
      >
        <div class="card shadow-sm border-0 h-100">
          <div class="card-body text-center">
            <i :class="getKPIIcon(key)" class="text-primary mb-2"></i>
            <h6 class="card-title text-secondary">{{ key }}</h6>
            <h4 class="fw-bold text-dark">{{ value }}</h4>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts Section -->
    <div v-if="summary" class="mt-5 row">
      <!-- Active vs Past Bookings -->
      <div class="col-md-6 mb-4">
        <div class="card shadow-sm border-0">
          <div class="card-body">
            <h5 class="card-title fw-semibold text-center">
              Active vs Past Bookings
            </h5>
            <canvas ref="bookingChart" height="200"></canvas>
          </div>
        </div>
      </div>

      <!-- Monthly Cost Chart -->
      <div class="col-md-6 mb-4">
        <div class="card shadow-sm border-0">
          <div class="card-body">
            <h5 class="card-title fw-semibold text-center">
              Monthly Cost Trend
            </h5>
            <canvas ref="costChart" height="200"></canvas>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import { nextTick } from "vue";

export default {
  name: "UserSummary",
  data() {
    return {
      summary: null,
      kpis: {},
      loading: true,
      chartInstances: {},
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
    // Fetch User Summary Data
    async fetchSummary() {
      try {
        const token = localStorage.getItem("token");
        const res = await fetch("http://127.0.0.1:8000/api/user/summary", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!res.ok) throw new Error("Failed to fetch user summary");
        this.summary = await res.json();
      } catch (err) {
        console.error("❌ Fetch error:", err);
      }
    },

    // Set KPI values from summary
    setKPIs() {
      this.kpis = {
        "Total Bookings": this.summary.total_bookings ?? 0,
        "Total Cost (₹)": this.summary.total_cost?.toFixed(2) ?? "0.00",
        "Active Bookings": this.summary.active ?? 0,
        "Past Bookings": this.summary.past ?? 0,
      };
    },

    // Icon Mapping for KPI Cards
    getKPIIcon(key) {
      const icons = {
        "Total Bookings": "fas fa-ticket-alt fa-2x",
        "Total Cost (₹)": "fas fa-wallet fa-2x",
        "Active Bookings": "fas fa-calendar-check fa-2x",
        "Past Bookings": "fas fa-history fa-2x",
      };
      return icons[key] || "fas fa-chart-bar fa-2x";
    },

    // Render Charts using Chart.js
    renderCharts() {
      const Chart = this.$Chart;
      if (!Chart) {
        console.error("❌ Chart.js not found in global properties.");
        return;
      }

      // Destroy previous chart instances if they exist
      Object.values(this.chartInstances).forEach((chart) => chart.destroy());

      const animationOptions = {
        duration: 1200,
        easing: "easeOutQuart",
      };

      /** Chart 1: Active vs Past Bookings (Doughnut) **/
      const active = this.summary.active || 0;
      const past = this.summary.past || 0;
      const total = active + past;

      this.chartInstances.bookingChart = new Chart(this.$refs.bookingChart, {
        type: "doughnut",
        data: {
          labels: ["Active", "Past"],
          datasets: [
            {
              data: total > 0 ? [active, past] : [1],
              backgroundColor:
                total > 0 ? ["#0d6efd", "#198754"] : ["#6c757d"],
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            legend: { position: "bottom" },
            tooltip: {
              callbacks: {
                label: function (ctx) {
                  return total > 0
                    ? `${ctx.label}: ${ctx.parsed}`
                    : "No Data Available";
                },
              },
            },
          },
          animation: animationOptions,
        },
      });

      /** Chart 2: Monthly Cost Trend (Bar) **/
      const labels = Object.keys(this.summary.monthly_cost || {});
      const data = Object.values(this.summary.monthly_cost || {});

      this.chartInstances.costChart = new Chart(this.$refs.costChart, {
        type: "bar",
        data: {
          labels: labels.length ? labels : ["No Data"],
          datasets: [
            {
              label: "Cost (₹)",
              data: data.length ? data : [0],
              backgroundColor: data.length ? "#ffc107" : "#6c757d",
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                label: function (ctx) {
                  return data.length
                    ? `₹${ctx.parsed.y}`
                    : "No cost data available";
                },
              },
            },
          },
          animation: animationOptions,
          scales: {
            y: { beginAtZero: true },
          },
        },
      });
    },
  },
};
</script>

<style scoped>
.card {
  border-radius: 1rem;
}
.card-title {
  font-size: 1rem;
}
.card-body i {
  display: block;
}
</style>
