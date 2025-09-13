<template>
  <div id="app" class="d-flex flex-column min-vh-100">
    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark shadow-sm">
      <div class="container-fluid">
        <a class="navbar-brand fw-bold" href="#">Parking App</a>
        <button
          class="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarNav"
        >
          <span class="navbar-toggler-icon"></span>
        </button>

        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav ms-auto align-items-center">
            <!-- If NOT logged in -->
            <template v-if="!isLoggedIn">
              <li class="nav-item">
                <router-link to="/" class="nav-link">Home</router-link>
              </li>
              <li class="nav-item">
                <router-link to="/login" class="btn btn-outline-light mx-2">
                  Login
                </router-link>
              </li>
              <li class="nav-item">
                <router-link to="/register" class="btn btn-primary">
                  Register
                </router-link>
              </li>
            </template>

            <!-- If logged in -->
            <template v-else>
              <li class="nav-item dropdown">
                <a
                  class="nav-link dropdown-toggle d-flex align-items-center"
                  href="#"
                  id="navbarDropdown"
                  role="button"
                  data-bs-toggle="dropdown"
                  aria-expanded="false"
                >
                  <span class="me-2">👤</span> {{ userName }}
                </a>
                <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="navbarDropdown">
                  <li>
                    <router-link to="/profile" class="dropdown-item">Profile</router-link>
                  </li>
                  <li><hr class="dropdown-divider" /></li>
                  <li>
                    <button class="dropdown-item text-danger" @click="logout">
                      Logout
                    </button>
                  </li>
                </ul>
              </li>
            </template>
          </ul>
        </div>
      </div>
    </nav>

    <!-- Main content -->
    <main class="container my-5 flex-grow-1">
      <router-view />
    </main>

    <!-- Footer -->
    <footer class="bg-dark text-white text-center py-3 mt-auto">
      <p class="mb-0">© 2025 Vehicle Parking App || All right reserved</p>
    </footer>
  </div>
</template>

<script>
export default {
  name: "App",
  data() {
    return {
      isLoggedIn: false,
      userName: "",
    };
  },
  mounted() {
    // Load from localStorage on refresh
    const user = localStorage.getItem("user");
    if (user) {
      const parsed = JSON.parse(user);
      this.isLoggedIn = true;
      this.userName = parsed.name || "User";
    }

    // Listen for login event
    this.$root.$on("user-logged-in", (user) => {
      this.isLoggedIn = true;
      this.userName = user.name || "User";
    });

    // Listen for logout event
    this.$root.$on("user-logged-out", () => {
      this.isLoggedIn = false;
      this.userName = "";
    });
  },
  methods: {
    logout() {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      this.isLoggedIn = false;
      this.userName = "";

      // Notify globally
      this.$root.$emit("user-logged-out");

      this.$router.push("/login");
    },
  },
};
</script>
