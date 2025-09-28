<template>
  <div>
    <h4 class="mb-3">📊 Your Parking Summary</h4>

    <div v-if="loading" class="text-center">Loading summary...</div>
    <div v-else>
      <div class="row">
        <div class="col-md-6 mb-4">
          <div class="card p-3 text-center shadow-sm">
            <h5>Total Bookings</h5>
            <p class="display-6 text-primary">{{ summary.total_bookings }}</p>
          </div>
        </div>
        <div class="col-md-6 mb-4">
          <div class="card p-3 text-center shadow-sm">
            <h5>Total Cost</h5>
            <p class="display-6 text-success">₹{{ summary.total_cost }}</p>
          </div>
        </div>
      </div>

      <div class="row">
        <div class="col-md-6 mb-4">
          <div class="card p-3 shadow-sm">
            <h5>Active vs Past Bookings</h5>
            <doughnut-chart :chart-data="bookingChartData" />
          </div>
        </div>
        <div class="col-md-6 mb-4">
          <div class="card p-3 shadow-sm">
            <h5>Booking Cost Over Time</h5>
            <bar-chart :chart-data="costChartData" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Doughnut, Bar } from "vue-chartjs";
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  CategoryScale,
  LinearScale,
  BarElement,
} from "chart.js";

ChartJS.register(Title, Tooltip, Legend, ArcElement, CategoryScale, LinearScale, BarElement);

export default {
  name: "UserSummary",
  components: {
    doughnutChart: {
      extends: Doughnut,
      props: ["chartData"],
      mounted() {
        this.renderChart(this.chartData, { responsive: true, maintainAspectRatio: false });
      },
    },
    barChart: {
      extends: Bar,
      props: ["chartData"],
      mounted() {
        this.renderChart(this.chartData, { responsive: true, maintainAspectRatio: false });
      },
    },
  },
  data() {
    return {
      summary: { total_bookings: 0, total_cost: 0 },
      bookingChartData: null,
      costChartData: null,
      loading: true,
    };
  },
  methods: {
    async fetchSummary() {
      this.loading = true;
      const token = localStorage.getItem("token");
      try {
        const res = await fetch("/api/user/summary", { headers: { Authorization: `Bearer ${token}` } });
        const data = await res.json();

        this.summary = {
          total_bookings: (data.active_reservations_count || 0) + (data.past_reservations_count || 0),
          total_cost: data.total_spent || 0,
        };

        this.bookingChartData = {
          labels: ["Active", "Past"],
          datasets: [{ label: "Bookings", backgroundColor: ["#0d6efd", "#198754"], data: [data.active_reservations_count || 0, data.past_reservations_count || 0] }],
        };

        // For cost over time, you can generate dummy sequential data if not provided
        this.costChartData = {
          labels: data.history?.map(r => `#${r.id}`) || ["Jan", "Feb", "Mar"],
          datasets: [{ label: "Cost", backgroundColor: "#ffc107", data: data.history?.map(r => r.cost) || [0, 0, 0] }],
        };
      } catch (err) {
        console.error("Error fetching user summary:", err);
      } finally {
        this.loading = false;
      }
    },
  },
  mounted() {
    this.fetchSummary();
  },
};
</script>
