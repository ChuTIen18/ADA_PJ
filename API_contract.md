# API Contract — Elephant/Mice CMS Demo

---

## Cổng & Môi trường

| Service | Cổng | Lệnh khởi động |
|---------|------|----------------|
| FastAPI backend | `8000` | `uvicorn app.main:app --reload --port 8000` |
| FE (VS Code Live Server) | `5500` | Mở `index.html` bằng Live Server extension |
| FE (mở file trực tiếp) | không có | Mở `index.html` bằng trình duyệt — vẫn cần CORS |

FE và BE chạy **2 server riêng biệt**, khác origin → bắt buộc cấu hình **CORS** trong `main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # dev: cho phép tất cả
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type"],
)
```

> ⚠️ Không có CORS → trình duyệt chặn request, FE không gọi được BE dù BE đang chạy bình thường.

---

## Base URL

```
http://localhost:8000
```

---

## Endpoint

### `POST /api/simulate`

Chạy mô phỏng thuật toán CMS (classic hoặc mixed) trên một bộ dữ liệu và trả về kết quả so sánh.

---

## Request

**Content-Type:** `application/json`

| Field | Type | Bắt buộc | Mô tả |
|---|---|---|---|
| `algorithm` | `string` | ✅ | `"classic"` (k=3) hoặc `"mixed"` (k_hot=2, k_cold=5) |
| `data_source` | `string` | ✅ | `"synthetic"` (data giả lập) hoặc `"real"` (data thực tế) |
| `n_hot` | `integer` | ✅ khi `synthetic` | Số lượng Elephant IP (VD: 5) |
| `n_cold` | `integer` | ✅ khi `synthetic` | Số lượng Mice IP (VD: 9995). Constraint: `n_hot + n_cold` = tổng IP duy nhất trong stream |
| `gap_factor` | `number` | ✅ khi `synthetic` | Tỉ lệ tần suất hot/cold — G > 1 (VD: 100). Xem mục Ghi chú kỹ thuật |
| `table_size` | `integer` | ✅ | Số ô đếm trong sketch (VD: 5000 ≈ 40KB RAM) |
| `total_packets` | `integer` | ✅ khi `synthetic` | Tổng số packet trong stream (VD: 10000000). Lưu ý: đây là số packet, không phải số IP |

**Ví dụ — Data giả lập:**

```json
{
  "algorithm": "mixed",
  "data_source": "synthetic",
  "n_hot": 5,
  "n_cold": 9995,
  "gap_factor": 100,
  "table_size": 5000,
  "total_packets": 10000000
}
```

**Ví dụ — Data thực tế:**

```json
{
  "algorithm": "classic",
  "data_source": "real",
  "table_size": 5000
}
```

---

## Response

**Content-Type:** `application/json`  
**Status:** `200 OK`

| Field | Type | Mô tả |
|---|---|---|
| `data_source` | `string` | `"synthetic"` hoặc `"real"` — để FE hiển thị nhãn rõ ràng |
| `algorithm` | `string` | Thuật toán đã chạy (`"classic"` hoặc `"mixed"`) |
| `elephant_detected` | `integer` | Số Elephant IP phát hiện đúng (nằm trong top estimate) |
| `elephant_total` | `integer` | Tổng số Elephant IP thực tế |
| `mice_avg_error` | `float` | Lỗi ước tính trung bình của Mice IP (0.12 = 12%). Xem công thức bên dưới |
| `top10` | `array` | Danh sách 10 IP có estimate cao nhất |
| `top10[].ip` | `string` | Địa chỉ IP |
| `top10[].true_count` | `integer` | Số lần xuất hiện thực tế |
| `top10[].estimate` | `integer` | Số lần ước tính bởi CMS |
| `top10[].is_elephant` | `boolean` | IP này có phải Elephant không |
| `real_meta` | `object \| null` | Chỉ có giá trị khi `data_source = "real"`, còn lại là `null` |
| `real_meta.hot_threshold_percent` | `float` | Ngưỡng % để xác định Elephant (VD: `0.05` = top 5% IP tần suất cao nhất) |
| `real_meta.total_unique_ips` | `integer` | Tổng số IP duy nhất trong dataset thực tế |

**Ví dụ — Data giả lập:**

```json
{
  "data_source": "synthetic",
  "algorithm": "mixed",
  "elephant_detected": 5,
  "elephant_total": 5,
  "mice_avg_error": 0.12,
  "real_meta": null,
  "top10": [
    {
      "ip": "10.0.0.1",
      "true_count": 95283,
      "estimate": 96100,
      "is_elephant": true
    },
    {
      "ip": "10.0.0.2",
      "true_count": 91047,
      "estimate": 92300,
      "is_elephant": true
    },
    {
      "ip": "192.168.1.44",
      "true_count": 1023,
      "estimate": 1089,
      "is_elephant": false
    }
  ]
}
```

**Ví dụ — Data thực tế:**

```json
{
  "data_source": "real",
  "algorithm": "classic",
  "elephant_detected": 4,
  "elephant_total": 6,
  "mice_avg_error": 0.31,
  "real_meta": {
    "hot_threshold_percent": 0.05,
    "total_unique_ips": 12483
  },
  "top10": [
    {
      "ip": "203.0.113.5",
      "true_count": 48201,
      "estimate": 61500,
      "is_elephant": true
    }
  ]
}
```

---

## Error Responses

