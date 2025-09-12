<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <div class="card shadow-lg p-4 rounded">
          <h3 class="text-center mb-3">Register</h3>

          <!-- Alerts -->
          <div v-if="alertMessage" :class="`alert alert-${alertType}`" role="alert">
            {{ alertMessage }}
          </div>

          <form @submit.prevent="registerUser">
            <div class="mb-3">
              <label class="form-label">Full Name</label>
              <input v-model="name" type="text" class="form-control" placeholder="Enter your name" required />
            </div>

            <div class="mb-3">
              <label class="form-label">Email</label>
              <input v-model="email" type="email" class="form-control" placeholder="Enter your email" required />
            </div>

            <div class="mb-3">
              <label class="form-label">Password</label>
              <input v-model="password" type="password" class="form-control" placeholder="Enter your password" required />
            </div>

            <div class="mb-3">
              <label class="form-label">Confirm Password</label>
              <input v-model="confirmPassword" type="password" class="form-control" placeholder="Confirm password" required />
            </div>

            <div class="mb-3">
              <small class="text-muted">By registering, you agree to our Terms of Service and Privacy Policy.</small>
            </div>

            <button type="submit" class="btn btn-primary w-100">Register</button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "RegisterView",
  data() {
    return {
      name: "",
      email: "",
      password: "",
      confirmPassword: "",
      alertMessage: null,
      alertType: "success",
    };
  },
  methods: {
    async registerUser() {
      // Check if passwords match
      if (this.password !== this.confirmPassword) {
        this.alertMessage = "Passwords do not match";
        this.alertType = "danger";
        return;
      }

      try {
        const response = await fetch("/api/signup", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            name: this.name,
            email: this.email,
            password: this.password,
          }),
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.message || "Signup failed");
        }

        this.alertMessage = data.message;
        this.alertType = "success";

        // Redirect to login after success
        setTimeout(() => {
          this.$router.push("/home");
        }, 1500);
      } catch (error) {
        this.alertMessage = error.message;
        this.alertType = "danger";
      }
    },
  },
};
</script>
