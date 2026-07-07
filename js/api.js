/**
 * api.js — wrapper DUY NHẤT gọi backend.
 * Do [C] Hiếu viết theo API_contract.md. [B] Mai chỉ import và gọi hàm
 * simulate(), KHÔNG tự viết fetch logic trong app.js.
 *
 * Khi backend chưa chạy / cần dev offline: đổi import trong app.js từ
 *   import { simulate } from "./api.js";
 * sang
 *   import { simulate } from "./mock_data.js";
 

const BASE_URL = "http://localhost:8000";

/**
 * Gọi POST /api/simulate
 * @param {Object} payload - xem schema Request trong API_contract.md
 * @param {"classic"|"mixed"} payload.algorithm
 * @param {"synthetic"|"real"} payload.data_source
 * @param {number} payload.table_size
 * @param {number} [payload.n_hot]
 * @param {number} [payload.n_cold]
 * @param {number} [payload.gap_factor]
 * @param {number} [payload.total_packets]
 * @returns {Promise<Object>} response JSON đúng schema SimulationResponse
 * @throws {Error} nếu response không phải 2xx (bao gồm 422, 500)
 */
export async function simulate(payload) {
  let res;
  try {
    res = await fetch(`${BASE_URL}/api/simulate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  } catch (networkErr) {
    // Thường gặp: backend chưa chạy, hoặc lỗi CORS bị browser chặn im lặng
    throw new Error(
      `Không gọi được backend tại ${BASE_URL}. ` +
        `Kiểm tra: (1) uvicorn đã chạy port 8000 chưa, (2) CORS đã bật trong main.py chưa. ` +
        `Chi tiết: ${networkErr.message}`
    );
  }

  if (!res.ok) {
    let detail = "";
    try {
      const errBody = await res.json();
      detail = JSON.stringify(errBody.detail ?? errBody);
    } catch {
      // response không phải JSON, bỏ qua
    }
    throw new Error(`HTTP ${res.status} từ /api/simulate. ${detail}`);
  }

  return res.json();
}

/**
 * Kiểm tra nhanh backend có sống không (dùng để debug CORS/port khi demo).
 * @returns {Promise<boolean>}
 */
export async function checkHealth() {
  try {
    const res = await fetch(`${BASE_URL}/health`);
    return res.ok;
  } catch {
    return false;
  }
}
