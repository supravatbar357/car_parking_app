<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <div class="card shadow-lg p-4 rounded">
          <h3 class="text-center mb-3">Login</h3>

          <!-- Alerts -->
          <div v-if="alertMessage" :class="`alert alert-${alertType}`" role="alert">
            {{ alertMessage }}
          </div>

          <form @submit.prevent="loginUser">
            <div class="mb-3">
              <label class="form-label">Email</label>
              <input v-model="email" type="email" class="form-control" placeholder="Enter your email" required />
            </div>

            <div class="mb-3">
              <label class="form-label">Password</label>
              <input v-model="password" type="password" class="form-control" placeholder="Enter your password" required />
            </div>

            <button type="submit" class="btn btn-success w-100">Login</button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "LoginView",
  data() {
    return {
      email: "",
      password: "",
      alertMessage: null,
      alertType: "success",
    };
  },
  methods: {
    async loginUser() {
      try {
        const response = await fetch("/api/login", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email: this.email,
            password: this.password,
          }),
        });

        let data = {};
        try {
          const text = await response.text();
          data = text ? JSON.parse(text) : {};
        } catch (err) {
          data = {};
        }

        if (!response.ok) {
          throw new Error(data.message || "Login failed");
        }

        this.alertMessage = data.message || "Login successful";
        this.alertType = "success";

        // Save token + user info
        if (data.token) {
          localStorage.setItem("token", data.token);
        }
        if (data.user) {
          localStorage.setItem("user", JSON.stringify(data.user));

          // ✅ Fix: Update App.vue state immediately
          this.$root.isLoggedIn = true;
          this.$root.userName = data.user.name || "User";

          // Still emit event for consistency
          this.$root.$emit("user-logged-in", data.user);
        }

        // Redirect based on role
        setTimeout(() => {
          if (data.user && data.user.is_admin) {
            this.$router.push("/AdminDashboard");
          } else {
            this.$router.push("/UserDashboard");
          }
        }, 1500);

      } catch (error) {
        this.alertMessage = error.message;
        this.alertType = "danger";
      }
    },
  },
};
</script>
