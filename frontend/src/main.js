import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import ChartPlugin from "./plugins/chart"; // <-- this is critical!

const app = createApp(App);
app.use(router);
app.use(ChartPlugin); // <-- register Chart.js globally
app.mount("#app");
