// plugins/chart.js
import { Chart, Title, Tooltip, Legend, BarElement, LineElement, PointElement, CategoryScale, LinearScale, ArcElement } from "chart.js";

export default {
  install(app) {
    // Register all necessary Chart.js components globally
    Chart.register(Title, Tooltip, Legend, BarElement, LineElement, PointElement, CategoryScale, LinearScale, ArcElement);

    // Add Chart.js to Vue global properties
    app.config.globalProperties.$Chart = Chart;
  },
};
