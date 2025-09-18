<template>
  <div class="container mt-5">
    <h2 class="mb-4">Available Parking Lots</h2>

    <!-- Parking Lots List -->
    <div v-if="parkingLots.length > 0">
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
      </div>
    </div>

    <div v-else>
      <p>No parking lots available.</p>
    </div>
  </div>
</template>

<script>
export default {
  name: "UserDashboard",
  data() {
    return {
      parkingLots: [],
    };
  },
  methods: {
    async fetchParkingLots() {
      const token = localStorage.getItem("token");
      if (!token) {
        console.warn("No token found, redirecting to login...");
        this.$router.push("/login");
        return;
      }

      try {
        const response = await fetch("http://127.0.0.1:5000/api/parking_lots", {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
        });

        console.log("API Status:", response.status);

        if (!response.ok) {
          const errMsg = await response.text();
          console.error("Error fetching parking lots:", errMsg);
          return;
        }

        const data = await response.json();
        console.log("Parking lots API response:", data);

        this.parkingLots = data.parking_lots || [];
      } catch (err) {
        console.error("Fetch error:", err);
      }
    },
  },
  mounted() {
    this.fetchParkingLots();
  },
};
</script>
