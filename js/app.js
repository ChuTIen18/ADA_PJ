import { mockData } from "./mock_data.js";
import { initChart, updateChart } from "./charts.js";

let currentMode = "synthetic";

const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

function renderTableRows(data) {
  const tbody = document.querySelector("#top10Table tbody");
  if (!tbody) return;

  tbody.innerHTML = data.top10
    .map(
      (r) => `
        <tr>
          <td>${r.ip}</td>
          <td>${r.true_count}</td>
          <td>${r.estimate_classic}</td>
          <td>${r.estimate_mixed}</td>
        </tr>
      `,
    )
    .join("");
}

function updateTableRealtime(progress, totalPackets, data) {
  const tbody = document.querySelector("#top10Table tbody");
  if (!tbody) return;

  const rows = tbody.querySelectorAll("tr");
  const progressRatio = Math.min(progress / totalPackets, 1);

  data.top10.forEach((row, index) => {
    const rowElement = rows[index];
    if (!rowElement) return;

    const classicValue = Math.max(
      0,
      Math.round(row.estimate_classic * (0.75 + progressRatio * 0.5)),
    );
    const mixedValue = Math.max(
      0,
      Math.round(row.estimate_mixed * (0.8 + progressRatio * 0.4)),
    );

    rowElement.cells[2].textContent = classicValue;
    rowElement.cells[3].textContent = mixedValue;
  });
}

function getSimulationParams() {
  const nHotInput = document.getElementById("nHot");
  const nColdInput = document.getElementById("nCold");

  const nHot = Math.max(1, parseInt(nHotInput?.value, 10) || 5);
  const nCold = Math.max(0, parseInt(nColdInput?.value, 10) || 9995);
  const totalPackets = nHot + nCold;

  return { nHot, nCold, totalPackets };
}

async function runSimulation() {
  const runBtn = document.getElementById("runBtn");
  const statusText = document.getElementById("statusText");
  const progressBar = document.getElementById("progressBar");
  const modeNotification = document.getElementById("modeNotification");

  runBtn.disabled = true;
  const data = mockData[currentMode];
  const { nHot, totalPackets } = getSimulationParams();

  initChart(document.getElementById("myChart").getContext("2d"));
  renderTableRows(data);

  statusText.innerText = "Trạng thái: Đang khởi tạo sketch CMS...";
  modeNotification.innerText = `Đang xử lý: 0% (0/${totalPackets.toLocaleString()} packets)`;
  progressBar.style.width = "0%";
  updateInterimUI(0, nHot);

  try {
    await delay(800);

    const batchSize = Math.max(1, Math.floor(totalPackets / 40));

    for (let i = 0; i <= totalPackets; i += batchSize) {
      const percent = Math.round((i / totalPackets) * 100);
      const progressFactor = 1 - i / totalPackets;
      const mockClassic = (Math.random() * 40 + 60) * progressFactor;
      const mockMixed = (Math.random() * 10 + 5) * progressFactor;
      const found = Math.min(nHot, Math.floor((i / totalPackets) * nHot));

      statusText.innerText = `Trạng thái: Đang stream ${i.toLocaleString()} packets...`;
      modeNotification.innerText = `Đang xử lý: ${percent}% (${i.toLocaleString()}/${totalPackets.toLocaleString()} packets)`;
      progressBar.style.width = `${percent}%`;

      updateChart(mockClassic.toFixed(1), mockMixed.toFixed(1), found);
      updateTableRealtime(i, totalPackets, data);
      updateInterimUI(i / batchSize, nHot);

      await delay(30);
    }

    statusText.innerText = "Trạng thái: Hoàn tất";
    modeNotification.innerText = "Hoàn tất simulation!";
    progressBar.style.width = "100%";
    updateChart(
      data.meta.mice_avg_error_classic,
      data.meta.mice_avg_error_mixed,
      data.meta.elephant_detected,
    );
  } finally {
    runBtn.disabled = false;
  }
}

function updateInterimUI(batchIndex, nHot) {
  const stats = document.getElementById("interimStats");
  const detected = Math.min(nHot, Math.floor((batchIndex / 40) * nHot));
  stats.innerHTML = `
    <small>
      CMS Classic: Elephant detected ${detected}/${nHot} | 
      Mice Error: ${Math.floor(Math.random() * 50) + 10}%
    </small>
  `;
}

document.getElementById("btnSynthetic").onclick = () => {
  currentMode = "synthetic";
  updateModeUI();
};
document.getElementById("btnReal").onclick = () => {
  currentMode = "real";
  updateModeUI();
};

function updateModeUI() {
  document
    .querySelectorAll(".source-btn")
    .forEach((b) => b.classList.toggle("active"));
  document.getElementById("modeNotification").innerText =
    `Đang xem: ${currentMode === "synthetic" ? "Data giả lập" : "Data thực tế"}`;
}

document.getElementById("runBtn").onclick = () => {
  runSimulation();
};
