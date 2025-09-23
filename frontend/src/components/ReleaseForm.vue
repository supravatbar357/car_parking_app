<template>
  <div class="container mt-4">
    <div class="card shadow p-4">
      <h3 class="text-center text-danger">🚪 Release Parking Spot</h3>

      <form @submit.prevent="releaseSpot">
        <div class="mb-3">
          <label class="form-label">Customer Name</label>
          <input type="text" v-model="form.customer_name" class="form-control" readonly />
        </div>

        <div class="mb-3">
          <label class="form-label">Vehicle Number</label>
          <input type="text" v-model="form.vehicle_number" class="form-control" readonly />
        </div>

        <div class="mb-3">
          <label class="form-label">Spot ID</label>
          <input type="text" v-model="form.spot_id" class="form-control" readonly />
        </div>

        <div class="mb-3">
          <label class="form-label">Booking Time</label>
          <input type="text" v-model="form.parking_timestamp" class="form-control" readonly />
        </div>

        <div class="d-flex justify-content-between">
          <button type="submit" class="btn btn-danger">Release</button>
          <button type="button" class="btn btn-secondary" @click="$router.push('/userdashboard')">Cancel</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: "ReleaseForm",
  data() {
    return {
      form: {
        customer_name: "",
        vehicle_number: "",
        spot_id: "",
        parking_timestamp: "",
      }
    };
  },
  async mounted() {
    try {
      const token = localStorage.getItem("token");
      const res = await fetch(`/api/reservations/${this.$route.params.id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await res.json();

      // prefill form
      this.form.customer_name = data.user_name || ""; // ensure your backend adds this
      this.form.vehicle_number = data.vehicle_number;
      this.form.spot_id = data.spot_id;
      this.form.parking_timestamp = data.parking_timestamp;
    } catch (err) {
      console.error("Failed to load reservation:", err);
    }
  },
  methods: {
    async releaseSpot() {
      try {
        const token = localStorage.getItem("token");
        const res = await fetch(`/api/reservations/${this.$route.params.id}`, {
          method: "PATCH",
          headers: { 
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json" 
          },
          body: JSON.stringify({ 
            action: "released", 
            leaving_time: new Date().toISOString() 
          })
        });

        if (!res.ok) {
          const errorData = await res.json();
          throw new Error(errorData.error || "Release failed");
        }

        alert("Spot released successfully!");
        this.$router.push("/userdashboard");
      } catch (err) {
        console.error("Release error:", err);
        alert("Failed to release spot.");
      }
    }
  }
};
</script>
