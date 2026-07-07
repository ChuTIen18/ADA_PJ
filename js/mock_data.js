// Mock Data Engine for Presentation & Testing
(() => {
  const MockDataRepository = {
    // 1. DATA GIẢ LẬP (SYNTHETIC DATA) - KỊCH BẢN BƯỚC 2
    synthetic: {
      classic: {
        data_source: "synthetic",
        algorithm: "classic",
        elephant_detected: 3,
        elephant_total: 5,
        mice_avg_error: 3.4, // ~340% lỗi như kịch bản
        real_meta: {
          hot_threshold_percent: 0.0005, // 5 / 10,000 IPs
          total_unique_ips: 10000,
        },
        top10: [
          {
            ip: "192.168.1.10",
            true_count: 450000,
            estimate: 452100,
            is_elephant: true,
          },
          {
            ip: "10.0.0.5",
            true_count: 380000,
            estimate: 385400,
            is_elephant: true,
          },
          {
            ip: "1.1.1.1",
            true_count: 310000,
            estimate: 420000,
            is_elephant: true,
          }, // Bị overestimate nặng
          {
            ip: "172.16.0.3",
            true_count: 2500,
            estimate: 290000,
            is_elephant: false,
          }, // Mice bị nhận nhầm thành Elephant (Va chạm hash)
          {
            ip: "192.168.1.50",
            true_count: 210000,
            estimate: 211000,
            is_elephant: true,
          },
          {
            ip: "8.8.8.8",
            thought_count: 1200,
            estimate: 185000,
            is_elephant: false,
          }, // Mice nhiễu cao
          {
            ip: "0.0.0.0",
            true_count: 190000,
            estimate: 140000,
            is_elephant: true,
          }, // Bị bỏ sót khỏi top đầu do nhiễu hàng xóm
          {
            ip: "192.168.2.1",
            true_count: 800,
            estimate: 95000,
            is_elephant: false,
          },
          {
            ip: "10.0.0.12",
            true_count: 450,
            estimate: 87000,
            is_elephant: false,
          },
          {
            ip: "172.16.5.9",
            true_count: 300,
            estimate: 82000,
            is_elephant: false,
          },
        ],
      },
      mixed: {
        data_source: "synthetic",
        algorithm: "mixed",
        elephant_detected: 5,
        elephant_total: 5, // Phát hiện chuẩn xác 5/5
        mice_avg_error: 0.12, // Lỗi Mice giảm sâu còn ~12%
        real_meta: {
          hot_threshold_percent: 0.0005,
          total_unique_ips: 10000,
        },
        top10: [
          {
            ip: "192.168.1.10",
            true_count: 450000,
            estimate: 450150,
            is_elephant: true,
          },
          {
            ip: "10.0.0.5",
            true_count: 380000,
            estimate: 380210,
            is_elephant: true,
          },
          {
            ip: "1.1.1.1",
            true_count: 310000,
            estimate: 310500,
            is_elephant: true,
          },
          {
            ip: "192.168.1.50",
            true_count: 210000,
            estimate: 210340,
            is_elephant: true,
          },
          {
            ip: "0.0.0.0",
            true_count: 190000,
            estimate: 190410,
            is_elephant: true,
          }, // Lên lại đúng vị trí
          {
            ip: "172.16.0.3",
            true_count: 2500,
            estimate: 2800,
            is_elephant: false,
          }, // Trả về đúng giá trị nhỏ
          {
            ip: "8.8.8.8",
            true_count: 1200,
            estimate: 1410,
            is_elephant: false,
          },
          {
            ip: "192.168.2.1",
            true_count: 800,
            estimate: 910,
            is_elephant: false,
          },
          {
            ip: "10.0.0.12",
            true_count: 450,
            estimate: 520,
            is_elephant: false,
          },
          {
            ip: "172.16.5.9",
            true_count: 300,
            estimate: 340,
            is_elephant: false,
          },
        ],
      },
    },

    // 2. DATA THỰC TẾ (REAL DATASET) - KỊCH BẢN BƯỚC 3 (Khớp cấu hình hình ảnh 5.4)
    real: {
      classic: {
        data_source: "real",
        algorithm: "classic",
        elephant_detected: 4,
        elephant_total: 6,
        mice_avg_error: 0.31, // Khớp chính xác 0.31 ở ảnh 5.4 của bạn
        real_meta: {
          hot_threshold_percent: 0.05,
          total_unique_ips: 74957,
        },
        top10: [
          {
            ip: "edams.ksc.nasa.gov",
            true_count: 6516,
            estimate: 7200,
            is_elephant: true,
          },
          {
            ip: "piweba4y.prodigy.com",
            true_count: 4846,
            estimate: 5100,
            is_elephant: true,
          },
          {
            ip: "ix-or1-27.ix.netcom.com",
            true_count: 3920,
            estimate: 4650,
            is_elephant: true,
          },
          {
            ip: "slv-in4.uu.net",
            true_count: 3110,
            estimate: 3990,
            is_elephant: true,
          },
          {
            ip: "tbl-mice-noise.net",
            true_count: 150,
            estimate: 3500,
            is_elephant: false,
          }, // Mice va chạm gây nhiễu
          {
            ip: "www-b2.proxy.aol.com",
            true_count: 2800,
            estimate: 2910,
            is_elephant: true,
          },
          {
            ip: "unicomp6.unicomp.net",
            true_count: 2540,
            estimate: 2100,
            is_elephant: true,
          },
        ],
      },
      mixed: {
        data_source: "real",
        algorithm: "mixed",
        elephant_detected: 6,
        elephant_total: 6, // Đạt hiệu suất tối đa
        mice_avg_error: 0.07, // Sai số giảm mạnh xuống còn 0.07
        real_meta: {
          hot_threshold_percent: 0.05,
          total_unique_ips: 74957,
        },
        top10: [
          {
            ip: "edams.ksc.nasa.gov",
            true_count: 6516,
            estimate: 6590,
            is_elephant: true,
          },
          {
            ip: "piweba4y.prodigy.com",
            true_count: 4846,
            estimate: 4890,
            is_elephant: true,
          },
          {
            ip: "ix-or1-27.ix.netcom.com",
            true_count: 3920,
            estimate: 3975,
            is_elephant: true,
          },
          {
            ip: "slv-in4.uu.net",
            true_count: 3110,
            estimate: 3150,
            is_elephant: true,
          },
          {
            ip: "www-b2.proxy.aol.com",
            true_count: 2800,
            estimate: 2840,
            is_elephant: true,
          },
          {
            ip: "unicomp6.unicomp.net",
            true_count: 2540,
            estimate: 2565,
            is_elephant: true,
          },
          {
            ip: "tbl-mice-noise.net",
            true_count: 150,
            estimate: 180,
            is_elephant: false,
          }, // Trả về đúng vị trí thấp
        ],
      },
    },
  };

  // Hàm global điều hướng bắn dữ liệu trực tiếp vào module hiển thị biểu đồ
  window.TriggerMockDataEngine = function (sourceType, algorithmType) {
    if (
      MockDataRepository[sourceType] &&
      MockDataRepository[sourceType][algorithmType]
    ) {
      const selectedDataset = MockDataRepository[sourceType][algorithmType];

      console.log(
        `[Mock Engine] Đang nạp nguồn: ${sourceType} | Thuật toán: ${algorithmType}`,
      );

      // Gọi hàm render đã viết sẵn ở app.js để map lên giao diện
      if (typeof window.RenderBackendAnalyticsData === "function") {
        window.RenderBackendAnalyticsData(selectedDataset);
      } else {
        console.error(
          "Không tìm thấy hàm RenderBackendAnalyticsData trên hệ thống!",
        );
      }
    } else {
      console.error("Tham số nguồn dữ liệu kiểm thử không hợp lệ!");
    }
  };
})();
// ==========================================
// 1. DATA GIẢ LẬP CHO TAB VISUALIZER (Cũ của bồ)
// ==========================================
const mockVisualizerInitialData = [
  "1.1.1.1",
  "10.0.0.5",
  "172.16.0.3", // ...đống IP cũ bồ đang chạy
];

// ==========================================
// 2. DATA GIẢ LẬP CHO TAB ANALYTICS (Nhét thêm vào đây)
// ==========================================
const mockRealAnalyticsData = {
  data_source: "real",
  algorithm: "classic",
  elephant_detected: 5, // Bắt trúng 5/5 Voi như kịch bản nói nhé
  elephant_total: 5,
  mice_avg_error: 12.5, // Sai số 12.5% cho Mixed CMS luôn
  real_meta: {
    hot_threshold_percent: 0.05,
    total_unique_ips: 74957,
  },
  top10: [
    {
      ip: "edams.ksc.nasa.gov",
      true_count: 6516,
      estimate: 6530,
      is_elephant: true,
    },
    {
      ip: "piweba4y.prodigy.com",
      true_count: 4846,
      estimate: 4890,
      is_elephant: true,
    },
    { ip: "192.168.1.50", true_count: 12, estimate: 14, is_elephant: false },
    { ip: "10.0.0.99", true_count: 5, estimate: 6, is_elephant: false },
  ],
};
