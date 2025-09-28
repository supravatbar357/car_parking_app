<template>
  <div class="container mt-4">
    <h3>Export Parking Data</h3>

    <div class="mb-3">
      <label>Email:</label>
      <input
        v-model="email"
        type="email"
        class="form-control"
        placeholder="Enter your email"
      />
    </div>

    <button
      class="btn btn-primary"
      :disabled="loading || !email"
      @click="startExport"
    >
      {{ loading ? "Exporting..." : "Start Export" }}
    </button>

    <div v-if="taskId" class="mt-3">
      <p>Task ID: {{ taskId }}</p>
      <p>Status: {{ status }}</p>
      <button
        v-if="downloadUrl"
        class="btn btn-success"
        @click="downloadCsv"
      >
        Download CSV
      </button>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      email: "",
      loading: false,
      taskId: null,
      status: "",
      downloadUrl: null,
      pollInterval: null,
    };
  },
  methods: {
    async startExport() {
      this.loading = true;
      this.status = "Pending...";
      this.taskId = null;
      this.downloadUrl = null;

      try {
        const res = await axios.post("/api/export-parking-data", {
          email: this.email,
        });
        this.taskId = res.data.task_id;
        this.pollStatus();
      } catch (err) {
        console.error(err);
        this.status = "Failed to start export.";
        this.loading = false;
      }
    },
    pollStatus() {
      this.pollInterval = setInterval(async () => {
        try {
          const res = await axios.get(`/api/export_status/${this.taskId}`);
          this.status = res.data.state;

          if (res.data.state === "SUCCESS") {
            clearInterval(this.pollInterval);
            this.status = "Completed!";
            // Assuming your task sends the filename back in info or result
            this.downloadUrl = `/api/exports/${res.data.info}`;
            this.loading = false;
          } else if (res.data.state === "FAILURE") {
            clearInterval(this.pollInterval);
            this.status = "Failed!";
            this.loading = false;
          }
        } catch (err) {
          console.error(err);
          clearInterval(this.pollInterval);
          this.status = "Error checking status.";
          this.loading = false;
        }
      }, 3000); // poll every 3 seconds
    },
    downloadCsv() {
      if (this.downloadUrl) {
        window.open(this.downloadUrl, "_blank");
      }
    },
  },
  beforeUnmount() {
    if (this.pollInterval) clearInterval(this.pollInterval);
  },
};
</script>

<style scoped>
.container {
  max-width: 500px;
}
</style>
