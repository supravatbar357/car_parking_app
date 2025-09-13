<template>
  <div class="container mt-4">
    <h2 class="mb-4 text-center">Admin Dashboard - Manage Parking Lots</h2>

    <!-- Loading spinner -->
    <div v-if="loading" class="text-center mt-3">
      <span class="spinner-border spinner-border-sm"></span> Loading...
    </div>

    <!-- Empty state -->
    <div v-else-if="parkingLots.length === 0" class="text-center mt-5">
      <div class="card empty-card p-4 shadow-sm">
        <div class="icon mb-3">
          <i class="bi bi-building-add" style="font-size: 3rem;"></i>
        </div>
        <h4>No Parking Lots Defined Yet</h4>
        <p class="text-muted">
          You have not added any parking lots. Click the button below to add your first parking lot.
        </p>
        <button
          class="btn btn-success btn-lg add-btn"
          @click="$router.push('/AdminDashboard/add-parking-lot')"
        >
          + Add New Parking Lot
        </button>
      </div>
    </div>

    <!-- Parking Lots Table -->
    <div v-else>
      <div class="mb-4 text-end">
        <button
          class="btn btn-success"
          @click="$router.push('/AdminDashboard/add-parking-lot')"
        >
          + Add New Parking Lot
        </button>
      </div>

      <table class="table table-striped table-bordered">
        <thead>
          <tr>
            <th>ID</th>
            <th>Location</th>
            <th>Price</th>
            <th>Address</th>
            <th>Pin Code</th>
            <th>Available Spots</th>
            <th style="width: 180px;">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="lot in parkingLots" :key="lot.id">
            <td>{{ lot.id }}</td>
            <td>
              <input
                v-if="lot.editing"
                v-model="lot.prime_location_name"
                class="form-control"
              />
              <span v-else>{{ lot.prime_location_name }}</span>
            </td>
            <td>
              <input
                v-if="lot.editing"
                v-model="lot.price"
                type="number"
                class="form-control"
              />
              <span v-else>₹{{ lot.price }}</span>
            </td>
            <td>
              <input
                v-if="lot.editing"
                v-model="lot.address"
                class="form-control"
              />
              <span v-else>{{ lot.address }}</span>
            </td>
            <td>
              <input
                v-if="lot.editing"
                v-model="lot.pin_code"
                class="form-control"
              />
              <span v-else>{{ lot.pin_code }}</span>
            </td>
            <td>
              {{ lot.spots.filter(s => s.status === "A").length }} /
              {{ lot.number_of_spots }}
            </td>
            <td>
              <!-- Edit / Update -->
              <button
                v-if="!lot.editing"
                class="btn btn-primary btn-sm me-1"
                @click="enableEdit(lot)"
              >
                Edit
              </button>
              <button
                v-else
                class="btn btn-success btn-sm me-1"
                @click="updateLot(lot)"
              >
                Save
              </button>

              <!-- Delete -->
              <button
                class="btn btn-danger btn-sm"
                @click="deleteLot(lot)"
              >
                Delete
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
export default {
  name: "AdminDashboard",
  data() {
    return {
      parkingLots: [],
      loading: false,
    };
  },
  methods: {
    async fetchParkingLots() {
      this.loading = true;
      try {
        const token = localStorage.getItem("token");
        const res = await fetch("/api/parking_lots", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!res.ok) throw new Error("Failed to fetch parking lots");
        const data = await res.json();

        this.parkingLots = data.parking_lots.map((lot) => ({
          ...lot,
          editing: false,
        }));
      } catch (err) {
        console.error(err);
        alert(err.message);
      } finally {
        this.loading = false;
      }
    },

    enableEdit(lot) {
      lot.editing = true;
    },

    async updateLot(lot) {
      try {
        const token = localStorage.getItem("token");
        const res = await fetch(`/api/parking_lots/${lot.id}`, {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            prime_location_name: lot.prime_location_name,
            price: lot.price,
            address: lot.address,
            pin_code: lot.pin_code,
            number_of_spots: lot.number_of_spots,
          }),
        });
        if (!res.ok) {
          const errData = await res.json();
          throw new Error(errData.message || "Failed to update lot");
        }
        const updated = await res.json();
        Object.assign(lot, updated, { editing: false });
        alert("Updated successfully!");
      } catch (err) {
        console.error(err);
        alert(err.message);
      }
    },

    async deleteLot(lot) {
      if (!confirm("Are you sure you want to delete this parking lot?")) return;
      try {
        const token = localStorage.getItem("token");
        const res = await fetch(`/api/parking_lots/${lot.id}`, {
          method: "DELETE",
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!res.ok) {
          const errData = await res.json();
          throw new Error(errData.message || "Failed to delete lot");
        }
        this.parkingLots = this.parkingLots.filter((l) => l.id !== lot.id);
        alert("Deleted successfully!");
      } catch (err) {
        console.error(err);
        alert(err.message);
      }
    },
  },
  mounted() {
    this.fetchParkingLots();
  },
};
</script>

<style scoped>
.table input {
  width: 120px;
}

.empty-card {
  background-color: #e9f7ef;
  border-radius: 12px;
  animation: fadeIn 0.8s ease-in-out;
}

.icon {
  color: #28a745;
  animation: bounce 1.2s infinite;
}

.add-btn {
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
  40% { transform: translateY(-10px); }
  60% { transform: translateY(-5px); }
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
