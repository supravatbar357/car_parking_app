<template>
  <div class="container mt-5">
    <h2 class="text-center mb-4 text-primary fw-bold">🚗 Smart Parking Dashboard</h2>

    <!-- Search bar -->
    <div class="mb-4 d-flex justify-content-center flex-wrap">
      <input
        v-model="searchQuery"
        type="text"
        class="form-control w-50 me-2 mb-2"
        placeholder="Search by PIN code or location"
      />
      <button class="btn btn-primary mb-2" @click="searchLots">Search</button>
    </div>

    <!-- Tabs -->
    <ul class="nav nav-tabs mt-4">
      <li class="nav-item">
        <button class="nav-link" :class="{ active: activeTab === 'lots' }" @click="activeTab = 'lots'">
          Parking Lots
        </button>
      </li>
      <li class="nav-item">
        <button class="nav-link" :class="{ active: activeTab === 'active' }" @click="activeTab = 'active'">
          Active Reservations
        </button>
      </li>
      <li class="nav-item">
        <button class="nav-link" :class="{ active: activeTab === 'history' }" @click="activeTab = 'history'">
          Booking History
        </button>
      </li>
      <li class="nav-item">
        <button class="nav-link" @click="goToSummary">
          Summary
        </button>
      </li>
    </ul>

    <!-- Parking Lots -->
    <div v-if="activeTab === 'lots'" class="row g-3 mt-3">
      <div v-for="lot in parkingLots" :key="lot.id" class="col-sm-12 col-md-6 col-lg-4">
        <div class="card h-100 shadow-sm hover-card">
          <div class="card-body d-flex flex-column justify-content-between">
            <div>
              <h5 class="card-title">Lot #{{ lot.id }}</h5>
              <p class="card-text">{{ lot.address }}</p>
              <p>
                <span class="badge bg-success me-2">{{ lot.spots.filter(s => s.status === 'A').length }} Available</span>
                <span class="badge bg-secondary">{{ lot.spots.length }} Total</span>
              </p>
            </div>
            <router-link
              :to="{ name: 'ReservationForm', params: { lotId: lot.id } }"
              class="btn btn-success w-100 mt-2"
              :disabled="lot.spots.filter(s => s.status === 'A').length === 0"
            >
              Book Now
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Active Reservations -->
    <div v-if="activeTab === 'active'" class="row g-3 mt-3">
      <div v-if="activeReservations.length === 0" class="col-12 text-muted text-center py-3">No active reservations.</div>
      <div v-for="res in activeReservations" :key="res.id" class="col-sm-12 col-md-6 col-lg-4">
        <div class="card shadow-sm border-primary hover-card">
          <div class="card-body d-flex flex-column justify-content-between">
            <div>
              <h6 class="fw-bold">Reservation #{{ res.id }}</h6>
              <p class="mb-1"><strong>Lot:</strong> {{ res.lot_id }}</p>
              <p class="mb-1"><strong>Spot:</strong> {{ res.spot_id }}</p>
              <p class="mb-1"><strong>Vehicle:</strong> {{ res.vehicle_number }}</p>
              <p class="mb-0"><strong>Start:</strong> {{ res.parking_timestamp }}</p>
            </div>
            <button class="btn btn-danger mt-2" @click="releaseReservation(res.id)">Release</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Booking History -->
    <div v-if="activeTab === 'history'" class="row g-3 mt-3">
      <div v-if="historyReservations.length === 0" class="col-12 text-muted text-center py-3">No past bookings.</div>
      <div v-for="res in historyReservations" :key="res.id" class="col-sm-12 col-md-6 col-lg-4">
        <div class="card shadow-sm border-secondary hover-card">
          <div class="card-body">
            <h6 class="fw-bold">Reservation #{{ res.id }}</h6>
            <p class="mb-1"><strong>Lot:</strong> {{ res.lot_id }}</p>
            <p class="mb-1"><strong>Spot:</strong> {{ res.spot_id }}</p>
            <p class="mb-1"><strong>Vehicle:</strong> {{ res.vehicle_number }}</p>
            <p class="mb-1"><strong>Start:</strong> {{ res.parking_timestamp }}</p>
            <p class="mb-1"><strong>End:</strong> {{ res.leaving_timestamp || 'Ongoing' }}</p>
            <p class="mb-0"><strong>Cost:</strong> {{ res.parking_cost || 'Pending' }}</p>
          </div>
        </div>
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
      activeTab: "lots",
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
      const token = localStorage.getItem("token");
      const res = await fetch("/api/parking_lots", { headers: { Authorization: `Bearer ${token}` } });
      const data = await res.json();
      this.parkingLots = data.parking_lots || [];
    },
    async searchLots() {
      const token = localStorage.getItem("token");
      const url = this.searchQuery ? `/api/parking_lots?query=${this.searchQuery}` : `/api/parking_lots`;
      const res = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });
      const data = await res.json();
      this.parkingLots = data.parking_lots || [];
    },
    async fetchReservations() {
      const token = localStorage.getItem("token");
      const res = await fetch("/api/reservations", { headers: { Authorization: `Bearer ${token}` } });
      const data = await res.json();
      this.reservations = data.reservations || [];
    },
    releaseReservation(id) {
      this.$router.push({ name: "ReleaseForm", params: { id } });
    },
    goToSummary() {
      this.$router.push({ name: "UserSummary" });
    },
  },
  mounted() {
    this.fetchParkingLots();
    this.fetchReservations();
  },
};
</script>

<style scoped>
.hover-card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  border-radius: 12px;
}
.hover-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 20px rgba(0,0,0,0.15);
}
.nav-tabs .nav-link.active {
  background-color: #0d6efd;
  color: white;
  font-weight: 600;
}
.card {
  border-radius: 10px;
}
.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
