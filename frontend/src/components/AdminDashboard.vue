<template>
  <div class="container mt-5">
    <h2 class="mb-4">Admin Dashboard</h2>

    <!-- Add Parking Lot Button -->
    <div class="mb-4">
      <router-link to="/admindashboard/add-parking-lot" class="btn btn-danger">
        Add Parking Lot
      </router-link>
    </div>

    <!-- Parking Lots List -->
    <div v-if="loading" class="text-center">
      <p>Loading parking lots...</p>
    </div>

    <div v-else-if="error" class="alert alert-danger">
      {{ error }}
    </div>

    <div v-else-if="parkingLots.length > 0">
      <div
        v-for="lot in parkingLots"
        :key="lot.id"
        class="card p-3 mb-3 shadow-sm"
      >
        <h5>{{ lot.prime_location_name }}</h5>
        <p><strong>Price:</strong> {{ lot.price }}</p>
        <p><strong>Address:</strong> {{ lot.address }}</p>
        <p><strong>Pincode:</strong> {{ lot.pin_code }}</p>
        <p><strong>Spots:</strong> {{ lot.number_of_spots }}</p>

        <button class="btn btn-primary btn-sm me-2" @click="editLot(lot.id)">
          Edit
        </button>
        <button class="btn btn-danger btn-sm" @click="deleteLot(lot.id)">
          Delete
        </button>
      </div>
    </div>

    <div v-else>
      <p>No parking lots available.</p>
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
        console.log("Parking lots API response:", data);

        // handle both array and object responses
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
        const response = await fetch(
          `api/parking_lots/${id}`,
          {
            method: "DELETE",
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (!response.ok) {
          const errMsg = await response.text();
          throw new Error(`Delete failed: ${errMsg}`);
        }

        // refresh list after delete
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