| Status | Mô tả |
|---|---|
| `422 Unprocessable Entity` | Request thiếu field hoặc sai kiểu dữ liệu |
| `500 Internal Server Error` | Lỗi khi chạy thuật toán hoặc nạp dataset |

**Ví dụ lỗi 422:**

```json
{
  "detail": [
    {
      "loc": ["body", "algorithm"],
      "msg": "value is not a valid enum value",
      "type": "type_error.enum"
    }
  ]
}
```

---

## Luồng xử lý (FE → BE → FE)

Khi người dùng bấm nút **Run** trên giao diện web, luồng xử lý diễn ra như sau:

```
[B] Mai bấm nút "Run" trên index.html
        │
        ▼
app.js gọi simulate() từ api.js
        │
        ▼
fetch POST → http://localhost:8000/api/simulate
        │  body: { algorithm, data_source, n_hot, ... }
        │
        ▼  (qua CORS middleware)
FastAPI main.py nhận request
        │
        ▼
request_models.py validate dữ liệu (Pydantic)
        │  → 422 nếu sai field
        ▼
simulation_service.py chạy:
  ├── data_generator.py  ([D] Tiên) → sinh stream packets
  └── cms.py / cms_mixed.py ([A] Khoa) → chạy thuật toán
        │
        ▼
metrics.py tính mice_avg_error, elephant_detected
        │
        ▼
response_models.py đóng gói JSON
        │
        ▼
FastAPI trả 200 OK + JSON body
        │
        ▼
api.js nhận response.json()
        │
        ▼
app.js chuyển data → charts.js vẽ biểu đồ + bảng top-10
```

`api.js` (do **[C] Hiếu** viết) là wrapper duy nhất gọi BE — [B] Mai chỉ import hàm, không tự viết fetch:

```js
// frontend/js/api.js
export async function simulate(payload) {
  const res = await fetch("http://localhost:8000/api/simulate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}
```

---

## Ghi chú kỹ thuật

### Phân phối packet theo `gap_factor` — dành cho [D] Tiên

`data_generator.py` phân phối `total_packets` theo công thức Step Distribution:

- Mỗi hot IP nhận tần suất tỉ lệ `gap_factor × λ_c`
- Mỗi cold IP nhận tần suất tỉ lệ `λ_c` (chuẩn hoá sao cho tổng = `total_packets`)
- Constraint bắt buộc: `n_hot + n_cold` = tổng số IP duy nhất trong stream (`total_packets` là số packet, không phải số IP)

### Công thức `mice_avg_error` — dành cho [A] Khoa

`metrics.py` phải tính đúng công thức:

```
mice_avg_error = mean( (estimate_i - true_count_i) / true_count_i )
```

Trong đó:
- Chỉ tính trên tập **Mice IP** (`is_elephant = false`), **không** tính Elephant
- Kết quả trả về là số thập phân (VD: `0.12` tương đương 12%)
- FE hiển thị nhân 100 và thêm dấu `%`

> ⚠️ **[C] Hiếu và [A] Khoa phải đồng thuận về công thức này trước khi code `simulation_service.py`.**

### Field `real_meta` — dành cho [B] Mai

- Khi `data_source = "real"`: `real_meta` luôn được trả về (không phải `null`)
- FE dùng `hot_threshold_percent` để hiển thị chú thích: _"Elephant = top 5% IP tần suất cao nhất"_
- FE dùng `total_unique_ips` để hiển thị context dataset
- Khi `data_source = "synthetic"`: `real_meta = null`, FE bỏ qua field này

### So sánh song song (Bước 4 kịch bản DEMO) — dành cho [B] Mai & [C] Hiếu

FE tự lưu state 2 lần gọi API riêng (1 lần synthetic, 1 lần real) — **không cần thêm endpoint `/api/simulate/compare`**. FE chỉ enable tab "So sánh" khi đã có đủ cả 2 kết quả.

---

## Ghi chú cho từng thành viên

**[A] Khoa** — `cms.py`, `cms_mixed.py`, `simulation_service.py`, `metrics.py`  
Output của `simulation_service` phải khớp chính xác với response schema trên. Công thức `mice_avg_error` theo mục Ghi chú kỹ thuật — chốt với [C] trước khi code.

**[B] Mai** — `frontend/js/app.js`, `charts.js`  
Dùng `mock_data.js` (do [E] cung cấp) với đúng schema response trên để code UI. Khi [C] xong API thật, chỉ cần đổi nguồn data — không cần sửa logic hiển thị. Xử lý `real_meta` và tab So sánh theo Ghi chú kỹ thuật.

**[C] Hiếu** — `main.py`, `schemas/`, `api.js`, `README.md`  
Pydantic models trong `request_models.py` và `response_models.py` phải map 1-1 với bảng trên (bao gồm `real_meta`). Phối hợp [A] chốt công thức `mice_avg_error` trước khi code `simulation_service.py`.

**[D] Tiên** — `data_generator.py`, `presets.py`  
Output của `generate_step()` phải tương thích để `simulation_service.py` chạy được với schema request trên. Phân phối packet theo `gap_factor` đúng công thức trong Ghi chú kỹ thuật.

**[E] Thịnh** — `mock_data.js`, `sample_response.json`  
Copy đúng ví dụ response ở trên (bao gồm `real_meta: null`) vào `sample_response.json`. Đây là file [B] dùng để dev FE độc lập.

---
