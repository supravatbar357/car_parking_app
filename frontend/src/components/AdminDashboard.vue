<template>
  <div class="container mt-5">
    <h2 class="mb-4">Admin Dashboard</h2>

    <!-- Tabs -->
    <ul class="nav nav-tabs mb-4">
      <li class="nav-item">
        <button
          class="nav-link"
          :class="{ active: activeTab === 'lots' }"
          @click="activeTab = 'lots'"
        >
          Parking Lots
        </button>
      </li>
      <li class="nav-item">
        <button
          class="nav-link"
          :class="{ active: activeTab === 'users' }"
          @click="activeTab = 'users'"
        >
          Users
        </button>
      </li>
    </ul>

    <!-- Parking Lots Tab -->
    <div v-if="activeTab === 'lots'">
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

      <!-- Parking Lots -->
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

              <!-- Parking Spots -->
              <div class="spots-grid" v-if="lot.spots">
                <div
                  v-for="spot in lot.spots"
                  :key="spot.id"
                  class="spot-box"
                  :class="spot.status === 'O' ? 'occupied' : 'available'"
                  :title="spot.status === 'O' ? getSpotDetails(spot) : 'Available'"
                >
                  {{ spot.id }}
                </div>
              </div>
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

    <!-- Users Tab -->
    <div v-if="activeTab === 'users'">
      <h4>Registered Users</h4>
      <div v-if="users.length === 0" class="alert alert-info">
        No users found.
      </div>
      <div v-else class="table-responsive">
        <table class="table table-striped">
          <thead>
            <tr>
              <th>User ID</th>
              <th>Email</th>
              <th>Name</th>
              <th>Parking History</th>
              <th>Total Cost</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in filteredUsers" :key="user.id">
              <td>{{ user.id }}</td>
              <td>{{ user.email }}</td>
              <td>{{ user.name }}</td>
              <td>
                <ul>
                  <li v-for="record in user.history" :key="record.id">
                    Spot {{ record.spot_id }} - ₹{{ record.cost }}
                  </li>
                </ul>
              </td>
              <td>₹{{ getTotalCost(user.history) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "AdminDashboard",
  data() {
    return {
      parkingLots: [],
      users: [],
      loading: true,
      error: null,
      activeTab: "lots",
    };
  },
  computed: {
    filteredUsers() {
      return this.users.filter((u) => u.email !== "admin@gmail.com");
    },
  },
  methods: {
    async fetchParkingLots() {
      const token = localStorage.getItem("token");
      try {
        const response = await fetch("/api/parking_lots", {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(`Error ${response.status}: ${errorText}`);
        }

        const data = await response.json();
        console.log("Fetched lots:", data);

        // handle both { parking_lots: [...] } and [ ... ]
        this.parkingLots = data.parking_lots || data || [];
      } catch (err) {
        console.error("Fetch error:", err);
        this.error = "Failed to fetch parking lots.";
      } finally {
        this.loading = false;
      }
    },
    async fetchUsers() {
      const token = localStorage.getItem("token");
      try {
        const response = await fetch("/api/users", {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(`Error ${response.status}: ${errorText}`);
        }

        const data = await response.json();
        console.log("Fetched users:", data);
        this.users = data.users || data || [];
      } catch (err) {
        console.error("Error fetching users:", err);
      }
    },
    editLot(id) {
      this.$router.push(`/admindashboard/edit-parking-lot/${id}`);
    },
    async deleteLot(id) {
      if (!confirm("Are you sure you want to delete this parking lot?")) return;
      const token = localStorage.getItem("token");
      try {
        const response = await fetch(`/api/parking_lots/${id}`, {
          method: "DELETE",
          headers: { Authorization: `Bearer ${token}` },
        });
        if (response.ok) {
          this.fetchParkingLots();
        } else {
          alert("Failed to delete parking lot.");
        }
      } catch (err) {
        console.error("Delete error:", err);
      }
    },
    getSpotDetails(spot) {
      return `Occupied by User ID: ${spot.user_id || "?"}`;
    },
    getTotalCost(history = []) {
      return history.reduce((sum, r) => sum + (r.cost || 0), 0);
    },
  },
  mounted() {
    this.fetchParkingLots();
    this.fetchUsers();
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
.spots-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 10px;
}
.spot-box {
  width: 35px;
  height: 35px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  font-size: 12px;
  font-weight: bold;
  color: #fff;
}
.available {
  background-color: green;
}
.occupied {
  background-color: red;
}
</style>
