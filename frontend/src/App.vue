<template>
  <div id="app" class="d-flex flex-column min-vh-100">
    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark shadow-sm">
      <div class="container-fluid">
        <router-link class="navbar-brand fw-bold" to="/">Parking App</router-link>

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
                <router-link to="/about" class="nav-link">About</router-link>
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
                  <i class="bi bi-person-circle fs-4 me-2"></i> {{ userName }}
                </a>
                <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="navbarDropdown">
                  <!-- Show Admin Dashboard for admins -->
                  <li v-if="userIsAdmin">
                    <router-link to="/AdminDashboard" class="dropdown-item">
                      Admin Dashboard
                    </router-link>
                  </li>
                  <!-- Show Profile for normal users -->
                  <li v-else>
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
      <p class="mb-0">© 2025 Vehicle Parking App. All rights reserved</p>
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
      userIsAdmin: false,
    };
  },
  created() {
    this.checkAuth();
    window.addEventListener("storage", this.checkAuth); // reactive update if localStorage changes
  },
  beforeUnmount() {
    window.removeEventListener("storage", this.checkAuth);
  },
  methods: {
    checkAuth() {
      const token = localStorage.getItem("token");
      const user = localStorage.getItem("user");

      if (token && user) {
        const parsed = JSON.parse(user);
        this.isLoggedIn = true;
        this.userName = parsed.name || "User";
        this.userIsAdmin = parsed.is_admin || false;
      } else {
        this.isLoggedIn = false;
        this.userName = "";
        this.userIsAdmin = false;
      }
    },
    logout() {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      this.checkAuth();
      this.$router.push("/login");
    },
  },
};
</script>
