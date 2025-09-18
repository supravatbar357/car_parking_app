<template>
  <div class="container mt-5">
    <h2 class="mb-4 text-center">🚗 Available Parking Lots</h2>

    <!-- Loading -->
    <div v-if="loading" class="text-center">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2">Fetching parking lots...</p>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="alert alert-danger text-center">
      {{ error }}
    </div>

    <!-- Parking Lots -->
    <div v-else-if="parkingLots.length > 0" class="row g-4">
      <div
        v-for="lot in parkingLots"
        :key="lot.id"
        class="col-md-6 col-lg-4"
      >
        <div class="card shadow-lg border-0 h-100 parking-card">
          <div class="card-body">
            <h5 class="card-title text-primary fw-bold">
              {{ lot.prime_location_name }}
            </h5>
            <p class="mb-1"><strong>💰 Price:</strong> ₹{{ lot.price }} / hr</p>
            <p class="mb-1"><strong>📍 Address:</strong> {{ lot.address }}</p>
            <p class="mb-1"><strong>📮 Pin Code:</strong> {{ lot.pin_code }}</p>
            <p class="mb-3"><strong>🅿️ Total Spots:</strong> {{ lot.number_of_spots }}</p>

            <h6 class="fw-bold">Parking Spots</h6>
            <div class="d-flex flex-wrap gap-2">
              <button
                v-for="spot in lot.spots"
                :key="spot.id"
                :class="[
                  'spot-btn',
                  spot.status === 'A' ? 'available' : 'occupied'
                ]"
                :disabled="spot.status !== 'A'"
                @click="goToReservation(lot.id, spot.id)"
              >
                #{{ spot.id }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- No Lots -->
    <div v-else class="text-center mt-5">
      <p class="text-muted">No parking lots available at the moment.</p>
    </div>

    <!-- My Reservations -->
    <div class="mt-5">
      <h2 class="mb-4 text-center">📋 My Reservations</h2>

      <div v-if="myReservations.length === 0" class="text-center text-muted">
        No active reservations.
      </div>

      <div v-else class="row g-4">
        <div
          v-for="res in myReservations"
          :key="res.id"
          class="col-md-6 col-lg-4"
        >
          <div class="card shadow-lg border-0 h-100 reservation-card">
            <div class="card-body">
              <h5 class="card-title fw-bold text-success">
                Reservation #{{ res.id }}
              </h5>
              <p><strong>🅿️ Spot:</strong> #{{ res.spot_id }}</p>
              <p><strong>⏰ Start:</strong> {{ formatDate(res.parking_timestamp) }}</p>
              <p v-if="res.leaving_timestamp">
                <strong>🏁 Left:</strong> {{ formatDate(res.leaving_timestamp) }}
              </p>
              <p v-if="res.parking_cost">
                <strong>💰 Cost:</strong> ₹{{ res.parking_cost }}
              </p>

              <button
                class="btn btn-warning w-100 mt-2"
                v-if="!res.leaving_timestamp"
                @click="releaseReservation(res.id)"
              >
                Release Spot
              </button>
            </div>
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
      myReservations: [],
      loading: true,
      error: null,
    };
  },
  methods: {
    async fetchParkingLots() {
      const token = localStorage.getItem("token");
      if (!token) {
        this.$router.push("/login");
        return;
      }

      try {
        const res = await fetch("/api/parking_lots", {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (!res.ok) throw new Error("Failed to fetch parking lots");

        const data = await res.json();
        this.parkingLots = data.parking_lots || [];
      } catch (err) {
        this.error = err.message;
      } finally {
        this.loading = false;
      }
    },

    async fetchReservations() {
      const token = localStorage.getItem("token");
      try {
        const res = await fetch("/api/reservations", {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (!res.ok) throw new Error("Failed to fetch reservations");

        const data = await res.json();
        this.myReservations = data.reservations || [];
      } catch (err) {
        this.error = err.message;
      }
    },

    async releaseReservation(reservationId) {
      const token = localStorage.getItem("token");
      try {
        const res = await fetch(`/api/reservations/${reservationId}`, {
          method: "PATCH",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            action: "released",
            leaving_time: new Date().toISOString(),
          }),
        });

        if (!res.ok) {
          const errData = await res.json();
          throw new Error(errData.error || "Failed to release reservation");
        }

        const data = await res.json();
        alert(`Spot released! Total cost: ₹${data.parking_cost}`);

        // Refresh data
        this.fetchReservations();
        this.fetchParkingLots();
      } catch (err) {
        alert(err.message);
      }
    },

    goToReservation(lotId, spotId) {
      if (!lotId || !spotId) return;
      this.$router.push({
        name: "ReservationForm",
        params: { lotId, spotId },
      });
    },

    formatDate(dateStr) {
      return new Date(dateStr).toLocaleString();
    },
  },
  mounted() {
    this.fetchParkingLots();
    this.fetchReservations();
  },
};
</script>

<style scoped>
.container {
  max-width: 1100px;
}

/* Card Styling */
.parking-card,
.reservation-card {
  border-radius: 15px;
  transition: transform 0.2s, box-shadow 0.2s;
}
.parking-card:hover,
.reservation-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
}

/* Spot Buttons */
.spot-btn {
  min-width: 50px;
  padding: 8px 12px;
  border-radius: 8px;
  border: none;
  font-weight: bold;
  color: white;
  cursor: pointer;
  transition: transform 0.15s ease-in-out;
}
.spot-btn:hover:enabled {
  transform: scale(1.1);
}

.spot-btn.available {
  background-color: #28a745; /* Green */
}
.spot-btn.occupied {
  background-color: #dc3545; /* Red */
  cursor: not-allowed;
  opacity: 0.7;
}
</style>
