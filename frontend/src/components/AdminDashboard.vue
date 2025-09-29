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
      <li class="nav-item">
        <button
          class="nav-link"
          :class="{ active: activeTab === 'summary' }"
          @click="activeTab = 'summary'"
        >
          Summary
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

      <div v-if="loadingLots" class="text-center">Loading parking lots...</div>
      <div v-else-if="errorLots" class="alert alert-danger">{{ errorLots }}</div>

      <div v-else-if="parkingLots.length > 0" class="row">
        <div v-for="lot in parkingLots" :key="lot.id" class="col-md-6 col-lg-4 mb-4">
          <div class="card h-100 shadow-sm hover-card">
            <div class="card-body">
              <h5 class="card-title">{{ lot.prime_location_name }}</h5>
              <p class="card-text">
                <span class="badge bg-success me-1">₹{{ lot.price }}/hr</span>
                <span class="badge bg-primary">{{ lot.number_of_spots }} Spots</span>
              </p>
              <p class="card-text"><strong>Address:</strong> {{ lot.address }}</p>
              <p class="card-text"><strong>Pincode:</strong> {{ lot.pin_code }}</p>

              <div class="spots-grid" v-if="lot.spots">
                <div
                  v-for="spot in lot.spots"
                  :key="spot.id"
                  class="spot-box"
                  :class="spot.status === 'O' ? 'occupied' : 'available'"
                  :title="spot.status === 'O' ? 'Reserved' : 'Available'"
                  @click="spot.status === 'O' ? openReservedSpot(spot) : null"
                >
                  {{ spot.id }}
                </div>
              </div>
            </div>
            <div class="card-footer d-flex justify-content-between">
              <button class="btn btn-primary btn-sm" @click="editLot(lot.id)">Edit</button>
              <button class="btn btn-danger btn-sm" @click="deleteLot(lot.id)">Delete</button>
            </div>
          </div>
        </div>
      </div>

      <div v-else>
        <p class="alert alert-info">No parking lots available.</p>
      </div>
    </div>

    <!-- Users Tab -->
    <div v-if="activeTab === 'users'">
      <h4>Registered Users</h4>
      <div v-if="users.length === 0" class="alert alert-info">No users found.</div>
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

    <!-- Summary Tab -->
    <div v-if="activeTab === 'summary'">
      <AdminSummary />
    </div>

    <!-- Reserved Spot Modal -->
    <div v-if="showSpotDetails" class="modal-overlay">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">🚗 Reserved Parking Spot Details</h5>
          <button class="btn-close" @click="closeSpotDetails"></button>
        </div>
        <div class="modal-body">
          <table class="table table-bordered table-sm">
            <tbody>
              <tr><th>Spot ID</th><td>{{ selectedSpot.id }}</td></tr>
              <tr><th>Customer ID</th><td>{{ selectedSpot.user_id }}</td></tr>
              <tr><th>Vehicle Number</th><td>{{ selectedSpot.car_number }}</td></tr>
              <tr><th>Parking Time</th><td>{{ formatDate(selectedSpot.reservation?.parking_timestamp) }}</td></tr>
            </tbody>
          </table>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="closeSpotDetails">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import AdminSummary from "./charts/AdminSummary.vue";

export default {
  name: "AdminDashboard",
  components: { AdminSummary },
  data() {
    return {
      parkingLots: [],
      users: [],
      loadingLots: true,
      errorLots: null,
      activeTab: "lots",
      showSpotDetails: false,
      selectedSpot: null,
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
        const res = await fetch("/api/parking_lots", {
          headers: { Authorization: `Bearer ${token}` },
        });
        const data = await res.json();
        this.parkingLots = data.parking_lots || [];
      } catch (err) {
        this.errorLots = "Failed to fetch parking lots.";
      } finally {
        this.loadingLots = false;
      }
    },
    async fetchUsers() {
      const token = localStorage.getItem("token");
      try {
        const res = await fetch("/api/users", {
          headers: { Authorization: `Bearer ${token}` },
        });
        const data = await res.json();
        this.users = data.users || [];
      } catch (err) {
        console.error(err);
      }
    },
    editLot(id) {
      this.$router.push(`/admindashboard/edit-parking-lot/${id}`);
    },
    async deleteLot(id) {
      if (!confirm("Are you sure you want to delete this parking lot?")) return;
      const token = localStorage.getItem("token");
      try {
        const res = await fetch(`/api/parking_lots/${id}`, {
          method: "DELETE",
          headers: { Authorization: `Bearer ${token}` },
        });
        if (res.ok) this.fetchParkingLots();
        else alert("Failed to delete parking lot.");
      } catch (err) {
        console.error("Delete error:", err);
      }
    },
    getTotalCost(history = []) {
      return history.reduce((sum, r) => sum + (r.cost || 0), 0);
    },
    openReservedSpot(spot) {
      this.selectedSpot = spot;
      this.showSpotDetails = true;
    },
    closeSpotDetails() {
      this.showSpotDetails = false;
      this.selectedSpot = null;
    },
    formatDate(date) {
      return date ? new Date(date).toLocaleString() : "N/A";
    },
  },
  mounted() {
    this.fetchParkingLots();
    this.fetchUsers();
  },
};
</script>

<style scoped>
.hover-card { transition: transform 0.2s, box-shadow 0.2s; }
.hover-card:hover { transform: translateY(-5px); box-shadow: 0 8px 20px rgba(0,0,0,0.15); }
.card-footer { background-color: #f8f9fa; }
.spots-grid { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; }
.spot-box { width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; border-radius: 6px; font-size: 13px; font-weight: bold; cursor: pointer; color: #fff; transition: transform 0.2s; }
.spot-box:hover { transform: scale(1.1); }
.available { background-color: #28a745; }
.occupied { background-color: #dc3545; }

/* Modal */
.modal-overlay { position: fixed; top:0; left:0; right:0; bottom:0; background-color: rgba(0,0,0,0.5); display:flex; align-items:center; justify-content:center; z-index:1050; }
.modal-content { background:#fff; border-radius:10px; width:420px; max-width:95%; box-shadow:0 5px 25px rgba(0,0,0,0.3); overflow:hidden; }
.modal-header { background:#007bff; color:#fff; padding:12px 16px; display:flex; justify-content:space-between; align-items:center; }
.modal-body { padding:16px; }
.modal-body table { width:100%; }
.modal-footer { background:#f8f9fa; padding:10px 16px; text-align:right; }
.btn-close { background:none; border:none; font-size:20px; color:#fff; cursor:pointer; }
</style>
