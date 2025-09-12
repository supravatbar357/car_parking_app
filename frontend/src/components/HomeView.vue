<template>
  <div class="text-center">
    <!-- Hero Section -->
    <div class="p-5 mb-4 bg-light rounded-3 shadow-sm">
      <div class="container py-5">
        <h1 class="display-4 fw-bold text-primary">Welcome to Vehicle Parking</h1>
        <p class="fs-5 text-muted">
          Manage your parking spots efficiently and securely.  
          Please login or register to continue.
        </p>
        <div class="d-flex justify-content-center gap-3 mt-4">
          <router-link
            to="/login"
            class="btn btn-primary btn-lg px-4"
          >
            Login
          </router-link>
          <router-link
            to="/register"
            class="btn btn-outline-secondary btn-lg px-4"
          >
            Register
          </router-link>
        </div>
      </div>
    </div>

    <!-- Features Section -->
    <div class="row mt-5">
      <div class="col-md-4">
        <div class="card shadow-sm border-0">
          <div class="card-body">
            <h5 class="card-title text-primary">🚘 Easy Booking</h5>
            <p class="card-text">Reserve parking spots quickly with just a few clicks.</p>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card shadow-sm border-0">
          <div class="card-body">
            <h5 class="card-title text-success">🔒 Secure</h5>
            <p class="card-text">Safe and secure system for managing your vehicle parking.</p>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card shadow-sm border-0">
          <div class="card-body">
            <h5 class="card-title text-danger">📍 Smart Locations</h5>
            <p class="card-text">Find available parking spaces in the best locations.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "HomeView",
};
</script>
