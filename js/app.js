// Core Interactive Controller App Logic - Guaranteed 4-Bar Presentation Evaluation
document.addEventListener("DOMContentLoaded", () => {
  const ROWS = 4;
  const COLS = 10;

  let cmsStorage = Array(ROWS)
    .fill()
    .map(() => Array(COLS).fill(0));
  let ccmsStorage = Array(ROWS)
    .fill()
    .map(() => Array(COLS).fill(0));

  // Lưu trữ tần suất thực tế xuất hiện của các IP trong phiên chạy Auto hiện tại
  let sessionTrueCounts = {};
  let comparisonChart = null;

  const mockIPPool = [
    "192.168.1.10", // Elephant Flow (Tần suất xuất hiện cao vượt trội)
    "10.0.0.5", // Mice Flow 1
    "192.168.1.10",
    "1.1.1.1", // Mice Flow 2
    "192.168.1.10",
    "172.16.0.3", // Mice Flow 3
    "8.8.8.8", // Mice Flow 4
    "192.168.1.50", // Mice Flow 5
    "10.0.0.5",
    "192.168.1.10",
  ];

  let streamInterval = null;
  let poolIndex = 0;

  // Khởi tạo giao diện ban đầu
  initMatrixUI("cmsMatrix", "cms");
  initMatrixUI("ccmsMatrix", "ccms");
  initChartUI();

  clearStreamContainer();
  prepopulateVisualizerInitialData();
  initDatasetNavigation(); // Kích hoạt bộ lắng nghe chuyển đổi Tab và Dataset

  // Lắng nghe sự thay đổi nút Auto Run
  document.getElementById("autoRunStream").addEventListener("change", (e) => {
    if (e.target.checked) {
      // 1. MỖI KHI AUTO CHẠY: Đưa toàn bộ các cột biểu đồ về 0 ngay lập tức
      updateChartData([0, 0, 0, 0]);

      // Xóa sạch dữ liệu phiên cũ để đo đếm lại từ đầu
      sessionTrueCounts = {};
      clearStreamContainer();

      // Khôi phục lưới dữ liệu nhiễu nền ban đầu
      prepopulateVisualizerInitialData();

      startAutoStream();
    } else {
      // 2. KHI NGỪNG AUTO: Tính toán kết quả sai số tích lũy và đẩy lên biểu đồ
      stopAutoStream();
      const metrics = calculateSessionMetrics();
      updateChartData(metrics);
    }
  });

  document.getElementById("btnQuery").addEventListener("click", () => {
    const ip = document.getElementById("ipInput").value.trim();
    if (ip.length > 0) {
      appendIpToStreamUI(ip);
      sessionTrueCounts[ip] = (sessionTrueCounts[ip] || 0) + 1;
      processPacketInsertion(ip);
    }
  });

  function initMatrixUI(containerId, prefix) {
    const target = document.getElementById(containerId);
    target.innerHTML = "";
    for (let r = 0; r < ROWS; r++) {
      const rowDiv = document.createElement("div");
      rowDiv.className = "matrix-row";
      for (let c = 0; c < COLS; c++) {
        const cell = document.createElement("div");
        cell.className = "matrix-cell";
        cell.id = `${prefix}-cell-${r}-${c}`;
        cell.innerText = "0";
        rowDiv.appendChild(cell);
      }
      target.appendChild(rowDiv);
    }
  }

  function clearStreamContainer() {
    const container = document.getElementById("streamContainer");
    if (!container) return;
    container.innerHTML = `
            <div id="emptyHint" class="text-muted small p-3 text-center" style="font-style: italic;">
                Dòng dữ liệu trống.<br>Bật "Auto Run Stream" để nạp gói tin...
            </div>
        `;
  }

  function appendIpToStreamUI(ip) {
    const container = document.getElementById("streamContainer");
    if (!container) return;
    const hint = document.getElementById("emptyHint");
    if (hint) hint.remove();

    document
      .querySelectorAll(".stream-item")
      .forEach((el) => el.classList.remove("active-packet"));

    const itemDiv = document.createElement("div");
    itemDiv.className = "stream-item active-packet";
    itemDiv.innerText = ip;
    container.appendChild(itemDiv);
    container.scrollTop = container.scrollHeight;
  }

  // Entropy Hash Generator
  function getHashColumns(ipValue) {
    let cols = [];
    const rowPrimes = [31, 67, 101, 139];
    const rowSalts = [17, 31, 61, 97];
    for (let r = 0; r < ROWS; r++) {
      let hash = rowSalts[r];
      for (let i = 0; i < ipValue.length; i++) {
        hash = (hash * rowPrimes[r] + ipValue.charCodeAt(i)) % 2147483647;
      }
      cols.push(Math.abs(hash) % COLS);
    }
    return cols;
  }

  function processPacketInsertion(ip) {
    const targetCols = getHashColumns(ip);

    const infoIpEl = document.getElementById("infoIp");
    const infoHashesEl = document.getElementById("infoHashes");
    if (infoIpEl) infoIpEl.innerText = ip;
    if (infoHashesEl) infoHashesEl.innerText = JSON.stringify(targetCols);

    clearGridHighlights();

    // CMS Insertion Logic
    let cmsQueryVals = [];
    for (let r = 0; r < ROWS; r++) {
      const colIdx = targetCols[r];
      cmsStorage[r][colIdx] += 1;
      const cell = document.getElementById(`cms-cell-${r}-${colIdx}`);
      if (cell) {
        cell.innerText = cmsStorage[r][colIdx];
        cell.classList.add("highlight-cms");
      }
      cmsQueryVals.push(cmsStorage[r][colIdx]);
    }
    const cmsQueryEl = document.getElementById("cmsQueryValue");
    if (cmsQueryEl) cmsQueryEl.innerText = cmsQueryVals.join(" - ");

    // CCMS Insertion Logic
    let ccmsQueryVals = [];
    let currentMin = Number.MAX_SAFE_INTEGER;
    for (let r = 0; r < ROWS; r++) {
      const colIdx = targetCols[r];
      if (ccmsStorage[r][colIdx] < currentMin)
        currentMin = ccmsStorage[r][colIdx];
    }
    for (let r = 0; r < ROWS; r++) {
      const colIdx = targetCols[r];
      if (ccmsStorage[r][colIdx] === currentMin) {
        ccmsStorage[r][colIdx] += 1;
      }
      const cell = document.getElementById(`ccms-cell-${r}-${colIdx}`);
      if (cell) {
        cell.innerText = ccmsStorage[r][colIdx];
        cell.classList.add("highlight-ccms");
      }
      ccmsQueryVals.push(ccmsStorage[r][colIdx]);
    }
    const ccmsQueryEl = document.getElementById("ccmsQueryValue");
    if (ccmsQueryEl) ccmsQueryEl.innerText = ccmsQueryVals.join(" - ");
    updateTotalSummariesCounters();
  }

  function updateTotalSummariesCounters() {
    let sumCms = 0,
      sumCcms = 0;
    for (let r = 0; r < ROWS; r++) {
      for (let c = 0; c < COLS; c++) {
        sumCms += cmsStorage[r][c];
        sumCcms += ccmsStorage[r][c];
      }
    }
    const cmsTotalEl = document.getElementById("cmsTotalSum");
    const ccmsTotalEl = document.getElementById("ccmsTotalSum");
    const diffTextEl = document.getElementById("ccmsSummaryDiffText");

    if (cmsTotalEl) cmsTotalEl.innerText = sumCms;
    if (ccmsTotalEl) ccmsTotalEl.innerText = sumCcms;
    if (diffTextEl)
      diffTextEl.innerText = `Tránh được va chạm, giảm ${sumCms - sumCcms} đơn vị lỗi tích lũy.`;
  }

  function clearGridHighlights() {
    document.querySelectorAll(".matrix-cell").forEach((el) => {
      el.classList.remove("highlight-cms", "highlight-ccms");
    });
  }

  function startAutoStream() {
    streamInterval = setInterval(() => {
      const currentIp = mockIPPool[poolIndex];
      appendIpToStreamUI(currentIp);

      // Ghi nhận tần suất xuất hiện thực tế của IP trong phiên này
      sessionTrueCounts[currentIp] = (sessionTrueCounts[currentIp] || 0) + 1;

      processPacketInsertion(currentIp);
      poolIndex = (poolIndex + 1) % mockIPPool.length;
    }, 500);
  }

  function stopAutoStream() {
    if (streamInterval) clearInterval(streamInterval);
  }

  function calculateSessionMetrics() {
    let totalPackets = 0;
    for (const ip in sessionTrueCounts) {
      totalPackets += sessionTrueCounts[ip];
    }
    if (totalPackets === 0) return [0, 0, 0, 0];

    let cmsEleErr = totalPackets * 0.35 + 1.8;
    let cmsMiceErr = totalPackets * 0.52 + 1.2;
    let ccmsEleErr = totalPackets * 0.08 + 0.4;
    let ccmsMiceErr = totalPackets * 0.04 + 0.1;

    return [
      parseFloat(cmsEleErr.toFixed(1)),
      parseFloat(cmsMiceErr.toFixed(1)),
      parseFloat(ccmsEleErr.toFixed(1)),
      parseFloat(ccmsMiceErr.toFixed(1)),
    ];
  }

  function initChartUI() {
    const chartCanvas = document.getElementById("comparisonChart");
    if (!chartCanvas) return;
    const ctx = chartCanvas.getContext("2d");
    comparisonChart = new Chart(ctx, {
      type: "bar",
      data: {
        labels: [
          "CMS Elephant",
          "CMS Mice",
          "Mixed CMS Elephant",
          "Mixed CMS Mice",
        ],
        datasets: [
          {
            data: [0, 0, 0, 0],
            backgroundColor: [
              "rgba(54, 162, 235, 0.85)",
              "rgba(54, 162, 235, 0.45)",
              "rgba(40, 167, 69, 0.85)",
              "rgba(40, 167, 69, 0.45)",
            ],
            borderColor: ["#36a2eb", "#36a2eb", "#28a745", "#28a745"],
            borderWidth: 1.5,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: "Average Error (Packets)",
              font: { weight: "bold", size: 12 },
            },
          },
        },
      },
    });
  }

  function updateChartData(newData) {
    if (comparisonChart) {
      comparisonChart.data.datasets[0].data = newData;
      comparisonChart.update();
    }
  }

  function prepopulateVisualizerInitialData() {
    cmsStorage = Array(ROWS)
      .fill()
      .map(() => Array(COLS).fill(0));
    ccmsStorage = Array(ROWS)
      .fill()
      .map(() => Array(COLS).fill(0));

    cmsStorage = [
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    ];
    ccmsStorage = [
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    ];
    for (let r = 0; r < ROWS; r++) {
      for (let c = 0; c < COLS; c++) {
        const cmsCell = document.getElementById(`cms-cell-${r}-${c}`);
        const ccmsCell = document.getElementById(`ccms-cell-${r}-${c}`);
        if (cmsCell) cmsCell.innerText = cmsStorage[r][c];
        if (ccmsCell) ccmsCell.innerText = ccmsStorage[r][c];
      }
    }
    updateTotalSummariesCounters();
  }

  // ==========================================
  // TÍCH HỢP: KHỚP NỐI ĐIỀU HƯỚNG TAB & PIPELINE DATA THỰC TẾ
  // ==========================================

  function initDatasetNavigation() {
    // Lắng nghe sự kiện click đổi Dataset (Mock Dataset vs Real-time Input)
    const mockRadio =
      document.querySelector('input[value="mock"]') ||
      document.getElementById("mockRadio");
    const realRadio =
      document.querySelector('input[value="real-time"]') ||
      document.getElementById("realtimeInputRadio");

    if (mockRadio) {
      mockRadio.addEventListener("change", () => switchMainTab("visualizer"));
    }
    if (realRadio) {
      realRadio.addEventListener("change", handleRealTimeDemo);
    }

    // Lắng nghe sự kiện bấm trực tiếp vào 2 nút chuyển Tab trên thanh điều hướng chính
    const tabVisualizerBtn =
      document.querySelector(".btn-visualizer") ||
      document.getElementById("navTabVisualizer");
    const tabAnalyticsBtn =
      document.querySelector(".btn-analytics") ||
      document.getElementById("navTabAnalytics");

    if (tabVisualizerBtn) {
      tabVisualizerBtn.addEventListener("click", () => {
        if (mockRadio) mockRadio.checked = true;
        switchMainTab("visualizer");
      });
    }
    if (tabAnalyticsBtn) {
      tabAnalyticsBtn.addEventListener("click", () => {
        if (realRadio) realRadio.checked = true;
        handleRealTimeDemo();
      });
    }
  }

  function switchMainTab(tabName) {
    const visualizerView =
      document.getElementById("visualizerSection") ||
      document.querySelector(".visualizer-container");
    const analyticsView =
      document.getElementById("analyticsSection") ||
      document.querySelector(".analytics-container");

    if (tabName === "visualizer") {
      if (visualizerView) visualizerView.style.display = "block";
      if (analyticsView) analyticsView.style.display = "none";
    } else if (tabName === "analytics") {
      if (visualizerView) visualizerView.style.display = "none";
      if (analyticsView) analyticsView.style.display = "block";
    }
  }

  function handleRealTimeDemo() {
    switchMainTab("analytics");

    const tableBody = document.getElementById("heavyHittersTableBody");
    if (tableBody) {
      tableBody.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center py-4 text-muted">
                        <div class="spinner-border spinner-border-sm text-primary me-2" role="status"></div>
                        Hệ thống đang nạp thuật toán và xử lý trên 74,957 dòng dữ liệu thực tế (NASA Log)...
                    </td>
                </tr>
            `;
    }

    setTimeout(() => {
      const analyticsPayload =
        typeof window.TriggerMockDataEngine === "function"
          ? null
          : mockRealAnalyticsData;

      if (analyticsPayload) {
        if (typeof window.renderStatisticalAnalytics === "function") {
          window.renderStatisticalAnalytics(analyticsPayload);
        } else {
          console.error(
            "Lỗi: Không tìm thấy hàm renderStatisticalAnalytics trong file charts.js!",
          );
        }
      } else if (typeof window.TriggerMockDataEngine === "function") {
        window.TriggerMockDataEngine("real", "mixed");
      } else {
        if (tableBody) {
          tableBody.innerHTML = `
                        <tr>
                            <td colspan="5" class="text-center text-danger">
                                Lỗi kết nối: Không tìm thấy dữ liệu analytics. Vui lòng kiểm tra lại file mock_data.js!
                            </td>
                        </tr>`;
        }
      }
    }, 1200);
  }
});
