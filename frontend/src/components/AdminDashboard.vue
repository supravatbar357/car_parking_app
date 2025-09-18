<template>
  <div class="container mt-5">
    <h2 class="mb-4">Admin Dashboard</h2>

    <!-- Add Parking Lot Button -->
    <div class="mb-4 text-end">
      <router-link to="/admindashboard/add-parking-lot" class="btn btn-danger">
        + Add Parking Lot
      </router-link>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center">
      <p>Loading parking lots...</p>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="alert alert-danger">
      {{ error }}
    </div>

    <!-- Parking Lots List -->
    <div v-else-if="parkingLots.length > 0" class="row">
      <div
        v-for="lot in parkingLots"
        :key="lot.id"
        class="col-md-6 col-lg-4 mb-4"
      >
        <div class="card h-100 shadow-sm hover-card">
          <div class="card-body">
            <h5 class="card-title">{{ lot.prime_location_name }}</h5>
            <p class="card-text">
              <span class="badge bg-success me-1">₹{{ lot.price }}/hr</span>
              <span class="badge bg-primary">{{ lot.number_of_spots }} Spots</span>
            </p>
            <p class="card-text"><strong>Address:</strong> {{ lot.address }}</p>
            <p class="card-text"><strong>Pincode:</strong> {{ lot.pin_code }}</p>
          </div>
          <div class="card-footer d-flex justify-content-between">
            <button class="btn btn-primary btn-sm" @click="editLot(lot.id)">
              Edit
            </button>
            <button class="btn btn-danger btn-sm" @click="deleteLot(lot.id)">
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- No lots -->
    <div v-else>
      <p class="alert alert-info">No parking lots available.</p>
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
      const token = localStorage.getItem("token");
      if (!token) {
        this.error = "Not authorized. Please log in again.";
        this.loading = false;
        this.$router.push("/login");
        return;
      }

      try {
        const response = await fetch("/api/parking_lots", {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          const errMsg = await response.text();
          throw new Error(`Error ${response.status}: ${errMsg}`);
        }

        const data = await response.json();
        this.parkingLots = Array.isArray(data)
          ? data
          : data.parking_lots || [];
      } catch (err) {
        console.error("Fetch error:", err);
        this.error = err.message || "Failed to fetch parking lots.";
      } finally {
        this.loading = false;
      }
    },
    editLot(id) {
      this.$router.push(`/admindashboard/edit-parking-lot/${id}`);
    },
    async deleteLot(id) {
      if (!confirm("Are you sure you want to delete this parking lot?")) return;

      const token = localStorage.getItem("token");
      if (!token) return;

      try {
        const response = await fetch(`api/parking_lots/${id}`, {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          const errMsg = await response.text();
          throw new Error(`Delete failed: ${errMsg}`);
        }

        this.fetchParkingLots();
      } catch (err) {
        console.error("Delete error:", err);
        alert("Failed to delete parking lot.");
      }
    },
  },
  mounted() {
    this.fetchParkingLots();
  },
};
</script>

<style scoped>
.hover-card {
  transition: transform 0.2s, box-shadow 0.2s;
}
.hover-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}
.card-footer {
  background-color: #f8f9fa;
}
</style>
