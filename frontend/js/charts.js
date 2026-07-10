function renderTop10Table(containerId, top10Array, options = {}) {
  const container = document.getElementById(containerId);
  if (!container) return;

  const threshold = Number(options.threshold ?? 0.5);
  const isComparison = Boolean(options.isComparison);

  const rows = (Array.isArray(top10Array) ? top10Array : [])
    .map((item, index) => {
      const isHot = item.is_hot === true || item.is_elephant === true;
      const typeLabel = isHot ? "Elephant Flow " : "Mice Flow ";
      const trueCount = Number(item.true_count ?? 0);
      const estimateCount = Number(item.estimate ?? item.estimate_count ?? 0);
      const mixedEstimate = Number(item.mixed_estimate ?? 0);

      let rowClass = "";
      let badge = "";

      if (!isHot && trueCount > 0) {
        const deviation = (estimateCount - trueCount) / trueCount;
        if (deviation >= threshold) {
          rowClass = "table-danger";
          badge = ' <span class="badge bg-danger ms-1">⚠️ Sai số lớn</span>';
        }
      }

      if (isComparison) {
        return `
          <tr class="${rowClass}">
            <td class="fw-bold text-center">${index + 1}</td>
            <td><code class="text-dark">${item.ip}</code></td>
            <td class="fw-semibold">${typeLabel}</td>
            <td class="text-end">${trueCount.toLocaleString()}</td>
            <td class="text-end fw-semibold">${estimateCount.toLocaleString()}${badge}</td>
            <td class="text-end fw-semibold">${mixedEstimate.toLocaleString()}</td>
          </tr>`;
      }

      return `
        <tr class="${rowClass}">
          <td class="fw-bold text-center">${index + 1}</td>
          <td><code class="text-dark">${item.ip}</code></td>
          <td class="fw-semibold">${typeLabel}</td>
          <td class="text-end">${trueCount.toLocaleString()}</td>
          <td class="text-end fw-bold">${estimateCount.toLocaleString()}${badge}</td>
        </tr>`;
    })
    .join("");

  const headers = isComparison
    ? `
      <th scope="col" class="text-center" style="width: 60px;">STT</th>
      <th scope="col">Địa chỉ IP</th>
      <th scope="col">Phân loại</th>
      <th scope="col" class="text-end">True Count</th>
      <th scope="col" class="text-end">Classic</th>
      <th scope="col" class="text-end">Mixed</th>`
    : `
      <th scope="col" class="text-center" style="width: 60px;">STT</th>
      <th scope="col">Địa chỉ IP</th>
      <th scope="col">Phân loại</th>
      <th scope="col" class="text-end">True Count</th>
      <th scope="col" class="text-end">Estimated</th>`;

  container.innerHTML = `
    <div class="table-responsive">
      <table class="table table-hover align-middle border">
        <thead class="table-light">
          <tr>${headers}</tr>
        </thead>
        <tbody>${rows || '<tr><td colspan="5" class="text-center text-muted">Không có dữ liệu hiển thị</td></tr>'}</tbody>
      </table>
    </div>`;
}

function renderErrorBarChart(canvasId, classicMiceError, mixedMiceError) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;

  new Chart(ctx, {
    type: "bar",
    data: {
      labels: ["Classic CMS (k=3)", "Mixed Hypergraph CMS"],
      datasets: [
        {
          label: "Sai số trung bình",
          data: [Number(classicMiceError), Number(mixedMiceError)],
          backgroundColor: ["#dc3545", "#198754"],
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: { y: { beginAtZero: true, ticks: { maxTicksLimit: 4 } } },
    },
  });
}

function renderDetectionBarChart(
  canvasId,
  classicDetected,
  classicTotal,
  mixedDetected,
  mixedTotal,
) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;

  const classicRate =
    classicTotal > 0 ? (classicDetected / classicTotal) * 100 : 0;
  const mixedRate = mixedTotal > 0 ? (mixedDetected / mixedTotal) * 100 : 0;

  new Chart(ctx, {
    type: "bar",
    data: {
      labels: ["Classic", "Mixed"],
      datasets: [
        {
          label: "Tỷ lệ phát hiện (%)",
          data: [classicRate, mixedRate],
          backgroundColor: ["#0d6efd", "#fd7e14"],
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        y: { min: 0, max: 100, ticks: { maxTicksLimit: 4 } },
      },
    },
  });
}

window.renderTop10Table = renderTop10Table;
window.renderErrorBarChart = renderErrorBarChart;
window.renderDetectionBarChart = renderDetectionBarChart;
