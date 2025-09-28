<template>
  <div class="container mt-5">
    <h2 class="text-center mb-4 text-primary fw-bold">📊 Admin Summary Dashboard</h2>

    <div class="row g-4">
      <!-- Total Reservations -->
      <div class="col-md-6">
        <div class="card shadow-lg p-3">
          <h5 class="text-center text-success">Total Reservations</h5>
          <canvas id="reservationChart"></canvas>
        </div>
      </div>

      <!-- Revenue -->
      <div class="col-md-6">
        <div class="card shadow-lg p-3">
          <h5 class="text-center text-info">Total Revenue (₹)</h5>
          <canvas id="revenueChart"></canvas>
        </div>
      </div>

      <!-- Parking Utilization -->
      <div class="col-md-6">
        <div class="card shadow-lg p-3">
          <h5 class="text-center text-warning">Parking Utilization</h5>
          <canvas id="utilizationChart"></canvas>
        </div>
      </div>

      <!-- Lots vs Spots -->
      <div class="col-md-6">
        <div class="card shadow-lg p-3">
          <h5 class="text-center text-danger">Lots vs Spots</h5>
          <canvas id="lotsSpotsChart"></canvas>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import {
  Chart,
  Title,
  Tooltip,
  Legend,
  BarElement,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  ArcElement,
} from "chart.js";

Chart.register(
  Title,
  Tooltip,
  Legend,
  BarElement,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  ArcElement
);

export default {
  name: "AdminSummary",
  data() {
    return {
      summary: null,
    };
  },
  async mounted() {
    await this.fetchSummary();
    if (this.summary) {
      this.renderCharts();
    }
  },
  methods: {
    async fetchSummary() {
      try {
        const token = localStorage.getItem("token"); // JWT token saved after login
        const res = await fetch("/api/admin/summary", {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
        });

        if (!res.ok) {
          throw new Error(`HTTP error! status: ${res.status}`);
        }

        this.summary = await res.json();
      } catch (err) {
        console.error("Error fetching admin summary:", err);
      }
    },
    renderCharts() {
      // Reservations Chart
      new Chart(document.getElementById("reservationChart"), {
        type: "bar",
        data: {
          labels: ["Reservations"],
          datasets: [
            {
              label: "Total Reservations",
              data: [this.summary.total_reservations],
              backgroundColor: "blue",
            },
          ],
        },
      });

      // Revenue Chart
      new Chart(document.getElementById("revenueChart"), {
        type: "bar",
        data: {
          labels: ["Revenue"],
          datasets: [
            {
              label: "Total Revenue (₹)",
              data: [this.summary.total_revenue],
              backgroundColor: "green",
            },
          ],
        },
      });

      // Parking Utilization Chart
      new Chart(document.getElementById("utilizationChart"), {
        type: "pie",
        data: {
          labels: ["Occupied", "Free"],
          datasets: [
            {
              label: "Utilization",
              data: [this.summary.occupied_spots, this.summary.free_spots],
              backgroundColor: ["orange", "lightgray"],
            },
          ],
        },
      });

      // Lots vs Spots Chart
      new Chart(document.getElementById("lotsSpotsChart"), {
        type: "bar",
        data: {
          labels: ["Lots", "Spots"],
          datasets: [
            {
              label: "Count",
              data: [this.summary.total_lots, this.summary.total_spots],
              backgroundColor: ["red", "purple"],
            },
          ],
        },
      });
    },
  },
};
</script>

<style scoped>
.card {
  min-height: 300px;
}
</style>
