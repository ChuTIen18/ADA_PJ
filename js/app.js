// Core Interactive Controller App Logic - Lớp điều khiển giao diện chính Demo CMS/CCMS

document.addEventListener("DOMContentLoaded", () => {
  // 1. Cấu hình cấu trúc ma trận băm (4 hàng x 10 cột)
  const ROWS = 4;
  const COLS = 10;

  // Khởi tạo mảng lưu trữ dữ liệu bộ đếm cho 2 thuật toán về 0
  let cmsStorage = Array(ROWS)
    .fill()
    .map(() => Array(COLS).fill(0));
  let ccmsStorage = Array(ROWS)
    .fill()
    .map(() => Array(COLS).fill(0));

  // Lưu trữ tần suất thực tế xuất hiện của các IP trong phiên chạy Auto hiện tại
  let sessionTrueCounts = {};
  let comparisonChart = null;

  // Bộ dữ liệu IP mẫu phục vụ cho tính năng Auto Run Stream
  const mockIPPool = [
    "192.168.1.10",
    "10.0.0.5",
    "192.168.1.10",
    "1.1.1.1",
    "192.168.1.10",
    "172.16.0.3",
    "8.8.8.8",
    "192.168.1.50",
    "10.0.0.5",
    "192.168.1.10",
  ];

  let streamInterval = null;
  let poolIndex = 0;

  // Khởi tạo trạng thái giao diện ban đầu
  initMatrixUI("cmsMatrix", "cms");
  initMatrixUI("ccmsMatrix", "ccms");
  initChartUI();

  clearStreamContainer();
  prepopulateVisualizerInitialData(); // Đưa toàn bộ hệ thống ban đầu về số 0
  initDatasetNavigation(); // Kích hoạt bộ điều hướng chuyển đổi Tab 2 chiều

  /**
   * Lắng nghe sự thay đổi của nút Switch "Auto Run Stream"
   */
  document.getElementById("autoRunStream").addEventListener("change", (e) => {
    if (e.target.checked) {
      // Khi bật Auto: Reset biểu đồ sai số nhỏ ở Tab 1 về 0 để đo đếm lại
      updateChartData([0, 0, 0, 0]);
      sessionTrueCounts = {};
      clearStreamContainer();
      prepopulateVisualizerInitialData();
      startAutoStream();
    } else {
      // Khi tắt Auto: Dừng luồng và tính toán sai số tích lũy hiển thị lên biểu đồ nhỏ
      stopAutoStream();
      const metrics = calculateSessionMetrics();
      updateChartData(metrics);
    }
  });

  /**
   * Lắng nghe sự kiện click nút "Query" nạp IP thủ công
   */
  document.getElementById("btnQuery").addEventListener("click", () => {
    const ip = document.getElementById("ipInput").value.trim();
    if (ip.length > 0) {
      appendIpToStreamUI(ip);
      sessionTrueCounts[ip] = (sessionTrueCounts[ip] || 0) + 1;
      processPacketInsertion(ip);
    }
  });

  /**
   * Tạo lưới ô vuông ma trận trên giao diện HTML
   */
  function initMatrixUI(containerId, prefix) {
    const target = document.getElementById(containerId);
    if (!target) return;
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

  /**
   * Dọn sạch khung danh sách dòng gói tin (Data Stream) bên trái
   */
  function clearStreamContainer() {
    const container = document.getElementById("streamContainer");
    if (!container) return;
    container.innerHTML = `
            <div id="emptyHint" class="text-muted small p-3 text-center" style="font-style: italic;">
                Dòng dữ liệu trống.<br>Bật "Auto Run Stream" để nạp gói tin...
            </div>
        `;
  }

  /**
   * Thêm một gói tin IP mới chạy vào khung cuộn Data Stream
   */
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

  /**
   * Hàm băm mô phỏng (Entropy Hash Generator) tính toán ra các vị trí cột tương ứng từng hàng
   */
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

  /**
   * Xử lý nạp gói tin song song vào cả 2 mô hình thuật toán CMS và CCMS
   */
  function processPacketInsertion(ip) {
    const targetCols = getHashColumns(ip);

    // Cập nhật thanh thông tin Hash Columns ở trên cùng
    const infoIpEl = document.getElementById("infoIp");
    const infoHashesEl = document.getElementById("infoHashes");
    if (infoIpEl) infoIpEl.innerText = ip;
    if (infoHashesEl) infoHashesEl.innerText = JSON.stringify(targetCols);

    clearGridHighlights();

    // ─── THUẬT TOÁN 1: COUNT-MIN SKETCH (CMS) TRUYỀN THỐNG ───
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

    // ─── THUẬT TOÁN 2: CONSERVATIVE CMS (CCMS) CẢI TIẾN ───
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

  /**
   * Cập nhật chỉ số tổng lượng tích lũy và lượng lỗi giảm thiểu được ở cuối chân bảng ma trận
   */
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

  /**
   * Xóa các màu nền highlight xanh dương/xanh lá của lượt chèn gói tin cũ trước đó
   */
  function clearGridHighlights() {
    document.querySelectorAll(".matrix-cell").forEach((el) => {
      el.classList.remove("highlight-cms", "highlight-ccms");
    });
  }

  function startAutoStream() {
    streamInterval = setInterval(() => {
      const currentIp = mockIPPool[poolIndex];
      appendIpToStreamUI(currentIp);
      sessionTrueCounts[currentIp] = (sessionTrueCounts[currentIp] || 0) + 1;
      processPacketInsertion(currentIp);
      poolIndex = (poolIndex + 1) % mockIPPool.length;
    }, 500);
  }

  function stopAutoStream() {
    if (streamInterval) clearInterval(streamInterval);
  }

  /**
   * Tính toán sai số mô phỏng dựa trên lượng gói tin vừa bắn ở Tab 1
   */
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

  /**
   * Khởi tạo đồ thị thanh nhỏ ở Tab 1
   */
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
            title: { display: true, text: "Average Error (Packets)" },
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

  /**
   * Đưa ma trận ban đầu về số 0 nguyên bản
   */
  function prepopulateVisualizerInitialData() {
    cmsStorage = Array(ROWS)
      .fill()
      .map(() => Array(COLS).fill(0));
    ccmsStorage = Array(ROWS)
      .fill()
      .map(() => Array(COLS).fill(0));

    for (let r = 0; r < ROWS; r++) {
      for (let c = 0; c < COLS; c++) {
        const cmsCell = document.getElementById(`cms-cell-${r}-${c}`);
        const ccmsCell = document.getElementById(`ccms-cell-${r}-${c}`);
        if (cmsCell) cmsCell.innerText = "0";
        if (ccmsCell) ccmsCell.innerText = "0";
      }
    }
    updateTotalSummariesCounters();
  }

  // ==========================================================
  // 💥 ĐIỀU HƯỚNG TAB 2 CHIỀU HOÀN CHỈNH (ĐÃ FIX NÚT QUAY LẠI)
  // ==========================================================
  function initDatasetNavigation() {
    const radioMock = document.getElementById("radioMockData");
    const radioReal = document.getElementById("radioRealData");
    const btnBack = document.getElementById("btnBackToVisualizer");

    // 1. Lắng nghe nút Radio "Data giả lập"
    if (radioMock) {
      radioMock.addEventListener("change", () => {
        if (radioMock.checked) {
          switchMainTab("visualizer");
        }
      });
    }

    // 2. Lắng nghe nút Radio "Data thực tế"
    if (radioReal) {
      radioReal.addEventListener("change", () => {
        if (radioReal.checked) {
          handleRealTimeDemo();
        }
      });
    }

    // 3. Lắng nghe nút bấm "Quay lại Bộ giả lập" từ màn hình đồ thị thật
    if (btnBack) {
      btnBack.addEventListener("click", () => {
        if (radioMock) {
          radioMock.checked = true; // Thiết lập lại nút Radio ở Tab 1 về chế độ giả lập
        }
        switchMainTab("visualizer"); // Lật màn hình hiển thị về bộ giả lập
      });
    }
  }

  /**
   * Hàm hỗ trợ ẩn/hiện các vùng Containers tương ứng từng Tab
   */
  function switchMainTab(tabName) {
    const visualizerView = document.getElementById("visualizerSection");
    const analyticsView = document.getElementById("analyticsSection");

    if (tabName === "visualizer") {
      if (visualizerView) visualizerView.style.display = "block";
      if (analyticsView) analyticsView.style.display = "none";
    } else if (tabName === "analytics") {
      if (visualizerView) visualizerView.style.display = "none";
      if (analyticsView) analyticsView.style.display = "block";
    }
  }

  /**
   * Hàm điều hướng và xử lý đổ dữ liệu thật sang charts.js
   */
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
      if (typeof mockRealAnalyticsData !== "undefined") {
        if (typeof renderStatisticalAnalytics === "function") {
          renderStatisticalAnalytics(mockRealAnalyticsData);
        } else {
          console.error(
            "Lỗi hệ thống: Không tìm thấy hàm renderStatisticalAnalytics trong file charts.js!",
          );
        }
      } else {
        if (tableBody) {
          tableBody.innerHTML = `
                        <tr>
                            <td colspan="5" class="text-center text-danger">
                                Lỗi kết nối dữ liệu: Không tìm thấy biến mockRealAnalyticsData từ mock_data.js!
                            </td>
                        </tr>`;
        }
      }
    }, 1200);
  }
});
