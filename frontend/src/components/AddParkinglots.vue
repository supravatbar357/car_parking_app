<template>
  <div class="container mt-4">
    <h2>Add New Parking Lot</h2>
    <div class="card p-3 mt-3">
      <form @submit.prevent="addParkingLot">
        <div class="row g-2">
          <div class="col-md-3">
            <input type="text" v-model="lot.prime_location_name" class="form-control" placeholder="Prime Location" required />
          </div>
          <div class="col-md-2">
            <input type="number" v-model="lot.price" class="form-control" placeholder="Price" required />
          </div>
          <div class="col-md-3">
            <input type="text" v-model="lot.address" class="form-control" placeholder="Address" required />
          </div>
          <div class="col-md-2">
            <input type="text" v-model="lot.pin_code" class="form-control" placeholder="Pin Code" required />
          </div>
          <div class="col-md-2">
            <input type="number" v-model="lot.number_of_spots" class="form-control" placeholder="Number of Spots" required />
          </div>
        </div>
        <button type="submit" class="btn btn-success mt-3">Add Parking Lot</button>
        <button type="button" class="btn btn-secondary mt-3 ms-2" @click="$router.push('/AdminDashboard')">Cancel</button>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: "AddParkinglots",
  data() {
    return {
      lot: {
        prime_location_name: "",
        price: "",
        address: "",
        pin_code: "",
        number_of_spots: ""
      }
    };
  },
  methods: {
    async addParkingLot() {
      try {
        const token = localStorage.getItem("token");
        const res = await fetch("/api/parking_lots", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`
          },
          body: JSON.stringify(this.lot)
        });
        if (!res.ok) {
          const errData = await res.json();
          throw new Error(errData.message || "Failed to add parking lot");
        }
        alert("Parking lot added successfully!");
        this.$router.push("/AdminDashboard");
      } catch (err) {
        console.error(err);
        alert(err.message);
      }
    }
  }
};
</script>

<style scoped>
input {
  width: 100%;
}
</style>
