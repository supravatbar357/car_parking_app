<template>
  <div class="container mt-5">
    <div class="card shadow-lg p-4 reservation-card">
      <h3 class="mb-4 text-center text-primary">📝 Reservation Form</h3>

      <!-- Alerts -->
      <div v-if="error" class="alert alert-danger text-center">{{ error }}</div>
      <div v-if="success" class="alert alert-success text-center">{{ success }}</div>

      <form @submit.prevent="makeReservation">
        <!-- Lot ID -->
        <div class="mb-3">
          <label class="form-label fw-bold">Lot ID</label>
          <input type="text" class="form-control" v-model="lotId" disabled />
        </div>

        <!-- Spot ID -->
        <div class="mb-3">
          <label class="form-label fw-bold">Spot ID</label>
          <input type="text" class="form-control" v-model="spotId" disabled />
        </div>

        <!-- Start Time -->
        <div class="mb-3">
          <label class="form-label fw-bold">Start Time</label>
          <input
            type="datetime-local"
            class="form-control"
            v-model="startTime"
            required
          />
          <small class="text-muted">Select the time you plan to park (ISO format).</small>
        </div>

        <!-- Submit -->
        <button type="submit" class="btn btn-primary w-100">
          Confirm Reservation
        </button>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: "ReservationForm",
  data() {
    return {
      lotId: this.$route.params.lotId,
      spotId: this.$route.params.spotId,
      startTime: "",
      error: null,
      success: null,
    };
  },
  methods: {
    async makeReservation() {
      const token = localStorage.getItem("token");
      if (!token) {
        this.error = "You must be logged in to make a reservation.";
        return;
      }

      try {
        const res = await fetch("/api/reservations", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            spot_id: this.spotId,
            lot_id: this.lotId,  // optional, backend ignores if unused
            start_time: this.startTime,
          }),
        });

        if (!res.ok) {
          const errData = await res.json();
          throw new Error(errData.error || "Failed to create reservation");
        }

        await res.json();
        this.success = "✅ Reservation created successfully!";
        this.error = null;

        // Redirect after short delay
        setTimeout(() => {
          this.$router.push("/UserDashboard");
        }, 1500);
      } catch (err) {
        this.error = err.message || "Failed to create reservation";
        this.success = null;
      }
    },
  },
};
</script>
