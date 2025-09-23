<template>
  <div class="container mt-4">
    <div class="card shadow p-4">
      <h3 class="text-center text-primary">📝 Reservation Form</h3>

      <form @submit.prevent="reserveSpot">
        <div class="mb-3">
          <label class="form-label">Lot ID</label>
          <input type="text" v-model="form.lot_id" class="form-control" readonly />
        </div>

        <div class="mb-3">
          <label class="form-label">Spot ID</label>
          <input type="text" v-model="form.spot_id" class="form-control" readonly />
        </div>

        <div class="mb-3">
          <label class="form-label">User ID</label>
          <input type="text" v-model="form.user_id" class="form-control" readonly />
        </div>

        <div class="mb-3">
          <label class="form-label">Start Time</label>
          <input type="text" v-model="form.start_time" class="form-control" readonly />
        </div>

        <div class="mb-3">
          <label class="form-label">Vehicle Number</label>
          <input type="text" v-model="form.vehicle_no" class="form-control" required />
        </div>

        <div class="d-flex justify-content-between">
          <button type="submit" class="btn btn-success">Reserve</button>
          <button type="button" class="btn btn-secondary" @click="$router.push('/userdashboard')">Cancel</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: "ReservationForm",
  data() {
    return {
      form: {
        lot_id: this.$route.params.lotId || "",
        spot_id: "",
        user_id: "",
        start_time: new Date().toISOString(),
        vehicle_no: ""
      }
    };
  },
  async mounted() {
    try {
      const token = localStorage.getItem("token");

      // Get logged-in user
      const userRes = await fetch(`/api/profile`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const userData = await userRes.json();
      this.form.user_id = userData.id;

      // Assign first available spot (backend should handle logic)
      const spotRes = await fetch(`/api/parking_lots/${this.form.lot_id}/spots`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const spots = await spotRes.json();
      const availableSpot = spots.find(s => s.status === "A");
      if (availableSpot) {
        this.form.spot_id = availableSpot.id;
      }
    } catch (err) {
      console.error(err);
    }
  },
  methods: {
    async reserveSpot() {
      try {
        const token = localStorage.getItem("token");
        const res = await fetch(`/api/reservations`, {
          method: "POST",
          headers: { 
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json" 
          },
          body: JSON.stringify(this.form)
        });
        if (!res.ok) throw new Error("Reservation failed");
        alert("Reservation successful!");
        this.$router.push("/userdashboard");
      } catch (err) {
        console.error(err);
      }
    }
  }
};
</script>
