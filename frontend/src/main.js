// import { createApp } from 'vue'
// import App from './App.vue'
// import router from './router'

// const app = createApp(App)

// app.use(router)

// app.mount('#app')

import { createApp } from 'vue';
import App from './App.vue';
import router from './router';

// Chart.js imports
import { Chart, Title, Tooltip, Legend, BarElement, LineElement, PointElement, CategoryScale, LinearScale, ArcElement } from 'chart.js';

// Register Chart.js components globally
Chart.register(
  Title,
  Tooltip,
  Legend,
  BarElement,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  ArcElement
);

const app = createApp(App);

app.use(router);

app.mount('#app');
