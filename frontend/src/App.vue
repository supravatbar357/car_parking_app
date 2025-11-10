<template>
  <div id="app" class="d-flex flex-column min-vh-100">
    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg custom-navbar shadow-sm">
      <div class="container-fluid">
        <router-link class="navbar-brand fw-bold text-light" to="/">
           Parking App
        </router-link>

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
              <router-link to="/Home" class="nav-link">Home</router-link>
              </li>
              <li class="nav-item">
                <router-link to="/about" class="nav-link">About</router-link>
              </li>
              <li class="nav-item">
                <router-link to="/login" class="btn btn-outline-light mx-2">
                  Login
                </router-link>
              </li>
              <li class="nav-item">
                <router-link to="/register" class="btn btn-warning fw-bold">
                  Register
                </router-link>
              </li>
            </template>

            <!-- If logged in -->
            <template v-else>
              <li class="nav-item dropdown">
                <a
                  class="nav-link dropdown-toggle d-flex align-items-center text-light"
                  href="#"
                  id="navbarDropdown"
                  role="button"
                  data-bs-toggle="dropdown"
                  aria-expanded="false"
                >
                  <i class="bi bi-person-circle fs-4 me-2"></i> {{ userName }}
                </a>
                <ul class="dropdown-menu dropdown-menu-end shadow-sm" aria-labelledby="navbarDropdown">
                  <!-- Show Admin Dashboard for admins -->
                  <li v-if="userIsAdmin">
                    <router-link to="/AdminDashboard" class="dropdown-item">
                      <i class="bi bi-speedometer2 me-2"></i> Admin Dashboard
                    </router-link>
                  </li>
                  <!-- Show Profile for normal users -->
                  <li v-else>
                    <router-link to="/profile" class="dropdown-item">
                      <i class="bi bi-person-lines-fill me-2"></i> Profile
                    </router-link>
                  </li>
                  <li><hr class="dropdown-divider" /></li>
                  <li>
                    <button class="dropdown-item text-danger" @click="logout">
                      <i class="bi bi-box-arrow-right me-2"></i> Logout
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
    <footer class="custom-footer text-center py-3 mt-auto">
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
    window.addEventListener("storage", this.checkAuth);
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

<style scoped>
/* Navbar with gradient */
.custom-navbar {
  background: linear-gradient(90deg, #0a0f3c, #1f4e79, #007bff);
  padding: 0.8rem 1rem;
}
.custom-navbar .nav-link {
  color: white !important;
  font-weight: 500;
  transition: all 0.3s ease;
}
.custom-navbar .nav-link:hover {
  color: #ffc107 !important;
}
.navbar-brand {
  font-size: 1.4rem;
  color: #fff !important;
  letter-spacing: 1px;
}

/* Dropdown menu */
.dropdown-menu {
  border-radius: 0.5rem;
  border: none;
  animation: fadeIn 0.2s ease-in-out;
}
.dropdown-item:hover {
  background-color: #f8f9fa;
}

/* Footer with gradient */
.custom-footer {
  background: linear-gradient(90deg, #0a0f3c, #1f4e79, #007bff);
  color: white;
  font-weight: 500;
  box-shadow: 0 -4px 10px rgba(0, 0, 0, 0.15);
}

/* Smooth dropdown animation */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-5px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
