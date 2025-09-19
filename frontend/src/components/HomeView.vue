<template>
  <div class="home-view">

    <!-- Hero / Search -->
    <div class="hero-section rounded-3 shadow-sm mb-4">
      <div class="container py-4 d-md-flex align-items-center justify-content-between content">
        <div class="me-md-4 text-white">
          <h1 class="display-5 fw-bold">Smart parking for every trip</h1>
          <p class="lead mb-3">
            Find, reserve and pay for parking in seconds — secure, real-time availability across top locations.
          </p>
          <p class="mb-0 small">
            Use the search box to find parking near your area — you can reserve after signing in via the navbar.
          </p>
        </div>

        <!-- Search card -->
        <div class="card shadow-sm mt-4 mt-md-0" style="min-width:320px; max-width:420px;">
          <div class="card-body p-3">
            <label class="form-label mb-2">Find parking near</label>
            <div class="input-group">
              <input
                v-model="pin"
                @keyup.enter="searchByPin"
                type="text"
                class="form-control"
                placeholder="Enter PIN code or city (e.g. 226001)"
                aria-label="Search parking by pin or city"
              />
              <button class="btn btn-primary" @click="searchByPin" aria-label="Find parking">
                <i class="bi bi-search me-1"></i> Find
              </button>
            </div>

            <div class="d-flex gap-2 mt-3">
              <button class="btn btn-outline-secondary flex-fill" @click="browseAll">
                <i class="bi bi-list-ul me-1"></i> Browse all lots
              </button>
              <button
                v-if="!isLoggedIn"
                class="btn btn-outline-light flex-fill"
                @click="$router.push('/login')"
              >
                <i class="bi bi-box-arrow-in-right me-1"></i> Sign in to reserve
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick stats -->
    <div class="row text-center mb-4">
      <div class="col-6 col-md-3 mb-3">
        <div class="border rounded p-3 h-100">
          <h4 class="mb-0">1,200+</h4>
          <small class="text-muted">Available spots</small>
        </div>
      </div>
      <div class="col-6 col-md-3 mb-3">
        <div class="border rounded p-3 h-100">
          <h4 class="mb-0">25+</h4>
          <small class="text-muted">Prime locations</small>
        </div>
      </div>
      <div class="col-6 col-md-3 mb-3">
        <div class="border rounded p-3 h-100">
          <h4 class="mb-0">10k+</h4>
          <small class="text-muted">Trusted users</small>
        </div>
      </div>
      <div class="col-6 col-md-3 mb-3">
        <div class="border rounded p-3 h-100">
          <h4 class="mb-0">From ₹20/hr</h4>
          <small class="text-muted">Affordable pricing</small>
        </div>
      </div>
    </div>

    <!-- Features -->
    <div class="row g-3 mb-5">
      <div class="col-md-3" v-for="feature in features" :key="feature.title">
        <div class="card h-100 shadow-sm border-0">
          <div class="card-body text-center">
            <div class="fs-2 mb-2">{{ feature.icon }}</div>
            <h6 class="card-title">{{ feature.title }}</h6>
            <p class="small text-muted">{{ feature.desc }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- How it works -->
    <div class="mb-5">
      <h3 class="h5 mb-3 text-center">How it works</h3>
      <div class="row text-center">
        <div class="col-md-4 mb-3" v-for="step in steps" :key="step.title">
          <div class="p-3 border rounded h-100">
            <div class="fs-3 mb-2">{{ step.icon }}</div>
            <h6>{{ step.title }}</h6>
            <p class="small text-muted">{{ step.desc }}</p>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
export default {
  name: "HomeView",
  data() {
    return {
      pin: "",
      isLoggedIn: !!localStorage.getItem("token"),
      features: [
        { icon: "🚘", title: "Quick booking", desc: "Reserve instantly without the hassle." },
        { icon: "📍", title: "Real-time availability", desc: "See which spots are free now." },
        { icon: "🔒", title: "Secure payments", desc: "Safe transactions & receipts." },
        { icon: "⚙️", title: "24/7 support", desc: "Help when you need it." },
      ],
      steps: [
        { icon: "1️⃣", title: "Search", desc: "Enter a PIN/city to find nearby parking spots." },
        { icon: "2️⃣", title: "Reserve", desc: "Choose a slot and reserve instantly (login required)." },
        { icon: "3️⃣", title: "Park", desc: "Arrive, verify your booking and park safely." },
      ],
    };
  },
  methods: {
    searchByPin() {
      const target = "/userdashboard";
      const trimmed = (this.pin || "").trim();
      if (trimmed) {
        this.$router.push({ path: target, query: { pin: trimmed } });
      } else {
        this.$router.push(target);
      }
    },
    browseAll() {
      this.$router.push("/userdashboard");
    },
  },
  mounted() {
    window.addEventListener("storage", () => {
      this.isLoggedIn = !!localStorage.getItem("token");
    });
  },
  beforeUnmount() {
    window.removeEventListener("storage", () => {
      this.isLoggedIn = !!localStorage.getItem("token");
    });
  },
};
</script>
<style scoped>
/* Hero Section */
.hero-section {
  position: relative;
  background: url("@/assets/parking-bg.png") no-repeat center center;
  background-size: cover;
  color: white;
  min-height: 70vh;
  display: flex;
  align-items: center;
  border-radius: 0;
}

.hero-section::before {
  content: "";
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
}

.hero-section .content {
  position: relative;
  z-index: 1;
  width: 100%;
}

/* Page background */
.home-view {
  background: #f4f6f9;   /* light gray instead of white */
  min-height: 100vh;
  padding: 2rem 0;
}

/* Section wrappers */
.section {
  background: #ffffff;
  border-radius: 12px;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}

/* Stats cards */
.home-view .row.text-center .border {
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.05);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.home-view .row.text-center .border:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 12px rgba(0,0,0,0.1);
}

/* Feature cards */
.home-view .card {
  border-radius: 14px;
  background: #fff;
  border: none;
  box-shadow: 0 3px 10px rgba(0,0,0,0.05);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.home-view .card:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 14px rgba(0,0,0,0.12);
}

/* Feature icons bigger */
.home-view .card .fs-2 {
  font-size: 2.2rem;
}
.home-view .card-body h6 {
  font-weight: 600;
  margin-top: 0.5rem;
}

/* Section titles */
.home-view h3.h5 {
  font-weight: 700;
  color: #333;
  margin-bottom: 1.5rem;
}

/* Steps cards */
.home-view .p-3.border {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  transition: transform 0.2s ease;
}
.home-view .p-3.border:hover {
  transform: translateY(-3px);
}

/* Lead text */
.home-view .lead {
  max-width: 46rem;
}
@media (min-width: 768px) {
  .home-view .display-5 { font-size: 2.4rem; }
}
</style>
