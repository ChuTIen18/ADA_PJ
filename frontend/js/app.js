let lastResponse = null;
let currentDataSource = "synthetic";

function getElementByAnyId(ids) {
  for (const id of ids) {
    const el = document.getElementById(id);
    if (el) return el;
  }
  return null;
}

function getTableContainerId() {
  return document.getElementById("heavyHittersTableBody")
    ? "heavyHittersTableBody"
    : "content";
}

function updateUIElementsAndLabels() {
  const labelEl = document.getElementById("dataSourceLabel");
  if (!labelEl) return;

  if (currentDataSource === "real" || currentDataSource === "nasa") {
    labelEl.className =
      "alert alert-success fw-bold text-center py-2 shadow-sm mb-3";
    labelEl.innerText = "📊 Đang xem: Data thực tế (NASA HTTP Access Log)";
  } else {
    labelEl.className =
      "alert alert-warning fw-bold text-center py-2 text-dark shadow-sm mb-3";
    labelEl.innerText =
      "🧪 Đang xem: Data giả lập (Synthetic Step Distribution)";
  }
}

function enableStepControls(enable) {
  const btnMixed =
    document.getElementById("btnRunMixedScript") ||
    document.getElementById("btnMixed");
  const tabMixed = document.getElementById("tab-mixed");
  const tabCompare = document.getElementById("tab-compare");

  const toggleState = (el, isEnabled) => {
    if (!el) return;
    el.disabled = !isEnabled;
    el.classList.toggle("disabled", !isEnabled);
    el.classList.toggle("opacity-50", !isEnabled);
    el.setAttribute("aria-disabled", String(!isEnabled));
  };

  if (enable) {
    toggleState(btnMixed, true);
    toggleState(tabMixed, true);
    toggleState(tabCompare, true);
  } else {
    toggleState(btnMixed, false);
    toggleState(tabMixed, false);
    toggleState(tabCompare, false);
  }
}

function activateMixedControls() {
  const btnMixed =
    document.getElementById("btnRunMixedScript") ||
    document.getElementById("btnMixed");
  const mixedTab = document.getElementById("tab-mixed");
  const compareTab = document.getElementById("tab-compare");

  if (btnMixed) {
    btnMixed.disabled = false;
    btnMixed.classList.remove("disabled", "opacity-50");
    btnMixed.setAttribute("aria-disabled", "false");
  }

  if (mixedTab) {
    mixedTab.disabled = false;
    mixedTab.classList.remove("disabled", "opacity-50");
    mixedTab.setAttribute("aria-disabled", "false");
  }

  if (compareTab) {
    compareTab.disabled = false;
    compareTab.classList.remove("disabled", "opacity-50");
    compareTab.setAttribute("aria-disabled", "false");
  }
}

function switchTabDOM(tabId) {
  const tabTrigger = document.getElementById(tabId);
  if (tabTrigger && typeof bootstrap !== "undefined") {
    const tabInstance = bootstrap.Tab.getOrCreateInstance(tabTrigger);
    tabInstance.show();
  }
}

async function runSimulation(dataSource, params) {
  const spinner = document.getElementById("simulationSpinner");
  if (spinner) spinner.style.display = "inline-block";

  try {
    currentDataSource = dataSource;

    if (typeof window.api?.simulate === "function") {
      lastResponse = await window.api.simulate(dataSource, params);
    } else if (typeof window.MockDataRepository !== "undefined") {
      await new Promise((resolve) => setTimeout(resolve, 400));

      const mockDataset = window.MockDataRepository[dataSource] || {};
      const mockResults = mockDataset.results
        ? {
            classic: mockDataset.results.classic || mockDataset.classic || {},
            mixed: mockDataset.results.mixed || mockDataset.mixed || {},
          }
        : {
            classic: mockDataset.classic || {},
            mixed: mockDataset.mixed || {},
          };

      lastResponse = {
        success: true,
        data_source: dataSource,
        results: mockResults,
      };
    } else {
      console.error("Không tìm thấy API thật hoặc mock data!");
      return;
    }

    updateUIElementsAndLabels();
    showClassicPanel();
    switchTabDOM("tab-classic");
    activateMixedControls();
    enableStepControls(true);
  } catch (error) {
    console.error("Lỗi khi chạy mô phỏng:", error);
  } finally {
    if (spinner) spinner.style.display = "none";
  }
}

