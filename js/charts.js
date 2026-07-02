let myChart = null;

export function initChart(ctx) {
  if (myChart) {
    myChart.destroy();
  }

  myChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: ["CMS Classic", "CMS Mixed"],
      datasets: [
        {
          label: "Mice Error Rate (%)",
          data: [0, 0],
          backgroundColor: ["#ff1900", "#57db8e"],
        },
      ],
    },
    options: {
      responsive: true,
      animation: { duration: 0 },
      plugins: {
        title: {
          display: true,
          text: "Đang khởi tạo...",
        },
      },
    },
  });

  return myChart;
}

export function updateChart(classicErr, mixedErr, elephantDetected) {
  if (!myChart) return;

  myChart.data.datasets[0].data = [classicErr, mixedErr];
  myChart.options.plugins.title.text = `Elephant phát hiện: ${elephantDetected}`;
  myChart.update("none");
}
