<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <div class="card shadow-sm border-0">
          <div class="card-body">
            <h3 class="mb-4 text-center">My Profile</h3>

            <form @submit.prevent="updateProfile">
              <div class="mb-3">
                <label class="form-label">Full Name</label>
                <input v-model="form.name" type="text" class="form-control" required />
              </div>

              <div class="mb-3">
                <label class="form-label">Email</label>
                <input v-model="form.email" type="email" class="form-control" required />
              </div>

              <div class="mb-3">
                <label class="form-label">Password</label>
                <input
                  v-model="form.password"
                  type="password"
                  class="form-control"
                  placeholder="Leave blank to keep current"
                />
              </div>

              <button type="submit" class="btn btn-primary w-100">Update Profile</button>
            </form>

            <div v-if="message" class="alert alert-success mt-3">
              {{ message }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "ProfileView",
  data() {
    return {
      form: {
        name: "",
        email: "",
        password: "",
      },
      message: "",
      user: {},
    };
  },
  mounted() {
    // Load user from localStorage (replace with API call if available)
    this.user = JSON.parse(localStorage.getItem("user") || "{}");
    this.form.name = this.user.name || "";
    this.form.email = this.user.email || "";
  },
  methods: {
    updateProfile() {
      // Simulate API update (keep is_admin intact)
      const updatedUser = {
        ...this.user,
        name: this.form.name,
        email: this.form.email,
      };

      localStorage.setItem("user", JSON.stringify(updatedUser));

      this.message = "Profile updated successfully!";
      this.form.password = ""; // reset password field

      // Redirect after short delay
      setTimeout(() => {
        if (updatedUser.is_admin) {
          this.$router.push("/AdminDashboard");
        } else {
          this.$router.push("/UserDashboard");
        }
      }, 1000);
    },
  },
};
</script>