function showClassicPanel() {
  if (!lastResponse || !lastResponse.results?.classic) return;

  const classicData = lastResponse.results.classic;
  if (typeof window.renderTop10Table === "function") {
    window.renderTop10Table(getTableContainerId(), classicData.top10 || [], {
      algorithm: "classic",
    });
  }
}

function showMixedPanel() {
  if (!lastResponse || !lastResponse.results?.mixed) return;

  const mixedData = lastResponse.results.mixed;
  if (typeof window.renderTop10Table === "function") {
    window.renderTop10Table(getTableContainerId(), mixedData.top10 || [], {
      algorithm: "mixed",
    });
  }
}

function showComparisonTab() {
  if (
    !lastResponse ||
    !lastResponse.results?.classic ||
    !lastResponse.results?.mixed
  )
    return;

  const classic = lastResponse.results.classic;
  const mixed = lastResponse.results.mixed;

  const contentEl = document.getElementById("content");
  if (contentEl && !document.getElementById("miceErrorChart")) {
    contentEl.innerHTML = `
      <div class="row g-3 align-items-stretch">
        <div class="col-md-6">
          <div class="border rounded p-2 bg-white shadow-sm h-100">
            <h6 class="fw-bold text-center border-bottom pb-2 mb-2 small">Tỷ lệ phát hiện Elephant Flow (%)</h6>
            <div style="height: 220px;">
              <canvas id="elephantChart"></canvas>
            </div>
          </div>
        </div>
        <div class="col-md-6">
          <div class="border rounded p-2 bg-white shadow-sm h-100">
            <h6 class="fw-bold text-center border-bottom pb-2 mb-2 small">Sai số trung bình dòng Mice Flow</h6>
            <div style="height: 220px;">
              <canvas id="miceErrorChart"></canvas>
            </div>
          </div>
        </div>
      </div>`;
  }

  if (typeof window.renderErrorBarChart === "function") {
    window.renderErrorBarChart(
      "miceErrorChart",
      classic.mice_avg_error,
      mixed.mice_avg_error,
    );
  }

  if (typeof window.renderDetectionBarChart === "function") {
    window.renderDetectionBarChart(
      "elephantChart",
      classic.elephant_detected,
      classic.elephant_total,
      mixed.elephant_detected,
      mixed.elephant_total,
    );
  }

  const classicTop10 = classic.top10 || [];
  const mixedTop10 = mixed.top10 || [];
  const combinedTop10 = classicTop10.map((cItem) => {
    const mItem = mixedTop10.find((m) => m.ip === cItem.ip);
    return {
      ip: cItem.ip,
      is_hot: cItem.is_hot ?? cItem.is_elephant ?? false,
      true_count: cItem.true_count ?? 0,
      estimate: cItem.estimate ?? 0,
      mixed_estimate: mItem ? (mItem.estimate ?? 0) : 0,
    };
  });

  if (typeof window.renderTop10Table === "function") {
    window.renderTop10Table("heavyHittersTableBody", combinedTop10, {
      isComparison: true,
    });
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const runBtn = getElementByAnyId(["btnRunSimulation", "btnRun"]);
  const mixedBtn = getElementByAnyId(["btnRunMixedScript", "btnMixed"]);
  const classicTab = getElementByAnyId(["tab-classic"]);
  const mixedTab = getElementByAnyId(["tab-mixed"]);
  const compareTab = getElementByAnyId(["tab-compare"]);

  if (mixedBtn && mixedBtn.disabled) {
    mixedBtn.disabled = true;
    mixedBtn.classList.add("disabled", "opacity-50");
  }

  runBtn?.addEventListener("click", () => {
    const sourceSelect = document.getElementById("dataSourceSelect");
    const packetInput = document.getElementById("totalPacketsInput");

    const dataSource = sourceSelect ? sourceSelect.value : "synthetic";
    const params = {
      total_packets: packetInput ? parseInt(packetInput.value, 10) : 500000,
      seed: 42,
    };

    runSimulation(dataSource, params);
  });

  mixedBtn?.addEventListener("click", () => {
    if (!lastResponse || !lastResponse.results?.mixed) return;

    showMixedPanel();
    activateMixedControls();

    if (typeof bootstrap !== "undefined") {
      const tabTrigger = document.getElementById("tab-mixed");
      if (tabTrigger) {
        const tabInstance = bootstrap.Tab.getOrCreateInstance(tabTrigger);
        tabInstance.show();
      }
    }
  });

  classicTab?.addEventListener("click", showClassicPanel);
  mixedTab?.addEventListener("click", showMixedPanel);
  compareTab?.addEventListener("click", showComparisonTab);

  enableStepControls(false);
});
