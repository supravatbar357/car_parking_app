<template>
  <div id="app">
    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark shadow-sm">
      <div class="container-fluid">
        <a class="navbar-brand fw-bold" href="#">🚗 Parking App</a>
        <button
          class="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarNav"
        >
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav ms-auto">
            <li class="nav-item">
              <router-link to="/" class="nav-link">Home</router-link>
            </li>
            <li class="nav-item">
              <router-link to="/login" class="nav-link">Login</router-link>
            </li>
            <li class="nav-item">
              <router-link to="/register" class="nav-link">Register</router-link>
            </li>
          </ul>
        </div>
      </div>
    </nav>

    <!-- Main content (router view) -->
    <main class="container my-5">
      <router-view />
    </main>

    <!-- Footer -->
    <footer class="bg-dark text-white text-center py-3 mt-auto">
      <p class="mb-0">© 2025 Vehicle Parking App | Designed with ❤️</p>
    </footer>
  </div>
</template>

<script>
export default {
  name: "App",
};
</script>
