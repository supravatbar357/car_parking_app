<template>
  <div class="container mt-5">
    <h3 class="mb-4 text-center text-primary">🚗 Parking Lots</h3>

    <!-- Search bar -->
    <div class="mb-3 d-flex">
      <input
        v-model="searchQuery"
        type="text"
        class="form-control me-2"
        placeholder="Search by PIN code or location"
      />
      <button class="btn btn-outline-primary" @click="searchLots">Search</button>
    </div>

    <!-- Parking lots table -->
    <table class="table table-bordered table-hover shadow">
      <thead class="table-dark">
        <tr>
          <th>Lot ID</th>
          <th>Address</th>
          <th>Available Spots</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="lot in parkingLots" :key="lot.id">
          <td>{{ lot.id }}</td>
          <td>{{ lot.address }}</td>
          <td>{{ lot.spots.filter(s => s.status === 'A').length }}/{{ lot.spots.length }}</td>
          <td>
            <router-link
              :to="{ name: 'ReservationForm', params: { lotId: lot.id } }"
              class="btn btn-success btn-sm"
              :disabled="lot.spots.filter(s => s.status === 'A').length === 0"
            >
              Book
            </router-link>
          </td>
        </tr>
        <tr v-if="parkingLots.length === 0">
          <td colspan="4" class="text-center text-muted">No parking lots found</td>
        </tr>
      </tbody>
    </table>

    <!-- Tabs for reservations -->
    <ul class="nav nav-tabs mt-4" role="tablist">
      <li class="nav-item">
        <button class="nav-link" :class="{ active: activeTab === 'active' }" @click="activeTab = 'active'">Active Reservations</button>
      </li>
      <li class="nav-item">
        <button class="nav-link" :class="{ active: activeTab === 'history' }" @click="activeTab = 'history'">Booking History</button>
      </li>
    </ul>

    <!-- Active Reservations -->
    <div v-show="activeTab === 'active'" class="mt-3">
      <div v-if="activeReservations.length === 0" class="text-muted">No active reservations.</div>
      <div v-for="res in activeReservations" :key="res.id" class="card mt-3 p-3 shadow-sm">
        <p><strong>Reservation ID:</strong> {{ res.id }}</p>
        <p><strong>Lot ID:</strong> {{ res.lot_id }}</p>
        <p><strong>Spot ID:</strong> {{ res.spot_id }}</p>
        <p><strong>Vehicle:</strong> {{ res.vehicle_number }}</p>
        <p><strong>Start:</strong> {{ res.parking_timestamp }}</p>
        <button class="btn btn-danger btn-sm" @click="releaseReservation(res.id)">Release</button>
      </div>
    </div>

    <!-- Booking History -->
    <div v-show="activeTab === 'history'" class="mt-3">
      <div v-if="historyReservations.length === 0" class="text-muted">No past bookings.</div>
      <div v-for="res in historyReservations" :key="res.id" class="card mt-3 p-3 shadow-sm">
        <p><strong>Reservation ID:</strong> {{ res.id }}</p>
        <p><strong>Lot ID:</strong> {{ res.lot_id }}</p>
        <p><strong>Spot ID:</strong> {{ res.spot_id }}</p>
        <p><strong>Vehicle:</strong> {{ res.vehicle_number }}</p>
        <p><strong>Start:</strong> {{ res.parking_timestamp }}</p>
        <p><strong>End:</strong> {{ res.leaving_timestamp || 'Ongoing' }}</p>
        <p><strong>Cost:</strong> {{ res.parking_cost || 'Pending' }}</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "UserDashboard",
  data() {
    return {
      parkingLots: [],
      reservations: [],
      searchQuery: "",
      activeTab: "active",
    };
  },
  computed: {
    activeReservations() {
      return this.reservations.filter(res => !res.leaving_timestamp);
    },
    historyReservations() {
      return this.reservations.filter(res => res.leaving_timestamp);
    },
  },
  methods: {
    async fetchParkingLots() {
      try {
        const token = localStorage.getItem("token");
        const res = await fetch(`/api/parking_lots`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        const data = await res.json();
        this.parkingLots = data.parking_lots || [];
      } catch (err) {
        console.error("Error fetching parking lots:", err);
      }
    },

    async searchLots() {
      try {
        const token = localStorage.getItem("token");
        const url = this.searchQuery
          ? `/api/parking_lots?query=${this.searchQuery}`
          : `/api/parking_lots`;
        const res = await fetch(url, {
          headers: { Authorization: `Bearer ${token}` },
        });
        const data = await res.json();
        this.parkingLots = data.parking_lots || [];
      } catch (err) {
        console.error("Error searching parking lots:", err);
      }
    },

    async fetchReservations() {
      try {
        const token = localStorage.getItem("token");
        const res = await fetch(`/api/reservations`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        const data = await res.json();
        this.reservations = data.reservations || [];
      } catch (err) {
        console.error("Error fetching reservations:", err);
      }
    },

    releaseReservation(id) {
      this.$router.push({ name: "ReleaseForm", params: { id } });
    },
  },
  mounted() {
    this.fetchParkingLots();
    this.fetchReservations();
  },
};
</script>

<style scoped>
.table-hover tbody tr:hover {
  background-color: #f5f5f5;
}
.nav-tabs .nav-link.active {
  background-color: #0d6efd;
  color: white;
}
</style>
