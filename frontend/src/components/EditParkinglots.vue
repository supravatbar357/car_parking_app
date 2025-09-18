<template>
  <div class="container mt-5">
    <h2 class="mb-4">Edit Parking Lot</h2>

    <!-- Error message -->
    <div v-if="error" class="alert alert-danger">
      {{ error }}
    </div>

    <!-- Success message -->
    <div v-if="success" class="alert alert-success">
      {{ success }}
    </div>

    <form v-if="lotLoaded" @submit.prevent="updateParkingLot">
      <div class="mb-3">
        <label class="form-label">Prime Location Name</label>
        <input
          v-model="form.prime_location_name"
          type="text"
          class="form-control"
          placeholder="Enter location name"
          required
        />
      </div>

      <div class="mb-3">
        <label class="form-label">Price (₹ per hour)</label>
        <input
          v-model.number="form.price"
          type="number"
          class="form-control"
          placeholder="Enter price"
          required
        />
      </div>

      <div class="mb-3">
        <label class="form-label">Address</label>
        <textarea
          v-model="form.address"
          class="form-control"
          placeholder="Enter address"
          required
        ></textarea>
      </div>

      <div class="mb-3">
        <label class="form-label">Pin Code</label>
        <input
          v-model="form.pin_code"
          type="text"
          class="form-control"
          placeholder="Enter pincode"
          required
        />
      </div>

      <div class="mb-3">
        <label class="form-label">Number of Spots</label>
        <input
          v-model.number="form.number_of_spots"
          type="number"
          class="form-control"
          placeholder="Enter number of spots"
          required
        />
      </div>

      <div class="d-flex justify-content-between">
        <button type="submit" class="btn btn-primary">Update Parking Lot</button>
        <router-link to="/admindashboard" class="btn btn-secondary">Cancel</router-link>
      </div>
    </form>

    <div v-else class="text-center">
      <p>Loading parking lot details...</p>
    </div>
  </div>
</template>

<script>
export default {
  name: "EditParkinglots",
  data() {
    return {
      form: {
        prime_location_name: "",
        price: null,
        address: "",
        pin_code: "",
        number_of_spots: null,
      },
      error: null,
      success: null,
      lotLoaded: false,
    };
  },
  methods: {
    async fetchLot() {
      const token = localStorage.getItem("token");
      if (!token) {
        this.error = "Not authorized. Please log in.";
        return;
      }

      const lotId = this.$route.params.id;

      try {
        const response = await fetch(`/api/parking_lots/${lotId}`, {
          method: "GET",
          headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        });

        if (!response.ok) {
          const errText = await response.text();
          throw new Error(`Error ${response.status}: ${errText}`);
        }

        const data = await response.json();
        this.form = {
          prime_location_name: data.prime_location_name,
          price: data.price,
          address: data.address,
          pin_code: data.pin_code,
          number_of_spots: data.number_of_spots,
        };
        this.lotLoaded = true;
      } catch (err) {
        this.error = err.message || "Failed to fetch parking lot.";
      }
    },
    async updateParkingLot() {
      const token = localStorage.getItem("token");
      const lotId = this.$route.params.id;

      if (!token) {
        this.error = "Not authorized. Please log in.";
        return;
      }

      try {
        const response = await fetch(`/api/parking_lots/${lotId}`, {
          method: "PUT",
          headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify(this.form),
        });

        if (!response.ok) {
          const errText = await response.text();
          throw new Error(`Error ${response.status}: ${errText}`);
        }

        this.success = "Parking lot updated successfully!";
        this.error = null;

        setTimeout(() => {
          this.$router.push("/admindashboard");
        }, 1000);
      } catch (err) {
        this.error = err.message || "Failed to update parking lot.";
        this.success = null;
      }
    },
  },
  mounted() {
    this.fetchLot();
  },
};
</script>

<style scoped>
.container {
  max-width: 600px;
}
</style>
