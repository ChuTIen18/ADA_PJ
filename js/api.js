// frontend/js/api.js
// Sở hữu: C (Hiếu) — dù nằm trong frontend/js/, KHÔNG do B (Mai) viết,
// vì C là người hiểu rõ nhất schema request/response đã chốt (rules.md §3.4).
// B chỉ gọi callSimulate()/fetchPresets(), không tự viết fetch() trong app.js.

const API_BASE = "http://localhost:8000/api"; // đổi qua config nếu deploy khác

/**
 * Gọi GET /api/presets — lấy 3 bộ tham số mẫu (main / paper_faithful / stress).
 * @returns {Promise<Object>} { presets: [{ id, label, params }, ...] }
 */
async function fetchPresets() {
  const response = await fetch(`${API_BASE}/presets`, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  });

  const data = await response.json();

  if (!response.ok || data.error) {
    throw new Error(data?.error?.message || `fetchPresets failed: HTTP ${response.status}`);
  }

  return data;
}

/**
 * Gọi POST /api/simulate — MỘT request duy nhất trả về kết quả CẢ classic
 * lẫn mixed cùng lúc, chạy trên cùng 1 stream/seed (rules.md §3.4).
 * app.js (B) gọi hàm này đúng 1 lần rồi cache lại, không gọi lại khi chỉ
 * chuyển panel hiển thị classic/mixed/so-sánh.
 * @param {Object} payload - khớp schema SimulationRequest (rules.md §3.4)
 * @returns {Promise<Object>} khớp schema SimulationResponse
 */
async function callSimulate(payload) {
  const response = await fetch(`${API_BASE}/simulate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  const data = await response.json();

  // Khuôn lỗi chuẩn hoá: { error: { code, message } } — rules.md §3.5
  if (!response.ok || data.error) {
    throw new Error(data?.error?.message || `callSimulate failed: HTTP ${response.status}`);
  }

  return data;
}
