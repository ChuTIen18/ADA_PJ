import { mockData } from "./mock_data.js";
import { renderChart } from "./charts.js";

let currentMode = "synthetic";

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
  const nHot = document.getElementById("nHot").value;
  const nCold = document.getElementById("nCold").value;
  console.log(`Simulation running with ${nHot} Elephants and ${nCold} Mice`);

  const data = mockData[currentMode];
  renderChart(document.getElementById("myChart").getContext("2d"), data.meta);

  const tbody = document.querySelector("#top10Table tbody");
  tbody.innerHTML = data.top10
    .map(
      (r) => `
        <tr><td>${r.ip}</td><td>${r.true_count}</td><td>${r.estimate_classic}</td><td>${r.estimate_mixed}</td></tr>
    `,
    )
    .join("");
};
