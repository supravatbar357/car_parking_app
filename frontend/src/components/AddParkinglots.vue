<template>
  <div class="d-flex justify-content-center align-items-center min-vh-100 bg-light">
    <div class="card shadow-lg rounded-4 form-window">
      <div class="card-body p-4">
        <h2 class="mb-4 text-center text-primary fw-bold">Add Parking Lot</h2>

        <!-- Error message -->
        <div v-if="error" class="alert alert-danger">
          {{ error }}
        </div>

        <!-- Success message -->
        <div v-if="success" class="alert alert-success">
          {{ success }}
        </div>

        <form @submit.prevent="addParkingLot">
          <div class="mb-3">
            <label class="form-label fw-semibold">Prime Location Name</label>
            <input
              v-model="form.prime_location_name"
              type="text"
              class="form-control"
              placeholder="Enter location name"
              required
            />
          </div>

          <div class="mb-3">
            <label class="form-label fw-semibold">Price (₹ per hour)</label>
            <input
              v-model.number="form.price"
              type="number"
              class="form-control"
              placeholder="Enter price"
              min="0"
              required
            />
          </div>

          <div class="mb-3">
            <label class="form-label fw-semibold">Address</label>
            <textarea
              v-model="form.address"
              class="form-control"
              placeholder="Enter address"
              required
            ></textarea>
          </div>

          <div class="mb-3">
            <label class="form-label fw-semibold">Pin Code</label>
            <input
              v-model="form.pin_code"
              type="text"
              class="form-control"
              placeholder="Enter pincode"
              pattern="\d{6}"
              title="6 digit pin code"
              required
            />
          </div>

          <div class="mb-3">
            <label class="form-label fw-semibold">Number of Spots</label>
            <input
              v-model.number="form.number_of_spots"
              type="number"
              class="form-control"
              placeholder="Enter number of spots"
              min="1"
              required
            />
          </div>

          <div class="d-flex justify-content-between mt-4">
            <button type="submit" class="btn btn-success px-4">Add</button>
            <router-link to="/admindashboard" class="btn btn-outline-secondary px-4">Cancel</router-link>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "AddParkinglots",
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
    };
  },
  methods: {
    async addParkingLot() {
      const token = localStorage.getItem("token");
      if (!token) {
        this.error = "Not authorized. Please log in again.";
        return;
      }

      try {
        const response = await fetch("/api/parking_lots", {
          method: "POST",
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

        this.success = "Parking lot added successfully!";
        this.error = null;

        // Reset form
        this.form = {
          prime_location_name: "",
          price: null,
          address: "",
          pin_code: "",
          number_of_spots: null,
        };

        // Redirect to Admin Dashboard after 1 second
        setTimeout(() => {
          this.$router.push("/admindashboard");
        }, 1000);
      } catch (err) {
        this.error = err.message || "Failed to add parking lot.";
        this.success = null;
      }
    },
  },
};
</script>

<style scoped>
.form-window {
  width: 100%;
  max-width: 600px;
  background: #fff;
}
</style>
