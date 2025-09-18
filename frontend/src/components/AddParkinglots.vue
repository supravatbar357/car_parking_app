<template>
  <div class="container mt-4">
    <h2 class="mb-3">Parking Lots</h2>

    <!-- Error message -->
    <div v-if="error" class="alert alert-danger">
      {{ error }}
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center">
      <span>Loading parking lots...</span>
    </div>

    <!-- Parking lots table -->
    <table v-if="!loading && parkingLots.length" class="table table-striped">
      <thead>
        <tr>
          <th>ID</th>
          <th>Prime Location</th>
          <th>Price</th>
          <th>Address</th>
          <th>Pin Code</th>
          <th>Spots</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="lot in parkingLots" :key="lot.id">
          <td>{{ lot.id }}</td>
          <td>{{ lot.prime_location_name }}</td>
          <td>{{ lot.price }}</td>
          <td>{{ lot.address }}</td>
          <td>{{ lot.pin_code }}</td>
          <td>{{ lot.number_of_spots }}</td>
        </tr>
      </tbody>
    </table>

    <!-- If no lots -->
    <div v-if="!loading && !parkingLots.length" class="alert alert-info">
      No parking lots found. Please add one.
    </div>
  </div>
</template>

<script>
export default {
  name: "AdminDashboard",
  data() {
    return {
      parkingLots: [],
      loading: true,
      error: null,
    };
  },
  methods: {
    async fetchParkingLots() {
      try {
        const token = localStorage.getItem("token"); // JWT from login
        if (!token) {
          this.error = "Not authorized. Please log in again.";
          this.loading = false;
          return;
        }

        const response = await fetch("http://127.0.0.1:5000/api/parking_lots", {
          method: "GET",
          headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
          }
        });

        if (!response.ok) {
          const errText = await response.text();
          throw new Error(`Error ${response.status}: ${errText}`);
        }

        const data = await response.json();
        this.parkingLots = data.parking_lots || [];
      } catch (err) {
        this.error = err.message || "Failed to fetch parking lots.";
      } finally {
        this.loading = false;
      }
    },
  },
  mounted() {
    this.fetchParkingLots();
  },
};
</script>

<style scoped>
.container {
  max-width: 900px;
}
</style>
