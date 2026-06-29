let myChart = null;
export function renderChart(ctx, meta) {
  if (myChart) myChart.destroy();
  myChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: ["CMS Classic", "CMS Mixed"],
      datasets: [
        {
          label: "Mice Error Rate (%)",
          data: [meta.mice_avg_error_classic, meta.mice_avg_error_mixed],
          backgroundColor: ["#e74c3c", "#27ae60"],
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: `Elephant phát hiện: ${meta.elephant_detected}`,
        },
      },
    },
  });
}
