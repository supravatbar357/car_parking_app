// plugins/chart.js
import {
  Chart,
  Title,
  Tooltip,
  Legend,
  BarElement,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  ArcElement,
  BarController,
  LineController,
  DoughnutController,
  PieController,
} from "chart.js";

export default {
  install(app) {
    Chart.register(
      // Controllers
      BarController,
      LineController,
      DoughnutController,
      PieController,
      // Elements
      BarElement,
      LineElement,
      PointElement,
      ArcElement,
      // Scales
      CategoryScale,
      LinearScale,
      // Plugins
      Title,
      Tooltip,
      Legend
    );

    app.config.globalProperties.$Chart = Chart;
  },
};
